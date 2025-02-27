import argparse
import csv
from datetime import datetime
from pathlib import Path

from wca_result_csv.data.download_handler import process_zip_file


def download_wca(zip_url):
    target_files = [
        "WCA_export_Results.tsv",
        "WCA_export_Persons.tsv",
        "WCA_export_Competitions.tsv"
    ]  # the file to extract
    output_dir = Path("data")  # replace with the desired output directory

    if zip_url:
        # call the process_zip_file function to download and extract the file
        _ = process_zip_file(zip_url, target_files, output_dir)

    return [output_dir / file for file in target_files]


def load_person_data(persons_file):
    person_headers = ["subid", "name", "countryId", "gender", "id"]

    # Read the Persons.tsv file
    id2person = dict()
    with open(persons_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        # compare the headers with the person_headers
        if reader.fieldnames is None:
            raise ValueError("Headers are None")
        if set(reader.fieldnames) != set(person_headers):
            raise ValueError(f"Headers do not match: {set(reader.fieldnames)} != {set(person_headers)}")

        for row in reader:
            id2person[row["id"]] = row["name"]

    return id2person


def load_competition_data(competitions_file):
    id2competition = dict()
    with open(competitions_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            # use "id" as the key, and project only the fields: "year", "month", "day"
            id2competition[row["id"]] = {
                "year": row["year"],
                "month": row["month"],
                "day": row["day"],
            }

    return id2competition


def get_competition_date_range(id2comp):
    # Initialize min and max dates
    min_date = None
    max_date = None

    for comp in id2comp.values():
        # Create a date object from the year, month, and day
        comp_date = datetime(int(comp["year"]), int(comp["month"]), int(comp["day"]))

        # Update min and max dates
        if min_date is None or comp_date < min_date:
            min_date = comp_date
        if max_date is None or comp_date > max_date:
            max_date = comp_date

    return min_date, max_date


def load_results_data(results_file):
    comp_results = []
    with open(results_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            # project only the fields: "competitionId", "eventId", "best", "average", "personId"
            comp_results.append(
                {
                    "competitionId": row["competitionId"],
                    "eventId": row["eventId"],
                    "best": row["best"],
                    "average": row["average"],
                    "personId": row["personId"],
                }
            )

    return comp_results


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Download WCA data.")
    parser.add_argument("--zip_url", type=str, help="URL of the zip file to download", default=None)
    parser.add_argument("--event", type=str, help="Event ID to filter results", default="333")
    parser.add_argument("--top_n", type=int, help="Keep only the top N persons", default=20)
    parser.add_argument("--rank_type", type=str, choices=["best", "average"], help="best or average", default="best")
    args = parser.parse_args()

    extracted_files = download_wca(args.zip_url)

    id2person = load_person_data(extracted_files[1])
    id2comp = load_competition_data(extracted_files[2])

    comp_results = load_results_data(extracted_files[0])

    min_date, max_date = get_competition_date_range(id2comp)

    # Ensure we have valid dates
    if min_date is None or max_date is None:
        print("Error: No valid competition dates found")
        return
    now = datetime.now()
    max_date = min(max_date, now)
    print(f"Competition date range: {min_date} to {max_date}")

    # Generate headers for all months between min_date and max_date
    headers = ["personId", "personName"]
    month_keys = []
    current_date = min_date
    while current_date <= max_date:
        headers.append(current_date.strftime("%Y-%m"))
        month_keys.append(current_date.strftime("%Y-%m"))
        # Move to next month
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, current_date.day)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, current_date.day)

    # Create a dictionary to store best results by person and month
    person_results = {}
    for result in comp_results:
        if result["eventId"] != args.event:
            continue

        person_id = result["personId"]
        if person_id not in person_results:
            person_results[person_id] = {
                "personName": id2person.get(person_id, "Unknown"),
                "months": {m: float("inf") for m in month_keys},
                "best_so_far": {m: float("inf") for m in month_keys}
            }

        # Get competition date
        comp_info = id2comp[result["competitionId"]]
        comp_date = datetime(int(comp_info["year"]), int(comp_info["month"]), int(comp_info["day"]))
        month_key = comp_date.strftime("%Y-%m")

        # Update best result for this month if it's better (smaller) than existing
        try:
            best = int(result[args.rank_type])
            if best <= 0:
                best = float("inf")
        except ValueError:
            best = float("inf")

        person_results[person_id]["months"][month_key] = min(
            person_results[person_id]["months"][month_key],
            best
        )

    # Create a new dictionary to store the best results so far
    for person_id, data in person_results.items():
        prev_month = None
        for month in month_keys:
            if prev_month is None:
                data["best_so_far"][month] = data["months"][month]
            else:
                data["best_so_far"][month] = min(data["best_so_far"][prev_month], data["months"][month])
            prev_month = month

    people_to_keep = set()
    for month in reversed(month_keys):
        # get the top N persons with the best result so far
        top_persons = sorted(person_results.items(), key=lambda x: x[1]["best_so_far"][month], reverse=False)[:args.top_n]
        people_to_keep.update([x[0] for x in top_persons])

    # Keep only the persons in the people_to_keep
    person_results = {
        person_id: data for person_id, data in person_results.items()
        if person_id in people_to_keep
    }

    # Write to CSV file
    output_file = Path("data/person_best_history.csv")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for person_id, data in person_results.items():
            row = [person_id, data["personName"]]
            # Add results for each month in headers (skip personId and personName)
            for month in headers[2:]:
                # result = data["months"].get(month, "")
                result = data["best_so_far"].get(month, "")
                # Convert infinity back to empty string
                row.append("" if result == float("inf") else f"{result/100.0:.2f}")
            writer.writerow(row)

    print(f"Results written to {output_file}")


if __name__ == "__main__":
    main()

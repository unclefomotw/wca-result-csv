import argparse
import csv
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


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Download WCA data.")
    parser.add_argument("--zip_url", type=str, help="URL of the zip file to download", default=None)
    args = parser.parse_args()

    extracted_files = download_wca(args.zip_url)

    id2person = load_person_data(extracted_files[1])
    id2comp = load_competition_data(extracted_files[2])

    results_file = extracted_files[0]
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

    print(comp_results[0])
    print(comp_results[1])


if __name__ == "__main__":
    main()

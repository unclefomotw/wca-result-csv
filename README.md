# WCA Result CSV

A Python tool for processing and analyzing World Cube Association (WCA) competition results in CSV format.

## Purpose

This repository contains tools to work with WCA (World Cube Association) competition results data. It provides functionality to:
- Process WCA competition results
- Analyze competition data
- Generate CSV reports from WCA results

## Requirements

- Python 3.12 or higher
- Poetry (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wca-result-csv.git
cd wca-result-csv
```

2. Install dependencies using Poetry:
```bash
poetry install
```

This will create a virtual environment and install all required dependencies.

## Project Structure

```
wca-result-csv/
├── data/           # Data files directory
├── src/            # Source code
│   └── wca_result_csv/
│       ├── data/           # Data processing modules
│       └── result_analysis/# Analysis modules
├── tests/          # Test files
├── pyproject.toml  # Project configuration
└── poetry.lock     # Lock file for dependencies
```

## Usage

1. Activate the Poetry virtual environment:
```bash
poetry shell
```

2. Run the desired script (example):
```bash
# zip url available at: https://www.worldcubeassociation.org/export/results
python -m wca_result_csv.result_analysis.33_people_best_history \
  --zip_url "https://assets.worldcubeassociation.org/export/results/WCA_export052_20250221T000205Z.tsv.zip"
```

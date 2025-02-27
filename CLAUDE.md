# WCA Result CSV Project Guide

## Commands
- **Install**: `poetry install`
- **Run script**: `poetry run python -m wca_result_csv.result_analysis.33_people_best_history [options]`
- **Lint**: `poetry run ruff check .`
- **Format**: `poetry run ruff format .`
- **Test**: `poetry run pytest`
- **Single test**: `poetry run pytest tests/path_to_test.py::test_function_name -v`

## Code Style
- **Project Structure**: "Src" pattern with code under `src/wca_result_csv/`
- **Imports**: Standard library first, then third-party, then local
- **Quotes**: Double quotes for string literals
- **Typing**: Use type hints (Python 3.12+)
- **Docstrings**: Function docstrings with Args, Returns, Raises sections
- **Error Handling**: Use explicit exception types, handle gracefully
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **PEP8**: Follow PEP8 conventions for Python code
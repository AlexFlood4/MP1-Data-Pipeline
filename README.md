# MP1 Data Pipeline

This project is a command-line data pipeline that loads a CSV file, validates it, cleans it, and saves the cleaned result. Data moves through the pipeline in order: the input and configuration files are checked and loaded, the data is validated, the cleaning steps are applied, and the cleaned data is saved to the output path along with a printed cleaning report. `pipeline.py` coordinates this workflow, while the reusable modules live in `src/` and the settings live in `config/config.yaml`, so a different compatible CSV can be cleaned by changing only the command-line paths and the configuration. `src/utils.py` sets up logging and checks that input files exist, and `src/data_loaders.py` loads CSV, JSON, and YAML files based on their extension. `src/data_validator.py` makes sure the required columns exist and removes rows whose numeric columns contain values that cannot be converted to numbers. `src/data_processor.py` removes duplicate rows, rows with missing values, and outliers, and builds the cleaning report. `src/data_output.py` saves the cleaned data as a CSV file, creating the output folder if it does not exist.

## Example

```bash
python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
```

Output:

```text
14:42:56 DEBUG    __main__ — Arguments parsed: input=fixtures/sample_data.csv, output=output/clean.csv, config=config/config.yaml
14:42:56 INFO     src.utils — Input file validated: fixtures/sample_data.csv
14:42:56 INFO     src.utils — Input file validated: config/config.yaml
14:42:56 INFO     src.data_loaders — Loaded CSV file: fixtures/sample_data.csv (100 rows)
14:42:56 INFO     src.data_loaders — Loaded YAML file: config/config.yaml
14:42:56 WARNING  src.data_validator — Invalid numeric value in rating at row 94: not_available
14:42:56 WARNING  src.data_validator — Invalid numeric value in rating at row 95: error
14:42:56 WARNING  src.data_validator — Removed 2 rows with invalid numeric values in rating
14:42:56 DEBUG    src.data_validator — Validation: 100 → 98 rows (98 valid, 2 removed)
14:42:56 INFO     __main__ — Validation complete: 100 → 98 rows
14:42:56 DEBUG    src.data_processor — remove_duplicates: 98 → 96 rows (2 removed)
14:42:56 DEBUG    src.data_processor — handle_missing: 96 → 94 rows (2 removed)
14:42:56 DEBUG    src.data_processor — rating: method=iqr, threshold=1.5, lower=43.625, upper=106.625, removed=2
14:42:56 INFO     __main__ — Processing complete: 98 → 92 rows
14:42:56 DEBUG    src.data_output — Saved 92 rows to output/clean.csv
14:42:56 INFO     __main__ — Saved cleaned data to output/clean.csv

Cleaning report:
{
  "rows_before": 98,
  "rows_after": 92,
  "rows_removed": 6,
  "columns_before": 5,
  "columns_after": 5,
  "columns_removed": 0
}
```

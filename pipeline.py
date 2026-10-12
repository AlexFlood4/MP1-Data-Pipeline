
"""
Data Processing Pipeline - CLI Template
DS 3500 - MP1
Usage:
python pipeline.py --input data.csv --output clean.csv
python pipeline.py --input data.csv --output results.json --format json --verbose
"""
import argparse
import json
import logging
import sys

from src import (
    create_cleaning_report,
    load_data,
    process_data,
    save_data,
    setup_logging,
    validate_dataframe,
    validate_input,
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Data processing pipeline")
    parser.add_argument("--input", "-i", required=True,
                        help="Path to the input file")
    parser.add_argument("--config", "-c", required=True,
                        help="Path to the YAML configuration file")
    parser.add_argument("--output", "-o", required=True,
                        help="Path to the output file")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")
    return parser.parse_args()


def main():
    """Main pipeline function."""
    args = parse_arguments()
    setup_logging(args.verbose)
    logger.debug("Arguments parsed: input=%s, output=%s, config=%s",
                 args.input, args.output, args.config)

    if not validate_input(args.input):
        sys.exit(1)

    if not validate_input(args.config):
        sys.exit(1)

    try:
        data = load_data(args.input)
        config = load_data(args.config)
    except ValueError:
        sys.exit(1)

    required_columns = config["validation"]["required_columns"]
    numeric_columns = config["validation"]["numeric_columns"]

    rows_loaded = len(data)
    try:
        data = validate_dataframe(data, required_columns, numeric_columns)
    except ValueError:
        sys.exit(1)
    logger.info("Validation complete: %d → %d rows", rows_loaded, len(data))

    data_before = data.copy()

    try:
        data_cleaned = process_data(data, config)
    except ValueError:
        sys.exit(1)

    report = create_cleaning_report(data_before, data_cleaned)
    logger.info("Processing complete: %d → %d rows",
                report["rows_before"], report["rows_after"])

    output_path = save_data(data_cleaned, args.output)
    logger.info("Saved cleaned data to %s", output_path)

    print("\nCleaning report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

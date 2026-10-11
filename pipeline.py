
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
from pathlib import Path

import pandas as pd
import yaml

from data_processor import process_data, create_cleaning_report

logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure logging for the pipeline."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


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


def validate_input(filepath):
    """Check whether the input path exists and is a file."""
    if not Path(filepath).is_file():
        logger.error("Input file not found: %s", filepath)
        return False
    logger.info("Input file validated: %s", filepath)
    return True


def load_csv(filepath):
    """Load a CSV file into a pandas DataFrame."""
    df = pd.read_csv(filepath)
    logger.info("Loaded CSV file: %s (%d rows)", filepath, len(df))
    return df


def load_json(filepath):
    """Load a JSON file into a Python object."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info("Loaded JSON file: %s", filepath)
    return data


def load_yaml(filepath):
    """Load a YAML file into a Python object."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    logger.info("Loaded YAML file: %s", filepath)
    return data


def load_data(filepath):
    """Pick the right loader based on the file extension."""
    path = Path(filepath)
    ext = path.suffix.lower()

    if ext == ".csv":
        return load_csv(path)
    elif ext == ".json":
        return load_json(path)
    elif ext == ".yaml":
        return load_yaml(path)
    else:
        logger.error("Unsupported file format: %s", ext)
        raise ValueError(f"Unsupported file format: {ext}")


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

    data_before = data.copy()

    try:
        data_cleaned = process_data(data, config)
    except ValueError:
        sys.exit(1)

    report = create_cleaning_report(data_before, data_cleaned)
    print(json.dumps(report, indent=2))
    logger.info("Processing complete: %d → %d rows",
                report["rows_before"], report["rows_after"])

    data_cleaned.to_csv(args.output, index=False)
    logger.info("Saved cleaned data to %s", args.output)


if __name__ == "__main__":
    main()

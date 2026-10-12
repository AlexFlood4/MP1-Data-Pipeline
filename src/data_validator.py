# src/data_validator.py
import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be numeric.
    """
    rows_before = len(df)

    for col in required_columns:
        if col not in df.columns:
            logger.error("Missing required column: %s", col)
            raise ValueError(f"Missing required column: {col}")

    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    logger.warning("Invalid numeric value in %s at row %s: %s", col, i, value)
                    invalid_rows.append(i)

        df = df.drop(index=invalid_rows)
        if invalid_rows:
            logger.warning("Removed %d rows with invalid numeric values in %s",
                           len(invalid_rows), col)

        #convert to a numeric data type
        df[col] = pd.to_numeric(df[col])

    logger.debug("Validation: %d → %d rows (%d valid, %d removed)",
                 rows_before, len(df), len(df), rows_before - len(df))
    return df

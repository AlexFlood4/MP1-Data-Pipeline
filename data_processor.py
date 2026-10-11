# data_processor.py
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)
    result = df.drop_duplicates()
    rows_after = len(result)
    logger.debug("remove_duplicates: %d → %d rows (%d removed)",
                 rows_before, rows_after, rows_before - rows_after)
    return result


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        rows_before = len(df)
        result = df.dropna(axis=0)
        rows_after = len(result)
        logger.debug("handle_missing: %d → %d rows (%d removed)",
                     rows_before, rows_after, rows_before - rows_after)
    elif axis == "columns":
        cols_before = df.shape[1]
        result = df.dropna(axis=1)
        cols_after = result.shape[1]
        logger.debug("handle_missing: %d → %d columns (%d removed)",
                     cols_before, cols_after, cols_before - cols_after)
    else:
        logger.error("Unsupported axis: %s", axis)
        raise ValueError(f"Unsupported axis: {axis}")
    return result


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    result = df
    for column in columns:
        if column not in result.columns:
            logger.warning("Column not found: %s", column)
            continue
        if not pd.api.types.is_numeric_dtype(result[column]):
            logger.warning("Column is not numeric: %s", column)
            continue

        values = result[column]
        rows_before = len(result)

        if method == "iqr":
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            is_outlier = (values < lower) | (values > upper)
            result = result[~is_outlier]
            logger.debug("%s: method=%s, threshold=%s, lower=%s, upper=%s, removed=%d",
                         column, method, threshold, lower, upper,
                         rows_before - len(result))
        else:
            mean = values.mean()
            std = values.std()
            if std == 0 or pd.isna(std):
                is_outlier = pd.Series(False, index=values.index)
            else:
                is_outlier = ((values - mean) / std).abs() > threshold
            result = result[~is_outlier]
            logger.debug("%s: method=%s, threshold=%s, removed=%d",
                         column, method, threshold, rows_before - len(result))

    return result


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    settings = config["processing"]
    result = df

    if settings.get("remove_duplicates", False):
        result = remove_duplicates(result)

    missing = settings.get("missing", {})
    if missing.get("enabled", False):
        result = handle_missing(result, axis=missing["axis"])

    outliers = settings.get("outliers", {})
    if outliers.get("enabled", False):
        result = remove_outliers(result, outliers["columns"],
                                 outliers["method"], outliers["threshold"])

    return result


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before, columns_before = df_before.shape
    rows_after, columns_after = df_after.shape
    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }

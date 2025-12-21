from __future__ import annotations

import pandas as pd

from eda_cli.core import (
    compute_quality_flags,
    correlation_matrix,
    flatten_summary_for_print,
    missing_table,
    summarize_dataset,
    top_categories,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [10, 20, 30, None],
            "height": [140, 150, 160, 170],
            "city": ["A", "B", "A", None],
        }
    )


def test_summarize_dataset_basic():
    df = _sample_df()
    summary = summarize_dataset(df)

    assert summary.n_rows == 4
    assert summary.n_cols == 3
    assert any(c.name == "age" for c in summary.columns)
    assert any(c.name == "city" for c in summary.columns)

    summary_df = flatten_summary_for_print(summary)
    assert "name" in summary_df.columns
    assert "missing_share" in summary_df.columns


def test_missing_table_and_quality_flags():
    df = _sample_df()
    missing_df = missing_table(df)

    assert "missing_count" in missing_df.columns
    assert missing_df.loc["age", "missing_count"] == 1

    summary = summarize_dataset(df)
    flags = compute_quality_flags(summary, missing_df)
    assert 0.0 <= flags["quality_score"] <= 1.0


def test_correlation_and_top_categories():
    df = _sample_df()
    corr = correlation_matrix(df)
    # корреляция между age и height существует
    assert "age" in corr.columns or corr.empty is False

    top_cats = top_categories(df, max_columns=5, top_k=2)
    assert "city" in top_cats
    city_table = top_cats["city"]
    assert "value" in city_table.columns
    assert len(city_table) <= 2


def test_has_constant_columns_flag():
    df = pd.DataFrame(
        {
            "constant_col": ["A", "A", "A", "A"],
            "varying_col": [1, 2, 3, 4],
        }
    )
    
    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df)

    assert flags["has_constant_columns"] is True

    df_no_const = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4],
            "col2": ["A", "B", "C", "D"],
        }
    )
    
    summary_no_const = summarize_dataset(df_no_const)
    missing_no_const = missing_table(df_no_const)
    flags_no_const = compute_quality_flags(summary_no_const, missing_no_const)
    
    assert flags_no_const["has_constant_columns"] is False


def test_has_high_cardinality_categoricals_flag():
    df_high_card = pd.DataFrame(
        {
            "user_id": list(range(20)),
            "country": [f"Country_{i}" for i in range(20)],
            "age": [25, 30, 35, 40] * 5,
        }
    )
    
    summary_high = summarize_dataset(df_high_card)
    missing_high = missing_table(df_high_card)
    flags_high = compute_quality_flags(summary_high, missing_high)

    assert flags_high["has_high_cardinality_categoricals"] is True

    df_normal_card = pd.DataFrame(
        {
            "country": ["USA", "UK", "USA", "UK", "Canada"] * 4,
            "age": [25, 30, 35, 40] * 5,
        }
    )
    
    summary_normal = summarize_dataset(df_normal_card)
    missing_normal = missing_table(df_normal_card)
    flags_normal = compute_quality_flags(summary_normal, missing_normal)
    
    assert flags_normal["has_high_cardinality_categoricals"] is False


def test_has_suspicious_id_duplicates_flag():
    df_dup_id = pd.DataFrame(
        {
            "user_id": [1, 2, 2, 3, 3, 4],
            "name": ["Alice", "Bob", "Bob", "Charlie", "Charlie", "David"],
            "age": [25, 30, 30, 35, 35, 40],
        }
    )
    
    summary_dup = summarize_dataset(df_dup_id)
    missing_dup = missing_table(df_dup_id)
    flags_dup = compute_quality_flags(summary_dup, missing_dup)

    assert flags_dup["has_suspicious_id_duplicates"] is True

    df_unique_id = pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4, 5, 6],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"],
            "age": [25, 30, 35, 40, 45, 50],
        }
    )
    
    summary_unique = summarize_dataset(df_unique_id)
    missing_unique = missing_table(df_unique_id)
    flags_unique = compute_quality_flags(summary_unique, missing_unique)
    
    assert flags_unique["has_suspicious_id_duplicates"] is False
    df_no_id = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
        }
    )
    
    summary_no_id = summarize_dataset(df_no_id)
    missing_no_id = missing_table(df_no_id)
    flags_no_id = compute_quality_flags(summary_no_id, missing_no_id)
    
    assert flags_no_id["has_suspicious_id_duplicates"] is False


def test_quality_score_considers_new_flags():
    df_problematic = pd.DataFrame(
        {
            "user_id": [1, 1, 2, 2],
            "constant": ["A", "A", "A", "A"],
            "high_card": ["val1", "val2", "val3", "val4"],
        }
    )
    
    summary_prob = summarize_dataset(df_problematic)
    missing_prob = missing_table(df_problematic)
    flags_prob = compute_quality_flags(summary_prob, missing_prob)

    df_good = pd.DataFrame(
        {
            "user_id": list(range(1, 101)),
            "category": (["A", "B", "C"] * 33) + ["A"],
            "value": list(range(100)),
        }
    )
    
    summary_good = summarize_dataset(df_good)
    missing_good = missing_table(df_good)
    flags_good = compute_quality_flags(summary_good, missing_good)

    assert flags_prob["quality_score"] < flags_good["quality_score"]
    assert 0.0 <= flags_prob["quality_score"] <= 1.0
    assert 0.0 <= flags_good["quality_score"] <= 1.0
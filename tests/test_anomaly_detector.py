import pandas as pd

from models.anomaly_detector import (
    add_deviation_features,
    detect_anomalies,
)


def make_behavior_dataframe():
    return pd.DataFrame({
        "user_id": [1] * 12,
        "username": ["user_1"] * 12,
        "login_hour": [9, 9, 10, 9, 10, 9, 10, 9, 10, 9, 23, 2],
        "actions_count": [30, 32, 31, 29, 33, 30, 31, 29, 32, 30, 120, 140],
        "session_duration": [40, 42, 41, 39, 43, 40, 41, 39, 42, 40, 160, 180],
        "failed_attempts": [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 6, 7],
        "ip_changed": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        "device_changed": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        "location_changed": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    })


def test_add_deviation_features_creates_required_columns():
    df = make_behavior_dataframe()

    result = add_deviation_features(df)

    assert "login_hour_dev" in result.columns
    assert "actions_dev" in result.columns
    assert "duration_dev" in result.columns
    assert "failed_dev" in result.columns


def test_detect_anomalies_adds_result_columns():
    df = make_behavior_dataframe()

    result = detect_anomalies(df)

    assert "anomaly" in result.columns
    assert "anomaly_label" in result.columns
    assert "model_reason" in result.columns


def test_detect_anomalies_returns_only_expected_labels():
    df = make_behavior_dataframe()

    result = detect_anomalies(df)

    assert set(result["anomaly"].unique()).issubset({1, -1})
    assert set(result["anomaly_label"].unique()).issubset({"Норма", "Аномалія"})


def test_detect_anomalies_detects_at_least_one_anomaly_on_extreme_rows():
    df = make_behavior_dataframe()

    result = detect_anomalies(df)

    assert (result["anomaly"] == -1).sum() >= 1
import pandas as pd

from services.risk_service import calculate_user_risk_score


def test_risk_score_returns_zero_for_empty_dataframe():
    df = pd.DataFrame()

    result = calculate_user_risk_score(df)

    assert result == 0


def test_risk_score_is_within_valid_range():
    df = pd.DataFrame({
        "anomaly": [1, -1, -1, 1],
        "behavior_outlier": [0, 1, 1, 0],
        "ip_changed": [0, 1, 0, 0],
        "device_changed": [0, 0, 1, 0],
        "location_changed": [0, 0, 0, 1],
        "failed_dev": [0, 3, 4, 1],
    })

    result = calculate_user_risk_score(df)

    assert 0 <= result <= 100


def test_risk_score_increases_for_more_anomalies():
    normal_user = pd.DataFrame({
        "anomaly": [1, 1, 1, 1],
        "behavior_outlier": [0, 0, 0, 0],
        "ip_changed": [0, 0, 0, 0],
        "device_changed": [0, 0, 0, 0],
        "location_changed": [0, 0, 0, 0],
        "failed_dev": [0, 0, 0, 0],
    })

    risky_user = pd.DataFrame({
        "anomaly": [-1, -1, -1, 1],
        "behavior_outlier": [1, 1, 1, 0],
        "ip_changed": [1, 1, 0, 0],
        "device_changed": [1, 0, 1, 0],
        "location_changed": [0, 1, 1, 0],
        "failed_dev": [5, 4, 3, 1],
    })

    normal_score = calculate_user_risk_score(normal_user)
    risky_score = calculate_user_risk_score(risky_user)

    assert risky_score > normal_score
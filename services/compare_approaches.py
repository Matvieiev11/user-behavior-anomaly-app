from time import perf_counter

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from models.anomaly_detector import add_deviation_features, detect_anomalies


BASE_FEATURES = [
    "login_hour",
    "actions_count",
    "session_duration",
    "failed_attempts",
    "ip_changed",
    "device_changed",
    "location_changed",
]


def _validate_columns(data: pd.DataFrame, columns: list[str]) -> None:
    missing_columns = [column for column in columns if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing columns for comparison: {missing_columns}")


def _build_metrics(
    approach_name: str,
    result: pd.DataFrame,
    anomaly_column: str,
    execution_time: float,
    uses_profile: bool,
    has_explanation: bool,
    has_risk_score: bool,
) -> dict:
    total_sessions = len(result)
    anomalies_count = int((result[anomaly_column] == -1).sum())
    anomaly_rate = round((anomalies_count / total_sessions) * 100, 2) if total_sessions else 0

    return {
        "Підхід": approach_name,
        "Сеансів": total_sessions,
        "Аномалій": anomalies_count,
        "Частка аномалій, %": anomaly_rate,
        "Час виконання, с": round(execution_time, 3),
        "Профіль користувача": "так" if uses_profile else "ні",
        "Пояснення причин": "так" if has_explanation else "ні",
        "Risk Score": "так" if has_risk_score else "ні",
    }


def evaluate_rule_based_baseline(data: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    _validate_columns(data, BASE_FEATURES + ["user_id"])

    start_time = perf_counter()
    result = data.copy()
    result["rule_based_prediction"] = 1

    for user_id, user_data in result.groupby("user_id"):
        user_index = result["user_id"] == user_id

        actions_threshold = user_data["actions_count"].quantile(0.95)
        duration_threshold = user_data["session_duration"].quantile(0.95)

        suspicious = (
            (result.loc[user_index, "failed_attempts"] >= 5)
            | (result.loc[user_index, "ip_changed"] == 1)
            | (result.loc[user_index, "device_changed"] == 1)
            | (result.loc[user_index, "location_changed"] == 1)
            | (result.loc[user_index, "actions_count"] >= actions_threshold)
            | (result.loc[user_index, "session_duration"] >= duration_threshold)
        )

        result.loc[user_index, "rule_based_prediction"] = suspicious.map(
            {True: -1, False: 1}
        )

    execution_time = perf_counter() - start_time
    return result, execution_time


def evaluate_isolation_forest_without_profile(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, float]:
    _validate_columns(data, BASE_FEATURES + ["user_id"])

    start_time = perf_counter()
    result_parts = []

    for user_id, user_data in data.groupby("user_id"):
        user_data = user_data.copy()

        if len(user_data) < 10:
            user_data["iforest_base_prediction"] = 1
            result_parts.append(user_data)
            continue

        features = user_data[BASE_FEATURES]
        scaled_features = StandardScaler().fit_transform(features)

        model = IsolationForest(
            n_estimators=200,
            contamination=0.10,
            random_state=42,
        )

        user_data["iforest_base_prediction"] = model.fit_predict(scaled_features)
        result_parts.append(user_data)

    result = pd.concat(result_parts).sort_index()
    execution_time = perf_counter() - start_time
    return result, execution_time


def evaluate_statistical_profile(data: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    _validate_columns(data, BASE_FEATURES + ["user_id"])

    start_time = perf_counter()
    result = add_deviation_features(data)
    result["statistical_prediction"] = 1

    for user_id, user_data in result.groupby("user_id"):
        user_index = result["user_id"] == user_id

        actions_threshold = user_data["actions_dev"].quantile(0.95)
        duration_threshold = user_data["duration_dev"].quantile(0.95)
        login_threshold = user_data["login_hour_dev"].quantile(0.95)
        failed_threshold = max(3, user_data["failed_attempts"].quantile(0.95))

        suspicious = (
            (result.loc[user_index, "actions_dev"] >= actions_threshold)
            | (result.loc[user_index, "duration_dev"] >= duration_threshold)
            | (result.loc[user_index, "login_hour_dev"] >= login_threshold)
            | (result.loc[user_index, "failed_attempts"] >= failed_threshold)
        )

        result.loc[user_index, "statistical_prediction"] = suspicious.map(
            {True: -1, False: 1}
        )

    execution_time = perf_counter() - start_time
    return result, execution_time


def evaluate_proposed_approach(data: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    start_time = perf_counter()
    result = detect_anomalies(data)
    execution_time = perf_counter() - start_time
    return result, execution_time


def compare_detection_approaches(data: pd.DataFrame) -> pd.DataFrame:
    comparison_rows = []

    rule_result, rule_time = evaluate_rule_based_baseline(data)
    comparison_rows.append(
        _build_metrics(
            "Rule-based baseline",
            rule_result,
            "rule_based_prediction",
            rule_time,
            uses_profile=False,
            has_explanation=True,
            has_risk_score=False,
        )
    )

    iforest_result, iforest_time = evaluate_isolation_forest_without_profile(data)
    comparison_rows.append(
        _build_metrics(
            "Isolation Forest без профілювання",
            iforest_result,
            "iforest_base_prediction",
            iforest_time,
            uses_profile=False,
            has_explanation=False,
            has_risk_score=False,
        )
    )

    statistical_result, statistical_time = evaluate_statistical_profile(data)
    comparison_rows.append(
        _build_metrics(
            "Статистичний підхід",
            statistical_result,
            "statistical_prediction",
            statistical_time,
            uses_profile=True,
            has_explanation=True,
            has_risk_score=False,
        )
    )

    proposed_result, proposed_time = evaluate_proposed_approach(data)
    comparison_rows.append(
        _build_metrics(
            "Запропонований підхід",
            proposed_result,
            "anomaly",
            proposed_time,
            uses_profile=True,
            has_explanation=True,
            has_risk_score=True,
        )
    )

    return pd.DataFrame(comparison_rows)


def print_detection_approaches_comparison(data: pd.DataFrame) -> None:
    comparison = compare_detection_approaches(data)

    print("\n Порівняння підходів до виявлення аномалій ")
    print(comparison.to_string(index=False))
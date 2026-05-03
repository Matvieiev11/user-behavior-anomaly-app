import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "login_hour",
    "actions_count",
    "session_duration",
    "failed_attempts",
    "ip_changed",
    "device_changed",
    "location_changed",
    "login_hour_dev",
    "actions_dev",
    "duration_dev",
    "failed_dev",
]


def add_deviation_features(data):
    df = data.copy()

    df["login_hour_dev"] = 0.0
    df["actions_dev"] = 0.0
    df["duration_dev"] = 0.0
    df["failed_dev"] = 0.0

    for user_id, user_data in df.groupby("user_id"):
        normal_profile = user_data[
            (user_data["ip_changed"] == 0)
            & (user_data["device_changed"] == 0)
            & (user_data["location_changed"] == 0)
            & (user_data["failed_attempts"] <= 1)
        ]

        if normal_profile.empty:
            normal_profile = user_data

        login_median = normal_profile["login_hour"].median()
        actions_median = normal_profile["actions_count"].median()
        duration_median = normal_profile["session_duration"].median()
        failed_median = normal_profile["failed_attempts"].median()

        user_index = df["user_id"] == user_id

        df.loc[user_index, "login_hour_dev"] = (
            df.loc[user_index, "login_hour"] - login_median
        ).abs()

        df.loc[user_index, "actions_dev"] = (
            df.loc[user_index, "actions_count"] - actions_median
        ).abs()

        df.loc[user_index, "duration_dev"] = (
            df.loc[user_index, "session_duration"] - duration_median
        ).abs()

        df.loc[user_index, "failed_dev"] = (
            df.loc[user_index, "failed_attempts"] - failed_median
        ).abs()

    return df


def add_behavior_outliers(df):
    result = df.copy()
    result["behavior_outlier"] = 0
    result["behavior_reason"] = ""

    for user_id, user_data in result.groupby("user_id"):
        user_index = result["user_id"] == user_id

        actions_thr = user_data["actions_dev"].quantile(0.85)
        duration_thr = user_data["duration_dev"].quantile(0.85)
        login_thr = user_data["login_hour_dev"].quantile(0.85)

        min_actions_dev = 10
        min_duration_dev = 8
        min_login_dev = 3

        for index, row in result[user_index].iterrows():
            reasons = []

            if row["actions_dev"] >= actions_thr and row["actions_dev"] > min_actions_dev:
                reasons.append("activity")

            if row["duration_dev"] >= duration_thr and row["duration_dev"] > min_duration_dev:
                reasons.append("duration")

            if row["login_hour_dev"] >= login_thr and row["login_hour_dev"] > min_login_dev:
                reasons.append("login_time")

            if reasons:
                result.at[index, "behavior_outlier"] = 1
                result.at[index, "behavior_reason"] = ", ".join(reasons)

    return result


def detect_with_isolation_forest(df):
    result_parts = []

    for user_id, user_data in df.groupby("user_id"):
        user_data = user_data.copy()

        if len(user_data) < 10:
            user_data["iforest_prediction"] = 1
            user_data["iforest_score"] = 0
            result_parts.append(user_data)
            continue

        features = user_data[FEATURE_COLUMNS]

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        model = IsolationForest(
            n_estimators=200,
            contamination=0.10,
            random_state=42
        )

        user_data["iforest_prediction"] = model.fit_predict(scaled_features)
        user_data["iforest_score"] = model.decision_function(scaled_features)

        result_parts.append(user_data)

    return pd.concat(result_parts).sort_index()


def compute_behavior_anomaly_score(df):
    result = df.copy()

    result["behavior_anomaly_score"] = 0.0
    result["model_reason"] = ""

    for user_id, user_data in result.groupby("user_id"):
        user_index = result["user_id"] == user_id

        actions_base = user_data["actions_dev"].median() + 1
        duration_base = user_data["duration_dev"].median() + 1
        failed_base = user_data["failed_dev"].median() + 1

        login_norm = result.loc[user_index, "login_hour_dev"] / 12
        actions_norm = result.loc[user_index, "actions_dev"] / actions_base
        duration_norm = result.loc[user_index, "duration_dev"] / duration_base
        failed_norm = result.loc[user_index, "failed_dev"] / failed_base

        context_score = (
            result.loc[user_index, "ip_changed"] * 0.4
            + result.loc[user_index, "device_changed"] * 0.3
            + result.loc[user_index, "location_changed"] * 0.3
        )

        score = (
            login_norm * 20
            + actions_norm * 30
            + duration_norm * 30
            + failed_norm * 15
            + context_score * 10
        )

        result.loc[user_index, "behavior_anomaly_score"] = score.clip(0, 100)

    return result

def add_extreme_behavior_anomalies(df):
    result = df.copy()

    result["extreme_behavior_anomaly"] = 0
    result["extreme_behavior_reason"] = ""

    for user_id, user_data in result.groupby("user_id"):
        user_index = result["user_id"] == user_id

        if len(user_data) < 20:
            continue

        actions_thr = user_data["actions_dev"].quantile(0.95)
        duration_thr = user_data["duration_dev"].quantile(0.95)
        login_thr = user_data["login_hour_dev"].quantile(0.95)

        # Мінімальні абсолютні пороги
        min_actions_dev = 30
        min_duration_dev = 35
        min_login_dev = 7

        for index, row in result[user_index].iterrows():
            reasons = []

            activity_extreme = (
                row["actions_dev"] >= actions_thr
                and row["actions_dev"] >= min_actions_dev
            )

            duration_extreme = (
                row["duration_dev"] >= duration_thr
                and row["duration_dev"] >= min_duration_dev
            )

            login_extreme = (
                row["login_hour_dev"] >= login_thr
                and row["login_hour_dev"] >= min_login_dev
            )

            if activity_extreme:
                reasons.append("activity")

            if duration_extreme:
                reasons.append("duration")

            if login_extreme:
                reasons.append("login_time")

            # аномалією стає тільки сесія з мінімум 2 сильними відхиленнями
            if len(reasons) >= 2:
                result.at[index, "extreme_behavior_anomaly"] = 1
                result.at[index, "extreme_behavior_reason"] = ", ".join(reasons)

            # якщо одна метрика дуже сильно вилітає за межі
            elif activity_extreme and row["actions_dev"] >= min_actions_dev * 1.7:
                result.at[index, "extreme_behavior_anomaly"] = 1
                result.at[index, "extreme_behavior_reason"] = "activity"

            elif duration_extreme and row["duration_dev"] >= min_duration_dev * 1.7:
                result.at[index, "extreme_behavior_anomaly"] = 1
                result.at[index, "extreme_behavior_reason"] = "duration"

            elif login_extreme and row["login_hour_dev"] >= min_login_dev * 1.5:
                result.at[index, "extreme_behavior_anomaly"] = 1
                result.at[index, "extreme_behavior_reason"] = "login_time"

    return result

def classify_behavior_anomalies(df):
    result = df.copy()
    result["anomaly"] = 1
    result["model_reason"] = ""

    for user_id, user_data in result.groupby("user_id"):
        user_index = result["user_id"] == user_id

        iforest_anomaly = (
            result.loc[user_index, "iforest_prediction"] == -1
            if "iforest_prediction" in result.columns
            else False
        )

        extreme_behavior_anomaly = (
            result.loc[user_index, "extreme_behavior_anomaly"] == 1
            if "extreme_behavior_anomaly" in result.columns
            else False
        )

        final_anomaly = iforest_anomaly | extreme_behavior_anomaly

        result.loc[user_index, "anomaly"] = final_anomaly.map({
            True: -1,
            False: 1
        })

    for index, row in result.iterrows():
        reasons = []

        extreme_reason = str(row.get("extreme_behavior_reason", ""))
        behavior_reason = str(row.get("behavior_reason", ""))

        if "activity" in extreme_reason or "activity" in behavior_reason:
            reasons.append("activity")

        if "duration" in extreme_reason or "duration" in behavior_reason:
            reasons.append("duration")

        if "login_time" in extreme_reason or "login_time" in behavior_reason:
            reasons.append("login_time")

        if row.get("failed_attempts", 0) >= 5:
            reasons.append("failed_attempts")

        if not reasons and row.get("anomaly", 1) == -1:
            reasons.append("combined_behavior")

        result.at[index, "model_reason"] = ", ".join(reasons)

    result["anomaly_label"] = result["anomaly"].map({
        1: "Норма",
        -1: "Аномалія"
    })

    return result

def detect_anomalies(data):
    df = add_deviation_features(data)
    df = add_behavior_outliers(df)

    missing_columns = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns for anomaly detection: {missing_columns}")

    df = detect_with_isolation_forest(df)
    df = compute_behavior_anomaly_score(df)
    df = add_extreme_behavior_anomalies(df)
    df = classify_behavior_anomalies(df)

    return df

def evaluate_model(result_df):
    return None

def compare_models(result_df):
    comparison = {
        "Behavioral Model": {
            "detected_anomalies": int((result_df["anomaly"] == -1).sum()),
            "total_records": len(result_df),
        }
    }

    if "iforest_prediction" in result_df.columns:
        comparison["Isolation Forest"] = {
            "detected_anomalies": int((result_df["iforest_prediction"] == -1).sum()),
            "total_records": len(result_df),
        }

    return comparison
def calculate_user_risk_score(user_data):
    total_sessions = len(user_data)

    if total_sessions == 0:
        return 0

    anomalies_count = len(user_data[user_data["anomaly"] == -1])

    behavior_outliers = (
        int(user_data["behavior_outlier"].sum())
        if "behavior_outlier" in user_data.columns
        else 0
    )

    ip_changes = (
        int(user_data["ip_changed"].sum())
        if "ip_changed" in user_data.columns
        else 0
    )

    device_changes = (
        int(user_data["device_changed"].sum())
        if "device_changed" in user_data.columns
        else 0
    )

    location_changes = (
        int(user_data["location_changed"].sum())
        if "location_changed" in user_data.columns
        else 0
    )

    if "failed_dev" in user_data.columns:
        avg_failed_dev = float(user_data["failed_dev"].mean())
    elif "failed_attempts" in user_data.columns:
        avg_failed_dev = float(user_data["failed_attempts"].mean())
    else:
        avg_failed_dev = 0

    anomaly_ratio = anomalies_count / total_sessions
    behavior_ratio = behavior_outliers / total_sessions

    ip_rate = ip_changes / total_sessions
    device_rate = device_changes / total_sessions
    location_rate = location_changes / total_sessions

    context_rate = (ip_rate + device_rate + location_rate) / 3

    anomaly_count_risk = min(anomalies_count * 5, 50)
    anomaly_ratio_risk = min(anomaly_ratio * 100, 25)
    behavior_risk = min(behavior_ratio * 25, 15)
    failed_risk = min(avg_failed_dev * 2.5, 10)

    context_risk = 0
    if anomalies_count > 0:
        context_risk = min(context_rate * 20, 10)

    risk_score = (
        anomaly_count_risk
        + anomaly_ratio_risk
        + behavior_risk
        + failed_risk
        + context_risk
    )

    if anomalies_count == 0:
        risk_score = min(risk_score, 25)
    elif anomalies_count <= 3:
        risk_score = min(risk_score, 45)
    elif anomalies_count <= 5:
        risk_score = min(risk_score, 65)

    return min(100, round(risk_score))
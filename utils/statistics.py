def get_user_statistics(data):
    stats = {}

    users = data["user_id"].unique()

    for user in users:
        user_data = data[data["user_id"] == user]

        total_sessions = len(user_data)
        avg_duration = user_data["session_duration"].mean()
        avg_actions = user_data["actions_count"].mean()
        avg_login_hour = user_data["login_hour"].mean()
        anomalies_count = len(user_data[user_data["anomaly"] == -1])

        stats[user] = {
            "total_sessions": total_sessions,
            "avg_duration": round(avg_duration, 2),
            "avg_actions": round(avg_actions, 2),
            "avg_login_hour": round(avg_login_hour, 2),
            "anomalies_count": anomalies_count
        }

    return stats
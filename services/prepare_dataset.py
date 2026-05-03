from pathlib import Path
import random
import pandas as pd

INPUT_FILE = Path("data/linux_auth_logs_labeled.csv")
OUTPUT_FILE = Path("data/linux_behavior_ready.csv")

def prepare_real_dataset(
    sample_size=20000,
    min_records_per_user=15,
    max_users=500
):
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return None

    df = pd.read_csv(INPUT_FILE)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "username", "source_ip"])

    # Залишаємо тільки користувачів з достатньою історією
    user_counts = df["username"].value_counts()
    valid_users = user_counts[user_counts >= min_records_per_user].index
    df = df[df["username"].isin(valid_users)]

    # Обмежуємо кількість користувачів
    top_users = df["username"].value_counts().head(max_users).index
    df = df[df["username"].isin(top_users)]

    # Збалансована вибірка по користувачах
    if sample_size and len(df) > sample_size:
        users_count = df["username"].nunique()
        records_per_user = max(min_records_per_user, sample_size // users_count)

        sampled_parts = []

        for username, user_data in df.groupby("username"):
            take_count = min(len(user_data), records_per_user)
            sampled_parts.append(
                user_data.sample(n=take_count, random_state=42)
            )

        df = pd.concat(sampled_parts, ignore_index=True)

        if len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)

    # Повторна фільтрація після sample
    user_counts = df["username"].value_counts()
    valid_users = user_counts[user_counts >= min_records_per_user].index
    df = df[df["username"].isin(valid_users)].reset_index(drop=True)

    df = df.sort_values(by=["username", "timestamp"]).reset_index(drop=True)

    # Основні поведінкові ознаки
    df["login_hour"] = df["timestamp"].dt.hour
    df["user_id"] = pd.factorize(df["username"])[0] + 1

    df["attempts"] = df["attempts"].fillna(0).astype(int)
    df["status_lower"] = df["status"].astype(str).str.lower()
    df["service_lower"] = df["service"].astype(str).str.lower()
    df["protocol_lower"] = df["protocol"].astype(str).str.lower()

    # failed_attempts
    df["failed_attempts"] = df["attempts"]
    df.loc[df["status_lower"] == "success", "failed_attempts"] = 0

    # actions_count
    service_activity = {
        "ssh": 35,
        "login": 30,
        "sudo": 55,
        "su": 60,
        "cron": 15,
    }

    protocol_bonus = {
        "tcp": 5,
        "udp": 3,
    }

    random.seed(42)

    df["service_base"] = df["service_lower"].map(service_activity).fillna(25)
    df["protocol_bonus"] = df["protocol_lower"].map(protocol_bonus).fillna(2)

    df["status_bonus"] = df["status_lower"].apply(
        lambda x: 10 if x == "failed" else 0
    )

    df["noise"] = [
        random.randint(-5, 8) for _ in range(len(df))
    ]

    df["actions_count"] = (
        df["service_base"]
        + df["attempts"] * 4
        + df["protocol_bonus"]
        + df["status_bonus"]
        + df["noise"]
    ).clip(lower=1).astype(int)

    # session_duration
    service_duration = {
        "ssh": 45,
        "login": 35,
        "sudo": 18,
        "su": 15,
        "cron": 8,
    }

    df["session_duration"] = (
        15
        + df["attempts"] * 3
        + df["service_lower"].map(service_duration).fillna(20)
    ).astype(int)

    df.loc[df["status_lower"] == "failed", "session_duration"] = (
        df["attempts"] * 2 + 2
    ).clip(lower=1)

    # ip_changed
    typical_ip = df.groupby("username")["source_ip"].agg(
        lambda x: x.value_counts().idxmax()
    )

    df["typical_ip"] = df["username"].map(typical_ip)
    df["ip_changed"] = (df["source_ip"] != df["typical_ip"]).astype(int)

    # location_changed
    df["ip_region"] = df["source_ip"].astype(str).str.split(".").str[0]

    typical_region = df.groupby("username")["ip_region"].agg(
        lambda x: x.value_counts().idxmax()
    )

    df["typical_region"] = df["username"].map(typical_region)
    df["location_changed"] = (df["ip_region"] != df["typical_region"]).astype(int)

    # device_changed
    df["device_signature"] = (
        df["protocol"].fillna("unknown").astype(str)
        + "_"
        + df["service"].fillna("unknown").astype(str)
        + "_"
        + df["port"].astype(str)
    )

    typical_device = df.groupby("username")["device_signature"].agg(
        lambda x: x.value_counts().idxmax()
    )

    df["typical_device"] = df["username"].map(typical_device)
    df["device_changed"] = (df["device_signature"] != df["typical_device"]).astype(int)

    result = df[
        [
            "user_id",
            "username",
            "login_hour",
            "actions_count",
            "session_duration",
            "failed_attempts",
            "ip_changed",
            "device_changed",
            "location_changed",
            "service",
            "status",
            "source_ip",
            "server",
            "protocol",
            "port",
        ]
    ].copy()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Prepared dataset saved to: {OUTPUT_FILE}")
    print(f"Rows: {len(result)}")
    print(f"Users: {result['user_id'].nunique()}")
    print(f"Min records per user: {result['username'].value_counts().min()}")
    print(f"Max records per user: {result['username'].value_counts().max()}")
    print()
    print("Columns:")
    print(list(result.columns))

    return result


if __name__ == "__main__":
    prepare_real_dataset(
        sample_size=20000,
        min_records_per_user=15,
        max_users=500
    )
from pathlib import Path

import pandas as pd

import services.prepare_dataset as prepare_dataset


def create_raw_auth_log(path: Path):
    rows = []

    for user_index in range(2):
        username = f"user_{user_index + 1}"

        for i in range(15):
            rows.append({
                "timestamp": f"2026-01-01 {8 + (i % 4):02d}:00:00",
                "source_ip": f"10.0.{user_index}.{i % 3 + 1}",
                "server": "server-1",
                "username": username,
                "service": "ssh" if i % 2 == 0 else "login",
                "attempts": 1 if i % 5 != 0 else 4,
                "status": "success" if i % 5 != 0 else "failed",
                "port": 22,
                "protocol": "tcp",
                "comment": "test event",
                "anomaly_label": "normal",
            })

    pd.DataFrame(rows).to_csv(path, index=False)


def test_prepare_real_dataset_creates_ready_csv(tmp_path, monkeypatch):
    input_file = tmp_path / "linux_auth_logs_labeled.csv"
    output_file = tmp_path / "linux_behavior_ready.csv"

    create_raw_auth_log(input_file)

    monkeypatch.setattr(prepare_dataset, "INPUT_FILE", input_file)
    monkeypatch.setattr(prepare_dataset, "OUTPUT_FILE", output_file)

    result = prepare_dataset.prepare_real_dataset(
        sample_size=None,
        min_records_per_user=15,
        max_users=10,
    )

    assert result is not None
    assert output_file.exists()


def test_prepare_real_dataset_contains_required_columns(tmp_path, monkeypatch):
    input_file = tmp_path / "linux_auth_logs_labeled.csv"
    output_file = tmp_path / "linux_behavior_ready.csv"

    create_raw_auth_log(input_file)

    monkeypatch.setattr(prepare_dataset, "INPUT_FILE", input_file)
    monkeypatch.setattr(prepare_dataset, "OUTPUT_FILE", output_file)

    result = prepare_dataset.prepare_real_dataset(
        sample_size=None,
        min_records_per_user=15,
        max_users=10,
    )

    expected_columns = {
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
    }

    assert expected_columns.issubset(set(result.columns))


def test_prepare_real_dataset_returns_none_if_input_missing(tmp_path, monkeypatch):
    input_file = tmp_path / "missing.csv"
    output_file = tmp_path / "linux_behavior_ready.csv"

    monkeypatch.setattr(prepare_dataset, "INPUT_FILE", input_file)
    monkeypatch.setattr(prepare_dataset, "OUTPUT_FILE", output_file)

    result = prepare_dataset.prepare_real_dataset()

    assert result is None
    assert not output_file.exists()
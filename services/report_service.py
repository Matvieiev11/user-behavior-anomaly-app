from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from translations import translations

REPORT_FILE = Path("data/analysis_report.pdf")
CHART_DIR = Path("data/report_charts")
FONT_PATH = "C:/Windows/Fonts/arial.ttf"
BOLD_FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"

def register_fonts():
    pdfmetrics.registerFont(TTFont("AppFont", FONT_PATH))
    pdfmetrics.registerFont(TTFont("AppFont-Bold", BOLD_FONT_PATH))

def tr(language, key):
    return translations.get(language, translations["uk"]).get(key, key)

def _risk_level(score, language="uk"):
    if score < 30:
        return tr(language, "pdf_low")
    if score < 70:
        return tr(language, "pdf_medium")
    return tr(language, "pdf_high")

def _format_reason(reason_text, language="uk"):
    if not reason_text:
        return "-"

    reason_map = {
        "activity": tr(language, "reason_high_activity"),
        "duration": tr(language, "reason_unusual_duration"),
        "login_time": tr(language, "reason_unusual_login_time"),
        "failed_attempts": tr(language, "reason_failed_attempts"),
        "combined_behavior": tr(language, "reason_combined_behavior"),
    }

    reasons = [r.strip() for r in str(reason_text).split(",") if r.strip()]
    translated = [reason_map.get(reason, reason) for reason in reasons]

    return ", ".join(translated) if translated else "-"

def _table_style(header_bg="#E5E7EB"):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "AppFont-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "AppFont"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ])

def _normal_table_style():
    return TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "AppFont"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ])

def _get_basic_metrics(user_data, risk_score, language="uk"):
    total_sessions = len(user_data)
    anomalies_count = len(user_data[user_data["anomaly"] == -1])
    anomaly_rate = round((anomalies_count / total_sessions) * 100, 2) if total_sessions else 0

    typical_time = round(float(user_data["login_hour"].median()), 2)
    typical_activity = round(float(user_data["actions_count"].median()), 2)
    typical_duration = round(float(user_data["session_duration"].median()), 2)

    ip_changes = int(user_data["ip_changed"].sum()) if "ip_changed" in user_data.columns else 0
    device_changes = int(user_data["device_changed"].sum()) if "device_changed" in user_data.columns else 0
    location_changes = int(user_data["location_changed"].sum()) if "location_changed" in user_data.columns else 0

    max_dev = max([
        (tr(language, "activity_short"), float(user_data["actions_dev"].max())),
        (tr(language, "login_time_short"), float(user_data["login_hour_dev"].max())),
        (tr(language, "duration_short"), float(user_data["duration_dev"].max())),
    ], key=lambda x: x[1])

    return {
        "total_sessions": total_sessions,
        "anomalies_count": anomalies_count,
        "anomaly_rate": anomaly_rate,
        "typical_time": typical_time,
        "typical_activity": typical_activity,
        "typical_duration": typical_duration,
        "ip_changes": ip_changes,
        "device_changes": device_changes,
        "location_changes": location_changes,
        "max_dev": max_dev,
        "risk_score": int(round(risk_score)),
        "risk_level": _risk_level(risk_score, language),
    }

def _build_risk_factors(user_data, metrics, language="uk"):
    factors = []

    if metrics["anomalies_count"] > 0:
        factors.append(tr(language, "pdf_factor_anomalies"))

    if "model_reason" in user_data.columns:
        reasons_text = " ".join(user_data["model_reason"].fillna("").astype(str).tolist())

        if "activity" in reasons_text:
            factors.append(tr(language, "pdf_factor_activity"))

        if "duration" in reasons_text:
            factors.append(tr(language, "pdf_factor_duration"))

        if "login_time" in reasons_text:
            factors.append(tr(language, "pdf_factor_login_time"))

        if "failed_attempts" in reasons_text:
            factors.append(tr(language, "pdf_factor_failed"))

    if user_data["failed_attempts"].mean() > 1:
        if tr(language, "pdf_factor_failed") not in factors:
            factors.append(tr(language, "pdf_factor_failed"))

    if (
        metrics["ip_changes"] > 0
        or metrics["device_changes"] > 0
        or metrics["location_changes"] > 0
    ):
        factors.append(tr(language, "pdf_factor_context"))

    if not factors:
        factors.append(tr(language, "behavior_within_normal_range"))

    return factors

def _build_recommendations(metrics, language="uk"):
    recommendations = [
        tr(language, "pdf_recommendation_1"),
        tr(language, "pdf_recommendation_2"),
    ]

    if metrics["risk_score"] >= 70:
        recommendations.append(tr(language, "pdf_recommendation_3"))

    recommendations.append(tr(language, "pdf_recommendation_4"))

    return recommendations

def _save_user_charts(user_data, language="uk"):
    plt.rcParams["font.family"] = "Arial"
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    activity_path = CHART_DIR / "activity_chart.png"
    deviation_path = CHART_DIR / "deviation_chart.png"
    normal = user_data[user_data["anomaly"] == 1]
    anomalies = user_data[user_data["anomaly"] == -1]

    # Графік активності
    plt.figure(figsize=(7.2, 3.6))
    plt.scatter(
        normal["login_hour"],
        normal["actions_count"],
        label=tr(language, "plot_normal"),
        s=28,
        alpha=0.9,
    )
    plt.scatter(
        anomalies["login_hour"],
        anomalies["actions_count"],
        label=tr(language, "plot_anomaly"),
        s=36,
        alpha=0.95,
    )
    plt.title(tr(language, "pdf_activity_chart"))
    plt.xlabel(tr(language, "plot_login_hour"))
    plt.ylabel(tr(language, "plot_actions_count"))
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(activity_path, dpi=160)
    plt.close()

    # Графік відхилень
    x = range(len(user_data))

    plt.figure(figsize=(7.2, 3.6))
    plt.plot(
        x,
        user_data["login_hour_dev"],
        marker="o",
        markersize=2.5,
        linewidth=1,
        label=tr(language, "plot_login_deviation"),
    )
    plt.plot(
        x,
        user_data["actions_dev"],
        marker="o",
        markersize=2.5,
        linewidth=1,
        label=tr(language, "plot_activity_deviation"),
    )
    plt.plot(
        x,
        user_data["duration_dev"],
        marker="o",
        markersize=2.5,
        linewidth=1,
        label=tr(language, "plot_duration_deviation"),
    )

    if not anomalies.empty:
        plt.scatter(
            anomalies.index,
            anomalies["actions_dev"],
            s=45,
            label=tr(language, "plot_anomaly"),
            edgecolors="black",
            linewidths=0.5,
            zorder=5,
        )

    plt.title(tr(language, "pdf_deviation_chart"))
    plt.xlabel(tr(language, "plot_session"))
    plt.ylabel(tr(language, "plot_deviation_value"))
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(deviation_path, dpi=160)
    plt.close()

    return activity_path, deviation_path

def _build_top_anomalies_table(user_data, language="uk", limit=12):
    anomalies = user_data[user_data["anomaly"] == -1].copy()

    styles = getSampleStyleSheet()

    cell_style = ParagraphStyle(
        name="PdfTableCell",
        parent=styles["Normal"],
        fontName="AppFont",
        fontSize=8,
        leading=10,
    )

    header_style = ParagraphStyle(
        name="PdfTableHeader",
        parent=styles["Normal"],
        fontName="AppFont-Bold",
        fontSize=8,
        leading=10,
    )

    if anomalies.empty:
        return Paragraph(tr(language, "pdf_no_anomalous_sessions"), cell_style)

    if "behavior_anomaly_score" in anomalies.columns:
        anomalies = anomalies.sort_values(by="behavior_anomaly_score", ascending=False)

    anomalies = anomalies.head(limit).reset_index(drop=False)

    rows = [[
        Paragraph(tr(language, "pdf_session"), header_style),
        Paragraph(tr(language, "pdf_login_hour"), header_style),
        Paragraph(tr(language, "pdf_actions"), header_style),
        Paragraph(tr(language, "pdf_duration"), header_style),
        Paragraph(tr(language, "pdf_failed_attempts"), header_style),
        Paragraph(tr(language, "pdf_reason"), header_style),
    ]]

    for _, row in anomalies.iterrows():
        session_number = int(row["index"]) + 1 if "index" in row else "-"
        reason = _format_reason(row.get("model_reason", ""), language)

        rows.append([
            Paragraph(str(session_number), cell_style),
            Paragraph(str(row.get("login_hour", "-")), cell_style),
            Paragraph(str(row.get("actions_count", "-")), cell_style),
            Paragraph(str(row.get("session_duration", "-")), cell_style),
            Paragraph(str(row.get("failed_attempts", "-")), cell_style),
            Paragraph(reason, cell_style),
        ])

    table = Table(
        rows,
        colWidths=[42, 62, 65, 70, 78, 205],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "AppFont-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "AppFont"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))

    return table

def generate_pdf_report(
    user,
    analyzed_user_data,
    file_path,
    risk_score,
    language="uk"
):
    register_fonts()
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    username = user.get("username", "unknown") if user else "unknown"
    email = user.get("email", "unknown") if user else "unknown"

    analyzed_username = analyzed_user_data.iloc[0]["username"]
    analyzed_user_id = analyzed_user_data.iloc[0]["user_id"]

    metrics = _get_basic_metrics(analyzed_user_data, risk_score, language)
    risk_factors = _build_risk_factors(analyzed_user_data, metrics, language)
    recommendations = _build_recommendations(metrics, language)

    activity_chart, deviation_chart = _save_user_charts(
        analyzed_user_data,
        language
    )

    styles = getSampleStyleSheet()

    for style_name in styles.byName:
        styles[style_name].fontName = "AppFont"

    styles["Title"].fontName = "AppFont-Bold"
    styles["Heading2"].fontName = "AppFont-Bold"
    styles["Heading3"].fontName = "AppFont-Bold"

    styles.add(ParagraphStyle(
        name="ReportBody",
        parent=styles["Normal"],
        fontName="AppFont",
        fontSize=10,
        leading=14,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="ReportList",
        parent=styles["Normal"],
        fontName="AppFont",
        fontSize=10,
        leading=14,
        leftIndent=12,
        spaceAfter=5,
    ))

    doc = SimpleDocTemplate(
        str(REPORT_FILE),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    summary_text = (
        tr(language, "pdf_no_anomalies_summary").format(username=analyzed_username)
        if metrics["anomalies_count"] == 0
        else tr(language, "pdf_summary_text").format(
            username=analyzed_username,
            sessions=metrics["total_sessions"],
            anomalies=metrics["anomalies_count"],
            risk=metrics["risk_score"],
            level=metrics["risk_level"],
        )
    )

    max_dev_text = f"{metrics['max_dev'][0]} (+{metrics['max_dev'][1]:.1f})"

    content = []

    # Титульна сторінка
    content.extend([
        Paragraph(tr(language, "pdf_report_title"), styles["Title"]),
        Spacer(1, 14),

        Paragraph(tr(language, "pdf_analysis_info"), styles["Heading2"]),
    ])

    info_cell_style = ParagraphStyle(
        name="InfoTableCell",
        parent=styles["Normal"],
        fontName="AppFont",
        fontSize=9,
        leading=11,
    )

    info_label_style = ParagraphStyle(
        name="InfoTableLabel",
        parent=styles["Normal"],
        fontName="AppFont-Bold",
        fontSize=9,
        leading=11,
    )

    info_table = Table([
        [
            Paragraph(tr(language, "pdf_generated_by"), info_label_style),
            Paragraph(f"{username} ({email})", info_cell_style),
        ],
        [
            Paragraph(tr(language, "pdf_analyzed_user"), info_label_style),
            Paragraph(f"{analyzed_username} (ID: {analyzed_user_id})", info_cell_style),
        ],
        [
            Paragraph(tr(language, "pdf_date"), info_label_style),
            Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), info_cell_style),
        ],
        [
            Paragraph(tr(language, "pdf_file"), info_label_style),
            Paragraph(str(file_path), info_cell_style),
        ],
    ], colWidths=[170, 350])

    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    content.extend([
        info_table,
        Spacer(1, 16),
    ])

    # Короткий висновок
    content.extend([
        Paragraph(tr(language, "pdf_executive_summary"), styles["Heading2"]),
        Paragraph(summary_text, styles["ReportBody"]),
        Spacer(1, 12),
    ])

    # Метрики
    metrics_table = Table([
        [tr(language, "pdf_metric"), tr(language, "pdf_value")],
        [tr(language, "pdf_total_sessions"), metrics["total_sessions"]],
        [tr(language, "pdf_anomalies"), metrics["anomalies_count"]],
        [tr(language, "pdf_anomaly_rate"), f"{metrics['anomaly_rate']}%"],
        [tr(language, "pdf_risk_score"), f"{metrics['risk_score']}/100"],
        [tr(language, "pdf_risk_level"), metrics["risk_level"]],
        [tr(language, "pdf_typical_login_time"), metrics["typical_time"]],
        [tr(language, "pdf_typical_activity"), metrics["typical_activity"]],
        [tr(language, "pdf_typical_duration"), metrics["typical_duration"]],
        [tr(language, "pdf_ip_changes"), metrics["ip_changes"]],
        [tr(language, "pdf_device_changes"), metrics["device_changes"]],
        [tr(language, "pdf_location_changes"), metrics["location_changes"]],
        [tr(language, "pdf_max_deviation"), max_dev_text],
    ], colWidths=[250, 270])
    metrics_table.setStyle(_table_style())

    content.extend([
        Paragraph(tr(language, "pdf_key_metrics"), styles["Heading2"]),
        metrics_table,
        Spacer(1, 16),
    ])

    # Фактори ризику
    content.append(Paragraph(tr(language, "pdf_risk_factors"), styles["Heading2"]))

    for factor in risk_factors:
        content.append(Paragraph(f"- {factor}", styles["ReportList"]))

    # Графіки
    content.extend([
        PageBreak(),

        Paragraph(tr(language, "pdf_charts"), styles["Heading2"]),
        Spacer(1, 8),

        Paragraph(tr(language, "pdf_activity_chart"), styles["Heading3"]),
        Spacer(1, 4),
        Image(str(activity_chart), width=470, height=225),
        Spacer(1, 12),

        Paragraph(tr(language, "pdf_deviation_chart"), styles["Heading3"]),
        Spacer(1, 4),
        Image(str(deviation_chart), width=470, height=225),

        PageBreak(),
    ])

    # Топ аномалій
    content.extend([
        Paragraph(tr(language, "pdf_anomalous_sessions"), styles["Heading2"]),
        _build_top_anomalies_table(analyzed_user_data, language, limit=12),
        Spacer(1, 16),
    ])

    # Рекомендації
    content.append(Paragraph(tr(language, "pdf_recommendations"), styles["Heading2"]))

    for recommendation in recommendations:
        content.append(Paragraph(f"- {recommendation}", styles["ReportList"]))

    content.append(Spacer(1, 12))

    # Методології
    content.extend([
        Paragraph(tr(language, "pdf_methodology"), styles["Heading2"]),
        Paragraph(tr(language, "pdf_methodology_text"), styles["ReportBody"]),
    ])

    doc.build(content)

    return REPORT_FILE
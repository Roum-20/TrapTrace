import streamlit as st
import pandas as pd
import json
import datetime
import plotly.express as px
from pathlib import Path
from fpdf import FPDF

st.set_page_config(page_title="Honeypot Dashboard", layout="wide")
st.title("🛡️ Honeypot Graphical Attack Dashboard")

LOG_DIR = Path("honeypot_logs")
LOG_DIR.mkdir(exist_ok=True)

def load_logs(log_file):
    logs = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except:
                continue
    return logs

def analyze_logs(logs):
    hourly = {}
    ip_stats = {}

    for log in logs:
        try:
            timestamp = datetime.datetime.fromisoformat(log["timestamp"])
            hour = timestamp.replace(minute=0, second=0, microsecond=0)
            hourly[hour] = hourly.get(hour, 0) + 1

            ip = log["remote_ip"]
            port = log["port"]
            payload = log["data"].strip()

            if ip not in ip_stats:
                ip_stats[ip] = {
                    "attempts": 0,
                    "ports": set(),
                    "payloads": set(),
                    "first": timestamp,
                    "last": timestamp
                }

            ip_stats[ip]["attempts"] += 1
            ip_stats[ip]["ports"].add(port)
            ip_stats[ip]["payloads"].add(payload)
            ip_stats[ip]["last"] = timestamp
        except:
            continue

    results = []
    for ip, s in ip_stats.items():
        duration = (s["last"] - s["first"]).total_seconds()
        score = s["attempts"] * 0.5 + len(s["ports"]) * 5 + len(s["payloads"]) * 4 + duration / 60
        score = min(round(score, 2), 100)
        severity = "Low" if score <= 30 else "Medium" if score <= 70 else "High"
        results.append({
            "IP": ip,
            "Attempts": s["attempts"],
            "Ports": len(s["ports"]),
            "Payloads": len(s["payloads"]),
            "Duration (s)": duration,
            "Risk Score": score,
            "Severity": severity
        })

    df = pd.DataFrame(results)
    return df, pd.Series(hourly)

def generate_pdf(df, filename="risk_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Honeypot Risk Report", ln=True, align='C')
    pdf.ln(10)
    for index, row in df.iterrows():
        for k, v in row.items():
            pdf.cell(0, 10, f"{k}: {v}", ln=True)
        pdf.ln(5)
    pdf.output(filename)

# Load the latest log file
log_files = sorted(LOG_DIR.glob("*.json"), reverse=True)
if not log_files:
    st.warning("No log files found in honeypot_logs/. Run honeypot.py first.")
    st.stop()

logs = load_logs(log_files[0])
df, hourly_series = analyze_logs(logs)

# Graphs only

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Severity Distribution")
    fig = px.pie(df, names="Severity", title="Attack Severity Levels")
    st.plotly_chart(fig)

with col2:
    st.subheader("📈 Risk Score per IP")
    fig = px.bar(df, x="IP", y="Risk Score", color="Severity", title="Risk Scores")
    st.plotly_chart(fig)

st.subheader("🕒 Hourly Attack Timeline")
fig = px.line(hourly_series.sort_index(), labels={"value": "Attack Count", "index": "Hour"})
st.plotly_chart(fig)

# Export section
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV Report", csv_data, "risk_report.csv")

if st.button("📄 Generate PDF Report"):
    generate_pdf(df)
    with open("risk_report.pdf", "rb") as f:
        st.download_button("⬇️ Download PDF", f, "risk_report.pdf")

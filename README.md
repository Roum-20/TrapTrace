# 🛡️ TrapTrace-Trap and trace attackers
This project is a powerful honeypot attack analyzer and dashboard built using **Python** and **Streamlit**. It simulates, logs, analyzes, and visualizes suspicious activities like brute force attacks and port scanning attempts in real time.
## 🚀 Features

- 🕵️ Real-time honeypot log analysis
- 📊 Visual dashboard with:
  - Severity-based pie chart
  - Risk score bar chart
  - Hourly attack timeline
- 🔎 Filters by IP, port, and time range
- 📁 Log file auto-loading from 
- 🧪 Built-in attack simulation 
- 📤 Export results as CSV or PDF
## 🚀 Getting Started
### 2. Start the Honeypot
```bash
python honeypot.py
```
Open another terminal
### 3. Simulate Attacks(optional)
```bash
python honeypot_simulator.py --target 127.0.0.1 --intensity high --duration 60
```
Open an another termianl
### 4. Analyze Logs
```bash
streamlit run dashboard.py
```
## 🧠 Risk Scoring & Severity
 Risk is calculated from attempts, port & payload diversity, and duration.
- Severity:
  - 0–30 → Low
  - 31–70 → Medium
  - 71–100 → High
## ⚠️ Disclaimer
   This is for educational and research use only.

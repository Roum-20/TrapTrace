# 🛡️ TrapTrace-Trap and trace attackers
It is a Python-based honeypot system with attacker simulation, behavioral log analysis, and CSV risk reporting. Lightweight and ideal for research, testing, and deception-based security setups.

## 🚀 Getting Started
### 1. Start the Honeypot
```bash
python honeypot.py
```
Open another terminal
### 2. Simulate Attacks(optional)
```bash
python honeypot_simulator.py --target 127.0.0.1 --intensity high --duration 60
```
Open an another termianl
### 3. Analyze Logs
```bash
python analyze_logs.py honeypot_logs/honeypot_YYYYMMDD.json
```
## 🧠 Risk Scoring & Severity
 Risk is calculated from attempts, port & payload diversity, and duration.
- Severity:
  - 0–30 → Low
  - 31–70 → Medium
  - 71–100 → High
## ⚠️ Disclaimer
   This is for educational and research use only.

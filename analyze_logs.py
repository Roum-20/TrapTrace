import datetime
import json
import csv
import sys
from pathlib import Path

def analyze_logs(log_file):
    ip_analysis = {}
    port_analysis = {}
    hourly_attacks = {}
    data_patterns = {}

    with open(log_file, 'r') as f:
        for line in f:
            try:
                activity = json.loads(line)
                timestamp = datetime.datetime.fromisoformat(activity['timestamp'])
                ip = activity['remote_ip']
                port = activity['port']
                data = activity['data']

                if ip not in ip_analysis:
                    ip_analysis[ip] = {
                        'total_attempts': 0,
                        'first_seen': timestamp,
                        'last_seen': timestamp,
                        'targeted_ports': set(),
                        'unique_payloads': set()
                    }

                ip_analysis[ip]['total_attempts'] += 1
                ip_analysis[ip]['last_seen'] = timestamp
                ip_analysis[ip]['targeted_ports'].add(port)
                ip_analysis[ip]['unique_payloads'].add(data.strip())

            except (json.JSONDecodeError, KeyError):
                continue

    csv_filename = f"risk_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['IP', 'Total Attempts', 'Unique Ports', 'Payloads', 'Active Duration', 'Risk Score', 'Severity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for ip, stats in ip_analysis.items():
            duration = (stats['last_seen'] - stats['first_seen']).total_seconds()
            num_ports = len(stats['targeted_ports'])
            num_payloads = len(stats['unique_payloads'])
            score = (
                stats['total_attempts'] * 0.5 +
                num_ports * 5 +
                num_payloads * 4 +
                (duration / 60.0)
            )
            risk_score = min(100, round(score, 2))
            if risk_score <= 30:
                severity = "Low"
            elif risk_score <= 70:
                severity = "Medium"
            else:
                severity = "High"

            writer.writerow({
                'IP': ip,
                'Total Attempts': stats['total_attempts'],
                'Unique Ports': num_ports,
                'Payloads': num_payloads,
                'Active Duration': f"{duration:.1f}s",
                'Risk Score': risk_score,
                'Severity': severity
            })

    print(f"\n✅ Risk report with severity exported to: {csv_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_logs.py <log_file>")
    else:
        analyze_logs(sys.argv[1])

import socket
import sys
import datetime
import json
import threading
from pathlib import Path
import time

LOG_DIR = Path("honeypot_logs")
LOG_DIR.mkdir(exist_ok=True)

class Honeypot:
    def __init__(self, bind_ip="0.0.0.0", ports=None):
        self.bind_ip = bind_ip
        self.ports = ports or [21, 22, 80, 443]
        self.log_file = LOG_DIR / f"honeypot_{datetime.datetime.now().strftime('%Y%m%d')}.json"

    def log_activity(self, port, remote_ip, data):
        activity = {
            "timestamp": datetime.datetime.now().isoformat(),
            "remote_ip": remote_ip,
            "port": port,
            "data": data.decode('utf-8', errors='ignore')
        }
        with open(self.log_file, 'a') as f:
            json.dump(activity, f)
            f.write('\n')

    def handle_connection(self, client_socket, remote_ip, port):
        service_banners = {
            21: "220 FTP server ready\r\n",
            22: "SSH-2.0-OpenSSH_8.2p1 Ubuntu\r\n",
            80: "HTTP/1.1 200 OK\r\nServer: Apache\r\n\r\n",
            443: "HTTP/1.1 200 OK\r\nServer: Apache\r\n\r\n"
        }
        try:
            if port in service_banners:
                client_socket.send(service_banners[port].encode())
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.log_activity(port, remote_ip, data)
                client_socket.send(b"Command not recognized.\r\n")
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            client_socket.close()

    def start_listener(self, port):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.bind_ip, port))
            server.listen(5)
            print(f"[*] Listening on {self.bind_ip}:{port}")
            while True:
                client, addr = server.accept()
                print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
                threading.Thread(target=self.handle_connection, args=(client, addr[0], port)).start()
        except Exception as e:
            print(f"[!] Failed to bind port {port}: {e}")

def main():
    honeypot = Honeypot()
    for port in honeypot.ports:
        t = threading.Thread(target=honeypot.start_listener, args=(port,))
        t.daemon = True
        t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Honeypot shutting down.")
        sys.exit(0)

if __name__ == "__main__":
    main()


### honeypot_simulator.py

import socket
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
import argparse

class HoneypotSimulator:
    def __init__(self, target_ip="127.0.0.1", intensity="medium"):
        self.target_ip = target_ip
        self.intensity = intensity
        self.target_ports = [21, 22, 23, 25, 80, 443, 3306, 5432]
        self.attack_patterns = {
            21: ["USER admin\r\n", "PASS admin123\r\n", "LIST\r\n", "STOR malware.exe\r\n"],
            22: ["SSH-2.0-OpenSSH_7.9\r\n", "admin:password123\n", "root:toor\n"],
            80: ["GET / HTTP/1.1\r\nHost: localhost\r\n\r\n", "POST /admin HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n"]
        }
        self.intensity_settings = {
            "low": {"max_threads": 2, "delay_range": (1, 3)},
            "medium": {"max_threads": 5, "delay_range": (0.5, 1.5)},
            "high": {"max_threads": 10, "delay_range": (0.1, 0.5)}
        }

    def simulate_connection(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            print(f"[*] Attempting connection to {self.target_ip}:{port}")
            sock.connect((self.target_ip, port))
            try:
                banner = sock.recv(1024)
                print(f"[+] Received banner from port {port}: {banner.decode('utf-8', 'ignore').strip()}")
            except:
                pass
            if port in self.attack_patterns:
                for command in self.attack_patterns[port]:
                    print(f"[*] Sending command to port {port}: {command.strip()}")
                    sock.send(command.encode())
                    try:
                        response = sock.recv(1024)
                        print(f"[+] Response: {response.decode('utf-8', 'ignore').strip()}")
                    except socket.timeout:
                        print(f"[-] No response received from port {port}")
                    time.sleep(random.uniform(*self.intensity_settings[self.intensity]["delay_range"]))
            sock.close()
        except Exception as e:
            print(f"[-] Error connecting to port {port}: {e}")

    def simulate_port_scan(self):
        for port in self.target_ports:
            self.simulate_connection(port)
            time.sleep(random.uniform(0.1, 0.3))

    def simulate_brute_force(self, port):
        users = ["admin", "root", "user"]
        passwords = ["123456", "password", "admin123"]
        for user in users:
            for pwd in passwords:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect((self.target_ip, port))
                    if port == 21:
                        sock.send(f"USER {user}\r\n".encode())
                        sock.recv(1024)
                        sock.send(f"PASS {pwd}\r\n".encode())
                    elif port == 22:
                        sock.send(f"{user}:{pwd}\n".encode())
                    sock.close()
                    time.sleep(random.uniform(0.1, 0.3))
                except Exception as e:
                    print(f"[-] Error brute-forcing {port}: {e}")

    def run_continuous_simulation(self, duration=300):
        end_time = time.time() + duration
        with ThreadPoolExecutor(max_workers=self.intensity_settings[self.intensity]["max_threads"]) as executor:
            while time.time() < end_time:
                choices = [lambda: self.simulate_port_scan(),
                           lambda: self.simulate_brute_force(21),
                           lambda: self.simulate_brute_force(22),
                           lambda: self.simulate_connection(80)]
                executor.submit(random.choice(choices))
                time.sleep(random.uniform(*self.intensity_settings[self.intensity]["delay_range"]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="127.0.0.1")
    parser.add_argument("--intensity", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--duration", type=int, default=300)
    args = parser.parse_args()
    simulator = HoneypotSimulator(args.target, args.intensity)
    simulator.run_continuous_simulation(args.duration)

if __name__ == "__main__":
    main()

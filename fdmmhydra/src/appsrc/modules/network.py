import ipaddress
import socket 
import subprocess
import threading
import logging
import logging
from typing import Tuple

def _run_ping(host) -> subprocess.CompletedProcess:
    """Helper, runs the os ping command as a subprocess"""
    return subprocess.run(
        ['ping', '-n', '2', '-w', '1500', host],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def scan_ip(host:str, output:dict, retries=3) -> None:
    """
    Pings an ip to see if it's online
    """
    try:
        for i in range(retries):
            result = _run_ping(host)
            if result.returncode or 'unreachable' in result.stdout:
                continue
        output[host] = (
            result.returncode == 0
            and "Reply from" in result.stdout
            and not 'unreachable' in result.stdout
        )
    except subprocess.CalledProcessError as e:
        output[host] = False

def scan_ip_range(ip_range:str) -> list[str]:
    """
    Scan a range of ip address in cider notation
    """
    logging.info(f"Running ping-scan on {ip_range}")
    if '*' in ip_range:
        ips = [
            str(ip)
            for ip in
            ipaddress.IPv4Network(ip_range.replace('*', '0/24'), strict=False)
        ]
    else:
        ips = [str(ip) for ip in ipaddress.IPv4Network(ip_range, strict=False)]
    output, threads = {}, []
    # Remove .255 addresses
    for host in [ip for ip in ips if not ip.rsplit(".", 1)[1] in ["255"]]:
        threads.append(
            threading.Thread(target=scan_ip, args=(host, output))
        )
    for t in threads: t.start()
    for t in threads: t.join()
    return [ip for ip in output if output[ip]]

def resolve_host_name(ip:str, output:dict) -> None:
    """
    Resolves an ip to its hostname, aliases, list of ips, and fqdn
    """
    try:
        output[ip] = [*socket.gethostbyaddr(ip), socket.getfqdn(ip)]
    except:
        output[ip] = ["UNKNOWN", [], [ip], ip]
        
def resolve_host_names(ips:list) -> dict[str:Tuple[str, list[str], list[str], str]]:
    """
    Resolves a list of ips to a list of tuples in the form
    hostname, aliases, ips, and fqdn
    """
    hosts = {}
    threads = []
    for ip in ips:
        t = threading.Thread(target=resolve_host_name, args=(ip, hosts))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return hosts

class Scanner():
    """Object to handle periodic scans"""
    def __init__(self, ranges:list[str]=[]):
        self.ranges = ranges
        self.data = {}

    def scan(self) -> dict[str:Tuple[str, list[str], list[str], str]]:
        """Returns a dict of ips to tuples scan results"""
        logging.info("Running periodic network scan")
        online = []
        for r in self.ranges:
            online.extend(scan_ip_range(r))
        self.data = resolve_host_names(online)
        return self.data

# ips = scan_ip_range("192.168.1.*")
# hosts = resolve_host_names(ips)
# print(json.dumps(hosts, indent=2))
# print(f"Found {len(hosts)} online hosts")
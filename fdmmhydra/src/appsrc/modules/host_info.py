from werkzeug.datastructures import ImmutableDict
import psutil
import socket
import platform
import datetime

def get_processes():
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info', 'num_threads']):
        try:
            processes.append(p.info)
        except:
            pass
    return processes

def get_memory():
    memory = ImmutableDict()
    vmem = psutil.virtual_memory()
    memory.total = vmem.total
    memory.available = vmem.available
    memory.percent = vmem.percent
    return memory

def get_disk_info():
    disk_info = {}
    for partition in psutil.disk_partitions():
        usage = psutil.disk_usage(partition.mountpoint)
        disk_info[partition.device] = {
            'mountpoint': partition.mountpoint,
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent_used': usage.percent
        }
    return disk_info

def get_network_connections():
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        connections.append({
            'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
            'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
            'status': conn.status,
            'pid': conn.pid
        })
    return connections

def get_ips():
    ips = {}
    for interface, addrs in psutil.net_if_addrs().items():
        ips[interface] = [addr.address for addr in addrs if addr.family == socket.AF_INET]
    return ips

def get_host_info():
    info = ImmutableDict()
    info.hostname = socket.gethostname()
    info.ips = get_ips()
    info.network_connections = get_network_connections()
    info.cpu = platform.processor()
    info.memory = get_memory()
    info.cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
    info.processes = get_processes()
    info.disk_info = get_disk_info()
    info.boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    return info
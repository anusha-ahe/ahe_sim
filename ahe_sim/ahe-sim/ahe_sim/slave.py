from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.async_io import StartTcpServer
import subprocess

ip = '0.0.0.0'

def is_server_running(port):
    cmd = f"netstat -tlnp | grep {ip}:{port}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        netstat_output = result.stdout.strip().split()
        pid = netstat_output[-1].split('/')[0]
        return True, int(pid)
    return False, None


def force_kill_server(port):
    result, pid = is_server_running(port)
    if result:
        print(f"Server for map {name} is already running @ {ip}:{port}")
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Killed server for port {pid}")
        except Exception as e:
            print(f"Failed to kill server with PID {pid}@{port}: {e}")


def run_slave(server_context, port, name):
    identity = ModbusDeviceIdentification()
    force_kill_server(port)
    try:
        print(f"Starting server for map {name} @ {ip}:{port}")
        StartTcpServer(context=server_context, identity=identity, address=(ip, port))
    except Exception as e:
        print(f"Failed to start server for map {name}: {e}")
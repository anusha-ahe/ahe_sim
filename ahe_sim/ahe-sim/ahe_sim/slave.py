from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.async_io import StartTcpServer
import subprocess

ip = '0.0.0.0'

def is_server_running(port):
    cmd = f"netstat -tln | grep {ip}:{port}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0


def run_slave(server_context, port, name):
    identity = ModbusDeviceIdentification()
    if is_server_running(port):
        print(f"Server for map {name} is already running @ {ip}:{port}")
        return
    try:
        print(f"Starting server for map {name} @ {ip}:{port}")
        StartTcpServer(context=server_context, identity=identity, address=(ip, port))
    except Exception as e:
        print(f"Failed to start server for map {name}: {e}")
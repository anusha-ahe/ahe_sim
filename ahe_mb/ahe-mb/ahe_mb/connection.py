import time
from threading import Lock
import ahe_log
from pymodbus.client import ModbusTcpClient
from pymodbus.pdu import ExceptionResponse
from pymodbus.exceptions import ModbusIOException, ConnectionException


connections = dict()
global_lock = Lock()
FAIL = 1 << 0
PENDING = 1 << 1


class Connection:
    def __init__(self, ip, port, max_fail_count=3):
        self.ip = ip
        self.port = port
        self.connected = False
        self.max_fail_count = max_fail_count
        self.lock = Lock()
        self.logging = ahe_log.get_logger()

    def connect(self):
        if self.connected:
            return
        self.client = ModbusTcpClient(self.ip,
                                      port=int(self.port),
                                      strict=False,
                                      reset_socket=False)
        reply = self.client.connect()
        if reply:
            self.logging.info(f"Connected to Ip: {self.ip}, Port: {self.port}")
            self.connected = True
            self.fail_count = 0

    def format_log(self, block, unit, reg, start_address, msg):
        return f"#@#|{time.time()}|{block}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}||{msg}"

    def write(self, unit, reg, start_address, data, block):
        written = list()
        self.logging.debug(
            f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|write|{data}")
        self.lock.acquire()
        self.connect()
        if not self.connected:
            self.logging.debug(
                f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}| not connected")
            self.lock.release()
            return 1
        try:
            if reg in [1, "Coil"]:
                # this logic only works when data has to be written to individual addresses in the coils #
                for i in range(len(data)):
                    written.append(self.client.write_coil(
                        slave=unit, address=start_address + i, value=bool(data[i])))
            else:
                written.append(self.client.write_registers(
                    unit=unit, address=start_address, values=data))
        except ConnectionException as e:
            self.disconnect(3, e, unit, reg, start_address, start_address)
            self.lock.release()
            return 1
        if all(written):
            self.logging.debug(self.format_log(
                block, unit, reg, start_address, "OK"))
            self.lock.release()
            return 0
        self.lock.release()
        self.logging.debug(self.format_log(
            block, unit, reg, start_address, "failed"))
        return 1

    def read(self, unit, reg, start_address, end_address):
        self.logging.debug(
            f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|ready|{end_address - start_address}")
        self.lock.acquire()
        self.logging.debug(
            f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|read|{end_address - start_address}")
        self.connect()
        if not self.connected:
            self.lock.release()
            self.logging.warning(
                f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|not connected|{end_address - start_address}")
            return None
        try:
            if reg in [4, "Holding Register"]:
                modbus_reply = self.client.read_holding_registers(
                    start_address, end_address - start_address + 1, slave=unit)
            elif reg in [3, "Input Register"]:
                modbus_reply = self.client.read_input_registers(
                    start_address, end_address - start_address + 1, slave=unit)
            elif reg in [2, "Discrete Input"]:
                modbus_reply = self.client.read_discrete_inputs(
                    start_address, end_address - start_address + 1, slave=unit)
            elif reg in [1, "Coil"]:
                modbus_reply = self.client.read_coils(
                    start_address, end_address - start_address + 1, slave=unit)
            else:
                self.logging.error(
                    f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|error|invalid regiser type {reg}")
                self.lock.release()
                raise TypeError(f"invalid regiser type {reg}")
            self.fail_count = 0

        except ConnectionException as e:
            self.disconnect(1, e, unit, reg, start_address, end_address)
            self.lock.release()
            return None
        if type(modbus_reply) in [ExceptionResponse, ModbusIOException]:
            self.disconnect(2, modbus_reply, unit, reg,
                            start_address, end_address)
            self.lock.release()
            return None
        if reg in [4, "Holding Register", 3, "Input Register"]:
            if hasattr(modbus_reply, 'registers') and len(modbus_reply.registers) == end_address - start_address + 1:
                self.logging.debug(
                    f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|OK|{modbus_reply.registers}")
                self.lock.release()
                return modbus_reply.registers
            else:
                self.logging.debug(
                    f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|Cross Talk|")
                self.lock.release()
                return None
        if reg in [2, "Discrete Input", 1, "Coil"]:
            if hasattr(modbus_reply, 'bits') and len(modbus_reply.bits) >= end_address - start_address + 1:
                self.logging.debug(
                    f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|OK|{modbus_reply.bits}")
                self.lock.release()
                return modbus_reply.bits
            else:
                self.logging.debug(
                    f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|Cross Talk|")
                self.lock.release()
                return None

    def disconnect(self, msg, reason, unit, reg, start_address, end_address):
        self.logging.debug(f"active connections {connections.keys()}")
        self.logging.error(
            f"{time.time()}|MB$|{self.ip}:{self.port}#{unit}-{reg}@{start_address}|Error|{msg} {reason} fails {self.max_fail_count}")
        if type(reason) in [ExceptionResponse]:
            return
        self.connected = False
        if self.fail_count >= self.max_fail_count:
            self.logging.error(
                f"{time.time()}|MB$|{self.ip}:{self.port}|disconnecting|")
            self.fail_count += 1


def connect_modbus(ip_address, port):
    global global_lock
    key = (ip_address, port)
    global_lock.acquire()
    if key not in connections:
        connections[key] = Connection(ip_address, port)
    global_lock.release()
    return connections[key]



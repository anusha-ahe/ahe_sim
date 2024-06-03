from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('0.0.0.0', 5002)
client.connect()
client.write_register(1018,1)
reg = client.read_holding_registers(1018)
print(reg)
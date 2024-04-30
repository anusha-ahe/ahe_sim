
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import ahe_log
log = ahe_log.get_logger()


def run_server(port):
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [17]*400),
        co=ModbusSequentialDataBlock(0, [17]*400),
        hr=ModbusSequentialDataBlock(0, [17]*400),
        ir=ModbusSequentialDataBlock(0, [17]*400))

    slaves = {
        0x01: store,
    }
    context = ModbusServerContext(slaves=slaves, single=False)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = '1.5'

    StartTcpServer(context=context, identity=identity,
                   address=("0.0.0.0", port))


if __name__ == "__main__":
    run_server(5020)

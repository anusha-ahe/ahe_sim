import time
from unittest import TestCase
from unittest.mock import patch

from pymodbus.exceptions import ModbusIOException

from ahe_sim.models import SimulatorConfig
from ahe_sim.sim import Simulation
from pymodbus.datastore import ModbusServerContext
from ahe_mb.models import Map, Field, DeviceMap, SiteDevice
from pymodbus.client import ModbusTcpClient

from ahe_sys.models import DeviceType, Site, AheClient, SiteDeviceList


def simulation():
    return Simulation()



class SimTest(TestCase):
    def setUp(self):
        self.simulation  = simulation()
        SiteDevice.objects.filter().delete()
        self.device_type = DeviceType.objects.get_or_create(name='Test Inverter', device_category='inverter')[0]
        self.map_obj = Map.objects.get_or_create(name='test')[0]
        self.field1 = Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field1', field_address=1, field_format='uint16')[0]
        self.field2 = Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field2', field_address=2,field_format='uint16', field_scale=0.1)[0]
        self.device_map = DeviceMap.objects.get_or_create(device_type=self.device_type, map=self.map_obj)
        self.client = AheClient.objects.get_or_create(name='test')[0]
        self.site = Site.objects.get_or_create(name='test', client=self.client)[0]
        self.site_device_conf = SiteDeviceList.objects.get_or_create(site=self.site)[0]
        self.device =  SiteDevice.objects.get_or_create(device_type=self.device_type,ip_address='0.0.0.0', port=5232,unit=1,
                                                        site_device_conf= self.site_device_conf)[0]

    def test_set_context(self):
        self.simulation.set_context("server_identity", 10)
        assert "server_identity" in self.simulation.server_context
        assert isinstance(self.simulation.server_context["server_identity"], ModbusServerContext)

    def test_set_all_initial_values_to_0(self):
        self.simulation.set_context("server_identity", 10)
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        data = self.simulation.set_all_initial_values_to_0("server_identity")
        assert  data == {'server_identity': {'test_field1': 0, 'test_field2': 0}}

    def test_get_values(self):
        self.simulation.set_context("server_identity", 10)
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2.ahe_name}}
        self.simulation.set_all_initial_values_to_0("server_identity")
        value = self.simulation.get_values("server_identity", 'test', 'test_field1')
        assert value == 0

    def test_set_value_to_address(self):
        self.simulation.set_context("server_identity", 10)
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2.ahe_name}}
        self.simulation.maps = {"server_identity": self.map_obj.name}
        self.simulation.set_all_initial_values_to_0("server_identity")
        value = self.simulation.get_values("server_identity", 'test', 'test_field1')
        assert value == 0
        self.simulation.set_value_to_address("server_identity", 'test_field1',6)
        value = self.simulation.get_values("server_identity", 'test', 'test_field1')
        assert value == 6

    def test_set_value_to_address_with_scaling(self):
        self.simulation.set_context("server_identity", 10)
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2}}
        self.simulation.maps = {"server_identity": self.map_obj.name}
        self.simulation.set_all_initial_values_to_0("server_identity")
        value = self.simulation.get_values("server_identity", 'test', 'test_field2')
        assert value == 0
        self.simulation.set_value_to_address("server_identity", 'test_field2',6)
        value = self.simulation.get_values("server_identity", 'test', 'test_field2')
        assert value == 60

    def test_start_server(self):
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2}}
        self.simulation.devices = {"server_identity": self.map_obj.name}
        self.simulation.start_server()
        time.sleep(2)
        client = ModbusTcpClient('0.0.0.0', 5232)
        connection = client.connect()
        print("connection", client.connected)
        assert connection, "Client failed to connect to the server"
        client.close()

    def test_start_mul_ips_servers(self):
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2}}
        self.simulation.devices = {"server_identity": self.map_obj.name}
        self.simulation.start_server()
        time.sleep(3)
        client1 = ModbusTcpClient('192.168.1.21', 5021)
        client2 = ModbusTcpClient('192.168.1.22', 5020)
        connection1 = client1.connect()
        connection2 = client2.connect()
        print("Client 1 connected:", client1.connected)
        print("Client 2 connected:", client2.connected)
        assert connection1, "Client 1 failed to connect to the server"
        assert connection2, "Client 2 failed to connect to the server"
        client1.close()
        client2.close()

    @patch('pymodbus.client.ModbusTcpClient')
    def test_communication_timeout(self, MockModbusTcpClient):
        mock_client_instance = MockModbusTcpClient.return_value
        mock_client_instance.read_holding_registers.side_effect = ModbusIOException("Read timeout")
        self.simulation.set_context("server_identity", 10)
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2}}

        self.simulation.set_all_initial_values_to_0("server_identity")
        self.simulation.start_server()
        try:
            value = self.simulation.get_values("server_identity", 'test', 'test_field1')
        except ModbusIOException as e:
            self.assertEqual(str(e), "Read timeout")






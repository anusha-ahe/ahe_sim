from unittest import TestCase
from unittest.mock import patch
from ahe_sim.models import SimulatorConfig
from ahe_sim.sim import Simulation
from pymodbus.datastore import ModbusServerContext
from ahe_mb.models import Map, Field
from pymodbus.client import ModbusTcpClient
def simulation():
    return Simulation()



class SimTest(TestCase):
    def setUp(self):
        self.simulation  = simulation()
        self.map_obj = Map.objects.get_or_create(name='test')[0]
        self.field1 = Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field1', field_address=1, field_format='uint16')[0]
        self.field2 = Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field2', field_address=2,field_format='uint16', field_scale=0.1)[0]
        SimulatorConfig.objects.filter().delete()
        SimulatorConfig.objects.get_or_create(map_name=self.map_obj, port=5000)

    def test_set_context(self):
        self.simulation.set_context("server_identity", 10)
        assert "server_identity" in self.simulation.server_context
        assert isinstance(self.simulation.server_context["server_identity"], ModbusServerContext)

    def test_set_all_initial_values_to_0(self):
        self.simulation.set_context("server_identity", 10)
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        data = self.simulation.set_all_initial_values_to_0(self.map_obj, "server_identity")
        assert  data == {'server_identity': {'test_test_field1': 0, 'test_test_field2': 0}}

    def test_get_values(self):
        self.simulation.set_context("server_identity", 10)
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2.ahe_name}}
        self.simulation.set_all_initial_values_to_0(self.map_obj, "server_identity")
        value = self.simulation.get_values("server_identity", 'test', 'test_field1')
        assert value == 0

    def test_set_value_to_address(self):
        self.simulation.set_context("server_identity", 10)
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2.ahe_name}}
        self.simulation.maps = {"server_identity": self.map_obj.name}
        self.simulation.set_all_initial_values_to_0(self.map_obj, "server_identity")
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
        self.simulation.set_all_initial_values_to_0(self.map_obj, "server_identity")
        value = self.simulation.get_values("server_identity", 'test', 'test_field2')
        assert value == 0
        self.simulation.set_value_to_address("server_identity", 'test_field2',6)
        value = self.simulation.get_values("server_identity", 'test', 'test_field2')
        assert value == 60

    @patch("ahe_sim.sim.run_slave")
    def test_start_server(self, mock_run_slave):
        self.simulation.field_dict = {"server_identity": {1: self.field1.ahe_name, 2: self.field2.ahe_name}}
        self.simulation.get_field_dict = {"server_identity": {self.field1.ahe_name: self.field1,
                                                              self.field2.ahe_name: self.field2}}
        self.simulation.maps = {"server_identity": self.map_obj.name}
        mock_run_slave.return_value = None
        self.simulation.start_server()
        client = ModbusTcpClient('0.0.0.0', 5000)
        connection = client.connect()
        assert connection, "Client failed to connect to the server"
        client.close()





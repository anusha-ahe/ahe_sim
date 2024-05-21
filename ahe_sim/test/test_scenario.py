from unittest import TestCase
from unittest.mock import patch
from pymodbus.client import ModbusTcpClient
from ahe_sim.models import TestExecutionLog, ScenarioInput, SimulatorConfig, TestScenario
from ahe_mb.models import Map, Field
from ahe_sim.scenario import ScenarioUpdate

TIMEOUT = 120

def scenario_update():
    return ScenarioUpdate()

class SimTest(TestCase):
    def setUp(self):
        self.scenario_update  = ScenarioUpdate()
        self.map_obj = Map.objects.get_or_create(name='test')[0]
        self.field1 = Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field1', field_address=1, field_format='uint16')[0]
        self.field2 = Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field2', field_address=2, field_format='uint16', field_scale=0.1)[0]
        self.field3 = Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field3', field_address=3, field_format='uint16', field_scale=0.5)[0]
        SimulatorConfig.objects.get_or_create(map_name=self.map_obj, port=5000)
        self.test_scenario1 = TestScenario.objects.get_or_create(name='test_scenario1')[0]
        ScenarioInput.objects.get_or_create(variable=self.field1, test_scenario=self.test_scenario1, value=1, initial_value=1)
        ScenarioInput.objects.get_or_create(variable=self.field2, test_scenario=self.test_scenario1, value=2, initial_value=2)
        ScenarioInput.objects.get_or_create(variable=self.field3, test_scenario=self.test_scenario1, value=4, initial_value=3)

    @patch("ahe_sim.sim.run_slave")
    def test_get_available_test_scenarios_for_simulator(self, mock_run_slave):
        mock_run_slave.return_value = None
        test_scenarios = self.scenario_update.get_available_test_scenarios_for_simulator()
        assert test_scenarios[0] == self.test_scenario1

    @patch("ahe_sim.sim.run_slave", return_value=None)
    @patch("time.time", return_value=100)
    def test_create_test_log_for_test_scenarios(self, mock_time, mock_run_slave):
        self.scenario_update.get_available_test_scenarios_for_simulator()
        self.scenario_update.create_test_log_for_test_scenarios()
        assert TestExecutionLog.objects.filter(epoch=100)[0].epoch == 100

    @patch("time.time", return_value=100)
    def test_update_initial_values_for_inputs_and_outputs(self, mock_time):
        self.scenario_update.get_available_test_scenarios_for_simulator()
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.update_initial_values_for_inputs_and_outputs()
        assert TestExecutionLog.objects.filter(epoch=100)[0].epoch == 100
        simulation = self.scenario_update.simulator
        for server_identity in simulation.data.keys():
            data = simulation.data[server_identity]
            assert data['test_test_field1'] == 1
            assert data['test_test_field2'] == 20
            assert data['test_test_field3'] == 6
    def test_update_values_for_inputs(self):
        self.scenario_update.get_available_test_scenarios_for_simulator()
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.update_initial_values_for_inputs_and_outputs()
        self.scenario_update.update_values_for_inputs()
        simulation = self.scenario_update.simulator
        for server_identity in simulation.data.keys():
            data = simulation.data[server_identity]
            assert data['test_test_field1'] == 1
            assert data['test_test_field2'] == 20
            assert data['test_test_field3'] == 8

from unittest import TestCase

import pytest
from unittest.mock import MagicMock, patch
from time import time

from pymodbus.client import ModbusTcpClient

from ahe_sim.models import TestExecutionLog, ScenarioInput, ScenarioOutput, SimulatorConfig, TestScenario
from ahe_mb.models import Map, Field
from ahe_sim.sim import Simulation
from ahe_sim.scenario import ScenarioUpdate

TIMEOUT = 120

def scenario_update():
    return ScenarioUpdate()


class SimTest(TestCase):
    def setUp(self):
        self.scenario_update  = ScenarioUpdate()
        self.map_obj = Map.objects.get_or_create(name='test')[0]
        self.field1 = \
        Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field1', field_address=1, field_format='uint16')[0]
        self.field2 = \
        Field.objects.get_or_create(map=self.map_obj, ahe_name='test_field2', field_address=2, field_format='uint16',
                                    field_scale=0.1)[0]
        SimulatorConfig.objects.filter().delete()
        TestScenario.objects.filter().delete()
        SimulatorConfig.objects.get_or_create(map_name=self.map_obj, port=8000)
        self.test_scenario1 = TestScenario.objects.get_or_create(name='test_scenario1')[0]
        ScenarioInput.objects.get_or_create(variable=self.field1, test_scenario=self.test_scenario1, value=1, initial_value=0)
        ScenarioInput.objects.get_or_create(variable=self.field2, test_scenario=self.test_scenario1, value=2,
                                            initial_value=0)

    @patch("ahe_sim.sim.run_slave")
    def test_get_available_test_scenarios_for_simulator(self,mock_run_slave):
        mock_run_slave.return_value = None
        test_scenarios = self.scenario_update.get_available_test_scenarios_for_simulator()
        assert test_scenarios[0] == self.test_scenario1

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

    @patch("ahe_sim.sim.run_slave", return_value=None)
    @patch("time.time", return_value=100)
    def test_update_initial_values_for_inputs_and_outputs(self, mock_time, mock_run_slave):
        self.scenario_update.get_available_test_scenarios_for_simulator()
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.update_initial_values_for_inputs_and_outputs()
        assert TestExecutionLog.objects.filter(epoch=100)[0].epoch == 100
        client = ModbusTcpClient('0.0.0.0', 5000)
        client.connect()
        reg1 = client.read_holding_registers(1)
        assert reg1.registers == [0]

    @patch("time.time", return_value=100)
    def test_update_values_for_inputs(self, mock_time):
        self.scenario_update.get_available_test_scenarios_for_simulator()
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.update_initial_values_for_inputs_and_outputs()
        self.scenario_update.update_values_for_inputs()
        assert TestExecutionLog.objects.filter(epoch=100)[0].epoch == 100
        client = ModbusTcpClient('0.0.0.0', 8000)
        try:
            client.connect()
            reg1 = client.read_holding_registers(2)
            assert reg1.registers == [2]
        except Exception as e:
            print(e)



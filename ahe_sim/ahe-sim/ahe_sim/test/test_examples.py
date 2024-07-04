import time
from unittest import TestCase
from pymodbus.client import ModbusTcpClient
from ahe_sim.models import TestExecutionLog, Input, TestScenario, Output
from ahe_mb.models import Map, Field, SiteDevice, DeviceMap
from ahe_sim.scenario import ScenarioUpdate
from ahe_sys.models import AheClient, SiteDeviceList, Site, DeviceType


class SimTest(TestCase):
    def setUp(self):
        TestExecutionLog.objects.filter().delete()
        Output.objects.filter().delete()
        Input.objects.filter().delete()
        TestScenario.objects.filter().delete()
        SiteDevice.objects.filter().delete()
        self.client = AheClient.objects.get_or_create(name='test')[0]
        self.site = Site.objects.get_or_create(name='test', client=self.client)[0]
        self.site_device_conf = SiteDeviceList.objects.get_or_create(site=self.site, version=1)[0]
        self.device_type1 = DeviceType.objects.get(name='Enervenue Battery')
        self.device_type2 = DeviceType.objects.get(name='Trumpf AC 3025')
        self.map_obj1 = Map.objects.get(name='enervenue_battery_map')
        self.map_obj2 = Map.objects.get(name='trumpf_ac_3025')
        self.device1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type1, ip_address='0.0.0.0', port=5200, unit=1,
                                             name='battery_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.device2 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type2, ip_address='0.0.0.0', port=5201, unit=1,
                                             name='inverter_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.test_scenario1 = TestScenario.objects.get_or_create(name='test_scenario_when_voltage > 3.6',
                                                                 timeout=1)[0]
        self.field1 = Field.objects.get(map=self.map_obj1, ahe_name='voltage')
        self.field2 = Field.objects.get(map=self.map_obj2, ahe_name='activate_power_stage_w')
        Input.objects.get_or_create(variable=self.field1, device=self.device1, test_scenario=self.test_scenario1,
                                    function='equal_to',
                                    value=3.7, initial_value=3.4)
        Output.objects.get_or_create(variable=self.field2, device=self.device2, test_scenario=self.test_scenario1,
                                     value=2000, function='equal_to',
                                     initial_value=1000)
        self.test_scenario2 = TestScenario.objects.get_or_create(name='test to checkout communication error')[0]
        Input.objects.get_or_create(device=self.device1, test_scenario=self.test_scenario2,
                                    function='communication_error',
                                    variable=self.field1)
        Output.objects.get_or_create(variable=self.field2, device=self.device2, test_scenario=self.test_scenario2,
                                     value=0, function='equal_to',
                                     initial_value=1000)
        self.scenario_update = ScenarioUpdate()

    def test_log_success_status_when_voltage_greater_than_3(self):
        TestExecutionLog.objects.filter().delete()
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.start_servers()
        time.sleep(2)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)[0]
        self.scenario_update.update_and_translate_values('inverter_1', 'activate_power_stage_w', 1000)
        self.scenario_update.update_values_for_inputs(log, 'initial')
        self.scenario_update.update_log_status_from_output(log, 'initial')
        assert self.scenario_update.data['inverter_1']['inverter_1_activate_power_stage_w'] == 1000
        self.scenario_update.update_and_translate_values('inverter_1', 'activate_power_stage_w', 2000)
        self.scenario_update.update_values_for_inputs(log)
        self.scenario_update.update_log_status_from_output(log)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)
        assert log[0].status == 'success'
        self.scenario_update.stop_servers()

    def test_log_failed_status_when_max_cell_voltage_greater_than_3_when_initial_value_doesnt_match(self):
        TestExecutionLog.objects.filter().delete()
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.start_servers()
        time.sleep(2)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)[0]
        self.scenario_update.update_and_translate_values('inverter_1', 'activate_power_stage_w', 10)
        time.sleep(1)
        self.scenario_update.update_values_for_inputs(log, 'initial')
        self.scenario_update.update_log_status_from_output(log, 'initial')
        self.scenario_update.update_and_translate_values('inverter_1', 'activate_power_stage_w', 2000)
        self.scenario_update.update_values_for_inputs(log)
        self.scenario_update.update_log_status_from_output(log)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)
        assert log[0].status == 'failure'
        self.scenario_update.stop_servers()

    def test_log_status_when_communication_error(self):
        TestExecutionLog.objects.filter().delete()
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.start_servers()
        time.sleep(2)
        self.scenario_update.update_and_translate_values('inverter_1', 'activate_power_stage_w', 1000)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario2)[0]
        self.scenario_update.update_values_for_inputs(log, 'initial')
        self.scenario_update.update_log_status_from_output(log, 'initial')
        self.scenario_update.update_and_translate_values('inverter_1', 'activate_power_stage_w', 0)
        self.scenario_update.update_values_for_inputs(log)
        self.scenario_update.update_log_status_from_output(log)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario2)
        assert log[0].status == 'success'
        client = ModbusTcpClient('0.0.0.0', 5201)
        connection = client.connect()
        assert connection
        client = ModbusTcpClient('0.0.0.0', 5200)
        connection = client.connect()
        assert not connection
        self.scenario_update.stop_servers()
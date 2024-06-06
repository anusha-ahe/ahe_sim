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
        self.site_device_conf = SiteDeviceList.objects.get_or_create(site=self.site)[0]
        self.device_type1 = DeviceType.objects.get_or_create(name='SMA sunny_island pcs')[0]
        self.device_type2= DeviceType.objects.get_or_create(name='ebick_bms')[0]
        self.device_type3 = DeviceType.objects.get_or_create(name='SFERE 700m2 grid')[0]
        self.device_type4 = DeviceType.objects.get_or_create(name='SFERE 700m2 ess')[0]
        self.device_type5 = DeviceType.objects.get_or_create(name='phoenix')[0]
        self.map_obj1 = Map.objects.get_or_create(name='sma_sunny_island')[0]
        self.map_obj2 = Map.objects.get_or_create(name='ebick_bms')[0]
        self.map_obj3 = Map.objects.get_or_create(name='sfere_700m2_grid')[0]
        self.map_obj4 = Map.objects.get_or_create(name='sfere_700m2_ess')[0]
        self.map_obj5 = Map.objects.get_or_create(name='phoenix_ilc_171_eth_2_tx')[0]
        DeviceMap.objects.get_or_create(map=self.map_obj2,device_type=self.device_type2,)
        DeviceMap.objects.get_or_create(map=self.map_obj5, device_type=self.device_type5, )
        DeviceMap.objects.get_or_create(map=self.map_obj4, device_type=self.device_type4, )
        DeviceMap.objects.get_or_create(map=self.map_obj3, device_type=self.device_type3, )

        self.inverter_1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type1, ip_address='0.0.0.0', port=5200, unit=3,
                                             name='inverter_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.inverter_2 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type1, ip_address='0.0.0.0', port=5201, unit=3,
                                             name='inverter_2',
                                             site_device_conf=self.site_device_conf)[0]
        self.inverter_3 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type1, ip_address='0.0.0.0', port=5202, unit=3,
                                             name='inverter_3',
                                             site_device_conf=self.site_device_conf)[0]
        self.inverter_4 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type1, ip_address='0.0.0.0', port=5203, unit=3,
                                             name='inverter_4',
                                             site_device_conf=self.site_device_conf)[0]
        self.battery_1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type2, ip_address='0.0.0.0', port=5204, unit=1,
                                             name='battery_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.battery_2 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type2, ip_address='0.0.0.0', port=5205, unit=1,
                                             name='battery_2',
                                             site_device_conf=self.site_device_conf)[0]
        self.battery_3 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type2, ip_address='0.0.0.0', port=5206, unit=1,
                                             name='battery_3',
                                             site_device_conf=self.site_device_conf)[0]
        self.battery_4 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type2, ip_address='0.0.0.0', port=5207, unit=1,
                                             name='battery_4',
                                             site_device_conf=self.site_device_conf)[0]
        self.ems_1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type5, ip_address='0.0.0.0', port=5208, unit=1,
                                             name='ems_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.load_1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type3, ip_address='0.0.0.0', port=5209, unit=1,
                                             name='load_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.grid_1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type3, ip_address='0.0.0.0', port=5210, unit=1,
                                             name='grid_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.ess_1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type4, ip_address='0.0.0.0', port=5211, unit=1,
                                             name='ess_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.min_cell_voltage = Field.objects.get(map=self.map_obj2,ahe_name='min_cell_voltage')
        self.max_cell_voltage = Field.objects.get(map=self.map_obj2, ahe_name='max_cell_voltage')
        self.active_power = Field.objects.get(map=self.map_obj1, ahe_name='active_power')
        self.test_scenario1 = TestScenario.objects.get_or_create(name='turn off pcs1 when min_cell_voltage <= 2.8')[0]
        Input.objects.get_or_create(device=self.battery_1, test_scenario=self.test_scenario1,
                                    variable=self.min_cell_voltage,initial_value=2.9,value=2.8,function='equal_to')
        Output.objects.get_or_create(variable=self.active_power, device=self.inverter_1, test_scenario=self.test_scenario1,
                                     value=0, function='equal_to',
                                     initial_value=15)
        self.test_scenario2 = TestScenario.objects.get_or_create(name='turn off pcs2 when min_cell_voltage <= 2.8')[0]
        Input.objects.get_or_create(device=self.battery_2, test_scenario=self.test_scenario2,
                                    variable=self.min_cell_voltage, initial_value=2.9, value=2.8,function='equal_to')
        Output.objects.get_or_create(variable=self.active_power, device=self.inverter_2,
                                     test_scenario=self.test_scenario2,
                                     value=0, function='equal_to',
                                     initial_value=15)
        self.test_scenario3 = TestScenario.objects.get_or_create(name='turn off pcs1 when max_cell_voltage >= 3.6')[0]
        Input.objects.get_or_create(device=self.battery_1, test_scenario=self.test_scenario3,
                                    variable=self.max_cell_voltage, initial_value=3.6, value=3.8, function='equal_to')
        Output.objects.get_or_create(variable=self.active_power, device=self.inverter_1,
                                     test_scenario=self.test_scenario3,
                                     value=0, function='equal_to',
                                     initial_value=15)
        self.test_scenario4 = TestScenario.objects.get_or_create(name='turn off pcs1 when max_cell_voltage >= 3.6')[0]
        Input.objects.get_or_create(device=self.battery_1, test_scenario=self.test_scenario3,
                                    variable=self.max_cell_voltage, initial_value=3.6, value=3.8, function='equal_to')
        Output.objects.get_or_create(variable=self.active_power, device=self.inverter_1,
                                     test_scenario=self.test_scenario3,
                                     value=0, function='equal_to',
                                     initial_value=15)
        self.scenario_update = ScenarioUpdate()


    def test_log_success_status_when_min_cell_voltage_less_and_pcs_is_turned_off(self):
        TestExecutionLog.objects.filter().delete()
        simulation = self.scenario_update.simulator
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.start_servers()
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)[0]
        simulation.set_value('inverter_1', 'active_power', 1000)
        print("active_power",simulation.data['inverter_1']['active_power'])
        assert simulation.data['inverter_1']['active_power'] == 15
        self.scenario_update.update_values_for_inputs(log, 'initial')
        self.scenario_update.update_log_status_from_output(log, 'initial')
        simulation.set_value('inverter_1', 'active_power', 0)
        assert simulation.data['inverter_1']['active_power'] == 0
        self.scenario_update.update_values_for_inputs(log)
        self.scenario_update.update_log_status_from_output(log)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)
        assert log[0].status == 'success'
        log2= TestExecutionLog.objects.filter(test_scenario=self.test_scenario2)[0]
        simulation.set_value('inverter_2', 'active_power', 1000)
        assert simulation.data['inverter_2']['active_power'] == 15
        print("set value for active_power",simulation.data['inverter_2']['active_power'] )
        self.scenario_update.update_values_for_inputs(log2, 'initial')
        self.scenario_update.update_log_status_from_output(log2, 'initial')
        simulation.set_value('inverter_2', 'active_power', 0)
        assert simulation.data['inverter_2']['active_power'] == 0
        print("set intial value to 0")
        self.scenario_update.update_values_for_inputs(log2)
        self.scenario_update.update_log_status_from_output(log2)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario2)
        assert log[0].status == 'success'
        self.scenario_update.stop_servers()

    def test_log_failure_status_when_min_cell_voltage_less_and_pcs_is_not_turned_off(self):
        TestExecutionLog.objects.filter().delete()
        simulation = self.scenario_update.simulator
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.start_servers()
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)[0]
        simulation.set_value('inverter_1', 'active_power', 1000)
        assert simulation.data['inverter_1']['active_power'] == 15
        self.scenario_update.update_values_for_inputs(log, 'initial')
        self.scenario_update.update_log_status_from_output(log, 'initial')
        self.scenario_update.update_values_for_inputs(log)
        self.scenario_update.update_log_status_from_output(log)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)
        assert log[0].status == 'failure'
        self.scenario_update.stop_servers()

    def test_log_success_status_when_max_cell_voltage_greater_and_pcs_is_not_turned_off(self):
        TestExecutionLog.objects.filter().delete()
        simulation = self.scenario_update.simulator
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.start_servers()
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario3)[0]
        simulation.set_value('inverter_1', 'active_power', 1000)
        assert simulation.data['inverter_1']['active_power'] == 15
        self.scenario_update.update_values_for_inputs(log, 'initial')
        self.scenario_update.update_log_status_from_output(log, 'initial')
        simulation.set_value('inverter_1', 'active_power', 0)
        assert simulation.data['inverter_1']['active_power'] == 0
        self.scenario_update.update_values_for_inputs(log)
        self.scenario_update.update_log_status_from_output(log)
        log = TestExecutionLog.objects.filter(test_scenario=self.test_scenario3)
        assert log[0].status == 'success'
        self.scenario_update.stop_servers()


    def test_all_ex(self):
        TestExecutionLog.objects.filter().delete()
        simulation = self.scenario_update.simulator
        self.scenario_update.create_test_log_for_test_scenarios()
        self.scenario_update.start_servers()
        for log in TestExecutionLog.objects.filter():
            simulation.set_value('inverter_1', 'active_power', 1000)
            simulation.set_value('inverter_2', 'active_power', 1000)
            self.scenario_update.update_values_for_inputs(log, 'initial')
            self.scenario_update.update_log_status_from_output(log,  'initial')
            simulation.set_value('inverter_1', 'active_power', 0)
            simulation.set_value('inverter_2', 'active_power', 0)
            assert simulation.data['inverter_1']['active_power'] == 0
            self.scenario_update.update_values_for_inputs(log)
            self.scenario_update.update_log_status_from_output(log)
        assert TestExecutionLog.objects.filter(test_scenario=self.test_scenario1)[0].status == 'success'
        assert TestExecutionLog.objects.filter(test_scenario=self.test_scenario2)[0].status == 'success'






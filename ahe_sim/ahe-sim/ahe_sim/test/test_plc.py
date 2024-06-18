import time
from unittest import TestCase
import ahe_sim
from ahe_mb.models import Map, Field, SiteDevice, DeviceMap
from ahe_mb.master import ModbusMaster
from ahe_sim.models import TestExecutionLog, Input, TestScenario, Output
from ahe_sys.models import DeviceType, Site, AheClient, SiteDeviceList
from ahe_sim.plc_health import PlcHealth
from ahe_sim.sim import Simulation
import ahe_action
import ahe_sys


class SimTestPlc(TestCase):
    def setUp(self):
        TestExecutionLog.objects.filter().delete()
        Output.objects.filter().delete()
        Input.objects.filter().delete()
        TestScenario.objects.filter().delete()
        SiteDevice.objects.filter().delete()
        self.client = AheClient.objects.get_or_create(name='test')[0]
        self.site = Site.objects.get_or_create(name='test', client=self.client)[0]
        self.site_device_conf = SiteDeviceList.objects.get_or_create(site=self.site, version=1)[0]
        self.device_type1 = DeviceType.objects.get_or_create(name='SMA sunny_island pcs')[0]
        self.device_type2 = DeviceType.objects.get_or_create(name='ebick_bms')[0]
        self.device_type3 = DeviceType.objects.get_or_create(name='SFERE 700m2 grid')[0]
        self.device_type4 = DeviceType.objects.get_or_create(name='SFERE 700m2 ess')[0]
        self.device_type5 = DeviceType.objects.get_or_create(name='phoenix')[0]
        self.device_type6 = DeviceType.objects.get_or_create(name='Temperature Scanner')[0]
        self.map_obj1 = Map.objects.get_or_create(name='sma_sunny_island')[0]
        self.map_obj2 = Map.objects.get_or_create(name='ebick_bms')[0]
        self.map_obj3 = Map.objects.get_or_create(name='sfere_700m2_grid')[0]
        self.map_obj4 = Map.objects.get_or_create(name='sfere_700m2_ess')[0]
        self.map_obj5 = Map.objects.get_or_create(name='phoenix_ilc_171_eth_2_tx')[0]
        self.map_obj6 = Map.objects.get_or_create(name='multispan_temperature_scanner')[0]
        DeviceMap.objects.get_or_create(map=self.map_obj2, device_type=self.device_type2, )
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
        self.battery_1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type2, ip_address='0.0.0.0', port=5204, unit=1,
                                             name='battery_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.battery_2 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type2, ip_address='0.0.0.0', port=5205, unit=1,
                                             name='battery_2',
                                             site_device_conf=self.site_device_conf)[0]
        self.ems_1 = \
            SiteDevice.objects.get_or_create(device_type=self.device_type5, ip_address='0.0.0.0', port=5208, unit=1,
                                             name='ems_1',
                                             site_device_conf=self.site_device_conf)[0]
        self.min_cell_voltage = Field.objects.get(map=self.map_obj2, ahe_name='min_cell_voltage')
        self.max_cell_voltage = Field.objects.get(map=self.map_obj2, ahe_name='max_cell_voltage')
        self.active_power = Field.objects.get(map=self.map_obj1, ahe_name='active_power')
        self.pv_channel_1 = Field.objects.get(ahe_name='pv_channel_1', map=self.map_obj6)
        self.simulator = Simulation()

    def test_connection_plc(self):
        plc = PlcHealth(self.ems_1, self.simulator)
        plc.simulator.start_server(self.ems_1.name)
        time.sleep(1)
        assert plc.is_reachable()
        plc.simulator.stop_server(self.ems_1.name)

    def test_plc_can_connect_to_all_devices(self):
        plc = PlcHealth(self.ems_1, self.simulator)
        for dev in plc.connected_devices:
            plc.simulator.start_server(dev.name)
        plc.simulator.start_server(self.ems_1.name)
        time.sleep(1)
        mb = ModbusMaster(self.ems_1, '', {"block_name": "test_1"})
        mb.write({'ems_1_inverter_1_status': 1, 'ems_1_battery_1_status': 1, 'ems_1_battery_2_status': 1})
        status = plc.can_connect_to_all_devices()
        assert status['battery_1'] == 1
        assert status['battery_2'] == 1
        assert status['inverter_1'] == 1
        for dev in plc.connected_devices:
            plc.simulator.stop_server(dev.name)
        plc.simulator.stop_server(self.ems_1.name)

    def test_plc_can_not_to_connect_to_all_devices(self):
        plc = PlcHealth(self.ems_1, self.simulator)
        for dev in plc.connected_devices:
            plc.simulator.start_server(dev.name)
        plc.simulator.start_server(self.ems_1.name)
        time.sleep(1)
        mb = ModbusMaster(self.ems_1, '', {"block_name": "test_1"})
        mb.write({'ems_1_battery_1_status': 1, 'ems_1_battery_2_status': 1})
        status = plc.can_connect_to_all_devices()
        assert status['inverter_1'] == False
        for dev in plc.connected_devices:
            plc.simulator.stop_server(dev.name)
        plc.simulator.stop_server(self.ems_1.name)
        assert not plc.get_plc_health_status()

    def test_failed_plc_health_status_when_plc_is_not_reachable(self):
        plc = PlcHealth(self.ems_1, self.simulator)
        assert not plc.get_plc_health_status()




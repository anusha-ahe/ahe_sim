from random import randint
from django.test import TestCase
from parameterized import parameterized
# from ahe_mb.test.common import TestModbus
from ahe_mb.query import ModbusQuery
import unittest
from ahe_sys.update import create_site
# from ahe_mb.test.prepare import create_test_devices
from ahe_mb.update import create_modbus_map, create_device_conf
from ahe_mb.connection import connect_modbus 
from ahe_mb.models import DeviceMap

LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = 5020

@unittest.skip("redesign")
class TestQuery(TestCase):
    def setUp(self):
        # self.site = create_site(999, "site 999")
        # self.modbus = create_modbus_map(name="mb_t1")
        # self.modbus_coil = create_modbus_map(name='mb_coil', map_reg="Coil")
        self.device1 = create_device_conf()

    def test_modbus_connect_should_need_device_and_address_1(self):
        with self.assertRaises(TypeError):
            ModbusQuery()

    def test_modbus_connect_should_need_device_and_address_2(self):
        with self.assertRaises(TypeError):
            ModbusQuery("")

    def test_queries_should_use_same_connection(self):
        all_devices = self.device1.detail.all()
        print("all_devices", all_devices)
        maps =  DeviceMap.objects.filter(device_type=all_devices[0].device_type)
        print("maps", maps)
        query1 = ModbusQuery(all_devices[0], (0, 1), maps[0], "test_block")
        query2 = ModbusQuery(all_devices[0], (2, 5), maps[0], "test_block")
        self.assertTrue(query1 is not query2)
        self.assertTrue(query1.connection is query2.connection)

    QUERY_VARIABLE = [
        ((0, 1), {"test_device_1_var1", "test_device_1_var2"}),
        ((1, 10), {"test_device_1_var2", "test_device_1_var3"}),
        ((5, 5), {"test_device_1_var3"}),
        ((230, 240), {"test_device_1_var4"}),
        ]

    @parameterized.expand(QUERY_VARIABLE)
    def test_query_is_created_with_correct_variable(self, address_range, required):
        all_devices = self.device1.detail.all()
        print("-- self.device1", all_devices[0].device_type)
        maps =  DeviceMap.objects.filter(device_type=all_devices[0].device_type)
        print("-- maps", maps)
        query1 = ModbusQuery(all_devices[0], address_range, maps[0], "test_block")
        print("-- query1", query1.name_to_address)
        self.assertGreaterEqual(query1.name_to_address.keys(), required)
        self.assertGreaterEqual(query1.name_to_variable.keys(), required)

    QUERY_ADDRESS = [
        ((0, 1), {0, 1}),
        ((1, 10), {1, 5}),
        ((5, 5), {5}),
        ((230, 240), {240}),
        ]

    @parameterized.expand(QUERY_ADDRESS)
    def test_query_is_created_with_correct_addresses(self, address_range, required):
        all_devices = self.device1.detail.all()
        print("self.device1", all_devices[0].device_type)
        maps =  DeviceMap.objects.filter(device_type=all_devices[0].device_type)
        query1 = ModbusQuery(all_devices[0], address_range, maps[0], "test_block")
        print("query1", query1.address_to_variable)
        self.assertGreaterEqual(query1.address_to_variable.keys(), required)

    QUERY_VAR_REGISTERS =[
        ((0,1), [100, 101], 0, 100),
        ((0,1), [100, 101], 1, 101),
        ((0,5), [200, 201, 202, 203, 204, 205], 5, 205),
        ((4,5), [304, 305], 5, 305),
    ]

    @parameterized.expand(QUERY_VAR_REGISTERS)
    def test_query_updates_registers_correctly(self, address_range, registers, var_address, var_value):
        all_devices = self.device1.detail.all()
        print("self.device1", all_devices[0].device_type)
        maps =  DeviceMap.objects.filter(device_type=all_devices[0].device_type)
        query1 = ModbusQuery(all_devices[0], address_range, maps[0], "test_block")
        query1.assign_registers_to_variables(registers)
        print("query1", query1.address_to_variable)
        self.assertEqual(query1.address_to_variable[var_address].var.value, var_value)

    QUERY_VAR_VALUES =[
        ((0,1), {"test_device_1_var1": 5001}, "test_device_1_var1", 5001, {0: 5001}),
        ((0,1), {"test_device_1_var2": 5002}, "test_device_1_var2", 5002, {1: 5002}),
        ((2,5), {"test_device_1_var3": 5003}, "test_device_1_var3", 5003, {5: 5003}),
    ]

    @parameterized.expand(QUERY_VAR_VALUES)
    def test_query_updates_values_correctly(self, address_range, data, var_name, var_value, write_vals):
        # address_range = (0,1) 
        # data = {"test_device_1_v1": 5001} 
        # var_name = "test_device_1_v1" 
        # var_value = 5001
        all_devices = self.device1.detail.all()
        print("self.device1", all_devices[0].device_type)
        maps =  DeviceMap.objects.filter(device_type=all_devices[0].device_type)
        query1 = ModbusQuery(all_devices[0], address_range, maps[0], "test_block")
        result = query1.assign_values_to_variables(data)
        print("query1", query1.name_to_variable)
        self.assertEqual(query1.name_to_variable[var_name].var.value, var_value)
        self.assertEqual(result, write_vals)

    QUERY_BUFFER_VALUES = [
        ((0, 1), {0: 6000}, {0: [6000]}),
        ((0, 1), {1: 6001}, {1: [6001]}),
        ((0, 1), {0: 6000, 1: 6001}, {0: [6000, 6001]}),
        ((1, 5), {1: 6001}, {1: [6001]}),
        ((0, 5), {1: 6001}, {1: [6001]}),
        ((0, 5), {0: 6000, 1: 6001, 5: 6005}, {0: [6000, 6001], 5:[6005]}),
    ]

    @parameterized.expand(QUERY_BUFFER_VALUES)
    def test_query_data_to_buffers_correctly(self, address_range, data, expected):
        # address_range = (0,1) 
        # data = {0: 6001} 
        all_devices = self.device1.detail.all()
        print("self.device1", all_devices[0].device_type)
        maps =  DeviceMap.objects.filter(device_type=all_devices[0].device_type)
        query1 = ModbusQuery(all_devices[0], address_range, maps[0], "test_block")
        result = query1.data_to_buffers(data)
        print("result", result)
        self.assertEqual(result, expected)


    def test_query_read(self):
        address_range = (0,5)
        data = [110, 111, 112, 113, 114, 115] 
        expected = {'test_device_1_var1': 110, 'test_device_1_var2': 111, 'test_device_1_var3': 115}
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        conn1.write(1, 4, 0, data, "test_block")
        all_devices = self.device1.detail.all()
        print("self.device1", all_devices[0].device_type)
        maps =  DeviceMap.objects.filter(device_type=all_devices[0].device_type)
        query1 = ModbusQuery(all_devices[0], address_range, maps[0], "test_block")
        result = query1.read()
        print("result", result)
        result_match = True
        for k in expected:
            if result[k] != expected[k]:
                result_match = False
        self.assertTrue(result_match)

    def test_query_write(self):
        address_range = (0,5)
        expected = [210, 211, 212, 213, 214, 215] 
        data = {'test_device_1_var1': 210, 'test_device_1_var2': 211, 'test_device_1_var3': 215}
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        all_devices = self.device1.detail.all()
        print("self.device1", all_devices[0].device_type)
        maps =  DeviceMap.objects.filter(device_type=all_devices[0].device_type)
        query1 = ModbusQuery(all_devices[0], address_range, maps[0], "test_block")
        print("before write")
        result = query1.write(data)
        self.assertIsNone(result)
        res = conn1.read(1, 4, 0, 5)
        print("result", result, res)
        self.assertEqual(expected[0], res[0])
        self.assertEqual(expected[1], res[1])        
        self.assertEqual(expected[5], res[5])        
from random import randint
from django.test import TestCase
from parameterized import parameterized
from ahe_mb.update import create_modbus_map, REF_DEVICE_1, MAP_MOD_DATA, create_device_conf, create_device_map
import copy
import ahe_mb
from ahe_mb.master import ModbusMaster, compute_query_addresses
import unittest


@unittest.skip("redesign")
class TestMaster(TestCase):

    def test_modbus_master_should_need_device(self):
        with self.assertRaises(TypeError):
            ModbusMaster("")

    def test_modbus_master_create(self):
        device_conf = create_device_conf()
        devices = device_conf.detail.all()
        master = ahe_mb.ahe_open(
            devices[0], "", {"block_name": "test_block"})
        self.assertIsNotNone(master)
        self.assertEqual(type(master), ahe_mb.master.ModbusMaster)

    VALID_ADDRESS = [
        (0, 1, 'uint16', [0, 1]),
        (0, 2, 'uint16', [0, 2]),
        (10, 1, 'sint16', [10, 11]),
        (12, 1, 'sint32', [12, 13, 14]),
        (14, 1, 'uint32', [14, 15, 16]),
        (14, 2, 'uint32', [14, 16, 17]),
        (16, 1, 'float32', [16, 17, 18]),
    ]

    INVALID_ADDRESS = [
        (0, 1, 'uint16', [2]),
        (0, 2, 'uint16', [1, 3]),
        (10, 1, 'sint16', [9, 12]),
        (12, 1, 'sint32', [11, 15]),
        (14, 2, 'uint32', [13, 15, 18]),
    ]

    @parameterized.expand(VALID_ADDRESS)
    def test_valid_addresses(self, start_address, field_address, field_format, required_addresses):
        addresses = self.generate_addresses_for_master(start_address, field_address, field_format, required_addresses)
        for addr in required_addresses:
            self.assertIn(addr, addresses)

    def generate_addresses_for_master(self, start_address, field_address, field_format, required_addresses):
        field_data = [{'field_address': 0,
                       'name': 'v1',
                       "field_format": 'uint16'},
                      {'field_address': field_address,
                       'name': 'v2',
                       "field_format": field_format}]
        modbus_map = create_modbus_map(name="mb_t3", detail=field_data)
        print("---- ----- modbus map id", modbus_map.id)
        dev_type = create_device_map(detail=[{"map": modbus_map.id, "start_address": start_address}])        
        dev_map1 = ahe_mb.models.DeviceMap.objects.filter(device_type=dev_type)
        print("---- ----- dev_map id", dev_map1[0].map.id)

        device_data = copy.copy(REF_DEVICE_1)
        device_data["device_type"] = dev_type.id
        device_conf = create_device_conf(detail=[device_data])
        print("--- --- device_conf", device_conf)
        devices = device_conf.detail.all()
        for device in devices:
            print("^^^ ^^^ device", device, device.device_type.id)
            device_map = ahe_mb.models.DeviceMap.objects.filter(device_type=device.device_type).first()
            print("^^^ ^^^^ map", device_map.map.id)
        print("--- --- devices", device_conf, devices[0].device_type.id)
        master1 = ahe_mb.ahe_open(devices[0], "", {"block_name": "test_block"})
        device_maps =  ahe_mb.models.DeviceMap.objects.filter(device_type=devices[0].device_type)
        
        print(" ---- ---- device_maps id", device_maps[0].id, device_maps)
        addresses, _, _ = master1._list_map_addresses(device_maps[0])
        print("addresses", addresses)
        print("required_addresses", required_addresses)
        return addresses

    @parameterized.expand(INVALID_ADDRESS)
    def test_invalid_addresses(self, start_address, field_address, field_format, required_addresses):
        addresses = self.generate_addresses_for_master(start_address, field_address, field_format, required_addresses)
        for addr in required_addresses:
            self.assertNotIn(addr, addresses)

    def test_should_read_data(self):
        device_conf = create_device_conf()
        devices = device_conf.detail.all()
        master = ahe_mb.ahe_open(devices[0], "", {"block_name": "test_block"})
        
        self.assertIsNotNone(master)
        data = master.read(0)
        print("data a", data)
        self.assertIsNotNone(data)
        data = master.read(0)
        print("data b", data)
        self.assertIsNotNone(data)

    WRITE_DATA = [
        ({'test_device_1_var1': 11},),
        ({'test_device_1_var2': 22},),
        ({'test_device_1_var3': 33},),
        ({'test_device_1_var1': 111, 'test_device_1_var3': 313},),
        ({'test_device_1_var1': 211, 'test_device_1_var4': 214},),
    ]

    @parameterized.expand(WRITE_DATA)
    def test_should_write_data(self, write_values):
        device_conf = create_device_conf()
        devices = device_conf.detail.all()
        master = ahe_mb.ahe_open(devices[0], "", {"block_name": "test_block"})
        status = master.write(write_values)
        data = dict()
        while True:
            d = master.read(0)
            if not d:
                break
            data.update(d)
        print("data after update ", data, write_values)
        for k in write_values:
            self.assertEqual(data[k], write_values[k])
        self.assertEqual({"status": "received"}, status)

    @parameterized.expand(WRITE_DATA)
    def test_should_write_data_with_epoch(self, write_values):
        device_conf = create_device_conf()
        devices = device_conf.detail.all()
        master = ahe_mb.ahe_open(devices[0], "", {"flags": "data_with_epoch", "block_name": "test_block"})

        status = master.write(write_values)
        data = dict()
        while True:
            d = master.read(0)
            if not d:
                break
            data.update(d)
        print(data)
        for k in write_values:
            self.assertEqual(data[k]["value"], write_values[k])
        self.assertEqual({"status": "received"}, status)


QUERY_TESTS_CONTGIOUS = [
    [120, [1, 2, 3, 4], [(1, 4)]],
    [2, [1, 2, 3, 4], [(1, 2), (3, 4)]],
    [120, [1, 2, 203, 204], [(1, 2), (203, 204)]],
    [120, [1, 2, 103, 104], [(1, 2), (103, 104)]],
    [120, [1, 2, 3, 204], [(1, 3), (204, 204)]],
    [2, [1, 2, 3, 204], [(1, 2), (3, 3), (204, 204)]],
    [4, [1, 2, 3, 4], [(1, 4)]]
]


QUERY_TESTS_WITH_GAPES = [
    [120, [1, 2, 3, 4], [(1, 4)]],
    [2, [1, 2, 3, 4], [(1, 2), (3, 4)]],
    [120, [1, 2, 103, 104], [(1, 104)]],
    [20, [1, 2, 3, 20, 21], [(1, 20), (21, 21)]],
    [2, [1, 2, 4, 5], [(1, 2), (4, 5)]],
    [2, [1, 2, 4, 5, 7, 8], [(1, 2), (4, 5), (7, 8)]],
    [4, [1, 2, 4, 5, 7, 8], [(1, 4), (5, 8)]],
    [4, [1, 2, 3, 4], [(1, 4)]],
    [120, [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
           23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
           41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
           57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 86, 87, 88, 89, 90,
           91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105,
           106, 107, 108, 109, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341,
           1342, 1343, 1344, 1345, 1410, 1411, 1412, 1413, 1414, 1415], [(6, 109), (1334, 1415)]]
]


class TestQueryComputations(TestCase):
    @parameterized.expand(QUERY_TESTS_CONTGIOUS)
    def test_query_contigious(self, query_size, addresses, expected_queries):
        queries = compute_query_addresses(query_size, addresses, False)
        print(queries)
        print(expected_queries)
        self.assertEqual(queries, expected_queries)

    @parameterized.expand(QUERY_TESTS_WITH_GAPES)
    def test_query_with_gapes(self, query_size, addresses, expected_queries):
        queries = compute_query_addresses(query_size, addresses, True)
        self.assertEqual(queries, expected_queries)

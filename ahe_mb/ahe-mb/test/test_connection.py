from django.test import TestCase
from parameterized import parameterized
from ahe_mb.connection import connect_modbus, Connection 
from ahe_mb.test.common import TestModbus
import unittest

LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = 5020
INVALID_PORT = 5021

class TestConnection(TestCase):

    def test_modbus_connect(self):
        connection = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        self.assertIsNotNone(connection)
        self.assertEqual(type(connection), Connection)

    def test_modbus_connect_should_return_same_connection(self):
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        conn2 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        self.assertTrue(conn1 is conn2)

    def test_connection_should_read(self):
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        self.assertEqual(len(conn1.read(1, 4, 1, 11)), 11)

    def test_connections_should_read_same_data(self):
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        conn2 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        self.assertEqual(conn1.read(1, 4, 1, 10), conn2.read(1, 4, 1, 10))

    def test_connections_should_fail(self):
        conn1 = connect_modbus(LOCAL_HOST, INVALID_PORT)
        self.assertIsNone(conn1.read(1, 4, 1, 10))

    def test_connections_should_disconnect(self):
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        data = conn1.read(1, 4, 1, 10)
        print("data", data)
        self.assertEqual(conn1.connected, True)
        conn1.disconnect(None, 1, 0, 4, 0, 0)
        self.assertEqual(conn1.connected, False)

    def test_connections_should_not_disconnect_on_illegle_read(self):
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        data = conn1.read(1, 4, 100, 110)
        print("data", data)
        self.assertEqual(conn1.connected, True)
        self.assertEqual(conn1.fail_count, 0)

    def test_should_write_and_read(self):
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        conn2 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        data = [1, 2, 3, 4]
        conn1.write(1, 4, 10, data, "test_block")
        self.assertEqual(conn2.read(1, 4, 10, 13), data)
        data = [91, 92, 93, 94]
        conn1.write(1, 4, 10, data, "test_block")
        self.assertEqual(conn2.read(1, 4, 10, 13), data)

    def test_should_write_and_read_for_coil(self):
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        conn2 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        data = [1]
        conn1.write(1, 1, 10, data, "test_block")
        self.assertEqual(conn2.read(1, 1, 10, 11)[0:1], [True])

    def test_should_write_multiple_times_and_read_for_coil(self):
        conn1 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        conn2 = connect_modbus(LOCAL_HOST, LOCAL_PORT)
        conn1.write(1, 1, 34, [0], "test_block")
        self.assertEqual(conn2.read(1, 1, 34, 34)[0:3], [False, False, False])
        conn1.write(1, 1, 35, [1], "test_block")
        self.assertEqual(conn2.read(1, 1, 34, 35)[0:3], [False, True, False])
        conn1.write(1, 1, 36, [1], "test_block")
        self.assertEqual(conn2.read(1, 1, 34, 36)[0:3], [False, True, True])
        conn1.write(1, 1, 37, [1], "test_block")
        self.assertEqual(conn2.read(1, 1, 34, 37)[
                         0:4], [False, True, True, True])

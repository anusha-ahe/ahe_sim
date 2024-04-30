from importlib.util import module_for_loader
import string
import json
import os
import sys
from unittest import main
from django.test import TestCase
from ahe_translate.test.prepare import create_test_hirarchy
from ahe_translate import Transform
import pytest
import time

NODE_STRUCTURE = {
    "main": {},
    "battery_1": {
        "main": {},
        "battery_1_s_1": {
            "main": {},
            "battery_1_s_1_m_1": {},
            "battery_1_s_1_m_2": {}},
        "battery_1_s_2": {
            "main": {},
            "battery_1_s_2_m_1": {},
            "battery_1_s_2_m_2": {}}},
    "battery_2": {
        "main": {},
        "battery_2_s_1": {
            "main": {},
            "battery_2_s_1_m_1": {},
            "battery_2_s_1_m_2": {}},
        "battery_2_s_2": {
            "main": {},
            "battery_2_s_2_m_1": {},
            "battery_2_s_2_m_2": {}}}}


INPUT_DATA = {"epoch": 111,
              "battery_1_power": 10,
              "battery_2_power": 30,
              "_battery_2_s_1_power": 11,
              "_battery_2_s_2_power": 31,
              "__battery_2_s_2_m_1_power": 12,
              "__battery_2_s_2_m_2_power": 32}


RESULT_TREE = {'main':  {"epoch": 111},
               'battery_1': {'main': {'battery_1_power': 10},
                             'battery_1_s_1': {'main': {},
                                               'battery_1_s_1_m_1': {}, 'battery_1_s_1_m_2': {}},
                             'battery_1_s_2': {'main': {},
                                               'battery_1_s_2_m_1': {}, 'battery_1_s_2_m_2': {}}},
               'battery_2': {'main': {'battery_2_power': 30},
                             'battery_2_s_1': {'main': {'battery_2_s_1_power': 11},
                                               'battery_2_s_1_m_1': {},
                                               'battery_2_s_1_m_2': {}}, 'battery_2_s_2':
                             {'main': {'battery_2_s_2_power': 31},
                              'battery_2_s_2_m_1': {'battery_2_s_2_m_1_power': 12},
                              'battery_2_s_2_m_2': {'battery_2_s_2_m_2_power': 32}}}}


node_param = [{
    "name": "ROOT",
    "count": 1,
    "pattern": "",
    "variables": ["epoch"]
},
    {
    "name": "battery",
    "count": 2,
    "pattern": "battery_{d}_",
    "variables": []
},
    {
    "name": "string",
    "count": 2,
    "pattern": "s_{d}_",
    "variables": []
},
    {
    "name": "module",
    "count": 2,
    "pattern": "m_{d}_",
    "variables": []
}]


class TestHirarchy(TestCase):
    def setUp(self):
        hirarchy, nodes = create_test_hirarchy(node_param)
        self.hirarchy = hirarchy
        self.nodes = nodes
        self.transform = Transform(hirarchy)

    def perform_multiple_build(self):
        for node in self.nodes:
            if not node.parent:
                root_node = node
        print("root node", root_node)
        start_time = time.time()
        for _ in range(100):
            self.transform.build_structure(root_node)
        print("structure total time", time.time() - start_time)

    def test_build_structure(self):
        for node in self.nodes:
            if not node.parent:
                root_node = node
        print("root node", root_node)
        structure, refrence = self.transform.build_structure(root_node)
        print("refrence", refrence)
        self.assertEqual(structure, NODE_STRUCTURE)

    def test_flat_to_hirarchy(self):
        reply = self.transform.write(INPUT_DATA)
        print("reply", reply)
        print("expected", RESULT_TREE)
        self.assertEqual(reply, RESULT_TREE)

    def test_flat_to_hirarchy_azure(self):
        hirarchy, _ = create_test_hirarchy(node_param)
        transform = Transform(hirarchy)
        os.chdir(sys.path[0])
        print(os.getcwd())
        with open('edge1-azure.json') as fi:
            input_data = json.load(fi)
        reply = transform.write(input_data)
        with open('out.json') as fi:
            out_data = json.load(fi)
        # with open("outdata.json", "w") as fo:
        #     json.dump(reply, fo)
        self.assertEqual(out_data, reply)

    def time_azure_hirarchy(self):
        hirarchy, _ = create_test_hirarchy(node_param)
        transform = Transform(hirarchy)
        os.chdir(sys.path[0])
        print(os.getcwd())
        with open('edge1-azure.json') as fi:
            input_data = json.load(fi)
        start_time = time.time()
        for _ in range(100):
            reply = transform.write(input_data)
        print("azure total time", time.time() - start_time)


if __name__ == '__main__':
    th = TestHirarchy()
    th.setUp()
    th.perform_multiple_build()
    th.time_azure_hirarchy()

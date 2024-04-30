from collections import defaultdict
import os
import re
from django.conf import settings
import ahe_log
import django
import importlib
import ahe_translate
from functools import lru_cache
from mergedeep import merge
import re
import requests


if not settings.configured:
    settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
    # print("Using setting file:", settings_file)
    settings_module = importlib.import_module(settings_file)
    django.setup()


class Transform():
    def __init__(self, hirarchy_object):
        self.logger = ahe_log.get_logger('ahe_redis')
        self.hirarchy = hirarchy_object
        self.logger.info(f"started compute {hirarchy_object}")

    def build_structure(self, node, parent_name="", level=1):
        if level in (1, 2, 3):
            data_struct = {f"main": dict()}
        else:
            data_struct = dict()
        data_pointers = dict()
        # get all children
        children = ahe_translate.models.Node.objects.filter(parent=node)
        for child in children:
            for dev in range(1, child.count + 1):
                # get structure for each child
                device_name = self.gen_device_name(parent_name, dev, child)
                child_struct, child_pointers = self.build_structure(
                    child, device_name, level + 1)
                # combine
                data_struct[device_name.strip("_")] = child_struct
                if level in (1, 2):
                    data_pointers["^" + device_name] = child_struct["main"]
                else:
                    data_pointers["^" + device_name] = child_struct
                variables = ahe_translate.models.NodeVariable.objects.filter(
                    parent=node)
                for var in variables:
                    data_pointers[var.variable] = data_struct["main"]
                data_pointers.update(child_pointers)
        return data_struct, data_pointers

    def gen_device_name(self, parent_name, dev, child):
        if parent_name:
            return "_" + parent_name + \
                child.pattern.format(d=dev)
        else:
            return child.pattern.format(d=dev)

    def write(self, data):
        root_node = ahe_translate.models.Node.objects.get(
            hirarchy=self.hirarchy, parent=None)
        data_struct, data_pointers = self.build_structure(root_node)
        for pattern in data_pointers:
            for key in data:
                if (pattern[0] == "^" and key.startswith(pattern[1:])) or key == pattern:
                    data_pointers[pattern][key.lstrip("_")] = data[key]
        return data_struct


class Translate:
    def __init__(self, config, params=None):
        self.params = params
        self.logger = ahe_log.get_logger('ahe_redis')
        self.logger.info(
            f"translation name:{config.name} site_id:{config.site.id}")
        self.config = config
        self.translations = ahe_translate.models.Translation.objects.filter(
            config=config).order_by('seq')

    def get_list_of_variables(self):
        headers = {"api-key": "CxVHFo4L.Zr5jrOcxEftuhLgBLnzgknzrJvNwrosQ"}
        url = "https://demo.amperehourenergy.com/api/ems/v3/list-of-data-items"
        req_param = {"site_id": self.config.site.id}
        if self.params == "cell":
            req_param["cell"] = "true"
        res = requests.get(url, headers=headers, params=req_param)
        list_of_items = [key for key in res.json().keys()]
        return list_of_items

    def process_trasnlatation(self, translate, data, variables):
        variables = [var for var in variables if var is not None]
        if translate.func == "HIERACHY" and len(variables) == 0 and translate.dest not in data:
            data[translate.dest] = {}
        elif len(variables) == 0 and translate.func != "HIERACHY":
            data[translate.dest] = None
        elif translate.func == "HIERACHY":
            for var in variables:
                data[translate.dest].update(var)
        elif translate.func == "COPY":
            data[translate.dest] = variables[0]
        elif translate.func == "SUM":
            data[translate.dest] = sum(variables) if variables else 0
        elif translate.func == "AVG":
            data[translate.dest] = sum(
                variables) / len(variables) if variables else 0
        elif translate.func == "REPLACE":
            params = translate.param.split(',')
            for var in variables:
                for key, value in var.items():
                    dest = key.replace(params[0], params[1])
                    data[dest] = value
        elif translate.func == "COMBINE" and len(variables) == 2:
            fn_data1 = str(int(variables[0]))
            fn_data2 = str(int(variables[1]))
            fn_data1 = fn_data1 if len(fn_data1) > 1 else f"0{fn_data1}"
            fn_data2 = fn_data2 if len(fn_data2) > 1 else f"0{fn_data2}"
            data[translate.dest] = f"{fn_data1}:{fn_data2}"
        elif translate.func == "ADJUST":
            data[translate.dest] = 0 if - \
                5 <= variables[0] <= 5 else variables[0]
        elif translate.func == "MUL":
            total = 1
            print("variables", variables)
            for variable in variables:
                total *= variable
            data[translate.dest] = total
        elif translate.func == "SELECT":
            for var in variables:
                for key, value in var.items():
                    data[translate.dest].update(var)
        elif translate.func == "SUB":
            total = None
            for variable in variables:
                if total:
                    total -= variable
                else:
                    total = variable
            data[translate.dest] = abs(total)
        elif translate.func == "DIV" and len(variables) == 2:
            data[translate.dest] = float(variables[0]) / float(variables[1])

        self.logger.debug(
            f"translate func:{translate.func},value:{translate.dest}")
        return data

    def grab_variable(self, translate, data, removed_keys, select_key):
        variables = []
        for d in data:
            variable = re.search(translate.source, d)
            if variable:
                self.logger.debug(
                    f"translation found for variable:{d},pattern:{translate.source}")
                if translate.func in ("HIERACHY", "REPLACE"):
                    variables.append({d: data[d]})
                    removed_keys.append(d)
                elif translate.func == "SELECT":
                    variables.append({d: data[d]})
                    select_key.append(translate.dest)
                elif translate.func == "REMOVE":
                    removed_keys.append(d)
                else:
                    variables.append(data[d])
                if translate.param and translate.func not in ("HIERACHY", "REPLACE"):
                    variables.append(translate.param)

        if len(variables) == 0:
            self.logger.debug(
                f"not matched found for pattern: {translate.source}")
        return variables

    def write(self, data, items_list=None):
        if items_list:
            data = {k: v for k, v in data.items() if k in items_list or k in [
                "epoch"]}
        elif self.params:
            variables = self.get_list_of_variables()
            data = {k: v for k, v in data.items() if k in variables or k in [
                "epoch"]}
        removed_keys = []
        select_key = []
        data = defaultdict(dict, data)
        for translate in self.translations:
            variables = self.grab_variable(
                translate, data, removed_keys, select_key)
            if translate.func != "REMOVE":
                self.process_trasnlatation(translate, data, variables)
            data = defaultdict(
                dict, {k: v for k, v in data.items() if k not in removed_keys})
            removed_keys = []
        if select_key:
            selected_data = {}
            for k, v in data.items():
                if k == "epoch":
                    selected_data[k] = v
                elif k in select_key:
                    selected_data.update(data[k])
            data = selected_data.copy()
        return dict(data)



class KeyTranslate():

    def compute_nextkey(self, max_key):
        if not max_key:
            return 'A000'
        key_char = list(max_key)
        key_char[3] = chr(ord(key_char[3]) + 1)
        for idx in range(3, 0, -1):
            # print(key_char)
            if key_char[idx] == ':':
                key_char[idx] = 'A'
            if key_char[idx] == '[':
                key_char[idx] = '0'
                key_char[idx-1] = chr(ord(key_char[idx-1]) + 1)
        return "".join(key_char)

    def get_keymap_for_variables(self, vars):
        key_var_map = []
        for var in vars:
            key_obj = ahe_translate.models.KeyMap.objects.filter(var=var)
            if not key_obj:
                last_key = ahe_translate.models.KeyMap.objects.all().order_by('-key').first()
                if last_key:
                    new_key = self.compute_nextkey(last_key.key)
                else:
                    new_key = 'A000'
                key_obj = ahe_translate.models.KeyMap.objects.create(
                    key=new_key, var=var)
                key_var_map.append({"key": key_obj.key, "var": key_obj.var})
            else:
                key_var_map.append(
                    {"key": key_obj[0].key, "var": key_obj[0].var})
        return key_var_map

    @lru_cache(maxsize=10000)
    def get_key_for_var(self, var):
        key_objcts = ahe_translate.models.KeyMap.objects.filter(var=var)
        if key_objcts:
            return key_objcts[0].key
        else:
            return var

    @lru_cache(maxsize=10000)
    def get_var_for_key(self, key):
        key_objcts = ahe_translate.models.KeyMap.objects.filter(key=key)
        if key_objcts:
            return key_objcts[0].var
        else:
            raise KeyError("No variable defined for {key}")

    def compact_data(self, data):
        data_out = dict()
        for var in data:
            if var in ["epoch"]:
                data_out[var] = data[var]
                continue
            data_out[self.get_key_for_var(var)] = data[var]

        return data_out

    def expand_data(self, data):
        data_out = dict()
        for var in data:
            if var in ["epoch"]:
                data_out[var] = data[var]
                continue
            data_out[self.get_var_for_key(var)] = data[var]
        return data_out

    def send_data(self, url, data):
        requests.post(url, json=data)

    def transfer_keymaps(self, url, variables):
        data = self.get_keymap_for_variables(variables)
        self.send_data(url, data)


def ahe_open(data_config, _mode, _params):
    if type(data_config) == ahe_translate.models.Config:
        return Translate(data_config, _params)
    else:
        return None

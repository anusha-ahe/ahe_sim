import re
from collections import defaultdict
from ahe_translate.models import Hirarchy, Node
# from mergedeep import merge


# class Translator():
#     def __init__(self, name) -> None:
#         self.translation = Translation.objects.get(name=name)
#         self.mappings = dict()

#     def translate(self, data):
#         if not isinstance(data, dict):
#             raise TypeError("Translator only accepts dict")
#         reply = dict()
#         mappings = Mapping.objects.filter(translation=self.translation)
#         for key in data:
#             for mapping in mappings:
#                 print("key:", key)
#                 print("Pattern:", mapping.pattern)
#                 pe = re.compile(mapping.pattern)
#                 found = pe.search(key)
#                 print(found)
#                 if found is None:
#                     continue
#                 print("Found:", found)
#                 print(mapping.remove1, mapping.add1,
#                       mapping.remove2, mapping.add2)
#                 rem1 = re.search(mapping.remove1, key).span()
#                 new_key = key[:rem1[0]] + mapping.add1 + key[rem1[1]:]
#                 if mapping.remove2 is not None:
#                     rem2 = re.search(mapping.remove2, new_key).span()
#                     new_key = new_key[:rem2[0]] + \
#                         mapping.add2 + new_key[rem2[1]:]
#                 reply[new_key] = data[key]
#                 break
#         computes = Compute.objects.filter(translation=self.translation)
#         for compute in computes:
#             print("Compute:", compute.destination, compute.function,
#                   compute.source1, compute.source2)
#             fn_data1 = list()
#             fn_data2 = list()
#             for key in reply:
#                 res1 = re.search(compute.source1, key)
#                 print(res1)
#                 if res1 is not None:
#                     fn_data1.append(reply[key])
#                 if compute.source2 is not None:
#                     res2 = re.search(compute.source2, key)
#                     print(res2)
#                     if res2 is not None:
#                         fn_data2.append(reply[key])
#             print(fn_data1, fn_data2)
#             if compute.function == 'SUM' and len(fn_data1) > 0:
#                 print("sum", fn_data1)
#                 reply[compute.destination] = sum(fn_data1)
#         return reply


# class Aggrigator():
#     def __init__(self) -> None:
#         self.data = dict()

#     def add(self, topic, epoch, data):
#         self.data.update(data)
#         self.data[f'{topic}_epoch'] = epoch

#     def get_data(self):
#         return self.data


class Transform:
    def __init__(self, name):
        self.translation = Translation.objects.get(name=name)

    def get_tree_structure(self, list_of_dict):
        tree_str = []
        for data in list_of_dict:
            tree = {}
            for keys, value in data.items():
                t = tree
                for key in keys[:-1]:
                    t = t.setdefault(key, {})
            t[keys[-1]] = value
            tree_str.append(tree)
        return tree_str

    def check_if_is_device_part(self, key):
        is_device_part = Hirarchy.objects.filter(
            translation=self.translation, key_name=key).\
            values_list('is_device_part', flat=True)
        if is_device_part:
            is_device_part = is_device_part[0]
        else:
            is_device_part = False
        return is_device_part

    def flatten(self, d, is_device, parent_key=''):
        last_key = ''
        items = []
        for k, v in d.items():
            last_key = k
            new_key = parent_key + k if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten(v, is_device, new_key).items())
            else:
                if is_device:
                    new_key = new_key.replace(last_key, f"_{last_key}")
                items.append((f"{new_key}", v))
        return dict(items)

    def seperate_device_and_non_device_data(self, curr_data):
        device_data = {}
        non_device_data = {}
        for root_key, root_value in curr_data.items():
            for sub_k, sub_v in root_value.items():
                if self.check_if_is_device_part(root_key):
                    device_data.update({sub_k: sub_v})
                else:
                    non_device_data.update({f'{root_key}_{sub_k}': sub_v})
        return device_data, non_device_data

    def convert_flat_to_hierachy(self, data):
        temp_list = []
        hierachy_objs = Hirarchy.objects.filter(
            translation=self.translation).order_by('id').all()
        for hierachy_obj in hierachy_objs:
            if not hierachy_obj.has_variables:
                continue
            for hierachy in hierachy_obj.get_hierachy():
                if hierachy_obj.is_device_part:
                    parent_key = ''.join(hierachy[2:])
                else:
                    parent_key = ''.join(hierachy[1:])
                for key, value in data.items():
                    if key.startswith(parent_key):
                        key = key.replace(f'{parent_key}_', '')
                        d = {hierachy[1:]: {key: value}}
                        temp_list.append(d)
        temp_list = self.get_tree_structure(temp_list)
        hierachy_json = merge({}, *tuple(temp_list))
        return hierachy_json

    def convert_hierachy_to_flat(self, data):
        device_data, non_device_data = self.seperate_device_and_non_device_data(
            data)
        non_device_data_flat_json = self.flatten(non_device_data, False)
        device_data_flat_json = self.flatten(device_data, True)
        return {**non_device_data_flat_json, **device_data_flat_json}

import re
from threading import Condition
from django.db import transaction
from django.db.models.fields.related import ForeignKey
from django.db.models import Max
from ahe_sys.common.serializer import get_obj_with_max_version
# from ahe_sys.views import DeviceTypeUpdate

ERR_MISSING_IN_HEADER = "missing in the header"
MISSING_COLUMN_DATA = "is required in data"
INVALID_VALUE = "is invalid for"
ERR_GREATER = "should be greater than"
ALREADY_USED = "already used."


def is_valid_name(text):
    if text == "":
        return True
    re1 = re.compile(r"^[a-z][a-z0-9_]*$")
    if text:
        r = re1.search(text)
        return r
    return False


def is_address_overlaping(a1, a2):
    if a1[0] < a2[0]:
        p1 = a1
        p2 = a2
    else:
        p2 = a1
        p1 = a2
    if p1[1] >= p2[0]:
        return True
    return False


class Row:
    model = None
    REQUIRED_COLUMNS = []
    NONE_BLANK_COLUMNS = []
    NAME_FIELDS = []
    INT_FIELDS = []
    FLOAT_FIELDS = []
    RANGE_FIELDS = {}
    FIELD_RELATIVE = {}
    UNIQUE_FIELDS = []
    KEY_GENERATION_COLS = []
    VALID_OPTIONS = {}
    INVALID_OPTIONS = {}
    INVALID_COMBINATION = []
    VALID_COMBINATION = []
    CHAR_FIELDS = []

    def __str__(self):
        return f'{self.__class__.__name__}: {self.data}'

    def __init__(self, data) -> None:
        self.data = data
        self.err = list()
        self._check_for_missing_column()
        
        if not self.err:
            print("a", self.data)
            self._make_map_id()
            print("b")
            self._check_for_blank_values()
            print("c")
            self._check_for_valid_name()
            print("d")
            self._check_convet_int()
            print("e")
            self._check_convet_float()
            print("f")
            self._check_for_valid_range()
            print("g")
            self._check_for_relative_value()
            print("h")
            self._check_valid_choices()
            print("i")
            self._check_invalid_choices()
            print("j")
            self._prevent_invalid_combination()
            print("k")
            self._allow_valid_combination()
            print("l")
            self._check_for_character()
            print("m")

    def _make_map_id(self):
        self.map_id = tuple([self.data[k].lower().replace(" ", "_")
                            for k in self.KEY_GENERATION_COLS])

    def _check_for_missing_column(self):
        print("_check_for_missing_column")
        for k in self.REQUIRED_COLUMNS:
            if k not in self.data:
                self.err.append(f"{k} {ERR_MISSING_IN_HEADER}")

    def _check_for_blank_values(self):
        print(f"Check {self.NONE_BLANK_COLUMNS} in {self.data}")
        for h in self.NONE_BLANK_COLUMNS:
            if self.data[h] is None or self.data[h] == '':
                self.err.append(f'{h} {MISSING_COLUMN_DATA}')

    def _check_for_valid_name(self):
        for field in self.NAME_FIELDS:
            print("name check for ", field)
            if field in self.data:
                self.data[field] = self.data[field].lower()
            if field in self.data and not is_valid_name(self.data[field]):
                self.err.append(f'{self.data[field]} {INVALID_VALUE} {field}')

    def _check_convet_int(self):
        for field in self.INT_FIELDS:
            print("     # check for int", field)
            if field not in self.data:
                continue
            try:
                self.data[field] = int(self.data[field])
                print("succeed", self.data)
            except ValueError as e:
                print("failed", self.data)
                self.err.append(f'{self.data[field]} {INVALID_VALUE} {field}')

    def _check_convet_float(self):
        for field in self.FLOAT_FIELDS:
            if field not in self.data:
                continue
            try:
                self.data[field] = float(self.data[field])
            except ValueError as e:
                if self.data[field] != "":
                    self.err.append(
                        f'{self.data[field]} {INVALID_VALUE} {field}')
                else:
                    self.data[field] = None

    def _check_for_character(self):
        for field in self.CHAR_FIELDS:
            if field in self.data:
                if (self.data[field] != "") and (not self.data[field].isalpha()):
                    self.err.append(
                        f'{self.data[field]} {INVALID_VALUE} {field}')

    def _check_for_valid_range(self):
        for field in self.RANGE_FIELDS.keys():
            print("range check", field, self.RANGE_FIELDS[field], self.data)
            if field not in self.data:
                print("field missing", field)
                continue
            if type(self.data[field]) != int:
                print("Not int")
                continue
            if self.data[field] < self.RANGE_FIELDS[field]["min"]:
                self.err.append(f'{self.data[field]} {INVALID_VALUE} {field}')
            if self.data[field] > self.RANGE_FIELDS[field]["max"]:
                self.err.append(f'{self.data[field]} {INVALID_VALUE} {field}')

    def _check_for_relative_value(self):
        for field in self.FIELD_RELATIVE.keys():
            if type(self.data[field]) is not int:
                continue
            for key in self.FIELD_RELATIVE[field].keys():
                rel_field = self.FIELD_RELATIVE[field][key]
                if type(self.data[rel_field]) is not int:
                    continue
                if key == ">=":
                    if self.data[field] < self.data[rel_field]:
                        self.err.append(
                            f'{self.data[field]} {INVALID_VALUE} {field}')
                else:
                    self.err.append(f"unknown operator {key}")

    def _check_valid_choices(self):
        for field in self.VALID_OPTIONS.keys():
            if field not in self.data:
                continue
            choices = self.VALID_OPTIONS[field]
            print("allow valid choices", field, choices)
            if self.data[field] not in choices:
                self.err.append(f'{self.data[field]} {INVALID_VALUE} {field}')

    def _check_invalid_choices(self):
        for field in self.INVALID_OPTIONS.keys():
            if field not in self.data:
                continue
            choices = self.INVALID_OPTIONS[field]
            print("allow valid choices", field, choices)
            if self.data[field] in choices:
                self.err.append(f'{self.data[field]} {INVALID_VALUE} {field}')

    def _prevent_invalid_combination(self):

        for check_no in range(len(self.INVALID_COMBINATION)):
            # if field not in self.data:
            #     print(f"field {field} is missing")
            #     continue
            condition = self.INVALID_COMBINATION[check_no]["condition"]
            choices = self.INVALID_COMBINATION[check_no]["choices"]
            field = self.INVALID_COMBINATION[check_no]["field"]
            print(
                f"prevent invalid combination {check_no}, {choices}, {condition}")
            check = False
            reason = ""

            for k in condition:
                print(f"condition {self.data}")
                print(f"condition {condition[k]}")
                if condition[k] == "None" and (k not in self.data or not self.data[k]):
                    check = True
                    reason = f"{k} is {condition[k]}"
                if k in self.data and self.data[k] == condition[k]:
                    check = True
                    reason = f"{k} is {condition[k]}"

            if check and self.data[field] in choices:
                print(f"{self.data[field]} found in {choices}")
                self.err.append(
                    f'{self.data[field]} {INVALID_VALUE} {field} as {reason}')

    def _allow_valid_combination(self):
        for check_no in range(len(self.VALID_COMBINATION)):
            field = self.VALID_COMBINATION[check_no]["field"]

            if field not in self.data:
                continue
            condition = self.VALID_COMBINATION[check_no]["condition"]
            choices = self.VALID_COMBINATION[check_no]["choices"]
            print(
                f"allow valid combination {field}='{self.data[field]}', {choices}, {condition}")
            check = True
            for k in condition:
                if k not in self.data:
                    if condition[k] != "None":
                        check = False
                    continue

                print(f"condition {self.data[k]}-{condition[k]}")
                if condition[k] == "Not None":
                    print(self.data[k], not self.data[k])
                    if not self.data[k]:
                        print("Do not check any")
                        check = False
                elif self.data[k] != condition[k]:
                    print("Do not check match")
                    check = False

            if check and self.data[field] not in choices:
                print(f"{self.data[field]} not found in {choices}")
                key = list(condition.keys())[0]
                self.err.append(
                    f'{self.data[field]} {INVALID_VALUE} {field} as {key} is {condition[key]}')

    def get_row_field_data(self):
        foraign_keys = dict()
        print("self model", self.model)
        if self.model:
            for field in self.model._meta.fields:
                if isinstance(field, ForeignKey):
                    foraign_keys[field.name] = field
        data = dict()
        for k in self.ROW_FIELDS:
            print("  # Adding", k, foraign_keys)
            if k in self.data:
                # if k in foraign_keys:
                #     fk = foraign_keys[k]
                #     query = {"name": self.data[fk.name]}
                #     print("obtain FK id", k, fk)
                #     new_fkey = get_obj_with_max_version(
                #         fk.remote_field.model,
                #         query)
                #     if new_fkey:
                #         data[fk.name] = new_fkey.id
                # else:
                data[k] = self.data[k]
        return data


class FileLoader:
    UNIQUE_FIELDS = []
    OVERLAP_FIELDS = []
    MASTER_FIELDS = []
    row_processing_class = None
    row_class = None
    row_master_key = ""
    master_class = None
    update_class = None

    def __init__(self) -> None:
        self.maps = dict()
        self.err = list()

    def _check_duplicate(self, r):
        for k in self.UNIQUE_FIELDS:
            for row in self.maps[r.map_id]:
                if row.data[k] and row.data[k] == r.data[k]:
                    self.err.append(f"{r.data[k]} {ALREADY_USED} {k}")

    def _check_overlap(self, r):
        for o in self.OVERLAP_FIELDS:
            for row in self.maps[r.map_id]:
                if is_address_overlaping((row.data[o[0]], row.data[o[1]]), (r.data[o[0]], r.data[o[1]])):
                    self.err.append(
                        f"{r.data[o[0]]}-{r.data[o[1]]} {ALREADY_USED} {o[0]}-{o[1]}")

    def _load_rows(self, csv_data):
        for row in csv_data:
            r = self.row_processing_class(row)
            print("row", r)
            if r.err:
                self.err.extend(r.err)
            if hasattr(r, "map_id"):
                print(r.map_id)
                if r.map_id not in self.maps:
                    self.maps[r.map_id] = list()
                self._check_duplicate(r)
                self._check_overlap(r)
                self.maps[r.map_id].append(r)

    def _save_maps(self):
        for map_id in self.maps:
            print("Save map", map_id, self.maps[map_id], self.maps[map_id][0].data)
            map_name = "_".join(map_id)
            map_param = dict()
            map_param["name"] = map_name
            for field in self.MASTER_FIELDS:
                if field in self.maps[map_id][0].data:
                    map_param[field] = self.maps[map_id][0].data[field]
            detail_list = list()
            for row in self.maps[map_id]:
                detail_list.append(row.get_row_field_data())
            upd = self.update_class()
            ser = self.update_class.serializer()
            map_param['detail'] = detail_list
            print("map_param", map_param)
            self.before_master_update(map_id, map_param)
            upd.upsert(map_param)

    def load_csv(self, csv_data, replace=False):
        self._load_rows(csv_data)
        if self.err:
            return self.err
        self._save_maps()

    def before_master_update(self, map_id, map_param):
        # Impliment this function to perform task before master object creation
        pass

from django.db.models import Max
from django.db.models.fields.related import ForeignKey
import re
import copy
from ahe_sys.common.loader import ERR_MISSING_IN_HEADER, MISSING_COLUMN_DATA, INVALID_VALUE, ALREADY_USED
from ahe_sys.common.serializer import extract_errors, FIELD_REQUIRED


def update_parameters(kwargs, allowed_parameters, data):
    for k in kwargs:
        if k in allowed_parameters:
            data[k] = kwargs[k]

class Update():
    serializer = None
    csvserializer = None
    query_cols = ["name"]
    fk_query_col = "name"
    key = ["id"]

    def _list_other_foraign_keys(self):
        foraign_keys = list()
        for field in self.serializer.Meta.model._meta.fields:
            if isinstance(field, ForeignKey):
                foraign_keys.append(field)
        return foraign_keys

    def _upsert(self, data, partial, instance=None):
        print("_upsert", data, partial)
        if partial:
            ser = self.serializer(instance, data=data, partial=partial)
        else:
            ser = self.serializer(data=data)
        if ser.is_valid():
            ser.save()
            return ser.instance
        print("### Error  in _upsert:", ser.errors)
        raise ValueError(ser.errors)

    def upsert(self, data_in):
        """ Call this function to add or update a any data"""
        data = copy.deepcopy(data_in)
        if not self.query_cols:
            raise ValueError("query_cols is required for master detail update")
            
        cols = [x.name for x in self.serializer.Meta.model._meta.fields]
        query = dict()
        for key in self.query_cols:
            query[key] = data[key]
        if "version" not in cols:
            return self._upsert_normal(data, query)
        else:
            return self._upsert_with_version(data, query)

    def _upsert_with_version(self, data, query):
        query["version"] = self.serializer.Meta.model.objects.filter(
                **query).aggregate(Max('version'))["version__max"]
        prev_instance = self.serializer.Meta.model.objects.filter(**query).first()
        if prev_instance:
            data_to_save = self.serializer(prev_instance).data
        else:
            data_to_save = dict()
            data["version"] = 0
        data_to_save.update(data)
        data_to_save["version"] += 1
        if "id" in data_to_save:
            del data_to_save["id"]
        obj_v =  self._upsert(data_to_save, False)
        return obj_v

    def _upsert_normal(self, data, query):
        prev_instance = self.serializer.Meta.model.objects.filter(**query).first()
        if prev_instance:
            n_obj = self._upsert(data, True, prev_instance)
        else:
            n_obj = self._upsert(data, False)
        return n_obj
  
    def get_id(self, **kwargs):
        objects = self.serializer.Meta.model.objects.filter(**kwargs)
        if len(objects) < 1:
            return None
        if 'version' not in kwargs:
            version = objects.aggregate(Max('version'))["version__max"]
            objects = self.serializer.Meta.model.objects.filter(version=version, **kwargs)
        if len(objects) == 1:
            return objects.first().id
        else:
            return None

    def get(self, pk):
        instance = self.serializer.Meta.model.objects.filter(pk=pk).first()
        ser = self.serializer(instance)
        serializer_data = ser.data
        if isinstance(serializer_data, list):
            serializer_data = serializer_data[0]
        data = dict()
        for k in serializer_data:
            if isinstance(serializer_data[k], list):
                data[k] = [dict(x) for x in serializer_data[k]]
            else:
                data[k] = serializer_data[k]
        return data


    def load_csv(self, data):
        self.err = list()
        ser = self.serializer()
        detail_ser = ser.get_fields()[ser.Meta.detail_column].child
        master_column = detail_ser.Meta.master_column
        if master_column not in data[0]:
            self.err.append(FIELD_REQUIRED.format("bit_map"))
            return 
        master_key_list = list()
        detail = list()
        for d in data:
            print("data", d, self.query_cols)
            dict_data = dict()
            master_key = list()
            for col in self.query_cols:
                dict_data[col] = d[master_column]
                master_key.append(d[master_column])
                del  d[master_column]
            detail.append(d)
            master_key_list.append(tuple(master_key))
            print("dict_data", dict_data)
        master_key_set = set(master_key_list)
        print("master_key_list", master_key_set, len(master_key_set))
        if len(master_key_set) != 1:
            self.err.append(f"single master key required instead {master_key_set} found")
            return
        ser_data = dict()
        for c in range(len(self.query_cols)):
            ser_data[self.query_cols[c]] = master_key_list[0][c]
        ser_data[self.serializer.Meta.detail_column] = detail
        print("ser_data", ser_data)
        try:
            self.upsert(ser_data)
        except ValueError as e:
            print("ValueError", e)
            err = e.args[0]
            for key in err.keys():
                self.err.append(f"{key}: {err[key][0]}")
                print("-------err", key, err[key][0])

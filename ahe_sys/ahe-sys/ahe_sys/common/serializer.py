from rest_framework import serializers
from django.db.models.fields.related import ForeignKey
from rest_framework.utils import model_meta
from django.db.models import Max


def get_obj_with_max_version(fk_model, query):
    print("get_obj_with_max_version", fk_model, query)
    if not query:
        return None
    cols = [x.name for x in fk_model._meta.fields]
    if "version" in cols:
        remote_max_version = fk_model.objects.filter(**query).aggregate(Max('version'))["version__max"]
        query["version"] = remote_max_version
    return fk_model.objects.get(**query)


class MasterSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        print("MasterSerializer: create", validated_data)
        detail_serializer = self.get_fields()[self.Meta.detail_column].child
        detail_data = validated_data.pop(self.Meta.detail_column)
        print("detail data in master serializer", detail_data)
        # print("**   MAst:A", validated_data)
        self._assign_fk_objects(validated_data)
        # print("**   MAst:B", validated_data)
        self._assign_master_object(validated_data)
        master_obj = self.Meta.model.objects.create(**validated_data)
        for data in detail_data:
            print("master_obj before", master_obj.id)
            data[str(detail_serializer.__class__.Meta.master_column)] = master_obj
            print("master_obj", master_obj.id)
            print("data after master", data)
            ser = detail_serializer.__class__(data=data)
            if ser.is_valid():
                print("valid, save")
                ser.save()
            else:
                print("### detail Error:", ser.errors, ser.data)
                raise ValueError(ser.errors)

        return master_obj

    def _list_other_foraign_keys(self):
        foraign_keys = dict()
        for field in self.Meta.model._meta.fields:
            if isinstance(field, ForeignKey):
                foraign_keys[field.name] = field
        return foraign_keys

    def update(self, instance, validated_data):
        validated_data["version"] = instance.version + 1
        return self.create(validated_data)

    def run_validation(self, initial_data):
        print("MasterSerializer: run_validation", initial_data)
        for col in self.Meta.model._meta.fields:
            if hasattr(self, "prevalidate_" + col.name):
                fn = getattr(self, "prevalidate_" + col.name)
                initial_data[col.name] = fn(initial_data.get(col.name, None))
        self._store_fk_names(initial_data)
        return super().run_validation(initial_data)

    def _store_master_obj(self, initial_data):
        if not hasattr(self.Meta, "master_column"):
            return
        if self.Meta.master_column in initial_data:
            self.master_obj = initial_data.pop(self.Meta.master_column)

    def _store_fk_names(self, initial_data):
        self.fk_values = dict()
        if not hasattr(self.Meta, "fk_cols"):
            return
        for fk in self.Meta.fk_cols:
            if fk in initial_data:
                if type(initial_data[fk]) == dict:
                    self.fk_values[fk] = initial_data[fk][self.Meta.fk_cols[fk]]
                else:
                    self.fk_values[fk] = initial_data[fk]
                initial_data[fk] = self.fk_values[fk]

    def _assign_fk_objects(self, validated_data):
        if not hasattr(self.Meta, "fk_cols"):
            return
        foraign_fields = self._list_other_foraign_keys()
        for fk_f in self.Meta.fk_cols.keys():
            if fk_f in self.fk_values and self.fk_values[fk_f]:
                query = {self.Meta.fk_cols[fk_f]: self.fk_values[fk_f]}
                fk = foraign_fields[fk_f]
                fk_obj = get_obj_with_max_version(fk.remote_field.model, query)
                validated_data[fk_f] = fk_obj

    def _assign_master_object(self, validated_data):
        if not hasattr(self.Meta, "master_column"):
            print("master_column not present in ", self)
            return
        validated_data[self.Meta.master_column] = self.master_obj


class DetailSerializer(serializers.ModelSerializer):

    def run_validation(self, initial_data):
        print("DetailSerializer: initial_data", initial_data)
        for col in self.Meta.model._meta.fields:
            if hasattr(self, "prevalidate_" + col.name):
                fn = getattr(self, "prevalidate_" + col.name)
                initial_data[col.name] = fn(initial_data.get(col.name, None))

        self._store_master_obj(initial_data)
        self._store_fk_names(initial_data)
        return super().run_validation(initial_data)

    def _store_fk_names(self, initial_data):
        self.fk_values = dict()
        if not hasattr(self.Meta, "fk_cols"):
            return
        for fk in self.Meta.fk_cols:
            if fk in initial_data:
                if type(initial_data[fk]) == dict:
                    self.fk_values[fk] = initial_data[fk][self.Meta.fk_cols[fk]]
                else:
                    self.fk_values[fk] = initial_data[fk]
                initial_data[fk] = self.fk_values[fk]

    def _store_master_obj(self, initial_data):
        if not hasattr(self.Meta, "master_column"):
            return
        if self.Meta.master_column in initial_data:
            self.master_obj = initial_data.pop(self.Meta.master_column)

    def create(self, validated_data):
        print("DetailSerializer: create: validated_data", validated_data)
        self._assign_fk_objects(validated_data)
        self._assign_master_object(validated_data)
        det_obj = self.Meta.model.objects.create(**validated_data)
        print("created detail object", det_obj)
        return validated_data

    def _assign_fk_objects(self, validated_data):
        if not hasattr(self.Meta, "fk_cols"):
            return
        foraign_fields = self._list_other_foraign_keys()
        for fk_f in self.Meta.fk_cols.keys():
            if fk_f in self.fk_values:
                if self.fk_values[fk_f]:
                    query = {self.Meta.fk_cols[fk_f]: self.fk_values[fk_f]}
                    fk = foraign_fields[fk_f]
                    fk_obj = get_obj_with_max_version(fk.remote_field.model, query)
                    validated_data[fk_f] = fk_obj
                else:
                    del validated_data[fk_f]

    def _assign_master_object(self, validated_data):
        if not hasattr(self.Meta, "master_column"):
            return
        validated_data[self.Meta.master_column] = self.master_obj

    def update(self, instance, validated_data):
        self._assign_fk_objects(validated_data)
        self._assign_master_object(validated_data)
        info = model_meta.get_field_info(instance)
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        print("m2m_fields", m2m_fields)
        instance.save()
        return instance

    def _list_other_foraign_keys(self):
        foraign_keys = dict()
        for field in self.Meta.model._meta.fields:
            print("         field", field, type(field))
            if isinstance(field, ForeignKey):
                foraign_keys[field.name] = field
        print("Listed foraign_keys", foraign_keys)
        return foraign_keys
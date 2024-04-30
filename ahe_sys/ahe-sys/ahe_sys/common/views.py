from rest_framework import viewsets, mixins
from django.db.models import Max
from rest_framework.response import Response

from ahe_sys import serializer


class MasterDetailViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    master_serializer = None
    list_serializer = None
    search_field = "name"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset()[0]
        serializer = self.get_serializer(instance)
        print(f"retrieve:{self.kwargs}", serializer.data)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_queryset()[0]
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'list':
            if not self.list_serializer:
                raise ValueError("list_serializer is required")
            return self.list_serializer
        if not self.master_serializer:
            raise ValueError("master_serializer is required")
        return self.master_serializer


    def get_queryset(self):
        master_model = self.master_serializer.Meta.model
        print(f"get_queryset:{self.kwargs}", master_model)
        if self.search_field not in self.kwargs:
            query_params = self.request.query_params
            print("ALL", query_params.get('all', None))
            if query_params.get('all', None):
                return self._get_all(master_model)
            return self._get_all_latest(master_model)
        latest_obj = self._get_single_latest(master_model)
        print(f"returning:{self.kwargs}", latest_obj)
        return latest_obj

    def _get_single_latest(self, master_model):
        query = {self.search_field: self.kwargs[self.search_field]}
        print("_get_single_latest query", query)
        max_version = master_model.objects.filter(
            **query).aggregate(Max('version'))["version__max"]
        print("_get_latest max_version", max_version)
        latest_obj = master_model.objects.filter(
            **query, version=max_version)
        print("latest_obj", latest_obj, "***")
        return latest_obj

    def _get_all(self, master_model):
        return master_model.objects.all()

    def _get_all_latest(self, master_model):
        request_values = master_model.objects.all().values(self.search_field) \
            .annotate(max_version=Max('version'))
        print("request_values", request_values)
        resp_list = list()
        for x in request_values:
            query = {self.search_field: x[self.search_field], 
                     "version":x["max_version"]}
            print("query", query, master_model.objects.filter( **query).first())
            resp_list.append(master_model.objects.filter( **query).first())
            print("resp list", resp_list)
        return resp_list

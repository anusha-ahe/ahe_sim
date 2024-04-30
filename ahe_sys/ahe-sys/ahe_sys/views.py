from rest_framework import status, viewsets, mixins
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse
from rest_framework.decorators import api_view
from django.utils.encoding import uri_to_iri
from ahe_sys.serializer import SiteSerializer, SiteMetaConfSerializer, DeviceTypeListSerializer, \
    SiteVariableListSerializer, AheClientSerializer
from ahe_sys.models import Site, SiteMetaConf, SiteMeta, DeviceType, SiteVariableList, AheClient
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Max




class SiteViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):

    # queryset = Site.objects.all()
    serializer_class = SiteSerializer

    def get_queryset(self):
        client = self.request.query_params.get('client')
        client_id = self.request.query_params.get('client_id')
        if client_id is not None:
            queryset = Site.objects.filter(client=client_id)
        elif client is not None:
            queryset = Site.objects.filter(client__name=client)
        else:
            queryset = Site.objects.all()
        return queryset


class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeListSerializer


class AheClientViewSet(viewsets.ModelViewSet):
    queryset = AheClient.objects.all().order_by("start_site_id")
    serializer_class = AheClientSerializer    
    # queryset = DeviceType.objects.all()
    # serializer_class = DeviceTypeListSerializer




class SiteMetaConfViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):

    serializer_class = SiteMetaConfSerializer

    def get_queryset(self):
        max_version = SiteMetaConf.objects.filter(
            site=self.kwargs['site_pk']).aggregate(Max('version'))["version__max"]
        print("max_version", max_version)
        return SiteMetaConf.objects.filter(site=self.kwargs['site_pk'], version=max_version)




class SiteVariableListViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):

    serializer_class = SiteVariableListSerializer

    def get_queryset(self):
        print("get_queryset")
        max_version = SiteVariableList.objects.filter(
            site=self.kwargs['site_pk']).aggregate(Max('version'))["version__max"]
        print("max_version", max_version)
        return SiteVariableList.objects.filter(site=self.kwargs['site_pk'], version=max_version)



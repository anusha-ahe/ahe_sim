from rest_framework import viewsets
from ahe_sim.models import TestScenario, TestExecutionLog, Input, Output, SimulatorConfig
from .serializers import TestScenarioSerializer, TestExecutionLogSerializer
from ahe_mb.models import DeviceMap, Map, Field



class TestScenarioViewSet(viewsets.ModelViewSet):
    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer


class TestExecutionLogViewSet(viewsets.ModelViewSet):
    queryset = TestExecutionLog.objects.filter()
    serializer_class = TestExecutionLogSerializer






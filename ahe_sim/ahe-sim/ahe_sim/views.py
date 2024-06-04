import os
import subprocess
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework import viewsets
from ahe_sim.models import TestScenario, TestExecutionLog, Input, Output, SimulatorConfig
from .serializers import TestScenarioSerializer, TestExecutionLogSerializer




class TestScenarioViewSet(viewsets.ModelViewSet):
    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer


class TestExecutionLogViewSet(viewsets.ModelViewSet):
    queryset = TestExecutionLog.objects.filter()
    serializer_class = TestExecutionLogSerializer


class TestScenarioListView(View):
    def get(self, request):
        logs = TestExecutionLog.objects.all()
        return render(request, 'test.html', {'logs': logs})


def run_tests(request):
    if request.method == 'POST':
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'scenario.py')
            subprocess.Popen(['python3', script_path])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


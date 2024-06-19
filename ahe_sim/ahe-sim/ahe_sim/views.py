import os
import subprocess
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from rest_framework import viewsets
from .models import TestScenario, TestExecutionLog, Input, Output, SimulatorConfig
from .serializers import TestScenarioSerializer, TestExecutionLogSerializer
from .forms import InputForm, OutputForm,TestScenarioForm
from ahe_mb.models import SiteDevice, DeviceMap, Field




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


def input_view(request):
    if request.method == 'POST':
        test_scenario_form = TestScenarioForm(request.POST, prefix='test_scenario')
        input_form = InputForm(request.POST, prefix='input')
        output_form = OutputForm(request.POST, prefix='output')

        if test_scenario_form.is_valid():
            test_scenario_form.save()
            return redirect('input')
        elif input_form.is_valid():
            input_form.save()
            return redirect('input')
        elif output_form.is_valid():
            output_form.save()
            return redirect('input')
    else:
        test_scenario_form = TestScenarioForm(prefix='test_scenario')
        input_form = InputForm(prefix='input')
        output_form = OutputForm(prefix='output')

    return render(request, 'input.html', {
        'test_scenario_form': test_scenario_form,
        'input_form': input_form,
        'output_form': output_form
    })


def fetch_device_variables(request):
    device_id = request.GET.get('device_id')
    if device_id:
        try:
            device = SiteDevice.objects.get(id=device_id)
            fields = Field.objects.filter(map__devicemap__device_type=device.device_type)
            field_list = list(fields.values('id', 'ahe_name'))
            return JsonResponse({'fields': field_list})
        except SiteDevice.DoesNotExist:
            pass
    return JsonResponse({'fields': []})


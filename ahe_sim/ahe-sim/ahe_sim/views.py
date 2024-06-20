import json
import os
import subprocess
from collections import OrderedDict

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from rest_framework import viewsets
from .models import TestScenario, TestExecutionLog, Input, Output, SimulatorConfig
from .serializers import TestScenarioSerializer, TestExecutionLogSerializer
from .forms import InputForm, OutputForm, TestScenarioForm, DeviceForm
from ahe_mb.models import SiteDevice, DeviceMap, Field

def convert_ordered_dict_to_dict(obj):
    if isinstance(obj, OrderedDict):
        return {k: convert_ordered_dict_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ordered_dict_to_dict(i) for i in obj]
    else:
        return obj


class TestScenarioViewSet(viewsets.ModelViewSet):
    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer


class TestExecutionLogViewSet(viewsets.ModelViewSet):
    queryset = TestExecutionLog.objects.filter()
    serializer_class = TestExecutionLogSerializer


class TestScenarioListView(View):
    def get(self, request):
        logs = TestExecutionLog.objects.all()
        return render(request, 'test_status.html', {'logs': logs})


class TestDetailsListView(View):
    def get(self, request):
        distinct_device_ids = SiteDevice.objects.values_list('id', flat=True).distinct()
        combined_conditions = Q(inputs__device_id__in=distinct_device_ids) | Q(
            outputs__device_id__in=distinct_device_ids)
        test_scenarios = TestScenario.objects.filter(combined_conditions).order_by('priority').distinct()
        serializer = TestScenarioSerializer(test_scenarios, many=True)
        tests = json.dumps(serializer.data)
        print(tests)
        return render(request, 'test_details.html', {'tests': tests})


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
    print("device", device_id)
    if device_id:
        try:
            print("here", device_id)
            device = SiteDevice.objects.get(id=device_id)
            fields = Field.objects.filter(map__devicemap__device_type=device.device_type)
            field_list = list(fields.values('id', 'ahe_name'))
            print(field_list)
            return JsonResponse({'fields': field_list})
        except SiteDevice.DoesNotExist:
            pass
    return JsonResponse({'fields': []})


def device_view(request):
    if request.method == 'POST':
        device_form = DeviceForm(request.POST, prefix='device')
        if device_form.is_valid():
            device_form.save()
            return redirect('device')
    else:
        devices = SiteDevice.objects.all()
        device_form = DeviceForm(prefix='device')
        return render(request, 'device.html', {
            'device_form': device_form, 'devices': devices})
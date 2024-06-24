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


def all_list_view(request):
    return render(request, 'all.html')


class TestScenarioViewSet(viewsets.ModelViewSet):
    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer


class TestExecutionLogViewSet(viewsets.ModelViewSet):
    queryset = TestExecutionLog.objects.filter()
    serializer_class = TestExecutionLogSerializer


class TestScenarioListView(View):
    def get(self, request):
        logs = TestExecutionLog.objects.all()
        return render(request, 'logs.html', {'logs': logs})


class TestDetailsListView(View):
    def get(self, request):
        distinct_device_ids = SiteDevice.objects.values_list('id', flat=True).distinct()
        combined_conditions = Q(inputs__device_id__in=distinct_device_ids) | Q(
            outputs__device_id__in=distinct_device_ids)
        test_scenarios = TestScenario.objects.filter(combined_conditions).order_by('priority')
        serializer = TestScenarioSerializer(test_scenarios, many=True)
        tests = json.dumps(serializer.data)
        return render(request, 'test_details.html', {'tests': tests})


def run_tests(request):
    if request.method == 'POST':
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'scenario.py')
            subprocess.Popen(['python3', script_path])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


def test_scenario_view(request):
    if request.method == 'POST':
        test_scenario_form = TestScenarioForm(request.POST, prefix='test_scenario')
        if test_scenario_form.is_valid():
            test_scenario_form.save()
            return redirect('home')
    else:
        test_scenario_form = TestScenarioForm(prefix='test_scenario')
    return render(request, 'test_scenario.html', {
        'test_scenario_form': test_scenario_form,
    })


def condition_view(request):
    if request.method == 'POST':
        input_form = InputForm(request.POST, prefix='condition')
        if input_form.is_valid():
            input_form.save()
            return redirect('home')
    else:
        input_form = InputForm(prefix='condition')
    return render(request, 'condition.html', {'input_form': input_form})


def action_view(request):
    if request.method == 'POST':
        output_form = OutputForm(request.POST, prefix='action')
        if output_form.is_valid():
            output_form.save()
            return redirect('home')
    else:
        output_form = OutputForm(prefix='action')
    return render(request, 'action.html', {
        'output_form': output_form})


def fetch_device_variables(request):
    device_id = request.GET.get('device_id')
    try:
        device = SiteDevice.objects.get(id=device_id)
        fields = Field.objects.filter(map__devicemap__device_type=device.device_type)
        variables = [{'id': field.id, 'ahe_name': field.ahe_name} for field in fields]
        return JsonResponse({'variables': variables})
    except SiteDevice.DoesNotExist:
        return JsonResponse({'variables': []})


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


def delete_device(request):
    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        try:
            device = SiteDevice.objects.get(id=device_id)
            device.delete()
        except SiteDevice.DoesNotExist:
            print(f"Device Doesnt Exist {device_id}")
    return redirect('device')


def delete_test(request):
    if request.method == 'POST':
        test_id = request.POST.get('test_id')
        try:
            test = TestScenario.objects.get(id=test_id)
            test.delete()
            return JsonResponse({'success': True})
        except TestScenario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Test Scenario does not exist.'})
    return redirect('test_scenario')


def delete_logs(request):
    if request.method == 'POST':
        log_id = request.POST.get('log_id')
        try:
            log = TestExecutionLog.objects.get(id=log_id)
            log.delete()
        except TestExecutionLog.DoesNotExist:
            print(f"Log Doesnt Exist {log_id}")
    return redirect('logs')
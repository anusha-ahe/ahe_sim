import time
import logging
from django.db.models import Q
from ahe_mb.models import SiteDevice
from ahe_sim.models import TestExecutionLog, Input, Output, TestScenario
from ahe_sim.sim import Simulation
from ahe_sim.plc_health import PlcHealth


class ScenarioUpdate:
    def __init__(self):
        self.simulator = Simulation()
        self.stop_device = []
        self.device_names = SiteDevice.objects.exclude(name__icontains='ems').values_list('name', flat=True).distinct()
        self.plc_devices = SiteDevice.objects.filter(name__icontains='ems')

    def get_available_test_scenarios_for_simulator(self):
        distinct_device_ids = SiteDevice.objects.values_list('id', flat=True).distinct()
        combined_conditions = Q(inputs__device_id__in=distinct_device_ids) | Q(
            outputs__device_id__in=distinct_device_ids)
        return TestScenario.objects.filter(combined_conditions).order_by('priority').distinct()

    def start_servers(self):
        for device in self.device_names:
            self.simulator.start_server(device)
            print(f"Started server for device {device}")

    def stop_servers(self):
        for device in self.device_names:
            self.simulator.stop_server(device)
            print(f"Stopped server for device {device}")

    def create_test_log_for_test_scenarios(self):
        test_scenarios = self.get_available_test_scenarios_for_simulator()
        for scenario in test_scenarios:
            TestExecutionLog.objects.get_or_create(test_scenario=scenario, epoch=time.time(), status='pending')

    def update_values_for_inputs(self, log, value_type=None):
        for inp in Input.objects.filter(test_scenario=log.test_scenario):
            if inp.function == 'communication_error' and value_type == 'initial':
                self.simulator.stop_server(inp.device.name)
                self.stop_device.append(inp.device.name)
            value = inp.initial_value if value_type == 'initial' else inp.value
            if value:
                self.simulator.update_and_translate_values(inp.device.name, inp.variable.ahe_name, value)

    def compare_outputs(self, function, actual_output, expected_output):
        comparisons = {
            'equal_to': actual_output == expected_output,
            'greater_than': actual_output > expected_output,
            'less_than': actual_output < expected_output,
            'less_than_equal_to': actual_output <= expected_output,
            'greater_than_equal_to': actual_output >= expected_output,
            'not_equal_to': actual_output != expected_output,
        }
        return comparisons.get(function, False)

    def update_log_status_from_output(self, log, value_type=None):
        start_time = time.time()
        while time.time() - start_time <= log.test_scenario.timeout and log.status != 'failure':
            outputs = []
            for out in Output.objects.filter(test_scenario=log.test_scenario):
                actual_output = self.get_actual_output(out)
                cmp = self.compare_outputs(out.initial_function, actual_output,
                                           out.initial_value) if value_type == 'initial' else self.compare_outputs(
                    out.function, actual_output, out.value)
                outputs.append(cmp)
            if all(outputs):
                if value_type == 'initial':
                    break
                log.status = 'success'
                log.save()
                return
            else:
                print("sleep for before retry as output didn't match")
                time.sleep(1)
        else:
            print("Timeout reached")
            log.status = 'failure'
            log.save()

    def get_actual_output(self, out):
        print("output name", out.device.name)
        if 'ems' in out.device.name:
            plc_health = PlcHealth(out.device, self.simulator)
            plc_data = plc_health.get_plc_data()
            return plc_data[f"{out.device.name}_{out.variable.ahe_name}"]
        return self.simulator.get(out.device.name, out.variable.ahe_name)

    def process_log(self, log):
        self.update_values_for_inputs(log, 'initial')
        self.update_log_status_from_output(log, 'initial')
        log.refresh_from_db()
        if log.status != 'failure':
            self.update_values_for_inputs(log)
            self.update_log_status_from_output(log)
        if self.stop_device:
            for device in self.stop_device:
                self.simulator.start_server(device)

    def update_pending_test_log_status(self):
        self.create_test_log_for_test_scenarios()
        self.start_servers()
        plc_status = [PlcHealth(plc_device, self.simulator).get_plc_health_status() for plc_device in
                      self.plc_devices]
        for log in TestExecutionLog.objects.filter(status='pending'):
            if all(plc_status):
                self.process_log(log)
            else:
                log.status = 'plc_connection_failure'
                log.save()
                print(f"PLC health status failure for devices: {plc_status}")


if __name__ == '__main__':
    su = ScenarioUpdate()
    su.update_pending_test_log_status()
    su.stop_servers()

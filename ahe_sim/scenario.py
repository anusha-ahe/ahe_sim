import time

from django.db.models import Q

import ahe_mb.models
from ahe_sim.models import TestExecutionLog, Input, Output, TestScenario
from ahe_sim.sim import Simulation


class ScenarioUpdate:
    def __init__(self):
        self.simulator = Simulation()
        self.simulator.initialize_servers()
        self.input = dict()
        self.stop_device = list()

    def get_available_test_scenarios_for_simulator(self):
        distinct_device_ids = ahe_mb.models.SiteDevice.objects.values_list('id', flat=True).distinct()
        combined_conditions = Q(inputs__device_id__in=distinct_device_ids) | Q(
            outputs__device_id__in=distinct_device_ids)
        combined_test_scenarios = TestScenario.objects.filter(combined_conditions).order_by('priority').distinct()
        return combined_test_scenarios

    def sort_test_scenarios(self, test_scenarios):
        error_scenarios = []
        other_scenarios = []
        for scenario in test_scenarios:
            if Input.objects.filter(test_scenario=scenario, function='communication_error').exists():
                error_scenarios.append(scenario)
            else:
                other_scenarios.append(scenario)
        return error_scenarios + other_scenarios

    def start_servers(self):
        distinct_device_names = ahe_mb.models.SiteDevice.objects.values_list('name', flat=True).distinct()
        test_scenarios = self.get_available_test_scenarios_for_simulator()
        error_inputs = Input.objects.filter(
            test_scenario__in=test_scenarios,
            function='communication_error')
        stop_device_names = error_inputs.values_list('device__name', flat=True).distinct()
        for device in distinct_device_names:
            if device in stop_device_names:
                self.stop_device.append(device)
            else:
                self.simulator.start_server(device)
                print("started server for device", device)
        print("not started servers ", self.stop_device)

    def create_test_log_for_test_scenarios(self):
        test_scenarios = self.sort_test_scenarios(self.get_available_test_scenarios_for_simulator())
        for scenario in test_scenarios:
            TestExecutionLog.objects.get_or_create(test_scenario=scenario, epoch=time.time(), status='pending')

    def update_values_for_inputs(self, log, value_type=None):
        for inp in Input.objects.filter(test_scenario=log.test_scenario):
            if inp.function != 'communication_error' and value_type == 'initial':
                if inp.device.name in self.stop_device:
                    self.simulator.start_server(inp.device.name)
            value = inp.initial_value if value_type == 'initial' else inp.value
            if value:
                self.simulator.update_and_translate_values(inp.device.name, inp.variable.ahe_name, value)

    def compare_outputs(self, function, actual_output, expected_output):
        if function == 'equal_to' and actual_output == expected_output:
            return True
        elif function == 'greater_than' and actual_output > expected_output:
            return True
        elif function == 'less_than' and actual_output < expected_output:
            return True
        elif function == 'less_than_equal_to' and actual_output <= expected_output:
            return True
        elif function == 'greater_than_equal_to' and actual_output >= expected_output:
            return True
        elif function == 'not_equal_to' and actual_output != expected_output:
            return True
        return False

    def update_log_status_from_output(self, log, value_type=None):
        start_time = time.time()
        while time.time() - start_time <= log.test_scenario.timeout:
            for out in Output.objects.filter(test_scenario=log.test_scenario):
                actual_output = self.simulator.get_values(out.device.name, out.variable.map.name,
                                                          out.variable.ahe_name)
                cmp = self.compare_outputs(out.initial_function, actual_output, out.initial_value) \
                    if value_type == 'initial' else self.compare_outputs(out.function, actual_output, out.value)
                if cmp and value_type != 'initial':
                    log.status = 'success'
                    log.save()
                    break
                elif cmp and value_type == 'initial':
                    break
                else:
                    continue
            else:
                time.sleep(1)
                continue
            break
        else:
            log.status = 'failure'
            log.save()

    def update_pending_test_log_status(self):
        self.create_test_log_for_test_scenarios()
        self.start_servers()
        for log in TestExecutionLog.objects.filter(status='pending'):
            self.update_values_for_inputs(log, 'initial')
            self.update_log_status_from_output(log, 'initial')
            self.update_values_for_inputs(log)
            self.update_log_status_from_output(log)


if __name__ == '__main__':
    su = ScenarioUpdate()
    su.update_pending_test_log_status()

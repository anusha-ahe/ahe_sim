import time
from django.db.models import Q
import ahe_mb.models
from ahe_sim.models import TestExecutionLog, Input, Output, TestScenario
from ahe_sim.sim import Simulation
from ahe_sim.plc_health import PlcHealth


class ScenarioUpdate:
    def __init__(self):
        self.simulator = Simulation()
        self.simulator.initialize_servers()
        self.stop_device = list()
        self.device_names = ahe_mb.models.SiteDevice.objects.values_list('name', flat=True).distinct()

    def get_available_test_scenarios_for_simulator(self):
        distinct_device_ids = ahe_mb.models.SiteDevice.objects.values_list('id', flat=True).distinct()
        combined_conditions = Q(inputs__device_id__in=distinct_device_ids) | Q(
            outputs__device_id__in=distinct_device_ids)
        combined_test_scenarios = TestScenario.objects.filter(combined_conditions).order_by('priority').distinct()
        return combined_test_scenarios

    def start_servers(self):
        print("device names", self.device_names)
        for device in self.device_names:
            print("starting server for device", device)
            self.simulator.start_server(device)
            print("started server for device", device)

    def stop_servers(self):
        for device in self.device_names:
            self.simulator.stop_server(device)
            print("stopped server for device", device)

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
        print(function, actual_output, expected_output)
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
        outputs = list()
        print("start_time", start_time, log.test_scenario.timeout)
        while time.time() - start_time <= log.test_scenario.timeout and log.status != 'failure':
            for out in Output.objects.filter(test_scenario=log.test_scenario):
                actual_output = self.simulator.get(out.device.name,out.variable.ahe_name)
                cmp = self.compare_outputs(out.initial_function, actual_output, out.initial_value) \
                    if value_type == 'initial' else self.compare_outputs(out.function, actual_output, out.value)
                print("here", cmp, value_type, out.variable.ahe_name)
                outputs.append(cmp)
                print("all outputs", outputs)
            if all(outputs) and value_type != 'initial':
                print("success", log)
                log.status = 'success'
                log.save()
                return
            elif all(outputs) and value_type == 'initial':
                break
            else:
                print("sleep as case failed")
                time.sleep(1)
                continue

        else:
            print("timeout reached")
            log.status = 'failure'
            log.save()

    def update_pending_test_log_status(self):
        plc_status = []
        self.create_test_log_for_test_scenarios()
        self.start_servers()
        for plc_device in ahe_mb.models.SiteDevice.objects.filter(name__icontains='ems'):
            plc_health = PlcHealth(plc_device, self.simulator)
            plc_status.append(plc_health.get_plc_health_status())
        if all(plc_status):
            for log in TestExecutionLog.objects.filter(status='pending'):
                self.update_values_for_inputs(log, 'initial')
                self.update_log_status_from_output(log, 'initial')
                log = TestExecutionLog.objects.filter(id=log.id)[0]
                if log.status != 'failure':
                    self.update_values_for_inputs(log)
                    self.update_log_status_from_output(log)
                if self.stop_device:
                    for device in self.stop_device:
                        self.simulator.start_server(device)
        else:
            print("plc health status failed ", plc_status)



if __name__ == '__main__':
    su = ScenarioUpdate()
    su.update_pending_test_log_status()
    su.stop_servers()

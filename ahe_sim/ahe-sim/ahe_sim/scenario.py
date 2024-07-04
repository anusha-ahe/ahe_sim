import time
import logging
from django.db.models import Q
from ahe_mb.models import SiteDevice
from ahe_sim.models import TestExecutionLog, Input, Output, TestScenario
from ahe_sim.sim import Simulation
from ahe_sim.plc_health import PlcHealth
from ahe_translate import Translate
from ahe_translate.models import Config
from ahe_mb.master import ModbusMaster
from ahe_sys.models import Site

site = Site.objects.filter()[0]
Config.objects.filter().delete()
config = Config.objects.get_or_create(id=1, site=site, name='test')[0]


class ScenarioUpdate:
    def __init__(self):
        self.simulator = Simulation()
        self.stop_device = []
        self.device_names = SiteDevice.objects.exclude(name__icontains='ems').values_list('name', flat=True).distinct()
        self.plc_devices = SiteDevice.objects.filter(name__icontains='ems')
        self.devices = SiteDevice.objects.exclude(name__icontains='ems')
        self.mm = dict()
        self.data = dict()

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

    def get_modbus_data(self):
        for device in self.devices:
            if device.name not in self.data:
                self.data[device.name] = dict()
            if device.name not in self.mm:
                self.mm[device.name] = ModbusMaster(device, '', {'block_name': 'test'})
            t = time.time()
            for i in range(len(self.mm[device.name].queries)):
                read_data = self.mm[device.name].read(int(t))
                print("read modbus data", read_data, device.name)
                if read_data:
                    self.data[device.name].update(read_data)

    def update_and_translate_values(self, device_name, ahe_name, value):
        print("log check", device_name, ahe_name, value)
        self.get_modbus_data()
        translate = Translate(config)
        translated_data = translate.write(self.data[device_name])
        data_to_write = {k: translated_data.get(k) for k in self.data[device_name] if
                         translated_data.get(k) != self.data[device_name][k]}
        data_to_write[f"{device_name}_{ahe_name}"] = value
        print("writing values", data_to_write)
        status = self.mm[device_name].write(data_to_write)
        print("write status", status)
        self.get_modbus_data()
        print("after data", self.data)

    def update_values_for_inputs(self, log, value_type=None):
        for inp in Input.objects.filter(test_scenario=log.test_scenario):
            if inp.function == 'communication_error' and value_type == 'initial':
                print("communication error", value_type)
                self.simulator.stop_server(inp.device.name)
                self.stop_device.append(inp.device.name)
                return
            value = inp.initial_value if value_type == 'initial' else inp.value
            if value:
                self.update_and_translate_values(inp.device.name, inp.variable.ahe_name, value)

    def compare_outputs(self, function, actual_output, expected_output):
        actual_output = float(actual_output)
        expected_output = float(expected_output)
        comparisons = {
            'equal_to': actual_output == expected_output,
            'greater_than': actual_output > expected_output,
            'less_than': actual_output < expected_output,
            'less_than_equal_to': actual_output <= expected_output,
            'greater_than_equal_to': actual_output >= expected_output,
            'not_equal_to': actual_output != expected_output,
        }
        print("compare", comparisons, expected_output, function, type(expected_output), type(actual_output),
              actual_output)
        return comparisons.get(function, False)

    def update_log_status_from_output(self, log, value_type=None):
        start_time = time.time()
        while time.time() - start_time <= log.test_scenario.timeout and log.status != 'failure':
            outputs = []
            for out in Output.objects.filter(test_scenario=log.test_scenario):
                actual_output = self.get_actual_output(out)
                print("actual output", actual_output, out.variable.ahe_name)
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
        if 'ems' in out.device.name:
            plc_health = PlcHealth(out.device, self.simulator)
            plc_data = plc_health.get_plc_data()
            return plc_data[f"{out.device.name}_{out.variable.ahe_name}"]
        return self.data[f"{out.device.name}"][f"{out.device.name}_{out.variable.ahe_name}"]

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
            if all([status for plc_data, status in plc_status]):
                self.process_log(log)
            else:
                log.status = 'plc_connection_failure'
                log.save()
                failed_plc_data = [plc_data for plc_data, status in plc_status if not status]
                print(f"PLC health status failure for {log.test_scenario.name} : {failed_plc_data}")


if __name__ == '__main__':
    su = ScenarioUpdate()
    su.update_pending_test_log_status()
    su.stop_servers()

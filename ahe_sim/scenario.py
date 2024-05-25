from ahe_sim.models import TestExecutionLog, Input, Output, SimulatorConfig, TestScenario
import time
from ahe_mb.models import Field, Map
from ahe_sim.sim import Simulation




class ScenarioUpdate:
    def __init__(self):
        self.simulator = Simulation()
        self.simulator.start_server()
        self.input = dict()

    def download_test_scenarios(self):
        distinct_map_ids = SimulatorConfig.objects.values_list('map_name_id', flat=True).distinct()
        distinct_field_ids = Field.objects.filter(map_id__in=distinct_map_ids).values_list('id', flat=True).distinct()
        input_test_scenarios = TestScenario.objects.filter(inputs__variable_id__in=distinct_field_ids).distinct()
        output_test_scenarios = TestScenario.objects.filter(outputs__variable_id__in=distinct_field_ids).distinct()
        return



    def get_available_test_scenarios_for_simulator(self):
        test_scenarios = list()
        for map_name in self.simulator.map_names:
            fields = Field.objects.filter(map__name=map_name)
            scenario_inputs = Input.objects.filter(variable__in=fields)
            test_scenarios.extend([inp.test_scenario for inp in scenario_inputs])
        return list(set(test_scenarios))

    def create_test_log_for_test_scenarios(self):
        test_scenarios = self.get_available_test_scenarios_for_simulator()
        for scenario in test_scenarios:
            TestExecutionLog.objects.get_or_create(test_scenario=scenario, epoch=time.time(), status='pending')

    def update_values_for_inputs(self, value_type=None):
        for log in TestExecutionLog.objects.filter(status='pending'):
            for inp in Input.objects.filter(test_scenario=log.test_scenario):
                for identity in self.simulator.map[inp.variable.map.name]:
                    value = inp.initial_value if value_type == 'initial' else inp.value
                    print(value, "here2")
                    self.simulator.update_and_translate_values(identity, inp.variable.ahe_name, value)

    def compare_outputs(self, function, actual_output, expected_output):
        print(actual_output, function, expected_output)
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

    def update_log_status_from_output(self, value_type=None):
        for log in TestExecutionLog.objects.filter(status='pending'):
            start_time = time.time()
            while time.time() - start_time <= log.test_scenario.timeout:
                for out in Output.objects.filter(test_scenario=log.test_scenario):
                    for identity in self.simulator.map[out.variable.map.name]:
                        actual_output = self.simulator.get_values(identity, out.variable.map.name,
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
                    break
                else:
                    time.sleep(1)
                    continue
                break
            else:
                log.status = 'failure'
                log.save()
    def update_test_status(self):
        self.create_test_log_for_test_scenarios()
        self.update_values_for_inputs('initial')
        self.update_log_status_from_output('initial')
        self.update_values_for_inputs()
        self.update_log_status_from_output()
        print(TestExecutionLog.objects.filter().values())




if __name__ == '__main__':
    su = ScenarioUpdate()
    su.update_test_status()





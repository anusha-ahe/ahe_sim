from ahe_sim.models import TestExecutionLog, ScenarioInput, ScenarioOutput
import time
from ahe_mb.models import Field, Map
from ahe_sim.sim import Simulation

TIMEOUT = 120


class ScenarioUpdate:
    def __init__(self):
        self.simulator = Simulation()
        self.simulator.start_server()
        self.input = dict()

    def get_available_test_scenarios_for_simulator(self):
        test_scenarios = list()
        for map_name in self.simulator.map_names:
            fields = Field.objects.filter(map__name=map_name)
            scenario_inputs = ScenarioInput.objects.filter(variable__in=fields)
            test_scenarios.extend([inp.test_scenario for inp in scenario_inputs])
        return list(set(test_scenarios))

    def create_test_log_for_test_scenarios(self):
        test_scenarios = self.get_available_test_scenarios_for_simulator()
        for scenario in test_scenarios:
            TestExecutionLog.objects.get_or_create(test_scenario=scenario, epoch=time.time(), status='pending')
    def update_initial_values_for_inputs_and_outputs(self):
        for log in TestExecutionLog.objects.filter(status='pending'):
            for inp in ScenarioInput.objects.filter(test_scenario=log.test_scenario):
                for identity in self.simulator.map[inp.variable.map.name]:
                    self.simulator.update_and_translate_values(identity,inp.variable.ahe_name, inp.initial_value)
            for out in ScenarioOutput.objects.filter(test_scenario=log.test_scenario):
                for identity in self.simulator.map[out.variable.map.name]:
                    self.simulator.update_and_translate_values(identity,out.variable.ahe_name, out.initial_value)

    def update_values_for_inputs(self):
        for log in TestExecutionLog.objects.filter(status='pending'):
            for inp in ScenarioInput.objects.filter(test_scenario=log.test_scenario):
                for identity in self.simulator.map[inp.variable.map.name]:
                    self.simulator.update_and_translate_values(identity,inp.variable.ahe_name, inp.value)

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

    def update_test_status(self):
        self.create_test_log_for_test_scenarios()
        self.update_initial_values_for_inputs_and_outputs()
        self.update_values_for_inputs()
        for log in TestExecutionLog.objects.filter(status='pending'):
            start_time = time.time()
            while time.time() - start_time <= TIMEOUT:
                for out in ScenarioOutput.objects.filter(test_scenario=log.test_scenario):
                    for identity in self.simulator.map[out.variable.map.name]:
                        actual_output = self.simulator.get_values(identity, out.variable.map.name,out.variable.ahe_name)
                        if self.compare_outputs(out.function, actual_output, out.value):
                            log.status = 'success'
                            log.save()
                            break
                    else:
                        continue
                    break
                else:
                    time.sleep(10)
                    continue
                break
            else:
                log.status = 'failure'
                log.save()
        print(TestExecutionLog.objects.filter().values())




if __name__ == '__main__':
    su = ScenarioUpdate()
    su.update_test_status()





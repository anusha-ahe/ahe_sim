from django.db import models

from ahe_mb.models import Map, Field

# Create your models here.

STATUS_CHOICES = [
    ('pending', 'pending'),
    ('success', 'success'),
    ('failed', 'failed'),
]

FUNCTION_CHOICES = [("less_than", "less_than"),
                   ("less_than_equal_to", "less_than_equal_to"),
                   ("greater_than", "greater_than"),
                   ("greater_than_equal_to", "greater_than_equal_to"),
                   ("equal_to", "equal_to"),
                    ("not_equal_to", "not_equal_to"),]


class SimulatorConfig(models.Model):
    map_name = models.ForeignKey(Map, on_delete=models.CASCADE)
    port = models.IntegerField(default=5000)


class TestScenario(models.Model):
    name = models.CharField(max_length=255, primary_key=True)


class ScenarioInput(models.Model):
    test_scenario = models.ForeignKey(TestScenario, on_delete=models.CASCADE)
    variable = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.FloatField()
    initial_value = models.FloatField(default=0)

class ScenarioOutput(models.Model):
    test_scenario = models.ForeignKey(TestScenario, on_delete=models.CASCADE)
    variable = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.FloatField()
    initial_value = models.FloatField(default=0)
    function = models.CharField(max_length=50, choices=FUNCTION_CHOICES, default='equal_to')

class TestExecutionLog(models.Model):
    test_scenario = models.ForeignKey(TestScenario, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    epoch = models.IntegerField()

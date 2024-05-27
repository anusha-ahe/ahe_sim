from django.db import models

from ahe_mb.models import Map, Field, SiteDevice

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
    name = models.CharField(max_length=255)
    timeout = models.FloatField(default=10)
    enable = models.BooleanField(default=True)


class Input(models.Model):
    test_scenario = models.ForeignKey(TestScenario,related_name='inputs', on_delete=models.CASCADE)
    variable = models.ForeignKey(Field, on_delete=models.CASCADE)
    device = models.ForeignKey(SiteDevice, on_delete=models.CASCADE, default=None)
    value = models.FloatField(default=0)
    initial_value = models.FloatField(default=0)

class Output(models.Model):
    test_scenario = models.ForeignKey(TestScenario, related_name='outputs', on_delete=models.CASCADE)
    variable = models.ForeignKey(Field, on_delete=models.CASCADE)
    device = models.ForeignKey(SiteDevice, on_delete=models.CASCADE, default=None)
    value = models.FloatField(default=0)
    function = models.CharField(max_length=50, choices=FUNCTION_CHOICES, default='equal_to')
    initial_value = models.FloatField(default=0)
    initial_function = models.CharField(max_length=50, choices=FUNCTION_CHOICES, default='equal_to')

class TestExecutionLog(models.Model):
    test_scenario = models.ForeignKey(TestScenario, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    epoch = models.IntegerField()

from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
import itertools
from ahe_sys.models import Site


class Hirarchy(models.Model):
    name = models.CharField(primary_key=True, max_length=50)

    def __str__(self) -> str:
        return self.name


class Node(models.Model):
    name = models.CharField(max_length=50)
    hirarchy = models.ForeignKey(Hirarchy, on_delete=models.CASCADE)
    pattern = models.CharField(max_length=50, null=True, blank=True)
    parent = models.ForeignKey(
        'Node', on_delete=models.CASCADE, null=True, blank=True)
    has_variables = models.BooleanField()
    count = models.IntegerField()

    def __str__(self) -> str:
        if self.parent:
            return f'{self.parent}/{self.name}({self.count})'
        else:
            return f'{self.hirarchy} ->  /{self.name}({self.count})'


class NodeVariable(models.Model):
    variable = models.CharField(max_length=50)
    parent = models.ForeignKey(
        Node, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.parent}/{self.variable}'


class Config(models.Model):
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    config_type = models.CharField(blank=True, null=True, max_length=20)

    def __str__(self) -> str:
        return f"Translate: {self.name}"


class Translation(models.Model):
    config = models.ForeignKey(Config, on_delete=models.CASCADE)
    seq = models.IntegerField()
    source = models.CharField(max_length=100)
    dest = models.CharField(max_length=100)
    func = models.CharField(max_length=50)
    removed_match = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'Translation', on_delete=models.CASCADE, null=True, blank=True)
    param = models.CharField(null=True, blank=True,max_length=50)

    def __str__(self) -> str:
        return f"{self.source} -> {self.func} -> {self.dest}"



class KeyMap(models.Model):
    var = models.CharField(max_length=100, primary_key=True)
    key = models.CharField(max_length=10,unique=True)


    def __str__(self) -> str:
        return f'{self.key} --> {self.var}'

from rest_framework import serializers
from ahe_sim.models import  TestExecutionLog, Input, Output, TestScenario
from ahe_mb.models import Field, SiteDevice


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteDevice
        fields = ['id', 'name']


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['id','ahe_name']


class InputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    variable = FieldSerializer()
    device = DeviceSerializer()

    class Meta:
        model = Input
        fields = ['id', 'variable', 'value', 'device','initial_value']

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        internal_value['id'] = data.get('id')
        return internal_value


class OutputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    variable = FieldSerializer()
    device = DeviceSerializer()

    class Meta:
        model = Output
        fields = ['id', 'variable', 'initial_value', 'device','value', 'function']

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        internal_value['id'] = data.get('id')
        return internal_value


class TestScenarioSerializer(serializers.ModelSerializer):
    inputs = InputSerializer(many=True)
    outputs = OutputSerializer(many=True)

    class Meta:
        model = TestScenario
        fields = ['id', 'name', 'enable', 'timeout', 'inputs', 'outputs']

    def create(self, validated_data):
        inputs_data = validated_data.pop('inputs', [])
        outputs_data = validated_data.pop('outputs', [])
        instance = TestScenario.objects.create(**validated_data)
        for input_data in inputs_data:
            Input.objects.create(test_scenario=instance, **input_data)
        for output_data in outputs_data:
            Output.objects.create(test_scenario=instance,**output_data)
        return instance


    def update(self, instance, validated_data):
        inputs_data = validated_data.pop('inputs', [])
        outputs_data = validated_data.pop('outputs', [])
        inputs_data = [dict(input_data) for input_data in inputs_data]
        outputs_data = [dict(output_data) for output_data in outputs_data]
        print([input_data.get('id') for input_data in inputs_data])
        for input_data in inputs_data:
            input_id = input_data.get('id')
            if input_id:
                input_instance = Input.objects.get(id=input_id)
                print(type(inputs_data))
                print(inputs_data)
                for attr, value in input_data.items():
                    setattr(input_instance, attr, value)
                input_instance.save()
            else:
                Input.objects.create(**input_data)
        for output_data in outputs_data:
            output_id = output_data.get('id')
            if output_id:
                output_instance = Output.objects.get(id=output_id)
                for attr, value in output_data.items():
                    setattr(output_instance, attr, value)
                output_instance.save()
            else:
                Output.objects.create(**output_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class TestExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestExecutionLog
        fields = ['id', 'test_scenario', 'status', 'epoch']

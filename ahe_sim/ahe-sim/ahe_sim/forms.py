# forms.py
from django import forms
from .models import SimulatorConfig, TestScenario, Input, Output, TestExecutionLog, FUNCTION_CHOICES
from ahe_mb.models import SiteDevice, Field, DeviceMap

INPUT_FN_CHOICES = [('', ''),
                    ('communication_error', 'communication_error')]


class DeviceForm(forms.ModelForm):
    class Meta:
        model = SiteDevice
        fields = ['site_device_conf', 'name', 'device_type', 'ip_address', 'port', 'unit', 'data_hold_period']


class TestScenarioForm(forms.ModelForm):
    class Meta:
        model = TestScenario
        fields = ['name', 'timeout']


class InputForm(forms.ModelForm):
    device = forms.ModelChoiceField(
        queryset=SiteDevice.objects.all(),
        required=True,
        widget=forms.Select(attrs={'id': 'id_input-device'})
    )
    variable = forms.ModelChoiceField(
        queryset=Field.objects.none(),
        required=False,
        widget=forms.Select(attrs={'id': 'id_input-variable'})
    )
    function = forms.ChoiceField(choices=INPUT_FN_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super(InputForm, self).__init__(*args, **kwargs)
        if 'condition-device' in self.data:
            try:
                device_id = int(self.data.get('condition-device'))
                device = SiteDevice.objects.get(id=device_id)
                fields = Field.objects.filter(map__devicemap__device_type=device.device_type)
                self.fields['variable'].queryset = fields
            except Exception as e:
                self.fields['variable'].queryset = Field.objects.none()
        elif self.instance.pk:
            device = self.instance.device
            fields = Field.objects.filter(map__devicemap__device_type=device.device_type)
            self.fields['variable'].queryset = fields

    class Meta:
        model = Input
        fields = ['test_scenario', 'device', 'variable', 'function', 'value', 'initial_value']


class OutputForm(forms.ModelForm):
    device = forms.ModelChoiceField(
        queryset=SiteDevice.objects.all(),
        required=True,
        widget=forms.Select(attrs={'id': 'id_output-device'})
    )
    variable = forms.ModelChoiceField(
        queryset=Field.objects.values_list('id','ahe_name'),
        required=False,
        widget=forms.Select(attrs={'id': 'id_output-variable'})
    )
    function = forms.ChoiceField(choices=FUNCTION_CHOICES)
    initial_function = forms.ChoiceField(choices=FUNCTION_CHOICES)

    def __init__(self, *args, **kwargs):
        super(OutputForm, self).__init__(*args, **kwargs)
        if 'action-device' in self.data:
            try:
                device_id = int(self.data.get('action-device'))
                device = SiteDevice.objects.get(id=device_id)
                fields = Field.objects.filter(map__devicemap__device_type=device.device_type)
                self.fields['variable'].queryset = fields
            except Exception as e:
                self.fields['variable'].queryset = Field.objects.none()
        elif self.instance.pk:
            device = self.instance.device
            fields = Field.objects.filter(map__devicemap__device_type=device.device_type)
            self.fields['variable'].queryset = fields

    class Meta:
        model = Output
        fields = ['test_scenario', 'device', 'variable', 'value', 'function', 'initial_value', 'initial_function']


class TestExecutionLogForm(forms.ModelForm):
    class Meta:
        model = TestExecutionLog
        fields = ['test_scenario', 'status', 'epoch']

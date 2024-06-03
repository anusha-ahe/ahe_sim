from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()
    overwrite = forms.BooleanField(required=False, initial=False)
    redirect = forms.CharField(max_length=1, required=False, initial='Y')

class UploadBitmapForm(forms.Form):
    file = forms.FileField()
    overwrite = forms.BooleanField(required=False, initial=False)
    redirect = forms.CharField(max_length=1, required=False, initial='Y')


class UploadEnumForm(forms.Form):
    file = forms.FileField()
    overwrite = forms.BooleanField(required=False, initial=False)
    redirect = forms.CharField(max_length=1, required=False, initial='Y')

class UploadDeviceMap(forms.Form):
    file = forms.FileField()
    overwrite = forms.BooleanField(required=False, initial=False)
    redirect = forms.CharField(max_length=1, required=False, initial='Y')    
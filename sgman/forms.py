from django import forms
from .models import SgAccess


class SgAccessForm(forms.ModelForm):
    class Meta:
        model = SgAccess
        fields = ["employee_email", "allow_ip"]
        labels = {"employee_email": "Employee Email", "allow_ip": "Allow IP"}

    def save(self, **kwargs):
        user = kwargs.pop('user')
        instance = super(SgAccessForm, self).save(**kwargs)
        instance.added_by = user
        instance.save()
        return instance

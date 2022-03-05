from django import forms
from .models import SgAccess


class SgAccessForm(forms.ModelForm):
    class Meta:
        model = SgAccess
        fields = ["allow_ip"]
        labels = {"allow_ip": "Allow IP"}

    def save(self, **kwargs):
        user = kwargs.pop('user')
        instance = super(SgAccessForm, self).save(**kwargs)
        instance.added_by = user
        instance.save()
        return instance

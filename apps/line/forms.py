from django import forms
from django.shortcuts import get_object_or_404
from apps.core.models import Shop


class ShareForm(forms.Form):
    # lineToken = forms.CharField()
    select_num = forms.IntegerField()


class EmployForm(forms.Form):
    # lineToken = forms.CharField()
    shop_id = forms.UUIDField()
    employ_num = forms.IntegerField()

    def clean_shop_id(self):
        obtained_value = self.cleaned_data.get('shop_id')
        if get_object_or_404(Shop, id=obtained_value):
            return obtained_value

        raise forms.ValidationError('該当する店舗なし')


class EmployComfirmForm(EmployForm):
    employ_num = forms.IntegerField()

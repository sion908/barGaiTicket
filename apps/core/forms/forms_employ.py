from django import forms
from django.shortcuts import get_object_or_404
from ..models import Shop


class EmployForm(forms.Form):
    shop_id = forms.UUIDField()

    def clean_shop_id(self):
        obtained_value = self.cleaned_data.get('shop_id')
        if get_object_or_404(Shop, id=obtained_value):
            return obtained_value

        raise forms.ValidationError('該当する店舗なし')


class EmployComfirmForm(EmployForm):
    employ_num = forms.IntegerField()

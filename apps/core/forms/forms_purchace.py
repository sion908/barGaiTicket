from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


def create_buy_form(user, products, *arg):
    f = forms.Form(*arg)
    rems = {}
    for product in products:
        count = product.max_sell
        f.fields[str(product.pk)] = forms.IntegerField(label=str(product.pk), required=False, validators=[MinValueValidator(0), MaxValueValidator(count)])
        rems[product.pk] = count
    return f, rems

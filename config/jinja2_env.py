from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })

    def get_month(value,product,month):
        product_values = value.get(str(product.get("id")))
        if not product_values:
            return 0
        return product_values.get(month,0)

    env.filters["get_month"] = get_month
    return env

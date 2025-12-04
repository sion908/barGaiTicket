def stripe_product_retrieve():
    class cls():
        def __init__(self, dict) -> None:
            for key, value in dict.items():
                setattr(self, key, value)

    dict = {
        "id": "prod_M9HUZYjOVzOQKF",
        "object": "product",
        "active": False,
        "created": 1659123188,
        "default_price": None,
        "description": "description",
        "images": [],
        "livemode": False,
        "metadata": {},
        "name": "nameB",
        "package_dimensions": None,
        "shippable": None,
        "statement_descriptor": None,
        "tax_code": None,
        "unit_label": None,
        "updated": 1659127995,
        "url": None
    }
    return cls(dict)


def stripe_price_retrieve():
    class cls():
        def __init__(self, dict) -> None:
            for key, value in dict.items():
                setattr(self, key, value)

    dict = {
        "id": "price_1LS2PWIkZUNdggLMBHwl5pxt",
        "object": "price",
        "active": True,
        "billing_scheme": "per_unit",
        "created": 1659374890,
        "currency": "jpy",
        "custom_unit_amount": None,
        "livemode": False,
        "lookup_key": None,
        "metadata": {},
        "nickname": None,
        "product": "prod_M9HUZYjOVzOQKF",
        "recurring": {
            "aggregate_usage": None,
            "interval": "month",
            "interval_count": 1,
            "usage_type": "licensed"
        },
        "tax_behavior": "unspecified",
        "tiers_mode": None,
        "transform_quantity": None,
        "type": "recurring",
        "unit_amount": 2000,
        "unit_amount_decimal": "2000"
    }
    return cls(dict)

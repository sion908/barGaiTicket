from apps.product.models import Product


def create_prod_id(id):
    class Prod_class():
        id = ""

        def __init__(self, pro):
            self.id = pro
    return Prod_class(id)


def initial_get_product():

    """
    Creates a new object with the given kwargs,
    saving it to the database and returning the created object.
    """

    objs = [
        Product(
            name='ランチチケット',
            description='ランチに使えるよ',
            price=1500,
            max_sell=3,
            price_id='price_1KneMsIkZUNdggLMgyGwjT8u'
        ),
        Product(
            name='ディナーチケット',
            description='ディナーのチケットだよ',
            price=3000,
            max_sell=3,
            price_id='price_1KneiKIkZUNdggLMQWpqzfB7'
        )
    ]

    products = Product.objects.bulk_create(objs)

    return products

from django.test import TestCase
from apps.product.models import Product
from unittest import mock

from ..setup.stripe_setup import stripe_product_retrieve, stripe_price_retrieve


# Create your tests here.
class ProductModelTests(TestCase):

    def SetUp(self):
        # self.user = User.objects.create_user('uni', 'wa@yahoo.co.jp', "uni")
        pass

    def test_is_empty(self):
        """初期状態では何も登録されていないことをチェック"""
        saved_products = Product.objects.all()
        self.assertEqual(saved_products.count(), 0)

    def test_is_count_one(self):
        """1つレコードを適当に作成すると、レコードが1つだけカウントされることをテスト"""
        name, description, price = 'lunch', 'ランチチケット', 3000
        product = Product(name=name, description=description, price=price)
        product.save()
        actual_products = Product.objects.all()
        self.assertEqual(actual_products.count(), 1)
        actual_product = actual_products.first()

        self.assertEqual(actual_product.name, name, "製品の名前")
        self.assertEqual(actual_product.description, description, "製品の説明")
        self.assertEqual(actual_product.price, price, "製品の価格")
        self.assertEqual(actual_product.max_sell, 3, "製品販売数の最大値")
        self.assertEqual(actual_product.usage, Product.SITUATION_EVENLY, "チケットの埋め方がまんべんなく")

    @mock.patch('apps.product.models.stripe.Price.retrieve', mock.MagicMock(return_value=stripe_price_retrieve()))
    @mock.patch('apps.product.models.stripe.Product.retrieve', mock.MagicMock(return_value=stripe_product_retrieve()))
    def test_create_product_with_price_id(self):
        """stripeのpriceIDがある状態でそっちから情報をもってきて作る"""

        name, description, price = 'nameB', 'description', 2000
        Product.objects.setdata_from_stripe("price_1LFaA5IkZUNdggLMSXgomDvW")

        actual_products = Product.objects.all()
        self.assertEqual(actual_products.count(), 1)
        actual_product = actual_products.first()

        self.assertEqual(actual_product.name, name, "製品の名前")
        self.assertEqual(actual_product.description, description, "製品の説明")
        self.assertEqual(actual_product.price, price, "製品の価格")
        self.assertEqual(actual_product.max_sell, 3, "製品販売数の最大値")

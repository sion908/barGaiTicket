from django.test import TestCase
from django.urls import reverse, resolve
from apps.product.views import show_shops


class TestUrls(TestCase):
    """index ページへのURLでアクセスする時のリダイレクトをテスト"""

    def test_get_update_url(self):
        view = resolve(reverse('product:showShop'))
        self.assertEqual(view.func, show_shops)

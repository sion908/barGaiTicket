# from django.test import Client, TestCase
# from django.urls import reverse

# from apps.core.models import User, Shop


# class HomeTests(TestCase):
#     # """HomeViewのテストクラス"""

#     # def setUp(self):
#     #     self.username='uni'
#     #     self.email="wa@yahoo.co.jp"
#     #     self.password="uni"
#     #     self.user = User.objects.create_superuser(  # 'uni', 'wa@yahoo.co.jp', "uni"
#     #         username=self.username,
#     #         email=self.email,
#     #         password=self.password,
#     #     )

#     # def test_get(self):
#     #     """GET メソッドでアクセスしてステータスコード200を返されることを確認"""

#     #     self.client = Client()

#     #     login = self.client.login(username=self.username, password=self.password)
#     #     response = self.client.get(reverse('app:home'))
#     #     self.assertEqual(response.status_code, 200)

#     # def test_get_not_login(self):
#     #     """ログインしていない場合，エラーコード404を返す"""
#     #     response = self.client.get(reverse('app:home'))
#     #     self.assertEqual(response.status_code, 404)

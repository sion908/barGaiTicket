# from django.test import Client, TestCase
# from django.urls import reverse

# from apps.core.models import User, Shop
# from ..setup import initial_user, initial_shop, initial_owner

# class EmployTests(TestCase):
#     """EmployViewのテストクラス"""

#     def setUp(self):
#         initial_owner(self)
#         initial_shop(self,2)
#         # print(vars(self))

#     def test_get(self):
#         """GET メソッドでアクセスしてステータスコード200を返されることを確認"""

#         self.client = Client()

#         login = self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('app:employ'))
#         # import pdb
#         # pdb.set_trace()
#         self.assertEqual(response.status_code, 200)

#     def test_get_not_login(self):
#         """ログインしていない場合, エラーコード404を返す"""
#         response = self.client.get(reverse('app:home'))
#         self.assertEqual(response.status_code, 404)

#     def test_get_logined(self):
#         """ログインしている場合, 200を返す"""
#         self.client.login(username=self.username, password=self.password)

#         response = self.client.get(reverse('app:employ'))
#         # If csrf_token was template given.
#         # self.assertRedirects(response, reverse('app:employ'))
#         # If csrf_token was't template given.
#         self.assertEquals(200, response.status_code)

#     def test_post_index_01(self):
#         self.client = Client(enforce_csrf_checks=True)
#         response = self.client.post(reverse('app:employ'), data={})
#         # If csrf_token was template given.
#         # self.assertTemplateUsed(response, 'sample/index.html')
#         # If csrf_token was't template given.
#         self.assertEquals(403, response.status_code)

#     def test_post_index_02(self):
#         self.client = Client()
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.post(reverse('app:employ'), data={'shop_id': str(self.shops[0].pk)})
#         # If csrf_token was template given.
#         self.assertEquals(200, response.status_code)
#         # If csrf_token was't template given.
#         # self.assertEquals(403, response.status_code)

# from django.test import Client, TestCase
# from django.urls import reverse

# from apps.core.models import User, Shop
# from ..setup import initial_user, initial_shop, create_user_ticket

# class EmployConfTests(TestCase):
#     """EmployConfViewのテストクラス"""

#     def setUp(self):
#         # initial_user(self)
#         initial_shop(self,2)
#         create_user_ticket(self)

#     # def test_post(self):
#     #     """GET メソッドでアクセスしてステータスコード200を返されることを確認"""

#     #     self.client = Client()
#     #     self.client.force_login(self.user)
#     #     # print(self.shops[0].pk)
#     #     response = self.client.post(reverse('app:employ_procedure'), data={'shop_id': str(self.shops[0].pk), 'employ_num':"1"})
#     #     # If csrf_token was template given.
#     #     self.assertRedirects(response, reverse('app:employ_approve', kwargs={'pk':str(self.shops[0].pk),'employ_num':'1'}), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
#         # self.assertEqual(response.status_code, 404)

#     # def test_get_not_login(self):
#     #     """ログインしていない場合，エラーコード404を返す"""
#     #     response = self.client.get(reverse('app:home'))
#     #     self.assertEqual(response.status_code, 404)

#     # def test_post_index_01(self):
#     #     self.client = Client(enforce_csrf_checks=True)
#     #     response = self.client.post(reverse('app:employ'), data={})
#     #     # If csrf_token was template given.
#     #     # self.assertTemplateUsed(response, 'sample/index.html')
#     #     # If csrf_token was't template given.
#     #     self.assertEquals(403, response.status_code)

#     # def test_post_index_02(self):
#     #     self.client = Client(enforce_csrf_checks=True)
#     #     response = self.client.post(reverse('app:employ'), data={'shop_id': 'Test Message'})
#     #     # If csrf_token was template given.
#     #     self.assertRedirects(response, reverse('app:employ'))
#     #     # If csrf_token was't template given.
#     #     # self.assertEquals(403, response.status_code)

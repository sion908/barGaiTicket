from django.test import Client, TestCase
from apps.core.models import Owner


class OwnerModelTests(TestCase):

    def test_is_empty(self):
        """初期状態では何も登録されていないことをチェック"""
        saved_users = Owner.objects.all()
        self.assertEqual(saved_users.count(), 0)

    def test_is_count_one(self):
        """1つレコードを適当に作成すると、レコードが1つだけカウントされることをテスト"""
        user = Owner(username='test_username')  # , text='test_text')
        user.save()
        saved_users = Owner.objects.all()
        self.assertEqual(saved_users.count(), 1)

    def test_saving_and_retrieving_user(self):
        """内容を指定してデータを保存し、すぐに取り出した時に保存した時と同じ値が返されることをテスト"""
        user = Owner()
        username = 'test_username_to_retrieve'
        user.username = username
        user.save()

        saved_users = Owner.objects.all()
        actual_user = saved_users[0]

        self.assertEqual(actual_user.username, username)

    def test_create_superuser(self):
        """ superuser作成に関するテスト """

        username = 'uni'
        email = "wa@yahoo.co.jp"
        password = "uni"

        user = Owner.objects.create_superuser(  # 'uni', 'wa@yahoo.co.jp', "uni"
            username=username,
            email=email,
            password=password,
        )

        users = Owner.objects.all()
        user = Owner.objects.get(username=username)

        self.client = Client()

        login = self.client.login(username=username, password=password)

        self.assertEqual(users.count(), 1, "作られた人が一人")
        self.assertEqual(user.username, username, "usernameがあっている")
        self.assertEqual(user.email, email, "メアドがあっている")
        self.assertTrue(login, "ログインができている->パスワードがあっている")
        self.assertTrue(user.is_staff, "スタッフである")
        self.assertTrue(user.is_active, "activeである")

    def test_create_user(self):
        """ user作成に関するテスト """
        user = Owner.objects.create_user(  # 'uni', 'wa@yahoo.co.jp', "uni")
            username='uni',
            email='wa@yahoo.co.jp',
            password="uni"
        )

        users = Owner.objects.all()
        user = Owner.objects.get(username='uni')

        self.client = Client()

        login = self.client.login(username='uni', password='uni')

        self.assertEqual(users.count(), 1, "作られた人が一人")
        self.assertEqual(user.username, "uni", "usernameがあっている")
        self.assertEqual(user.email, "wa@yahoo.co.jp", "メアドがあっている")
        self.assertTrue(login, "ログインができている->パスワードがあっている")
        self.assertFalse(user.is_staff, "スタッフでない")
        self.assertTrue(user.is_active, "activeである")

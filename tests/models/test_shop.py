from django.test import TestCase
from apps.core.models import User, Shop, Owner


class ShopModelTest(TestCase):

    def SetUp(self):
        self.user = User.objects.create_user('uni', 'wa@yahoo.co.jp', "uni")

    def test_is_empty(self):
        """初期状態では何も登録されていないことをチェック"""
        saved_shops = Shop.objects.all()
        self.assertEqual(saved_shops.count(), 0)

    def test_is_count_one(self):
        """1つレコードを適当に作成すると、レコードが1つだけカウントされることをテスト"""
        shop = Shop(name='test_shopname')
        shop.save()
        saved_shops = Shop.objects.all()
        self.assertEqual(saved_shops.count(), 1)

    def test_saving_and_retrieving_user(self):
        """内容を指定してデータを保存し、すぐに取り出した時に保存した時と同じ値が返されることをテスト"""

        name, access, hour = "shopname", "adress", "time"

        Shop.objects.create(
            name=name,
            access=access,
            hour=hour,
        )

        actual_shop = Shop.objects.first()

        self.assertEqual(actual_shop.name, name, "店の名前")
        self.assertEqual(actual_shop.access, access, "店の住所")
        self.assertEqual(actual_shop.hour, hour, "店の営業時間")

    def test_create_shop_from_owner(self):
        """ Ownerから店のモデルを作成した場合 """

        owner = Owner.objects.create_user('uni', 'wa@yahoo.co.jp', "uni")
        name, access, hour = "shopname", "adress", "time"
        shop = Shop.objects.create(
            name=name,
            access=access,
            hour=hour,
        )
        owner.shop = shop
        owner.save()

        shops = Shop.objects.all()
        shop = shops.first()
        owner = Owner.objects.first()

        self.assertEqual(shops.count(), 1, "登録店舗が一つ")
        self.assertEqual(shop.name, name, "店の名前")
        self.assertEqual(shop.access, access, "店の住所")
        self.assertEqual(shop.hour, hour, "店の営業時間")

        self.assertEqual(shop.owner.first(), owner, "店の所有者")
        self.assertEqual(owner.shop, shop, "ユーザーに登録された店が正しい")

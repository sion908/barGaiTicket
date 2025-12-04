from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.contrib.auth.validators import UnicodeUsernameValidator
# from django.utils.translation import gettext_lazy as _  # 翻訳用
# from core.models import TicketBase
from apps.product.models import Product
from .manager import OwnerManager, TicketManager

import uuid

# class Setting(models.Model):
#     MAX_SELL = models.IntegerField("一人当たりのチケットの最大枚数", null=False, default=3)
#     objects = SettingManager()


class Owner(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField("username", max_length=50, unique=True,
                                validators=[username_validator], blank=True)
    email = models.EmailField("email_address", blank=True, null=True)
    is_staff = models.BooleanField("staff status", default=False)
    is_active = models.BooleanField("active", default=True)
    date_joined = models.DateTimeField("date joined", auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    # 編集しうる店
    shop = models.ForeignKey('Shop', on_delete=models.SET_NULL,
                             null=True, blank=True,
                             related_name="owner")

    user = models.OneToOneField('User', on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name="owner_u")

    objects = OwnerManager()
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['email']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.MAX_SELL = Setting.objects.first().MAX_SELL

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "owner"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def create_shop(self, **extra_fields):
        if not self.shop:
            created_shop = Shop.objects.create(
                **extra_fields
            )
            self.owner_shop = created_shop
            self.save()

            return created_shop
        else:
            return self.owner_shop

    def __str__(self):
        return f'{self.username if self.username else "スマホ"}'


class User(models.Model):

    date_joined = models.DateTimeField("date joined", auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)
    # lineUserID
    lineUserID = models.CharField(max_length=40, blank=True)
    username = models.CharField(max_length=40, blank=True, null=True)
    email = models.EmailField("email_address", unique=True, null=True)

    is_followed = models.BooleanField('フォローされているか', default=False)

    # email = models.EmailField("email_address", unique=True, null=True)

    def create_ticket(self, boughts):
        """
        boughts=[{
                'quantity': <int> 数量,
                'kind': <class 'product.models.Product'>,
                'is_pay': <bool> 支払済みか,
                'session_id':session_id,
                }, ... ]
        """
        # boughts=[{'quantity': 3,'kind': products[0],'is_pay': True,'active': True,},{'quantity': 3,'kind': products[1],'is_pay': True,'active': False,}]

        objs = []
        for bought in boughts:
            quantity = bought.pop('quantity')
            for i in range(quantity):
                obj = Ticket(**bought, owner=self)
                objs.append(obj)

        tickets = Ticket.objects.bulk_create(objs)
        return tickets

    def __str__(self):
        return f'{self.pk} {self.username if self.username else ""}'


class Shop(models.Model):

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    # 作られた日
    created_at = models.DateTimeField('作られた日', auto_now_add=True)
    # 更新日
    updated_at = models.DateTimeField('更新日', auto_now=True)
    is_active = models.BooleanField("active", default=True)

    name = models.CharField('店名', max_length=128)
    altname = models.CharField('表示名', max_length=128, null=True, blank=True)
    access = models.CharField('住所', max_length=128, null=True, blank=True)
    gpsLatitude = models.FloatField("Latitude", blank=True, null=True,
                                    help_text="degrees, floating point, South is negative")
    gpsLongitude = models.FloatField("Longtitude", blank=True, null=True,
                                     help_text="degrees, floating point, West is negative")
    phone = models.CharField('電話番号', max_length=14, null=True, blank=True)
    hour = models.CharField('営業時間', max_length=128, null=True, blank=True)
    menu = models.CharField('メニュー', max_length=256, null=True, blank=True)
    opictID = models.CharField('外見写真ID', max_length=35, null=True, blank=True)
    mpictID = models.CharField('メニュー写真ID', max_length=35, null=True, blank=True)

    def __str__(self):
        # return self.name
        return f'[{"x" if self.is_active else " "}] {self.name}'


class Ticket(models.Model):
    SITUATION_BEFORE = 0
    SITUATION_USABLE = 1
    SITUATION_USED = 2
    SITUATION_REFUND = 3
    SITUATION_CHOICES = (
        (SITUATION_BEFORE, "before"),  # 0 使用前
        (SITUATION_USABLE, "usable"),  # 1 使用可能
        (SITUATION_USED, "used"),    # 2 使用済み
        (SITUATION_REFUND, "refund"),    # 3 削除済み
    )

    purchase_at = models.DateTimeField('購入日', auto_now_add=True)
    pay_at = models.DateTimeField('支払日', blank=True, null=True)
    update_at = models.DateTimeField('更新日', auto_now=True)

    is_pay = models.BooleanField('支払いされたか', default=False)

    owner = models.ForeignKey('User', on_delete=models.CASCADE,
                              related_name="ticket", blank=True, null=True)
    purchaser = models.ForeignKey('User', on_delete=models.CASCADE,
                                  related_name="ticket_purchaser", blank=True, null=True)

    kind = models.ForeignKey(Product, on_delete=models.PROTECT, null=False, default=1, related_name='ticket')

    session_id = models.CharField('セッションID二重購入を防ぐ', max_length=100, null=True, blank=True)

    # active = models.BooleanField('期間内か', default=False)
    situation = models.IntegerField('状況', choices=SITUATION_CHOICES, default=SITUATION_BEFORE)

    objects = TicketManager()

    def get_used_stub(self):
        return self.stub.filter(is_used=True).count()


class Stub(models.Model):
    updated_at = models.DateTimeField('更新日', auto_now=True)

    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE,
                               related_name="stub")

    shop = models.ForeignKey('Shop', on_delete=models.SET_NULL,
                             null=True, related_name="stub")

    is_used = models.BooleanField("チケットが使われたか", default=False)

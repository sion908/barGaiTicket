from django.db import models
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField as BaseCloudinaryField

import stripe
import re


class CloudinaryField(BaseCloudinaryField):
    def upload_options(self, model_instance):
        return {
            'public_id': model_instance.name,
            'unique_filename': False,
            'overwrite': True,
            'resource_type': 'image',
            'tags': ['map', 'market-map'],
            'invalidate': True,
            'quality': 'auto:eco',
        }


class ProductManager(models.Manager):

    def setdata_from_stripe(self, price_id, **kwargs):
        con = {'price_id': price_id}
        data = stripe.Price.retrieve(price_id)
        prod_id = getattr(data, "product")
        price = getattr(data, "unit_amount")
        if price:
            con['price'] = price
        prod = stripe.Product.retrieve(prod_id)
        description = getattr(prod, 'description', None)
        if description:
            con['description'] = description
        name = getattr(prod, 'name', None)
        if name:
            con['name'] = name
        return self.create(**con, **kwargs)


class Product(models.Model):
    SITUATION_EVENLY = 0
    SITUATION_ONE_BY_ONE = 1
    USAGE_CHOICES = (
        (SITUATION_EVENLY, "evenly"),  # 0 まんべんなく
        (SITUATION_ONE_BY_ONE, "one_by_one"),  # 1 いちまいづつ
    )

    name = models.CharField("商品名", max_length=50)
    description = models.CharField('説明', max_length=100)
    long_description = models.TextField('利用規約', max_length=3000, default="")
    price = models.IntegerField("価格", blank=False, null=False,
                                validators=[MinValueValidator(0)])
    image = CloudinaryField('image', blank=True, null=True)

    max_sell = models.IntegerField("販売数の最大", default=3,
                                   validators=[MinValueValidator(0)])

    price_id = models.CharField("stripeのprice_ID", max_length=40, null=True, blank=True)

    allow_duplicate_store = models.BooleanField("店の重複を許すか", default=False, blank=True)
    stub_count = models.IntegerField('stubの許容数', default=3)
    stub_price = models.IntegerField('stubの単価', default=500)
    is_active = models.BooleanField("active", default=False)
    usage = models.IntegerField('stubの使われ方', choices=USAGE_CHOICES, default=SITUATION_EVENLY)
    questionnaire_url = models.URLField('アンケート用リンク', blank=True ,null=True)

    sale_dt = models.DateTimeField('販売開始', blank=True, null=True)
    start_dt = models.DateTimeField('イベント開始日', blank=True, null=True)
    end_dt = models.DateTimeField('イベント終了日', blank=True, null=True)

    objects = ProductManager()

    def __str__(self):
        year_str = self.sale_dt.strftime('%y') if self.sale_dt else None
        return f"{year_str}:{re.sub('<.+?>', '', self.name)}"

    """ Informative name for model """
    def __unicode__(self):
        try:
            public_id = self.image.public_id
        except AttributeError:
            public_id = ''
        return "Photo <%s:%s>" % (self.name, public_id)

    def create_stripe_price(self):

        args = {
            'name': self.name,
            'description': self.description,
        }
        if getattr(getattr(self, 'image', None), 'url', None):
            args['images'] = [self.image.url]
        res = stripe.Product.create(**args)
        product_id = res.id
        res = stripe.Price.create(unit_amount=self.price,
                                  currency="jpy",
                                  product=product_id,
                                  )
        self.price_id = res.id
        self.save()
        return self.price_id

    def initial_stripe(self):
        product_id = self.create_stripe_product()
        price_id = self.create_stripe_price()
        return [product_id, price_id]

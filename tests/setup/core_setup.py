from apps.core.models import Shop, Owner, Ticket, User
from .product_setup import initial_get_product


def initial_shop(self, count=2):
    """
    Creates a new object with the given kwselfs,
    saving it to the database and returning the created object.
    """

    objs = []

    for i in range(count):
        objs.append(Shop(name='shop-' + str(i)))

    self.shops = Shop.objects.bulk_create(objs)
    # return shops


def initial_user(self):
    """
    Creates a new object with the given kwargs,
    saving it to the database and returning the created object.
    """

    self.lineID = 'lineId'
    self.user = User.objects.create(lineUserID=self.lineID)


def initial_owner(self):
    """
    Creates a new object with the given kwargs,
    saving it to the database and returning the created object.
    """

    self.username = 'uni'
    self.email = "wa@yahoo.co.jp"
    self.password = "uni"
    self.owner = Owner.objects.create_superuser(  # 'uni', 'wa@yahoo.co.jp', "uni"
        username=self.username,
        email=self.email,
        password=self.password,
    )


def create_user_ticket(self):
    if not getattr(self, 'user', None):
        initial_user(self)
    products = initial_get_product()
    boughts = [{'quantity': 3, 'kind': products[0], 'is_pay': True, 'situation':Ticket.SITUATION_USABLE, },
               {'quantity': 3, 'kind': products[1], 'is_pay': True, 'situation':Ticket.SITUATION_BEFORE, }]
    self.tickets = self.user.create_ticket(boughts)

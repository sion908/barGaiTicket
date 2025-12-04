from django.contrib.auth.base_user import BaseUserManager
from django.db import models

from apps.product.models import Product


class OwnerManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username="", email="",
                     password=None, **extra_fields):
        if username:
            email = self.normalize_email(email)
            username = self.model.normalize_username(username)
            user = self.model(username=username, email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self.db)
            return user
        else:
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self.db)
            pk = user.id
            user.username = 'yamate' + str(pk)
            user.save()
            return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Emailを入力して下さい')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff=Trueである必要があります。')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser=Trueである必要があります。')
        return self._create_user(username, email, password, **extra_fields)

    # def create_line_user(self, lineUserID, **extra_fields):
    #     # user = self.model(lineUserID=lineUserID, **extra_fields)
    #     extra_fields.setdefault('is_staff', False)
    #     extra_fields.setdefault('is_superuser', False)
    #     extra_fields["lineUserID"] = lineUserID
    #     # user.save(using=self.db)
    #     # password = pass_gen(12)
    #     return self._create_user(**extra_fields)
    #     # return user

    # def pass_gen(size=12):
    #     chars = string.ascii_uppercase +
    #               string.ascii_lowercase + string.digits
    #     # 記号を含める場合
    #     # chars += '%&$#()'

    #     return ''.join(secrets.choice(chars) for x in range(size))


class TicketManager(models.Manager):

    def use_by_count(self, shop, count, product, **kwargs):
        from .models import Stub, Ticket
        selected_tickets = self.filter(
            situation=Ticket.SITUATION_USABLE,
            kind=product,
            **kwargs
        )
        stubs = []
        deal_tickets = []

        if not selected_tickets.count():
            raise ValueError("not ticket")

        if selected_tickets.count() == 1:
            ticket = selected_tickets.first()
            for i in range(count):
                stubs.append(Stub(shop=shop, ticket=ticket, is_used=True))
            if ticket.stub.count() + count == product.stub_count:
                ticket.situation = Ticket.SITUATION_USED
                deal_tickets = [ticket]

        else:
            sort_list = [[ticket, ticket.get_used_stub(), 0] for ticket in selected_tickets]

            if product.usage == Product.SITUATION_EVENLY:
                sorted_list = sorted(sort_list, key=lambda x: x[1], reverse=True)  # [[pk, usedcount, usecount], ...]

                for i in range(count):
                    num = 0
                    for j, a in enumerate(sorted_list):
                        if sorted_list[num][1] > a[1]:
                            num = j
                    sorted_list[num][2] += 1
                    sorted_list[num][1] += 1

            else:
                num = 0
                while True:
                    _stub_count = product.stub_count - sort_list[num][1]
                    if count > _stub_count:
                        count -= _stub_count
                        sort_list[num][2] = _stub_count
                        sort_list[num][1] += _stub_count
                        num += 1
                    else:
                        sort_list[num][2] = count
                        sort_list[num][1] += count
                        break

                sorted_list = sort_list

            for list in sorted_list:
                for i in range(list[2]):
                    stubs.append(Stub(shop=shop, ticket=list[0], is_used=True))
                if list[1] == product.stub_count:
                    list[0].situation = Ticket.SITUATION_USED
                    deal_tickets.append(list[0])

        Stub.objects.bulk_create(stubs)
        if deal_tickets:
            Ticket.objects.bulk_update(deal_tickets, fields=['situation'])

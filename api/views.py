# coding: utf-8

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
from django.urls import reverse
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncDay

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.core.models import Ticket, Shop, User
from apps.product.models import Product
from apps.line.views import get_lineuser_by_token
from config.setting import STRIPE_ENDPOINT_SECRET

import stripe
import datetime
import requests
import json

# class UserTicketViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = User.objects.filter(is_active=True)
#     serializer_class = UserTicketSerializer
#     lookup_field = 'lineUserID'

# class ShopViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Shop.objects.all()
#     serializer_class = ShopSerializer
#     lookup_field = 'id'

@api_view(['GET'])
def getShop_and_num(request, token, shopID):
    user, created = get_lineuser_by_token(token,create=True)

    if created:
        return Response({"url":reverse('line:purchase')})

    shop = get_object_or_404(Shop, id=shopID)
    product = Product.objects.filter(is_active=True).first()
    tickets = user.ticket.filter(kind=product, situation=Ticket.SITUATION_USABLE)
    used_count = 0
    can_use_count = 0
    for ticket in tickets:
        used_count += ticket.stub.filter(shop=shop).count()
        can_use_count += product.stub_count - ticket.get_used_stub()

    context = {
        'user': {'maxuse': can_use_count, 'used': used_count},
        'shop': {'name': shop.name}
    }
    print(context)
    return Response(context)


@api_view(['GET'])
def getStubs(request, token):
    condition = {'is_used': True}
    if "time" in request.GET:
        condition['updated_at__gt'] = request.GET.get('time')
    user, _ = get_lineuser_by_token(token)
    if not user:
        user = request.user
    # import pdb
    # pdb.set_trace()
    owner = user.owner_u
    shop = owner.shop
    stubs = shop.stub.filter(**condition)
    res_list = [
        {
            'pk': s.pk,
            'user_id': s.ticket.owner.pk,
            'time': s.updated_at,
        }
        for s in stubs
    ]
    return Response({'shop': shop.name, 'stubs': res_list})


@login_required
@api_view(['GET'])
def getStubsWithLogin(request):

    owner = request.user

    if owner.is_anonymous:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    condition = {'is_used': True}

    if "time" in request.GET:
        condition['updated_at__gt'] = request.GET.get('time')

    # import pdb
    # pdb.set_trace()
    shop = owner.shop
    if shop:
        if request.GET.get("per") == "Month":
            month_stubs = shop.stub.filter(**condition).annotate(
                    month=TruncMonth('updated_at')
                ).values('month').annotate(
                    total=Count('month')
                )
            return Response({'shop': shop.name, 'stubs': list(month_stubs)})
        elif request.GET.get("per") == "Day":
            day_stubs = shop.stub.filter(**condition).annotate(
                    day=TruncDay('updated_at')
                ).values('day').annotate(
                    total=Count('day')
                )
            return Response({'shop': shop.name, 'stubs_day': list(day_stubs)})
        else:
            stubs = shop.stub.filter(**condition)
            res_list = [
                {
                    'pk': s.pk,
                    'user_id': s.ticket.owner.pk,
                    'time': s.updated_at,
                }
                for s in stubs
            ]
            return Response({'shop': shop.name, 'stubs': res_list})
    else:
        return Response({'shop': "ありません", 'stubs': []})

@api_view(['POST'])
def getNotificationOfSuccessPayment(request):

    event = None
    payload = request.body
    # sig_header = request.headers['STRIPE_SIGNATURE']
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object'] # https://stripe.com/docs/api/checkout/sessions/object
        session_id = session.get("id")
        amount_subtotal = session.get("amount_subtotal")
        product = Product.objects.filter(is_active=True).first()
        had_tickets = Ticket.objects.filter(session_id=session_id)
        # productが一つならいいが二つ以上の場合はcheckoutsessionのritriveを行う
        purchased_ticket_num = amount_subtotal // product.price
        dt_now = make_aware(datetime.datetime.now())
        situ = Ticket.SITUATION_BEFORE
        if product.start_dt < dt_now and product.end_dt > dt_now:
            situ = Ticket.SITUATION_USABLE
        if had_tickets.count() != purchased_ticket_num:
            lineUserID = session.get("metadata").get("user_id")
            user = User.objects.get(lineUserID=lineUserID)
            user.create_ticket([{
                'quantity': purchased_ticket_num,
                'kind': product,
                'is_pay': True,
                'session_id': session_id,
                'situation': situ
            }])
            requests.post(
                "https://discord.com/api/webhooks/1047518934804463657/hRDEGkZCsDkKAogc-_H5-i9PXtCHfbEnyWPJqeeyEpeymaSaNtLkyjSEn1ZYzYjwQpq4",
                json.dumps({'content': f"<@685303720262893576>\nDjango:purchased Ticket > {purchased_ticket_num}\n{situ}\n{product.start_dt}\n{product.end_dt}\n{dt_now}\n(be:{product.start_dt < dt_now}) (af:{product.end_dt > dt_now}) <:o_:856372639060852736> "}),
                headers= {'Content-Type': 'application/json'}
            )

    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return Response({"success": True})

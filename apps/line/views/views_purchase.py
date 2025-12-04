from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.decorators.http import require_GET
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
# from django.utils import timezone
from django.utils.timezone import make_aware

import stripe
import datetime
import requests
import json

from apps.product.models import Product
from apps.core.forms import create_buy_form
from apps.core.models import User, Ticket
from .lineBase import line_bot_api, get_lineuser_by_token
from config import setting


class PurchaseView(TemplateView):  # , LoginRequiredMixin
    template_name = 'trans/purchase.html'
    # http_method_names = ['post']
    # login_url = '/login'

    # def get(self, request, *args, **kwargs):
    #     context = self.get_context_data(**kwargs)

    #     if "handtoken" in request.GET:
    #         token = request.GET.get("handtoken")

    #     return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # import pdb
        # pdb.set_trace()
        lineToken = request.POST.get('lineToken', None)
        user, _ = get_lineuser_by_token(lineToken)
        if not user:
            return redirect(reverse('line:purchase'))

        products = Product.objects.filter(is_active=True)
        form, _ = create_buy_form(user, products, request.POST)

        # 個数がおかしいとき用，どうやってテスト？
        if not form.is_valid():
            return redirect(reverse('line:purchase'))

        args = {
            'line_items': [],
            'mode': 'payment',
            'success_url': request.build_absolute_uri(reverse('line:purchase_suc')) + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': request.build_absolute_uri(reverse('line:purchase_can')),
            'metadata': {'user_id': user.lineUserID},
            'phone_number_collection': {'enabled': True, },
        }
        # if user.get('email'):# user.email:
        #     args['customer_email'] = user.email
        # import pdb
        # pdb.set_trace()
        for product in products:
            quantity = request.POST.get(str(product.pk), 0)

            if not quantity == '0':
                line_item = {
                    'price': product.price_id,
                    'quantity': quantity,
                }
                args['line_items'].append(line_item)
        # <process form cleaned data>
        # print(args)
        session = stripe.checkout.Session.create(**args)
        # import pdb
        # pdb.set_trace()
        return redirect(session.url, code=303)
        #     return redirect('/success/')
        # return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        # user = self.request.user
        context = super().get_context_data(**kwargs)

        products = Product.objects.filter(is_active=True)

        for product in products:
            tikcets = Ticket.objects.filter(kind=product).exclude(situation=Ticket.SITUATION_REFUND).count()
            if tikcets > product.max_sell:
                requests.post(
                    "https://discord.com/api/webhooks/1047518934804463657/hRDEGkZCsDkKAogc-_H5-i9PXtCHfbEnyWPJqeeyEpeymaSaNtLkyjSEn1ZYzYjwQpq4",
                    json.dumps({'content': f"<@685303720262893576>\n販売上限\n<:o_:856372639060852736><:o_:856372639060852736><:o_:856372639060852736>\n現在 : {tikcets}"}),
                    headers= {'Content-Type': 'application/json'}
                )
                context["cant_sell"] = True

        # context["kinds"] = ticket_pos_temp
        context["products"] = products

        context["liff_id"] = setting.LIFF_ID

        return context


@require_GET
def purchase_cansel(request):
    return HttpResponseRedirect(reverse('line:purchase'))


@require_GET
def purchase_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        raise Http404("keyerror")

    session = stripe.checkout.Session.retrieve(session_id, expand=['line_items'])
    content = {'status': session.get('status', 'open'), 'tickets': []}

    tickets_had = Ticket.objects.filter(session_id=session_id)

    # 指定のセッションからのチケットがなければとにかく作る
    if not tickets_had.count():
        line_items = session.get('line_items').get('data')
        situ = Ticket.SITUATION_USABLE if 'test' in session_id else Ticket.SITUATION_BEFORE
        lineuserID = session.get('metadata').get('user_id')
        user, _ = User.objects.get_or_create(lineUserID=lineuserID)
        boughts = []
        for item in line_items:
            prod = get_object_or_404(Product, price_id=item.get('price').get("id"))
            dt_now = make_aware(datetime.datetime.now())
            # situ = Ticket.SITUATION_USABLE
            if prod.start_dt < dt_now and prod.end_dt > dt_now:
                situ = Ticket.SITUATION_USABLE
                if not user.ticket.filter(kind=prod).count():
                    line_bot_api.link_rich_menu_to_user(lineuserID, setting.PURCHASED_RICHMENU)
            boughts.append({
                'quantity': item.get("quantity"),
                'kind': prod,
                'is_pay': True,
                'session_id': session_id,
                'situation': situ
            })
            requests.post(
                "https://discord.com/api/webhooks/1047518934804463657/hRDEGkZCsDkKAogc-_H5-i9PXtCHfbEnyWPJqeeyEpeymaSaNtLkyjSEn1ZYzYjwQpq4",
                json.dumps({'content': f"<@685303720262893576>\nDjango:purchased Ticket > {item.get('quantity')}\n{situ}\n{prod.start_dt}\n{prod.end_dt}\n{dt_now}\n(be:{prod.start_dt < dt_now}) (af:{prod.end_dt > dt_now}) <:o_:856372639060852736> "}),
                headers= {'Content-Type': 'application/json'}
            )
            content['tickets'].append({'prod': prod, 'quantity': item.get("quantity")})

        # 期間内のチケットがなく，作ったチケットが有効期限内であるとき
        # if user.ticket.filter(situation=Ticket.SITUATION_USABLE).count():
        #     pass
        user.create_ticket(boughts)

        # これはいらんかな
        if session.get('customer_details'):
            content['name'] = session.get('customer_details').get('name')
            user.email = session.get('customer_details').get('email')
            user.save()

        return render(request, 'trans/purchase_suc.html', content)

    else:
        kind_ids = tickets_had.values_list('kind', flat=True)
        list=[[],[]]
        for kind_id in kind_ids:
            if kind_id in list[0]:
             list[1][list[0].index(kind_id)]+=1
            else:
             list[0].append(kind_id)
             list[1].append(1)
        for id, num in zip(list[0], list[1]):
            prod = Product.objects.get(pk=id)
            content['tickets'].append({'prod': prod, 'quantity': num})
        content['name'] = tickets_had.first().owner.username
        return render(request, 'trans/purchase_suc.html', content)

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_GET
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
import stripe

from apps.product.models import Product
from ..models import Ticket
from ..forms import create_buy_form


class BuyView(TemplateView, LoginRequiredMixin):
    # template_name = "product/buy.html"
    http_method_names = ['post']
    # login_url = '/login'

    def post(self, request, *args, **kwargs):
        # ログインしていないユーザーの場合
        if request.user.is_anonymous:
            raise PermissionDenied

        user = request.user
        products = Product.objects.all()
        form, rems = create_buy_form(user, products, request.POST)

        # 個数がおかしいとき用，どうやってテスト？
        if not form.is_valid():
            return redirect(reverse('app:form'))

        args = {'line_items': [],
                'mode': 'payment',
                'success_url': request.build_absolute_uri(reverse('app:buy_comp')) + '?session_id={CHECKOUT_SESSION_ID}',
                'cancel_url': request.build_absolute_uri(reverse('app:home')),
                }
        if user.email:
            args['customer_email'] = user.email

        for product in products:
            quantity = request.POST.get(str(product.pk), 0)

            if not quantity == '0':
                line_item = {'price': product.price_id,
                             'quantity': quantity,
                             'adjustable_quantity': {'enabled': True,
                                                     'maximum': rems.get(product.pk, quantity),
                                                     },
                             }
                args['line_items'].append(line_item)

        # <process form cleaned data>
        session = stripe.checkout.Session.create(**args)
        return redirect(session.url, code=303)
        #     return redirect('/success/')
        # return render(request, self.template_name, {'form': form})

    # def get_context_data(self, **kwargs):
    #     user = self.request.user

    #     products = Product.objects.all()

    #     ticket_pos_temp = []
    #     for product in products:
    #         # pk = product.pk
    #         count = user.ticket.filter(kind=product).count()
    #         max_sell = product.max_sell
    #         ticket_pos_temp.append({'product': product, 'pos': max_sell - count})

    #     # ticket_pos = user.ticket.all()

    #     # ticket_pos_temp["lunch"] = (Setting.objects.first().MAX_SELL
    #     #                             - ticket_pos["lunch"])
    #     # ticket_pos_temp["dinner"] = (Setting.objects.first().MAX_SELL
    #     #                              - ticket_pos["dinner"])

    #     context = super().get_context_data(**kwargs)
    #     context["kinds"] = ticket_pos_temp
    #     return context


@login_required
@require_GET
def purchase_confirmation(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        raise Http404("keyerror")

    session = stripe.checkout.Session.retrieve(session_id, expand=['line_items'])
    content = {'status': session.get('status', 'open')}

    try:
        line_items = session.get('line_items').get('data')
        boughts = []
        for item in line_items:
            boughts.append({
                'quantity': item.get("quantity"),
                'kind': get_object_or_404(Product, product_id=item.get('price').get("product")),
                'is_pay': True,
                'session_id': session_id,
            })
    except KeyError:
        raise Http404("keyerror")

    tickets_had = Ticket.objects.filter(session_id=session_id)

    # 指定のセッションからのチケットがなければとにかく作る
    if not tickets_had.count():

        user = request.user
        content['tickets'] = user.create_ticket(boughts)
        # これはいらんかな
        content['name'] = stripe.Customer.retrieve(session.customer).name

        return render(request, 'purchase/confirm.html', content)

    else:
        return HttpResponseRedirect(reverse('app:home'))

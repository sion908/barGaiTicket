from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.db.models import Count
from django.db.models.functions import TruncMonth

from .models import Product
from apps.core.models import User, Shop, Ticket, Stub
from .forms import ProductForm

import qrcode
import base64
from io import BytesIO


def create_product(request):

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        context = {'posted': form.instance}
        if form.is_valid():
            # Uploads image and creates a model instance for it
            form.save()

        return render(request, 'product/detail.html', context)

    else:
        form = ProductForm()

        return render(request, "product/form.html", {'form': form})


def show_products(request):
    products = Product.objects.all()

    # たぶん画像消す用のやつ
    # for product in products:
    #     id = getattr(product.image, "public_id", None)
    #     if id:
    #         cloudinary.uploader.destroy(id)

    return render(request, "product/show.html", {"products": products})


def detail_product(request, id):

    product = get_object_or_404(Product, pk=id)

    return render(request, 'product/detail.html', {'product': product})


def update_products(request):

    user = request.user

    if getattr(user, 'is_superuser', False):
        #    ? return HttpResponseRedirect(reverse('app:home'))

        products = Product.objects.all()

        for product in products:
            product.initial_stripe()

    return HttpResponseRedirect(reverse('app:home'))


@login_required
@require_GET
def show_shops(request):
    context = {'products': []}
    owner = request.user
    context['owner'] = owner

    if not owner.is_staff:
        return redirect('accounts:login')

    shops = Shop.objects.filter(is_active=True)

    products = Product.objects.filter(is_active=True)

    for product in products:
        dict = {'name': product.name}
        tickets = Ticket.objects.filter(kind=product).exclude(situation=Ticket.SITUATION_REFUND).count()
        stubs = Stub.objects.filter(ticket__kind=product).order_by('updated_at')
        dict["month"] = [str(m) for m in range(
            stubs.first().updated_at.month,
            stubs.last().updated_at.month + 1
        ) ]
        dict["tickets"] = tickets if tickets else 0
        dict["stubs"] = stubs.count() or 0
        dict['no_used'] = tickets * product.stub_count - stubs.count()
        dict['id'] =  product.id
        context['products'].append(dict)

    shops_dict = []
    for shop in shops:
        shop_dict = vars(shop)
        text = f'https://liff.line.me/1657251421-rW78w9bW/employ/?ver=2023-f&shop_id={str(shop.id)}'
        img = qrcode.make(text)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr = base64.b64encode(buffer.getvalue()).decode().replace("'", "")
        shop_dict["qr"] = qr
        for product in products:
            _product_stubs = shop.stub.filter(ticket__kind=product).annotate(
                month=TruncMonth('updated_at')
            ).values('month').annotate(
                total=Count('month')
            )
            product_stubs_dict = {}
            for _product_stub in _product_stubs:
                # setattr(
                #     shop,
                #     f"{product.id}-{_product_stub.get('month').strftime('%y-%m')}",
                #     _product_stub.get("total")
                # )
                product_stubs_dict[str(_product_stub.get("month").month)] = str(_product_stub.get("total"))
            shop_dict[str(product.id)]= product_stubs_dict
        shops_dict.append(shop_dict)
    context['shops'] = shops_dict

    users = User.objects.all().count()
    context['users'] = users


    return render(request, 'product/show_shops.html', context)
    # たぶん画像消す用のやつ
    # for product in products:
    #     id = getattr(product.image, "public_id", None)
    #     if id:
    #         cloudinary.uploader.destroy(id)

    # return render(request, "product/show.html", {"products": products})

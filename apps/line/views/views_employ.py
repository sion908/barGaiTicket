from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from apps.core.models import Shop
from apps.product.models import Product
from config import setting
from .lineBase import get_lineuser_by_token
from ..forms import EmployForm


class EmployView(TemplateView, LoginRequiredMixin):
    "チケット購入用"
    template_name = "trans/employ.html"
    # http_method_names = ['get', 'post']

    # def get_context_data(self, **kwargs):

    #     context = super().get_context_data(**kwargs)
    #     context["is_get"] = 'True'
    #     return context
    # https://liff.line.me/1657251421-rW78w9bW/employ/?ver=2023-f&shop_id=42587da1-5329-4599-94b1-dac496666947
    # get処理
    def get(self, request, *args, **kwargs):
        content = {'shop': '', 'liff_id': setting.LIFF_ID}

        product = Product.objects.filter(is_active=True).first()
        if product and product.questionnaire_url:
            content['questionnaire_url'] = product.questionnaire_url

        if "shop_id" in request.GET:
            # query_paramが指定されている場合の処理
            # print(request.GET.get("shop_id"), request.GET.get("ver"))
            shop_id = request.GET.get("shop_id")
            ver = request.GET.get("ver")
            if ver == '2023-f':
                shop = get_object_or_404(Shop, pk=shop_id)
                content['shop'] = shop

        # endif

        return render(request, self.template_name, content)  # , {'is_first' : True})

    # post処理
    def post(self, request, *args, **kwargs):
        lineToken = request.POST.get('lineToken', None)
        user, _ = get_lineuser_by_token(lineToken)
        form = EmployForm(request.POST)
        product = Product.objects.filter(is_active=True).first()

        # 個数がおかしいとき用
        if not form.is_valid():
            self.kwargs["message"] = "該当する店がありません"
            return render(request, self.template_name, context=self.kwargs)

        shop_id = form.cleaned_data.get('shop_id')
        shop = Shop.objects.get(pk=shop_id)
        employ_num = form.cleaned_data.get('employ_num')

        user.ticket.use_by_count(shop=shop, count=employ_num, product=product)

        return JsonResponse({'success': 'ok'})

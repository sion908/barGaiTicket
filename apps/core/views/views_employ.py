from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.http import Http404

from ..models import Shop, Ticket
from ..forms import EmployForm, EmployComfirmForm


class EmployView(TemplateView, LoginRequiredMixin):
    template_name = "employ/qr.html"
    # http_method_names = ['get', 'post']

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["is_get"] = 'True'
        return context

    # get処理
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'is_get': True})

    # post処理
    def post(self, request, *args, **kwargs):
        # ログインしていないユーザーの場合
        user = request.user
        if user.is_anonymous:
            raise PermissionDenied

        form = EmployForm(request.POST)

        # 個数がおかしいとき用
        if not form.is_valid():
            self.kwargs["message"] = "該当する店がないです"
            self.kwargs["is_get"] = 'True'
            return render(request, self.template_name, context=self.kwargs)

        can_max_use = user.ticket.filter(situation=Ticket.SITUATION_USABLE).count()
        self.kwargs["can_max_use"] = can_max_use

        self.kwargs["is_get"] = ''
        shop = Shop.objects.get(pk=form.cleaned_data.get('shop_id'))
        self.kwargs["shop"] = shop
        return render(request, self.template_name, context=self.kwargs)


@login_required
@require_POST
def employ_confirmation(request):
    # ログインしていないユーザーの場合
    user = request.user
    if user.is_anonymous:
        raise PermissionDenied

    form = EmployComfirmForm(request.POST)
    if not form.is_valid():
        raise Http404("keyerror")
    shop_id = form.cleaned_data.get('shop_id')
    shop = Shop.objects.get(pk=shop_id)
    employ_num = form.cleaned_data.get('employ_num')

    user.ticket.use_by_count(shop=shop, count=employ_num)

    # リダイレクト時の二重処理を防ぐため，リダイレクトする
    return redirect('app:employ_approve', pk=str(shop.pk), employ_num=str(employ_num))


def employ_approve(request, employ_num, pk):
    # ログインしていないユーザーの場合
    shop = get_object_or_404(Shop, pk=pk)

    context = {'employ_num': employ_num, 'shop': shop}

    return render(request, 'employ/complete.html', context=context)

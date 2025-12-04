from django.shortcuts import render, redirect
from django.views.generic import TemplateView  # テンプレートタグ
from .forms import AccountForm  # ユーザーアカウントフォーム

# ログイン・ログアウト処理に利用
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.views import LogoutView

import re

def top(request):
    # def get(self, req):
    return redirect('https://nagasakiavenue.wixsite.com/avenue/post/premiumcoupon')
    return render(request, "top.html")


def howto(request):
    return render(request, "app/howto.html")


def asct(request):
    return render(request, "app/asct.html")


# ログイン
def Login(request):
    # POST
    if request.method == 'POST':
        # フォーム入力のユーザーID・パスワード取得
        ID = request.POST.get('userid')
        Pass = request.POST.get('password')

        # Djangoの認証機能
        user = authenticate(username=ID, password=Pass)

        # ユーザー認証
        if user:
            # ユーザーアクティベート判定
            if user.is_active:
                # ログイン
                login(request, user)

                if user.is_staff:
                    # ホームページ遷移
                    return HttpResponseRedirect(request.POST.get('next', reverse('app:home')))
                else:
                    # ホームページ遷移
                    return HttpResponseRedirect(request.POST.get('next', reverse('product:showShop')))
            else:
                # アカウント利用不可
                return HttpResponse("アカウントが有効ではありません")
        # ユーザー認証失敗
        else:
            return HttpResponse("ログインIDまたはパスワードが間違っています")

    # GET
    else:
        if request.user.is_anonymous:
            # print({"request.GET":request.GET})
            params = {
                'username': request.GET.get(key="username", default=""),
                'password': request.GET.get(key="password", default=""),
            }
            context = {'params': params}
            next = request.GET.get('next')
            if next:
                res = re.findall('\?username=(\w*)\&password=(\w*)', next)
                if len(res):
                    context["params"]['username'] = res[0][0]
                    context["params"]['password'] = res[0][1]
            else:
                next = reverse('product:showShop')
            context["next"] = next


            return render(request, 'accounts/login.html', context)
        else:
            return HttpResponseRedirect(reverse('app:home'))


# ログアウト
class Logout(LogoutView):
    # ログイン画面遷移
    Template_name = 'accounts/logout.html'


# # ホーム
# @login_required
# def home(request):
#     params = {"UserID":request.user, }
#     return render(request, "accounts/home.html", context=params)


# 新規登録
class AccountRegistration(TemplateView):

    def __init__(self):
        self.params = {
            "AccountCreate": False,
            "account_form": AccountForm(),
            # "add_account_form":AddAccountForm(),
        }

    # Get処理
    def get(self, request):
        self.params["account_form"] = AccountForm().as_table()
        # self.params["add_account_form"] = AddAccountForm()
        self.params["AccountCreate"] = False
        return render(request, "accounts/register.html", context=self.params)

    # Post処理
    def post(self, request):
        self.params["account_form"] = AccountForm(data=request.POST)
        # self.params["add_account_form"] = AddAccountForm(data=request.POST)

        # フォーム入力の有効検証
        if self.params["account_form"].is_valid():
            # アカウント情報をDB保存
            account = self.params["account_form"].save()
            # パスワードをハッシュ化
            account.set_password(account.password)
            # ハッシュ化パスワード更新
            account.save()

            # アカウント作成情報更新
            self.params["AccountCreate"] = True

        else:
            # フォームが有効でない場合
            # print(self.params["account_form"].errors)
            pass

        return render(request, "accounts/register.html", context=self.params)

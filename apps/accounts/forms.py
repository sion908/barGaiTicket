# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.forms import AuthenticationForm
# from app.models import  User
# from django.contrib.auth import get_user_model User = get_user_model()

from django import forms
from apps.core.models import Owner


# フォームクラス作成
class AccountForm(forms.ModelForm):
    # パスワード入力 : 非表示対応
    password = forms.CharField(widget=forms.PasswordInput(), label="パスワード")

    class Meta():
        # ユーザー認証
        model = Owner
        # フィールド指定
        fields = ('username', 'email', 'password')
        # フィールド名指定
        labels = {'username': "ユーザーID", 'email': "メール"}

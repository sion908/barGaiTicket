from django.shortcuts import get_object_or_404
import requests
from django.http import Http404

from apps.core.models import User

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from config import setting

line_bot_api = LineBotApi(channel_access_token=setting.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=setting.LINE_ACCESS_SECRET)


def get_lineuser_by_token(token, create=False):
    """
        tokenによって, 
        User    -> <class 'apps.core.models.User'>
        createflagで作るかどうかの確認
        created -> すでにあった場合にTrue
        を得る.
        tokenからユーザーIDが取れる場合はとにかくUserを 作る
    """
    # getでエラーようにtryしてるけどエラーはいたときは何をすればいいんだ？
    if not token:
        print("not token")
        raise Http404("accestoken not found.")
        # raise Http404("時間が経ちすぎました．もう一度お試しください")
    try:
        res = requests.get(f"https://api.line.me/oauth2/v2.1/verify?access_token={token}")
        res.raise_for_status()  # ステータスコード見て200番台以外だと例外発生するらしい
    except requests.exceptions.RequestException as e:
        print("invalid token", e.response.text)
        raise Http404("invalid accesstoken")

    # valid_token_url = 'https://api.line.me/oauth2/v2.1/verify?access_token=' + token
    # is_valid_token = requests.get(valid_token_url)
    # # import pdb
    # # pdb.set_trace()

    # if not is_valid_token.status_code == 200:
    #     return

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    try:
        req = requests.get('https://api.line.me/v2/profile', headers=headers)
        req.raise_for_status()  # ステータスコード見て200番台以外だと例外発生するらしい
    except requests.exceptions.RequestException:
        try:
            req = requests.get('https://api.line.me/v2/profile', headers=headers)
            req.raise_for_status()  # ステータスコード見て200番台以外だと例外発生するらしい
        except requests.exceptions.RequestException as e:
            print("not permission", e.response.text)
            raise Http404("not permission to view profile")

    # ここはない場合を考える必要があるのか？
    user_id = req.json().get('userId')
    if create:
        user, created = User.objects.get_or_create(lineUserID=user_id)
        disp_name=req.json().get("displayName")
        if disp_name:
            user.username = disp_name
            user.save()
    else:
        user = get_object_or_404(User,lineUserID=user_id)
        created = ""

    return [ user, created ]

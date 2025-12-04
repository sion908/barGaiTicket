from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from linebot.exceptions import InvalidSignatureError

from apps.core.models import User

from .lineBase import line_bot_api, handler
from linebot.models import (
    FollowEvent, UnfollowEvent, PostbackEvent, MessageEvent, JoinEvent,
    TextSendMessage, StickerMessage, FlexSendMessage
)
from . import line_message, line_introS


@csrf_exempt
def index(request):
    # リクエストヘッダーから署名検証のための値を取得
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    # リクエストボディを取得
    body = request.body.decode('utf-8')
    try:
        # 署名を検証し、問題なければhandleに定義されている関数を呼び出す
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名検証で失敗したときは例外をあげる
        HttpResponseForbidden()
    # handleの処理を終えればOK
    return HttpResponse('OK', status=200)


# addメソッドの引数にはイベントのモデルを入れる
# 関数名は自由

# メッセージイベントの場合の処理
# かつテキストメッセージの場合
# @handler.add(MessageEvent, message=TextMessage)
# def handle_text_message(event):
#     # メッセージでもテキストの場合はオウム返しする
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=event.message.text)
#     )

# メッセージイベントの場合の処理
# かつスタンプメッセージの場合
@handler.add(MessageEvent, message=StickerMessage)
def handle_text_message(event):
    line_introS.showTickets(event.reply_token)


# ポストバックイベントの場合の処理
@handler.add(PostbackEvent)
def handle_postback_message(event):

    pb_mess = event.postback.data
    if pb_mess == 'ShowTickets':
        # print(event.reply_token, event.source.user_id)
        line_message.showTickets(event.reply_token, event.source.user_id)
    elif pb_mess == 'StartQA':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="準備中です")
        )
    # # メッセージでもテキストの場合はオウム返しする
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text)
    # )


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=
                            "友達追加ありがとうございます！\n"+
                            "長崎居留地アベニュー実行委員会です。\n"+
                            "\n"+
                            "この公式LINEアカウントでは、「長崎居留地プレミアムクーポン2023」のオンラインクーポン購入から、店舗での決済まで使うことができます。\n"+
                            "\n"+
                            "◎期間：2023年9月16日（土）〜12月31日（日）\n"+
                            "1,000部限定の発行です。売り切れ次第、終了となりますので、お早めにお買い求めください。\n"+
                            "\n"+
                            "◎購入方法：\n"+
                            "下部に表示されるメニュー画面の「買う」ボタンをタップすると、購入画面に移動します。\n"+
                            "※販売開始は9月16日（土）10時からです。\n"+
                            "\n"+
                            "◎使用方法：\n"+
                            "下部に表示されるメニュー画面の「使う」ボタンをタップすると、決済画面に移動します。カメラが起動しますので、店舗に設置してあるQRコードを読み取りください。\n"+
                            "\n"+
                            "「確認」ボタンより、クーポンの残高（残数）を確認することができます。\n"+
                            "\n"+
                            "\n"+
                            "※ 「長崎居留地プレミアムクーポン2023」は紙クーポンもご用意しております。\n"+
                            "加盟店舗で直接購入、もしくは9月16〜18日の特別販売会にてお買い求めください。"
                            ),
            FlexSendMessage(alt_text="長崎居留地プレミアムクーポン2023開催！！", contents=line_message.makefollowedCarousel())
        ]
    )
    args = {'is_followed': True}
    profile = line_bot_api.get_profile(event.source.user_id)
    if profile:
        args["username"] = profile.display_name
    User.objects.update_or_create(lineUserID=event.source.user_id, defaults=args,)


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    user = User.objects.get(lineUserID=event.source.user_id)
    if user:
        user.is_followed = False
        user.save()


@handler.add(JoinEvent)
def handle_join(event):
    source = event.get("source")
    memberIDs=0

    if source.get("type") == "group":
        tag = "groupId"
        getIds = line_bot_api.get_group_member_ids
        leaveFun = line_bot_api.leave_group
    elif source.get("type") == "room":
        tag = "roomId"
        getIds = line_bot_api.get_room_member_ids
        leaveFun = line_bot_api.leave_room
    else:
        return
    
    id = source.get(tag)
    memberIDs = getIds(id)
    if not "U45a8486c1f11dacd2dc6c7abc8a74513" in memberIDs.member_ids:
        leaveFun(id)

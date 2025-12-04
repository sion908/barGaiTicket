from apps.core.models import Ticket, User
from apps.product.models import Product
from django.shortcuts import get_object_or_404
from linebot.models import FlexSendMessage, TextSendMessage

from copy import deepcopy
import datetime

from .lineBase import line_bot_api


def showTickets(rep_token, userid):
    user = get_object_or_404(User, lineUserID=userid)
    product = Product.objects.filter(is_active=True).first()
    if product:
        tickets = user.ticket.filter(kind=product).exclude(situation=Ticket.SITUATION_REFUND).order_by("situation")
        stub_price = product.stub_price

        if tickets.count():
            causel, stub_counter = makeTicketBubble_count(tickets, product)
            message = [
                TextSendMessage(text=f"購入済み : {tickets.count()}冊"),
                TextSendMessage(text=f"利用可能クーポン : {stub_counter}枚\n({ stub_counter * stub_price }円分)"),
                FlexSendMessage(alt_text=f"利用可能クーポン:{ stub_counter * stub_price }円分", contents=causel),
            ]
        else:
            message = [
                TextSendMessage(text="持っているチケットはありません"),
                TextSendMessage(text=f"もし, 購入したのに反映されていない場合は, 反映まで少し時間が掛かることがあります. それでも反映されない場合は,\nnagasaki.avenue@gmail.com\nまでご連絡ください.")
            ]
    else:
        message = [
            TextSendMessage(text="イベント期間外です")
        ]

    line_bot_api.reply_message(rep_token, message)


def makefollowedCarousel():
    return {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://res.cloudinary.com/hm3pxo0eu/image/upload/v1694215245/Frame_3_tinsw5.png",
                            "size": "full",
                            "aspectMode": "cover",
                            "aspectRatio": "1:1.414"
                        }
                    ],
                    "paddingAll": "0px"
                }
            },
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "詳しくは",
                            "align": "center",
                            "color": "#3A8B46",
                            "offsetBottom": "sm"
                        },
                        {
                            "type": "text",
                            "text": "webサイトを開く",
                            "gravity": "top",
                            "wrap": True,
                            "weight": "regular",
                            "align": "center",
                            "action": {
                                "type": "uri",
                                "label": "action",
                                "uri": "https://nagasakiavenue.wixsite.com/avenue/post/premiumcoupon"
                            },
                            "size": "xxl",
                            "color": "#3A8B46"
                        },
                        {
                            "type": "text",
                            "text": "＞＞",
                            "align": "center",
                            "size": "xl",
                            "color": "#3A8B46"
                        }
                    ],
                    "justifyContent": "center"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "2023 居留地アベニュー実行委員会",
                            "size": "xxs",
                            "align": "end",
                            "color": "#BB3A40"
                        }
                    ]
                },
                "action": {
                    "type": "uri",
                    "label": "action",
                    "uri": "https://nagasakiavenue.wixsite.com/avenue/post/bar-gai2022"
                },
                "styles": {
                    "body": {"backgroundColor": "#F8EDE7"},
                    "footer": {"backgroundColor": "#F8EDE7"}
                }
            }
        ]
    }


def makeTicketBubble_count(tickets, product):
    amount_ticket_money = 0
    used_ticket_money = 0
    stub_counter = 0
    now = datetime.datetime.now()

    stub_amout = product.stub_count
    stub_price = product.stub_price

    for t in tickets:
        _stub_count = t.stub.count()
        amount_ticket_money += stub_amout * stub_price
        used_ticket_money += _stub_count * stub_price
        stub_counter += stub_amout - _stub_count

    causel = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "長崎居留地プレミアムクーポン"
            }
            ],
            "backgroundColor": "#F8EDE7"
        },
        "hero": {
            "type": "image",
            "url": "https://res.cloudinary.com/hm3pxo0eu/image/upload/v1694096373/c6o7d1jpwpdccvrzn1ln.png",
            "size": "full",
            "aspectMode": "cover",
            "action": {
            "type": "uri",
            "uri": "http://linecorp.com/"
            },
            "aspectRatio": "421:239"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                {
                    "type": "text",
                    "text": "あと",
                    "flex": 6,
                    "offsetStart": "lg"
                }
                ]
            },
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                {
                    "type": "text",
                    "text": str(amount_ticket_money-used_ticket_money),
                    "flex": 5,
                    "size": "3xl",
                    "weight": "bold",
                    "align": "end",
                    "gravity": "center"
                },
                {
                    "type": "text",
                    "text": "/",
                    "flex": 1,
                    "size": "4xl",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": f"{amount_ticket_money}円",
                    "flex": 3,
                    "align": "start",
                    "gravity": "bottom",
                    "weight": "bold"
                }
                ]
            }
            ],
            "backgroundColor": "#F8EDE7"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
            {
                "type": "text",
                "text": f"{now.strftime('%y/%m/%d %H:%M')} 現在",
                "align": "end",
                "size": "xxs"
            },
            {
                "type": "text",
                "text": "2023 長崎アベニュー実行委員会",
                "align": "end",
                "size": "xxs"
            }
            ],
            "flex": 0,
            "backgroundColor": "#F8EDE7"
        }
    }
    return [causel, stub_counter]


def makeTicketBubble_stamp(tickets):
    stub_counter = 0
    header = {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {
                "type": "text",
                "text": "長崎居留地クーポン",
                "align": "center",
                "gravity": "center"
            }
        ],
        "paddingAll": "9px"
    }

    sep = {"type": "separator", "color": "#ffffff"}
    bubble_rights_orig = [
        {"type": "text", "text": "利用期間前", "color": "#ffffff", "align": "end", "size": "sm", "offsetEnd": "md"},
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "filler"},
                deepcopy(sep),
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        deepcopy(sep),
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": stampbox(base_num=1)
                        },
                        deepcopy(sep),
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": stampbox(base_num=6)
                        },
                        deepcopy(sep)
                    ],
                    "flex": 10,
                    "backgroundColor": "#abc2b5"
                },
                deepcopy(sep),
                {"type": "filler"}
            ]
        }
    ]
    car_conts = []
    for ticket in tickets:
        bubble_rights = deepcopy(bubble_rights_orig)
        stu = ticket.situation
        if stu == Ticket.SITUATION_BEFORE:
            bubble_rights[0]["text"] = "利用期間前"
        elif stu == Ticket.SITUATION_USABLE:
            bubble_rights[0]["text"] = "利用可能"
        elif stu == Ticket.SITUATION_USED:
            bubble_rights[0]["text"] = "利用済み"

        stubs = ticket.stub.all()

        for i, _ in enumerate(stubs):

            bubble_rights[1]["contents"][2]["contents"][i // 5 * 2 + 1]["contents"][i % 5 * 2]["text"] = "済"

        bubble = {
            "type": "bubble",
            "header": header,
            "hero": {
                "type": "image",
                "url": "https://res.cloudinary.com/hx7mef7m4/image/upload/v1668666312/20221116_102410344_iOS_b4zvhp.jpg",
                "margin": "none",
                "size": "full",
                "offsetTop": "0px",
                "offsetBottom": "0px",
                "aspectMode": "fit",
                "aspectRatio": "1.25:1"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": bubble_rights,
                "paddingAll": "none",
                "paddingTop": "sm",
                "backgroundColor": "#1E5B3A"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "居留地アベニュー実行委員会",
                        "size": "5px",
                        "align": "end",
                        "color": "#ffffff"
                    }
                ]
            },
            "styles": {
                "header": {
                    "backgroundColor": "#fefcfc"
                },
                "footer": {
                    "backgroundColor": "#1E5B3A"
                }
            }
        }
        car_conts.append(bubble)
        stub_counter += ticket.kind.stub_count - len(stubs)
    # end for ticket

    carousel = {
        "type": "carousel",
        "contents": car_conts,
    }
    # print(carousel)
    return [carousel, stub_counter]


def stampbox(base_num):
    box = []
    sep = {
        "type": "separator",
        "color": "#ffffff"
    }
    for i in range(5):
        box.append(deepcopy({
            "type": "text",
            "text": str(base_num + i),
            "align": "center",
            "color": "#ffffff"
        }))
        if not i == 4:
            box.append(deepcopy(sep))
    return box

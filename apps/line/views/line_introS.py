from apps.core.models import Shop

from .lineBase import line_bot_api
from linebot.models import (
    FlexSendMessage, LocationSendMessage
)


def showTickets(rep_token):
    shop = Shop.objects.order_by("?").first()
    message = [FlexSendMessage(alt_text="tickets", contents=makeShopflex(shop)),
               LocationSendMessage(
                   title=shop.name,
                   address=shop.access,
                   latitude=shop.gpsLatitude,
                   longitude=shop.gpsLongitude)
               ]

    line_bot_api.reply_message(
        rep_token,
        message
    )


def makeShopflex(shop):

    return {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://drive.google.com/uc?id=1jVETwngIUF2VNRLx5YrfMygvXJSkuU4I",
                            "backgroundColor": "#ffffff",
                            "align": "start",
                            "size": "30px",
                            "position": "relative",
                            "flex": 0,
                            "margin": "7px"
                        },
                        {
                            "type": "text",
                            "text": shop.name,
                            "align": "center",
                            "margin": "7px",
                            "gravity": "center",
                            "color": "#E2CE1F"
                        }
                    ],
                    "margin": "5px",
                    "paddingAll": "10px"
                },
                "hero": {
                    "type": "image",
                    "url": f"https://drive.google.com/uc?id={shop.opictID}",
                    "aspectMode": "fit",
                    "aspectRatio": "1:1",
                    "margin": "0px",
                    "position": "relative",
                    "size": "full"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": shop.phone,
                            "color": "#E2CE1F",
                            "offsetStart": "xxl"
                        },
                        {
                            "type": "text",
                            "text": shop.hour,
                            "color": "#E2CE1F",
                            "offsetStart": "xxl",
                            "size": "md"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "長崎居留地アベニュー実行委員会",
                            "size": "5px",
                            "align": "end",
                            "color": "#E2CE1F"
                        }
                    ]
                },
                "styles": {
                    "header": {
                        "backgroundColor": "#2A314B"
                    },
                    "body": {
                        "backgroundColor": "#2A314B"
                    },
                    "footer": {
                        "backgroundColor": "#2A314B"
                    }
                }
            },
            {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://drive.google.com/uc?id=1jVETwngIUF2VNRLx5YrfMygvXJSkuU4I",
                            "backgroundColor": "#ffffff",
                            "align": "start",
                            "size": "30px",
                            "position": "relative",
                            "flex": 0,
                            "margin": "7px"
                        },
                        {
                            "type": "text",
                            "text": "カフェレストラン kizuna",
                            "align": "center",
                            "margin": "7px",
                            "gravity": "center",
                            "color": "#E2CE1F"
                        }
                    ],
                    "margin": "5px",
                    "paddingAll": "10px"
                },
                "hero": {
                    "type": "image",
                    "url": f"https://drive.google.com/uc?id={shop.mpictID}",
                    "aspectMode": "fit",
                    "aspectRatio": "1:1",
                    "margin": "0px",
                    "position": "relative",
                    "size": "full"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": shop.menu,
                            "color": "#E2CE1F",
                            "offsetStart": "none",
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "長崎居留地アベニュー実行委員会",
                            "size": "5px",
                            "align": "end",
                            "color": "#E2CE1F"
                        }
                    ]
                },
                "styles": {
                    "header": {
                        "backgroundColor": "#2A314B"
                    },
                    "body": {
                        "backgroundColor": "#2A314B"
                    },
                    "footer": {
                        "backgroundColor": "#2A314B"
                    }
                }
            }
        ]
    }

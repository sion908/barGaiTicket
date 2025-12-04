# from settings import *
# from socket import gethostname
# print('gethostname()',gethostname())
# if "fusy-dev" in gethostname():
#     print('fusy')
#     from develop import *
#     # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.develop')
# else:
#     print('else')
#     from heroku import *
#     # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.heroku')
from .settings import (
    CHANNEL_ACCESS_TOKEN, LINE_ACCESS_SECRET,
    LIFF_ID, LIFF_ID_OWNER,
    PURCHASED_RICHMENU,
    STRIPE_ENDPOINT_SECRET
    )

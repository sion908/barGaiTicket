
from .settings import *
import django_heroku
import dj_database_url
# import cloudinary

db_from_env = dj_database_url.config()
DATABASES = {
    'default': dj_database_url.config()
}

ALLOWED_HOSTS = ['127.0.0.1', '.herokuapp.com']
# ALLOWED_HOSTS = ["*"]

# SECRET_KEY = os.environ['SECRET_KEY']
django_heroku.settings(locals())

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DJANGO_SETTINGS_MODULE = 'config.setting.heroku'

# cloudinary.config(
#         cloud_name='he93wwe4y',
#         api_key=os.environ['API_KEY'],
#         api_secret=os.environ['API_SECRET']
#     )

# stripe.api_key = os.environ['STRIPE_API_KEY']

DEBUG = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'apps'),
#                     os.path.join(BASE_DIR, 'api'),
#                     os.path.join(BASE_DIR, 'static'),
#                     ]
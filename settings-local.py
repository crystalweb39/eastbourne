# Django settings for eastbourne project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('chaol', 'chaol@1md.com.au'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'eastbourne'
DATABASE_USER = 'chaol'
DATABASE_PASSWORD = 'chaol'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = ''

TXT_SHOP_ORDER_STATUS_IN_PROGRESS = "In Progress"
TXT_SHOP_ORDER_STATUS_ORDERED = "Ordered"

TXT_SHOP_SHIPPING_UNABLE_TO_CALCULATE = "Unable to calculate Freight & Handling, please continue with your order, we will contact you to arrange for postage"

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'

AUTH_PROFILE_MODULE = "userprofile.Profile"

PRODUCTS_PER_PAGE = 9

BLOG_POSTS_PER_PAGE = 5

TIME_ZONE = 'Australia/Sydney'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

DOMAIN = 'localhost:100'#'www.eastbourneart.com.au'
USE_I18N = False

USERNAME = 'seller_1285220138_biz_api1.hotmail.com'#'Trish.Fraunfelter_api1.eastbourneart.com.au'
PASSWORD = "J69WZABQPESD83AB"#'WEW64ZQND8PN4EJW'
SIGNATURE = "APeY.Z31bxxe07mo2U32rE02RGuRA-Cc4gj-gGyqRUAc6JvZjPwTMZoo" # 'ALH14Vh5HUqNptiWLzp8qGYj22MgA6o-a1s-fUlk7gFBsII8UMiZ1cXg'

#TINYMCE_JS_URL = '/media/tiny_mce/tiny_mce_src.js'
#TINYMCE_DEFAULT_CONFIG = {
#    'plugins': "table,spellchecker,paste,searchreplace",
#    'theme': "simple",
#    #'cleanup_on_startup': True,
#    #'custom_undo_redo_levels': 10,
#    'valid_elements': "a[href|target=_blank],strong/b,div[align],br,img",
#}
#TINYMCE_SPELLCHECKER = True
#TINYMCE_COMPRESSOR = True

#URL_FILEBROWSER_MEDIA = "/media/filebrowser/"
FILEBROWSER_URL_FILEBROWSER_MEDIA = "/media/filebrowser/"

EXTENSIONS = {
    'Folder':[''],
    'Image':['.jpg', '.jpeg', '.gif','.png','.tif','.tiff'],
    'Video':['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    'Document':['.pdf','.doc','.rtf','.txt','.xls','.csv'],
    'Sound':['.mp3','.mp4','.wav','.aiff','.midi'],
    'Code':['.html','.py','.js','.css']
}
MAX_UPLOAD_SIZE = 5000000

# PIL's Error "Suspension not allowed here" work around:
# s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
IMAGE_MAXBLOCK = 1024*1024

# Exclude files matching any of the following regular expressions
# Default is to exclude 'sorl-thumbnail' style naming of jpg, png, or gif thumbnails
EXCLUDE = (r'_(jpg|png|gif)_.*_q\d{1,3}\.(jpg|png|gif)', )

THUMB_PREFIX = 'thumb_'

THUMBNAIL_SIZE = '50x50'
USE_IMAGE_GENERATOR = True
IMAGE_GENERATOR_DIRECTORY = '_versions'
IMAGE_GENERATOR_LANDSCAPE = [('thumbnail_',140),('small_',300),('medium_',460),('big_',620)]
IMAGE_GENERATOR_PORTRAIT = [('thumbnail_',140),('small_',300),('medium_',460),('big_',620)]
IMAGE_CROP_GENERATOR = [('cropped_',60,60),('croppedthumbnail_',140,140)]
CHECK_EXISTS = True
FORCE_GENERATOR = False
FORCE_GENERATOR_RUN = False

# if set True, then FileBrowser will not try to import a mis-installed PIL
STRICT_PIL = False

# list of names not allowed for folders
DISALLOWED_FOLDER_NAMES = ['mkdir', 'upload', 'rename', 'delete']


MEDIA_ROOT = '/home/chaol/workspace/eastbourneart/media/'

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/media/adminmedia/'

URL_FILEBROWSER_MEDIA = "/media/filebrowser/"
PATH_FILEBROWSER_MEDIA = MEDIA_ROOT+"filebrowser/"
URL_TINYMCE = "/media/tiny_mce/"



SECRET_KEY = 'q@kudm#a1t4xs=gq@!t7%u3qtpy3b9z(#zxyhg8w1=qb%ig*j-'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.request",
    "grappelli.context_processors.admin_template_path",
)


#SESSION_EXPIRE_AT_BROWSER_CLOSE = True

GRAPPELLI_ADMIN_TITLE = 'Eastbourne Art'

ROOT_URLCONF = 'eastbourne.urls'

TEMPLATE_DIRS = (
    "/home/telliott/workspace/eastbourne/backend/templates/",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'eastbourne.blog',
    'eastbourne.website',
    'eastbourne.shop',
    'eastbourne.userprofile',
    'eastbourne.stockists',
    'grappelli',
    'tagging',
    'filebrowser',
    'sorl.thumbnail',
    #'tinymce',
    'django.contrib.admin',
)

FIXTURE_DIRS = (
   '/home/craig/website/backend/fixtures/',
)

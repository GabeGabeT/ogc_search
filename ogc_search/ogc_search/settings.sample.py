"""
Django settings for ogc_search project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import logging.config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'changeme'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMIN_ENABLED = False

ALLOWED_HOSTS = []

INTERNAL_IPS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analytical',
    'markdown_filter',
    'debug_toolbar',
    'ATI',
    'briefing_notes',
    'grants',
    'national_action_plan',
    'open_data',
    'wet'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'ogc_search.middleware.QueryLoggingMiddleware',
]

MARKDOWN_FILTER_WHITELIST_TAGS = [
    'a',
    'p',
    'code',
    'h1', 'h2', 'h3', 'h4',
    'ul',
    'ol',
    'li',
    'br',
]

ROOT_URLCONF = 'ogc_search.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'static'),
            os.path.join(BASE_DIR, 'wet', 'templates'),
            os.path.join(BASE_DIR, 'ATI', 'templates'),
            os.path.join(BASE_DIR, 'briefing_notes', 'templates'),
            os.path.join(BASE_DIR, 'grants', 'templates'),
            os.path.join(BASE_DIR, 'national_action_plan', 'templates'),
            os.path.join(BASE_DIR, 'open_data', 'templates'),
            os.path.join(BASE_DIR, 'service_inventory', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ogc_search.wsgi.application'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-1234567-8'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'ogc_search': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
    'ogc_query': {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    },
})

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    ('wxt', os.path.join(BASE_DIR, "themes-dist-GCWeb")),
    ('cdts', os.path.join(BASE_DIR, "cdts", "v4_0_28")),
    ('open_data', os.path.join(BASE_DIR, "open_data", "static")),
    ('ati', os.path.join(BASE_DIR, "ATI", "static")),
    ('bn', os.path.join(BASE_DIR, "briefing_notes", "static")),
    ('gc', os.path.join(BASE_DIR, "grants", "static")),
    ('nap', os.path.join(BASE_DIR, "national_action_plan", "static")),
    ('si', os.path.join(BASE_DIR, "service_inventory", "static")),
]

# Search App Feature Flags

ADMIN_ENABLED = False
ATI_ENABLED = False
BN_ENABLED = False
GC_ENABLE = False
NAP_ENABLED = False
SI_ENABLED = False

# CKAN YAML files from https://github.com/open-data/ckanext-canada/tree/master/ckanext/canada/tables

CKAN_YAML_FILE = os.path.join(BASE_DIR, "ckan", "presets.yaml")
BRIEF_NOTE_YAML_FILE = os.path.join(BASE_DIR, "ckan", "briefingt.yaml")
GRANTS_YAML_FILE = os.path.join(BASE_DIR, "ckan", "grants.yaml")
NAP_YAML_FILE = os.path.join(BASE_DIR, "ckan", "nap.yaml")
SERVICES_YAML_FILE = os.path.join(BASE_DIR, "ckan", "service.yaml")
COUNTRY_JSON_FILE = os.path.join(BASE_DIR, "ckan", "country.json")
CURRENCY_JSON_FILE = os.path.join(BASE_DIR, "ckan", "currency.json")

# Open Data App Settings

OPEN_CANADA_EN_URL_BASE = "https://open.canada.ca/"
OPEN_CANADA_FR_URL_BASE = "https://ouvert.canada.ca/"
OPEN_DATA_EN_URL_BASE = "https://open.canada.ca/data/en/dataset/"
OPEN_DATA_FR_URL_BASE = "https://ouvert.canada.ca/data/fr/dataset/"
OPEN_DATA_EN_FGP_BASE = "https://open.canada.ca/data/en/fgpv_vpgf/"
OPEN_DATA_FR_FGP_BASE = "https://ouvert.canada.ca/data/fr/fgpv_vpgf/"
OPEN_DATA_DATASET_ID = "c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7"
OPEN_DATA_DATASET_TITLE_EN = "Open Data Portal Catalogue Dataset"
OPEN_DATA_DATASET_TITLE_FR = "Catalogue du portail de données ouvertes ensemble de données"
SOLR_URL = 'http://127.0.0.1:8983/solr/core_od_search'

# Briefing Note Title App Settings

BRIEFING_NOTE_DATASET_TITLE_EN = "Briefing Notes Dataest"
BRIEFING_NOTE_DATASET_TITLE_FR = "Note de breffage"
BRIEFING_NOTE_DATASET_ID = "ee9bd7e8-90a5-45db-9287-85c8cf3589b6"
BRIEF_NOTE_INFO_EN = 'A list of briefing note titles prepared for deputy ministers and ministers'
BRIEF_NOTE_INFO_FR = "Listes des notes d'information préparées à l'intention " \
                     "des sous-ministres et ministres"
SOLR_BN = 'http://127.0.0.1:8983/solr/core_bn_search'

# ATI App Settings

ATI_DATASET_TITLE_EN = "Access To Information"
ATI_DATASET_TITLE_FR = "Accès à l'information"
ATI_DATASET_ID = "0797e893-751e-4695-8229-a5066e4fe43c"
ATI_REQUEST_URL_EN = "https://open.canada.ca/search/ati/reference/"
ATI_REQUEST_URL_FR = "https://ouvert.canada.ca/fr/search/ati/reference/"
SOLR_ATI = 'http://127.0.0.1:8983/solr/core_ati_search'

# Grants and Contributions App Settings

SOLR_GC = 'http://127.0.0.1:8983/solr/core_gc_search'

# National Action Plan App Settings

NAP_DATASET_TITLE_EN = 'National Action Plan Dataset'
NAP_DATASET_TITLE_FR = 'Plan d’action national jeu de données'
NAP_DATASET_ID = 'd2d72709-e4bf-412d-a1bd-8c726d19393e'
SOLR_NAP = 'http://127.0.0.1:8983/solr/core_ap_search'

# Service Inventory App Settings

SI_DATASET_TITLE_EN = 'Service Inventory'
SI_DATASET_TITLE_FR = 'Répertoire des services'
SI_DATASET_ID = '3ac0d080-6149-499a-8b06-7ce5f00ec56c'
SI_DATAVIZ_PATH_EN = "/chart/si/index-en.html?"
SI_DATAVIZ_PATH_FR = "/chart/si/index-fr.html?"
SI_ITEMS_PER_PAGE = 25
SI_NOTE_INFO_EN = ''
SI_NOTE_INFO_FR = ''
SOLR_SI = 'http://127.0.0.1:8983/solr/core_sv_search'

EXPORT_FILE_CACHE_DIR = "/tmp"
EXPORT_FILE_CACHE_URL = ""

CDTS_VERSION = 'v4_0_28'

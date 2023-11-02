import logging

INSTALLED_APPS = [
    'huey.contrib.djhuey',
    'djangoex.test_app',
]

HUEY = {
    'name': 'test-django',
    'consumer': {
        'blocking': True,  # Use blocking list pop instead of polling Redis.
        'loglevel': logging.DEBUG,
        'workers': 4,
        'scheduler_interval': 1,
        'simple_log': True,
    },
}

DATABASES = {'default': {
    'NAME': ':memory:',
    'ENGINE': 'django.db.backends.sqlite3'}}

SECRET_KEY = 'foo'

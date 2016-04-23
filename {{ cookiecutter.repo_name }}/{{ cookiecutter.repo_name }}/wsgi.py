"""
WSGI config for {{ cookiecutter.repo_name }} project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
from os.path import abspath, dirname
from sys import path

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

SITE_ROOT = dirname(dirname(abspath(__file__)))
path.append(SITE_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ cookiecutter.repo_name }}.settings")
application = get_wsgi_application()
application = DjangoWhiteNoise(application)

#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Justin Naldzin'
SITENAME = 'Justin Naldzin'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('GitHub', 'https://github.com/justinnaldzin'))

# Social widget
SOCIAL = (('LinkedIn', 'https://www.linkedin.com/in/justinnaldzin'))

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Theme
THEME = "pelican-themes/pelican-bootstrap3"
JINJA_EXTENSIONS = ['jinja2.ext.i18n']
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['i18n_subsites']

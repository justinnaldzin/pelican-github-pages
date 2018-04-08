#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Justin Naldzin'
SITENAME = 'Justin Naldzin'
SITEURL = ''

PATH = 'content'
STATIC_PATHS = ['images', 'documents']

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
#LINKS = (('GitHub', 'https://github.com/justinnaldzin'),)

# Social widget
SOCIAL = (('LinkedIn', 'https://www.linkedin.com/in/justinnaldzin'),
          ('GitHub', 'https://www.github.com/justinnaldzin'),
          ('YouTube', 'https://www.youtube.com/justinnaldzin'),
          ('Facebook', 'https://www.facebook.com/justinnaldzin'),
          ('Twitter', 'https://www.twitter.com/justinnaldzin'),)

# Tags
DISPLAY_TAGS_ON_SIDEBAR = True
DISPLAY_TAGS_INLINE = True
DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Theme
THEME = "pelican-themes/pelican-bootstrap3"
JINJA_EXTENSIONS = ['jinja2.ext.i18n']
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['i18n_subsites', 'jupyter.markup', 'tag_cloud']
BOOTSTRAP_THEME = 'paper'
PYGMENTS_STYLE = 'emacs'
GITHUB_USER = 'justinnaldzin'

# Jupyter
MARKUP = ('md', 'ipynb')
IPYNB_USE_META_SUMMARY = True





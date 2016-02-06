# -*- coding: utf-8 -*-
"""
Simple adapter for Pylons 0.9.7 and greater.
Earlier versions of Pylons should use the Buffet adapter.
"""

from pylons.templating import pylons_globals
from breve import Template
from breve.tags.html import tags


def render(template_name, tmpl_params=None, loader=None, fragment=False):
    if tmpl_params is None:
        tmpl_params = {}

    g = pylons_globals()
    tmpl_params.update(g)

    try:
        opts = g['app_globals'].breve_opts
    except AttributeError:
        opts = {}

    t = Template(tags, **opts)
    return t.render(template_name, params=tmpl_params, loader=loader, fragment=fragment)

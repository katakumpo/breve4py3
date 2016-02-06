# -*- coding: utf-8 -*-
from breve.flatten import flatten
from breve.plugin.helpers import render_decorator
from breve.tags.entities import entities
from breve.tags.html import tags
from breve.tests.lib import expected_output, template_root, test_root


# disabled because maybe bs4 does some things differently but i don't use it anyway
def disabled_test_soup2breve():
    """ round-trip some html """
    import os
    try:
        from breve.tools.soup2breve import convert_file, meta_handler
    except ImportError:
        return
    breve_source = ''.join(
        convert_file(
            os.path.join(test_root(), 'html/index.html'),
            dict(meta=meta_handler)
        )
    )
    code_object = compile(breve_source, 'soup2breve', 'eval')

    _globals = dict(E=entities)
    _globals.update(tags)

    actual = flatten(eval(code_object, _globals))
    expected = open(os.path.join(test_root(), 'html/index.html')).read()
    assert actual == expected


def test_render_decorator():
    """test helpers.render_decorator"""
    @render_decorator('index', root=template_root(), namespace='v')
    def render_test():
        return dict(title='test decorator', message='hello, world')

    actual = render_test()
    expected = expected_output()
    assert actual == expected

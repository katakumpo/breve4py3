# -*- coding: utf-8 -*-
import os
from datetime import datetime

from breve import Template, escape, register_flattener, register_global
from breve.globals import get_stacks, pop, push
from breve.tags.html import tags as html
from breve.tests.lib import expected_output, my_name, template_root


def test_instantiation_parameters():
    """test instantiation parameters"""
    # change the defaults to something else
    args = {
        'tidy': True,
        'debug': True,
        'namespace': 'v',
        'mashup_entities': True,
        'extension': '.breve'
    }
    t = Template(html, root=template_root(), **args)
    actual = [getattr(t, k, 'not_set') for k in sorted(args)]
    expected = [v for k, v in sorted(args.items())]
    assert actual == expected


def test_render_parameters():
    """test render-time parameters"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    args = {
        'tidy': True,
        'debug': True,
        'namespace': 'v',
        'extension': '.breve'
    }
    t = Template(html, root=template_root())
    t.render('index', params, **args)
    actual = [getattr(t, k, 'not_set') for k in sorted(args)]
    expected = [v for k, v in sorted(args.items())]
    assert actual == expected


def test_simple_template():
    """simple template"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_include():
    """include() directive"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_nested_include():
    """nested include() directives"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_loop_include():
    """looping over include() with listcomp"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_assign_scope():
    """test assign directive's scope"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    # don't fail - use variable in scope
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_include_macros():
    """define macros via include() directive"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_nested_include_macros():
    """define macros inside nested include() directives"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_loop_macros():
    """loop using macro"""
    params = dict(
        message='hello, from breve',
        title=my_name(),
        url_data=[
            dict(url='http://www.google.com', label='Google'),
            dict(url='http://www.yahoo.com', label='Yahoo!'),
            dict(url='http://www.amazon.com', label='Amazon')
        ]
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_macro_includes():
    """include() directive inside macro"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_simple_inheritance():
    """simple inheritance"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    _test_name = my_name()
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_nested_inheritance():
    """nested inheritance"""
    params = dict(
        message='hello, from breve',
        title=my_name()
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_macros_inside_inherits():
    """test macros inside inherits(): scope issues"""
    # note: I'm not convinced this is the desired behaviour, but
    # it's *compatible* behaviour.
    params = dict(
        title=my_name(),
        message='Hello, from breve'
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_register_global():
    """register_global() function"""
    params = dict(
        title=my_name()
    )
    register_global('global_message', 'This is a global variable')

    _test_name = my_name()
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_stacks():
    """test stacks (push/pop)"""
    push(a=1, b=2)
    assert pop('a') == 1
    assert pop('b') == 2


def test_stacks_template():
    """test stacks in template"""
    params = dict(
        title=my_name(),
        message='hello, from breve'
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected
    # stack should be empty when we finish
    assert not get_stacks()


def test_register_flattener():
    """register_flattener() function"""
    def flatten_date(o):
        return escape(o.strftime('%Y/%m/%d'))
    register_flattener(datetime, flatten_date)
    register_global('flatten_date', flatten_date)

    params = dict(
        title=my_name(),
        today=datetime(2008, 4, 17)
    )
    _test_name = my_name()
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_custom_renderer():
    """custom renderer"""
    def render_row(tag, data):
        T = html
        tag.clear()
        return tag[
            [T.td[_i] for _i in data]
        ]
    register_global('render_row', render_row)

    params = dict(
        title=my_name(),
        my_data=[
            range(5),
            range(5, 10),
            range(10, 15)
        ]
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_custom_renderer_notag():
    """custom renderer returning non-Tag type"""
    def render_text(tag, data):
        tag.clear()
        return data
    register_global('render_text', render_text)

    params = dict(
        title=my_name(),
        message='hello, world'
    )
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_custom_loader():
    """custom loader"""
    class PathLoader(object):
        __slots__ = ['paths']

        def __init__(self, *paths):
            self.paths = paths

        def stat(self, template, root):
            for p in self.paths:
                f = os.path.join(root, p, template)
                if os.path.isfile(f):
                    timestamp = int(os.stat(f).st_mtime)
                    uid = f
                    return uid, timestamp
            raise OSError('No such file or directory %s' % template)

        def load(self, uid):
            return open(uid, 'U').read()

    loader = PathLoader(
        template_root(),
        os.path.join(template_root(), 'path1'),
        os.path.join(template_root(), 'path2'),
        os.path.join(template_root(), 'path3'),
    )

    params = dict(
        title=my_name(),
        message='hello, world'
    )
    _test_name = my_name()
    t = Template(html)  # note we're not setting root
    actual = t.render('index', params, namespace='v', loader=loader)
    expected = expected_output()
    assert actual == expected


def test_custom_loader_stack():
    """custom loader stack"""
    class PathLoader(object):
        __slots__ = ['paths']

        def __init__(self, *paths):
            self.paths = paths

        def stat(self, template, root):
            for p in self.paths:
                f = os.path.join(root, p, template)
                if os.path.isfile(f):
                    timestamp = int(os.stat(f).st_mtime)
                    uid = f
                    return uid, timestamp
            raise OSError('No such file or directory %s' % template)

        def load(self, uid):
            return open(uid, 'U').read()

    loader = PathLoader(
        template_root(),
        os.path.join(template_root(), 'path1'),
        os.path.join(template_root(), 'path2'),
        os.path.join(template_root(), 'path3'),
    )
    register_global('path_loader', loader)

    params = dict(
        title=my_name(),
        message='hello, world'
    )
    _test_name = my_name()
    t = Template(html, root=template_root())
    actual = t.render('index', params, namespace='v')
    expected = expected_output()
    assert actual == expected


def test_encoding():
    """encoding comments"""
    params = dict(
        title=my_name()
    )
    t = Template(html, root=template_root())
    expected = expected_output()
    actual = t.render('correct', params, namespace='v')
    assert actual == expected
    # maybe not needed anymore with common utf8 handling in python 3..dunno
    # actual = t.render('wrong', params, namespace='v')
    # assert actual != expected

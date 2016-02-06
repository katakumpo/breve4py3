# -*- coding: utf-8 -*-
import unittest

from breve.flatten import flatten
from breve.tags import AutoTag, Tag, assign, check, let, macro, xml
from breve.tags.entities import entities as E
from breve.tags.html import tags
from breve.tests.lib import my_name
from breve.util import Namespace


class SerializationTestCase(unittest.TestCase):

    def test_tag_serialization(self):
        """basic tag flattening"""

        T = tags
        template = T.html[
            T.head[T.title[my_name()]],
            T.body[T.div['okay']]
        ]
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_tag_serialization</title></head>'
             '<body><div>okay</div></body></html>')
        )

    def test_inlineJS(self):
        """inline Javascript flattening"""

        js = """
            if (x=1) {
                y=2;
            }
        """
        T = tags
        template = T.html[
            T.body[
                T.inlineJS(js)
            ]
        ]
        output = flatten(template)
        self.assertEqual(
            output,
            '<html><body>\n<script type="text/javascript">\n//<![CDATA[\n%s\n//]]></script>\n</body></html>' % js
        )

    def test_minJS(self):
        """inline minified Javascript flattening"""

        js = """
            if (x=1) {
                y=2;
            }
        """
        T = tags
        template = T.html[
            T.body[
                T.minJS(js)
            ]
        ]
        output = flatten(template)
        self.assertEqual(
            output,
            '<html><body>\n<script type="text/javascript">\n//<![CDATA[\nif(x=1){y=2;}\n//]]></script>\n</body></html>'
        )

    def test_unicode(self):
        """unicode and string coercion"""

        T = tags
        template = T.html[
            T.head[T.title[my_name()]],
            T.body[
                b'Brev\xc3\xa9 converts plain strings', T.br,
                'Brev\xe9 handles unicode strings', T.br,
                T.div["äåå? ▸ ", T.em["я не понимаю"], "▸ 3 km²"]
            ]
        ]
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_unicode</title></head>'
             '<body>Brevé converts plain strings<br />'
             'Brevé handles unicode strings<br />'
             '<div>äåå? ▸ <em>я не понимаю</em>▸ 3 km²</div></body></html>')
        )

    def test_unicode_attributes(self):
        """unicode and string coercion in attributes"""

        T = tags
        template = T.html[
            T.head[T.title[my_name()]],
            T.body[
                T.span(id='удерживать')["Coerce byte string to Unicode"],
                T.span(id='не оставляющий сомнений')["Explicit Unicode object"]
            ]
        ]
        output = flatten(template)

        self.assertEqual(
            output,
            ('<html><head><title>test_unicode_attributes</title></head><body>'
             '<span id="удерживать">Coerce byte string to Unicode</span>'
             '<span id="не оставляющий сомнений">Explicit Unicode object</span></body></html>')
        )

    def test_test(self):
        """test() function"""

        T = tags
        template = T.html[
            T.head[T.title[my_name()]],
            T.body[
                check(1 == 1) and (
                    T.span['This is displayed']
                ),
                check(1 == 0) and (
                    T.span['This is not displayed']
                )
            ]
        ]
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_test</title></head>'
             '<body><span>This is displayed</span></body></html>')
        )

    def test_escaping(self):
        """escaping, xml() directive"""

        T = tags
        template = T.html[
            T.head[T.title[my_name()]],
            T.body[
                T.div(style='width: 400px;<should be &escaped&>')[
                    T.p(class_='foo')['&&&'],
                    T.p['Coffee', E.nbsp, E.amp, E.nbsp, 'cream'],
                    xml ("""<div>this should be <u>unescaped</u> &amp; unaltered.</div>""")
                ]
            ]
        ]
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_escaping</title></head>'
             '<body><div style="width: 400px;&lt;should be &amp;escaped&amp;&gt;">'
             '<p class="foo">&amp;&amp;&amp;</p><p>Coffee&#160;&#38;&#160;cream</p>'
             '<div>this should be <u>unescaped</u> &amp; unaltered.</div></div></body></html>')
        )

    def test_tag_multiplication(self):
        """tag multiplication"""

        T = tags
        url_data = [
            dict(url='http://www.google.com', label='Google'),
            dict(url='http://www.yahoo.com', label='Yahoo!'),
            dict(url='http://www.amazon.com', label='Amazon')
        ]

        template = T.html[
            T.head[T.title[my_name()]],
            T.body[
                T.ul[
                    T.li[T.a(href="$url")["$label"]] * url_data
                ]
            ]
        ]
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_tag_multiplication</title></head>'
             '<body><ul><li><a href="http://www.google.com">Google</a></li>'
             '<li><a href="http://www.yahoo.com">Yahoo!</a></li>'
             '<li><a href="http://www.amazon.com">Amazon</a></li></ul></body></html>')
        )

    def test_flatten_callable(self):
        """test flattening of callables"""

        def my_callable():
            return "Hello, World"

        T = tags
        template = (
            T.html[
                T.head[T.title[my_name()]],
                T.body[
                    T.div[my_callable]
                ]
            ]
        )
        actual = flatten(template)
        self.assertEqual(
            actual,
            ('<html><head><title>test_flatten_callable</title></head>'
             '<body><div>Hello, World</div></body></html>')
        )


class MacrosTestCase(unittest.TestCase):

    def test_macros(self):
        """test macros"""

        T = tags
        url_data = [
            {'url': 'http://www.google.com', 'label': 'Google'},
            {'url': 'http://www.yahoo.com', 'label': 'Yahoo!'},
            {'url': 'http://www.amazon.com', 'label': 'Amazon'}
        ]

        template = (
            macro('test_macro', lambda url, label:
                  T.a(href=url)[label]
                  ),
            T.html[
                T.head[T.title[my_name()]],
                T.body[
                    T.ul[
                        [T.li[test_macro(**_item)]  # @UndefinedVariable
                         for _item in url_data]
                    ]
                ]
            ]
        )
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_macros</title></head>'
             '<body><ul><li><a href="http://www.google.com">Google</a></li>'
             '<li><a href="http://www.yahoo.com">Yahoo!</a></li>'
             '<li><a href="http://www.amazon.com">Amazon</a></li></ul></body></html>')
        )

    def test_nested_macros(self):
        """test nested macros"""

        T = tags
        url_data = [
            {'url': 'http://www.google.com', 'label': 'Google'},
            {'url': 'http://www.yahoo.com', 'label': 'Yahoo!'},
            {'url': 'http://www.amazon.com', 'label': 'Amazon'}
        ]

        template = (
            macro('list_macro', lambda url, label: (
                macro('link_macro', lambda _u, _l:
                      T.a(href=_u)[_l]
                      ),
                T.li[link_macro(url, label)]  # @UndefinedVariable
            )),
            T.html[
                T.head[T.title[my_name()]],
                T.body[
                    T.ul[
                        [list_macro(**_item)  # @UndefinedVariable
                         for _item in url_data]
                    ]
                ]
            ]
        )
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_nested_macros</title></head>'
             '<body><ul><li><a href="http://www.google.com">Google</a></li>'
             '<li><a href="http://www.yahoo.com">Yahoo!</a></li>'
             '<li><a href="http://www.amazon.com">Amazon</a></li></ul></body></html>')
        )

    def test_tag_multiplication_with_macro(self):
        """tag multiplication including macro"""

        T = tags
        url_data = [
            {'url': 'http://www.google.com', 'label': 'Google', 'class': 'link'},
            {'url': 'http://www.yahoo.com', 'label': 'Yahoo!', 'class': 'link'},
            {'url': 'http://www.amazon.com', 'label': 'Amazon', 'class': 'link'}
        ]

        template = (
            macro('test_macro', lambda url:
                  T.a(href=url)["$label"]
                  ),
            T.html[
                T.head[T.title[my_name()]],
                T.body[
                    T.ul[
                        T.li(class_="$class")[test_macro("$url")] * url_data  # @UndefinedVariable
                    ]
                ]
            ]
        )
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_tag_multiplication_with_macro</title></head>'
             '<body><ul><li class="link"><a href="http://www.google.com">Google</a></li>'
             '<li class="link"><a href="http://www.yahoo.com">Yahoo!</a></li>'
             '<li class="link"><a href="http://www.amazon.com">Amazon</a></li></ul></body></html>')
        )

    def test_let(self):
        """let directive"""

        T = tags
        template = (
            let(msg='okay'),
            T.html[
                T.head[T.title[my_name()]],
                T.body[T.div[msg]]  # @UndefinedVariable
            ]
        )
        output = flatten(template)
        self.assertEqual(
            output,
            '<html><head><title>test_let</title></head><body><div>okay</div></body></html>'
        )

    def test_assign(self):
        """assign directive"""

        T = tags
        template = (
            assign('msg', 'okay'),
            T.html[
                T.head[T.title[my_name()]],
                T.body[T.div[msg]]  # @UndefinedVariable
            ]
        )
        output = flatten(template)
        self.assertEqual(
            output,
            '<html><head><title>test_assign</title></head><body><div>okay</div></body></html>'
        )

    def test_assign_with_macro(self):
        """assign directive with macro"""

        T = tags
        template = (
            assign('msg', 'okay'),
            macro('display_msg', lambda _m:
                  T.span[_m]
                  ),
            T.html[
                T.head[T.title[my_name()]],
                T.body[T.div[display_msg(msg)]]  # @UndefinedVariable
            ]
        )
        output = flatten(template)
        self.assertEqual(
            output,
            ('<html><head><title>test_assign_with_macro</title></head>'
             '<body><div><span>okay</span></div></body></html>')
        )


class DOMTestCase(unittest.TestCase):

    def test_dom_traversal(self):
        """tag.walk() DOM traversal"""

        T = tags
        template = T.html[
            T.head[T.title[my_name()]],
            T.body[T.div['okay']]
        ]

        traversal = []

        def callback(item, is_tag):
            if is_tag:
                traversal.append(item.name)
            else:
                traversal.append(item)

        template.walk(callback)
        output = ''.join(traversal)
        self.assertEqual(
            output,
            'htmlheadtitle%sbodydivokay' % my_name(),
        )

    def test_dom_traversal_from_macro(self):
        """macro abuse: self-traversing template"""

        T = tags
        template = (
            assign('selectors', []),
            macro('css_sep', lambda attr:
                  attr == 'class' and '.' or '#'
                  ),
            macro('get_selectors', lambda tag, is_tag:
                  selectors.extend([  # @UndefinedVariable
                      "%s%s%s { }" % (tag.name, css_sep(_k.strip('_')), _v)  # @UndefinedVariable
                      for _k, _v in tag.attrs.items()
                      if _k.strip('_') in ('id', 'class')
                  ])
                  ),
            macro('extract_css', lambda tag:
                  tag.walk(get_selectors, True) and tag  # @UndefinedVariable
                  ),
            macro('css_results', lambda selectors:
                  T.pre['\n'.join(selectors)]
                  ),

            T.html[
                T.head[T.title['macro madness']],
                T.body[extract_css(# @UndefinedVariable
                    T.div('class', 'text', 'id', 'main-content')[
                        T.img('src', '/images/breve-logo.png', 'alt', 'breve logo'),
                        T.br,
                        T.span (class_='bold') [ """Hello from Breve!""" ]
                    ]
                ), css_results(selectors)]  # @UndefinedVariable
            ]

        )
        output = flatten(template)

        self.assertEqual(
            output,
            ('<html><head><title>macro madness</title></head>'
             '<body><div class="text" id="main-content">'
             '<img src="/images/breve-logo.png" alt="breve logo"></img>'
             '<br /><span class="bold">Hello from Breve!</span></div>'
             '<pre>div.text { }\ndiv#main-content { }\nspan.bold { }</pre>'
             '</body></html>')
        )


class CustomTagsTestCase(unittest.TestCase):

    def test_custom_tags(self):
        """custom tags"""

        from breve.tests.sitemap import tags, xmlns  # @Reimport
        T = Namespace(tags)

        # test data
        loc = 'http://www.example.com/',
        lastmod = '2008-01-01',
        changefreq = 'monthly',
        priority = 0.8

        template = T.urlset(xmlns=xmlns)[
            T.url[
                T.loc[loc],
                T.lastmod[lastmod],
                T.changefreq[changefreq],
                T.priority[priority]
            ]
        ]
        output = flatten(template)

        self.assertEqual(
            output,
            ('<urlset xmlns="http://www.google.com/schemas/sitemap/0.84/sitemap.xsd">'
             '<url><loc>http://www.example.com/</loc><lastmod>2008-01-01</lastmod>'
             '<changefreq>monthly</changefreq><priority>0.8</priority></url></urlset>')
        )

    def test_dynamic_tags(self):
        """test dynamic creation of tags"""

        template = (
            assign('mytag', Tag('mytag')),
            mytag(feature='foo')[  # @UndefinedVariable
                'hello, from mytag',
                Tag('explicit')(feature='bar')[
                    'hello from explicit tag'
                ]
            ]
        )
        actual = flatten(template)
        self.assertEqual(
            actual,
            '<mytag feature="foo">hello, from mytag<explicit feature="bar">hello from explicit tag</explicit></mytag>'
        )

    def test_auto_tags(self):
        """test AutoTag class"""

        T = AutoTag()
        template = (
            T.foo(attr='foo')[
                T.bar(attr='bar'),
                T.baz(attr='baz')
            ]
        )
        actual = flatten(template)
        self.assertEqual(
            actual,
            '<foo attr="foo"><bar attr="bar"></bar><baz attr="baz"></baz></foo>'
        )


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(SerializationTestCase, 'test'))
    suite.addTest(unittest.makeSuite(MacrosTestCase, 'test'))
    suite.addTest(unittest.makeSuite(DOMTestCase, 'test'))
    suite.addTest(unittest.makeSuite(CustomTagsTestCase, 'test'))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

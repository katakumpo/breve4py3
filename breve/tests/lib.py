# -*- coding: utf-8 -*-
import os
import sys


def my_name():
    return sys._getframe(1).f_code.co_name


def callers_name():
    return sys._getframe(2).f_code.co_name


def caller():
    return sys._getframe(2)


def test_root():
    return os.path.abspath(os.path.dirname(__file__))


def template_root():
    return os.path.join(test_root(), 'templates', callers_name())


def expected_output():
    return open(os.path.join(test_root(), 'output', '%s.html' % callers_name())).read().strip()

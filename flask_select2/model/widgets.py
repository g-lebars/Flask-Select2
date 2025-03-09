# coding: utf-8
__author__ = 'Paul Cunningham'
__copyright = 'Copyright 2017, Paul Cunningham'

from flask import url_for, json
from flask_select2._compat import as_unicode
from wtforms.widgets import html_params
from markupsafe import Markup
from sqlalchemy import inspect


class AjaxSelect2Widget(object):
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', 'select2-ajax')
        kwargs.setdefault('data-url', url_for('select2.ajax', name=field.loader.name))

        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'

        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', 'hidden')

        if self.multiple:
            result = []
            ids = []

            for value in field.data:
                data = field.loader.format(value)
                result.append(data)
                ids.append(as_unicode(data[0]))

            separator = getattr(field, 'separator', ',')

            kwargs['value'] = separator.join(ids)
            kwargs['data-json'] = json.dumps(result)
            kwargs['data-multiple'] = u'1'
        else:
            data = field.loader.format(field.data)

            if data:
                kwargs['value'] = data[0]
                kwargs['data-json'] = json.dumps(data)

        placeholder = field.loader.options.get('placeholder', 'Please select model')
        kwargs.setdefault('data-placeholder', placeholder)

        return Markup('<input %s>' % html_params(name=field.name, **kwargs))
    
class AjaxTagsSelect2Widget(object):
    def __init__(self, multiple=False, autocreate=True):
        self.multiple = multiple
        self.autocreate= autocreate

    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', 'select2-ajax')
        kwargs.setdefault('data-url', url_for('select2.ajax', name=field.loader.name))

        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'
        if self.autocreate:
            kwargs['data-allow-tags'] = u'1'
        else:
            kwargs['data-allow-tags'] = u'0'

        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', 'hidden')

        if self.multiple:
            result = []
            ids = []

            for value in field.data:
                data = field.loader.format(value)
                if not inspect(value).persistent:
                    result.append(data)
                    ids.append(data[1])
                else:
                    result.append(data)
                    ids.append(as_unicode(data[0]))

            separator = getattr(field, 'separator', ';')

            kwargs['value'] = separator.join(ids)
            kwargs['data-json'] = json.dumps(result)
            kwargs['data-multiple'] = u'1'
            #kwargs['data-token-separators']=separator
        else:
            if field.data:
                if not self.multiple:
                    data = field.loader.format(field.data)
                else:
                    data = field.loader.format(field.data[0])

                if data:
                    kwargs['value'] = data[0]
                    kwargs['data-json'] = json.dumps(data)
            kwargs['data-multiple'] = u'0'
            kwargs['multiple'] = False

        placeholder = field.loader.options.get('placeholder', 'Please select model')
        kwargs.setdefault('data-placeholder', placeholder)
        return Markup(u'<input %s>' % html_params(name=field.name, **kwargs))
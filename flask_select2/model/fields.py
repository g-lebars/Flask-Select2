# coding: utf-8
__author__ = 'Paul Cunningham'
__copyright = 'Copyright 2017, Paul Cunningham'

from wtforms import SelectFieldBase, ValidationError
from .widgets import AjaxSelect2Widget, AjaxTagsSelect2Widget
from sqlalchemy import or_


class AjaxSelectField(SelectFieldBase):
    """
        Ajax Model Select Field
    """
    widget = AjaxSelect2Widget()

    separator = ','

    def __init__(self, loader, label=None, validators=None, allow_blank=False, blank_text=u'', **kwargs):
        super(AjaxSelectField, self).__init__(label, validators, **kwargs)
        self.loader = loader

        self.allow_blank = allow_blank
        self.blank_text = blank_text

    def _get_data(self):
        if self._formdata:
            model = self.loader.get_one(self._formdata)

            if model is not None:
                self._set_data(model)

        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def _format_item(self, item):
        value = self.loader.format(self.data)
        return (value[0], value[1], True)

    def process_formdata(self, valuelist):
        if valuelist:
            if self.allow_blank and valuelist[0] == u'__None':
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]

    def pre_validate(self, form):
        if not self.allow_blank and self.data is None:
            raise ValidationError(self.gettext(u'Not a valid choice'))


class AjaxSelectMultipleField(AjaxSelectField):
    """
        Ajax-enabled model multi-select field.
    """
    widget = AjaxSelect2Widget(multiple=True)

    def __init__(self, loader, label=None, validators=None, default=None, **kwargs):
        if default is None:
            default = []

        super(AjaxSelectMultipleField, self).__init__(loader, label, validators, default=default, **kwargs)
        self._invalid_formdata = False

    def _get_data(self):
        formdata = self._formdata
        if formdata:
            data = []

            # TODO: Optimize?
            for item in formdata:
                model = self.loader.get_one(item) if item else None

                if model:
                    data.append(model)
                else:
                    self._invalid_formdata = True

            self._set_data(data)

        return self._data

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def process_formdata(self, valuelist):
        self._formdata = set()

        for field in valuelist:
            for n in field.split(self.separator):
                self._formdata.add(n)

    def pre_validate(self, form):
        if self._invalid_formdata:
            raise ValidationError(self.gettext(u'Not a valid choice'))
        
class AjaxTagsSelectField(AjaxSelectField):
    """
        Ajax-enabled model multi-select field with Tags.
    """
    #widget = AjaxTagsSelect2Widget(multiple=False)

    def __init__(self, loader, multiple=False, autocreate=True, label=None, validators=None, default=None, **kwargs):
        if default is None:
            default = []

        self.multiple=multiple
        self.autocreate=autocreate
        self.widget=AjaxTagsSelect2Widget(multiple=multiple, autocreate=autocreate)
        super(AjaxTagsSelectField, self).__init__(loader, label, validators, default=default, **kwargs)
        self._invalid_formdata = False

    def _get_data(self):
        formdata = self._formdata
        if formdata:
            data = []

            # TODO: Optimize?
            for item in formdata:
                model_item=None
                if item.isnumeric():
                    model_item = self.loader.get_one(item) if item else None
                if model_item:
                    data.append(model_item)
                elif self.autocreate and item:
                    filters = (field.ilike("%{}%".format(item)) for field in self.loader._cached_fields)
                    query=self.loader.get_query()
                    with self.loader.session.no_autoflush:
                        model = query.filter(or_(*filters)).first()
                    if not model:
                        model=self.loader.model()
                        setattr(model,self.loader.fields[0],item)
                        self.loader.session.add(model)
                    data.append(model)

            self._set_data(data)
        

        return self._data

    def _set_data(self, data):
        if data:
            if not isinstance(data, list):
                data=[data]
            if not self.multiple:
                data=data[0]
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def process_formdata(self, valuelist):
        self._formdata = set()

        for field in valuelist:
            for n in field.split(self.separator):
                self._formdata.add(n)

    def pre_validate(self, form):
        if not self.allow_blank and not self.data :
            raise ValidationError(self.gettext(u'Not a valid choice'))
        if self._invalid_formdata:
            raise ValidationError(self.gettext(u'Not a valid choice'))
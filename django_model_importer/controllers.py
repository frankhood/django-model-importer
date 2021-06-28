from __future__ import absolute_import, print_function, unicode_literals

import logging
from pathlib import Path

from dateutil.parser import parse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.db.models import fields
from django.utils.translation import ugettext_lazy as _

try:
    from django_countries import countries as COUNTRY_CHOICES
    from django_countries.fields import Country, CountryField
except ImportError as ex:
    Country = CountryField = None
    COUNTRY_CHOICES = []
import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class PandasCSVImporter(object):
    delimiter = ";"
    quotechar = '"'
    # escapechar = '\\'
    expected_cols = 1
    logger = logger
    from_row = 1

    def __init__(self, **kwargs):
        self.delimiter = kwargs.get('delimiter', self.delimiter)
        self.logger = kwargs.get('logger', self.logger)

    # def import_csv(self, file_path, **kwargs):
    #     logger.debug("importing csv {0}".format(file_path))
    #     data_frame = pd.read_csv(
    #         file_path, delimiter=self.delimiter, sep=self.quotechar,
    #         dtype=str, na_values=["", "NULL", "NaN", "n/a", "nan", "null"],
    #         keep_default_na=False)
    #     data_dict = data_frame.replace({np.nan:None}).to_dict('records')
    #     # data_dict = data_frame.to_dict('records')
    #
    #     imported_number = error_number = 0
    #     for row_number, row in enumerate(data_dict):
    #         if self._import_row(row, row_number+1, **kwargs):
    #             imported_number += 1
    #         else:
    #             error_number += 1
    #     self.logger.info(_("Imported CSV of {0} rows of which {1} were not processed"
    #                        "".format(len(data_dict),error_number)))
    #     return {'rows': len(data_dict), 'imported': imported_number, 'errors': error_number}

    def get_rows_as_data_frame(self, file_path, sheet_name=0):
        file_extension = Path(file_path).suffix[1:].lower()
        if file_extension in ["xls", "xlsx"]:
            return pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                dtype=str,
                na_values=[
                    "-1.#IND", "1.#QNAN", "1.#IND", "-1.#QNAN",
                    "#N/A N/A", "#N/A", "N/A", "n/a",
                    # "NA", 'ND',
                    "#NA", "NULL", "null", "NaN", "-NaN", "nan", "-nan",
                    "", '-', '#N/D', 'nd',
                ],
                keep_default_na=False
            )
        elif file_extension == "csv":
            return pd.read_csv(
                file_path, delimiter=self.delimiter, sep=self.quotechar,
                dtype=str, na_values=[
                    "-1.#IND", "1.#QNAN", "1.#IND", "-1.#QNAN",
                    "#N/A N/A", "#N/A", "N/A", "n/a",
                    # "NA", 'ND',
                    "#NA", "NULL", "null", "NaN", "-NaN", "nan", "-nan",
                    "", '-', '#N/D', 'nd',
                ],
                keep_default_na=False)
        else:
            raise NotImplementedError(f"get_rows_as_data_frame is not implemented yet "
                                      f"for file extension '{file_extension}'")

    def get_data_frame_as_dict(self, data_frame):
        # data_frame.columns = [self.db_mapping.get(column_name, column_name) for column_name in data_frame.columns]
        logger.info(f"data_frame : \n {data_frame}")
        data_dict = data_frame.replace({np.nan: ""}).to_dict('records')
        return data_dict

    def validate_columns(self, columns):
        """ Use this method to validate file structure"""
        logger.debug("Columns : {}".format(columns))

    def import_csv(self, file_path, **kwargs):
        logger.debug("importing csv {0}".format(file_path))
        data_frame = self.get_rows_as_data_frame(file_path,
                                                 sheet_name=kwargs.pop("sheet_name", 0) or 0)
        self.validate_columns(list(data_frame.columns))
        data_dict = self.get_data_frame_as_dict(data_frame)
        imported_number = error_number = 0
        for row_number, row in enumerate(data_dict):
            if self._import_row(row, row_number=row_number + 1, **kwargs):
                imported_number += 1
            else:
                error_number += 1
        self.logger.info(_("Imported CSV of {0} rows of which {1} were not processed"
                           "".format(len(data_dict), error_number)))
        return {'rows': len(data_dict), 'imported': imported_number, 'errors': error_number}

    def _import_row(self, row, row_number, **kwargs):
        callback = kwargs.get('callback', None)
        kwargs = kwargs or {}
        kwargs.update({'items': row})
        if callback and hasattr(self, callback):
            return getattr(self, callback)(**kwargs)
        else:
            return self.process_row(**kwargs)

    def process_row(self, **kwargs):
        raise NotImplementedError()


class BaseModelCSVImporter(PandasCSVImporter):
    model = None
    can_update = True
    can_create = True

    db_mapping = {
        # "Name":"name",
        # ...
    }

    def process_row(self, **kwargs):
        obj = self.model()
        _columns = kwargs.get('items')
        for key, value in _columns.iteritems():
            model_field = self.db_mapping.get(key)
            if model_field:
                setattr(obj, model_field, value)
        obj.save()


class ModelCSVImporter(BaseModelCSVImporter):
    model = None

    can_add_fk = True
    can_add_m2m = True

    m2m_separator = '|'

    db_mapping = {
        # "Name": "name",
        # ...
    }

    def get_model_field_name(self, csv_string):
        field = self.db_mapping.get(csv_string, csv_string) or csv_string
        return field.split('.')[0]

    def get_model_related_field_name(self, csv_string):
        field = self.db_mapping.get(csv_string, csv_string) or csv_string
        return field.split('.')[1] if len(field.split('.')) > 1 else field

    def get_import_id(self, columns):
        return columns[self.get_import_id_column_index()]

    def get_import_id_column_index(self):
        raise ImproperlyConfigured("Import ID not specified")

    def get_import_id_field_name(self):
        raise ImproperlyConfigured("Import ID Field Name not specified")

    def can_add_fk_object(self, fk_model):
        return self.can_add_fk

    def can_add_m2m_object(self, m2m_model, value=""):
        return self.can_add_m2m

    def get_m2m_object(self, m2m_model, m2m_field_name, m2m_field_value):
        return m2m_model.objects.get(**({m2m_field_name: m2m_field_value}))

    def create_m2m_object(self, m2m_model, m2m_field_name, m2m_field_value):
        return m2m_model.objects.create(**({m2m_field_name: m2m_field_value}))

    def set_model_attr(self, obj, _field_name, value):
        setattr(obj, _field_name, value)

    def process_date_field(self, obj, _field_name, value):
        setattr(obj, _field_name, parse(value).date())

    def process_time_field(self, obj, _field_name, value):
        setattr(obj, _field_name, parse(value).time())

    def process_datetime_field(self, obj, _field_name, value):
        setattr(obj, _field_name, parse(value))

    def process_fk_field(self, obj, _field_name, _column_name, value):
        fk_model = getattr(obj.__class__, _field_name).field.remote_field.related_model
        fk_name = self.get_model_related_field_name(_column_name)
        try:
            setattr(obj, _field_name, fk_model.objects.get(**({fk_name: value})))
        except ObjectDoesNotExist:
            if self.can_add_fk_object(fk_model):
                fk_obj = fk_model.objects.create(**({fk_name: int(value)}))
                setattr(obj, _field_name, fk_obj)

    def process_m2m_field(self, obj, _field_name, _column_name, value, _columns):
        m2m_map = {}
        if getattr(obj.__class__, _field_name).field.related_model:
            m2m_model = getattr(obj.__class__, _field_name).field.related_model
        elif getattr(obj.__class__, _field_name).field.remote_field.related_model:
            m2m_model = getattr(obj.__class__, _field_name).field.remote_field.related_model
        m2m_name = self.get_model_related_field_name(_column_name)
        print("m2m_model : {m2m_model}\nm2m_name : {m2m_name}\n".format(m2m_model=m2m_model,
                                                                        m2m_name=m2m_name))
        m2m_objs = []
        for _value in value.split(self.m2m_separator):
            _value = _value.strip()
            print("_value for model {model} : {value}".format(value=_value, model=m2m_model))
            try:
                m2m_obj = self.get_m2m_object(
                    m2m_model=m2m_model,
                    m2m_field_name=m2m_name,
                    m2m_field_value=_value
                )
            except ObjectDoesNotExist:
                if self.can_add_m2m_object(m2m_model, value=_value):
                    m2m_obj = self.create_m2m_object(
                        m2m_model=m2m_model,
                        m2m_field_name=m2m_name,
                        m2m_field_value=_value
                    )
                else:
                    m2m_obj = None
            if m2m_obj:
                m2m_objs.append(m2m_obj)
        if m2m_objs:
            m2m_map.update({_field_name: m2m_objs})
            # obj.save()
            # getattr(obj,_field_name).add(m2m_obj)
        return m2m_map

    def process_django_countries_field(self, obj, _field_name, value):
        _country_found = False
        if value == "China (PR)":
            value = "China"
        elif value == "USA":
            value = "United States of America"
        elif value == "Viet Nam":
            value = "Vietnam"
        elif value in ["Korea (Republic)", "Korea (the Republic of)"]:
            value = "North Korea"
        for _country_choice in COUNTRY_CHOICES:
            if _country_choice[1] == value:
                setattr(obj, _field_name, _country_choice[0])
                _country_found = True
        if not _country_found:
            logger.warning(
                "Not Found any Country with name {country_name} for entry {entry}".format(
                    country_name=value, entry=obj))

    def process_row(self, **kwargs):
        m2m_map = {}
        _columns = kwargs.get('items')
        import_id = self.get_import_id(_columns)
        import_id_field_name = self.get_import_id_field_name()
        _is_creation = True
        if import_id and import_id_field_name:
            try:
                obj = self.model.objects.get(**{import_id_field_name: import_id})
                _is_creation = False
                if self.can_update:
                    logger.info("Updating Model with id %s" % (import_id,))
            except ObjectDoesNotExist:
                obj = self.model()
                if self.can_create:
                    logger.info("Importing Model with id %s" % (import_id,))
                    # if isinstance(obj._meta.get_field(import_id_field_name), fields.related.ManyToManyField):
                    #     obj._meta.get_field(import_id_field_name).set(import_id)
                    # else:
                    setattr(obj, import_id_field_name, import_id)
        else:
            obj = self.model()

        if (_is_creation and self.can_create) or (not _is_creation and self.can_update):
            for key, value in _columns.items():
                _column_name = key
                if value is not None and value != 'NULL' and value != '':
                    if (
                        hasattr(obj.__class__, self.get_model_field_name(_column_name))
                        or hasattr(obj, self.get_model_field_name(_column_name))
                    ):
                        _field_name = self.get_model_field_name(_column_name)
                        model_field = obj._meta.get_field(_field_name)
                        logger.info("Setting attr %s with value %s" % (_field_name, value))
                        if isinstance(model_field, fields.DateField):
                            self.process_date_field(obj, _field_name, value)
                        elif isinstance(model_field, fields.TimeField):
                            self.process_time_field(obj, _field_name, value)
                        elif isinstance(model_field, fields.DateTimeField):
                            self.process_datetime_field(obj, _field_name, value)
                        elif isinstance(model_field, fields.related.ForeignKey):
                            self.process_fk_field(obj, _field_name, _column_name, value)
                        elif isinstance(model_field, fields.related.ManyToManyField):
                            new_m2m_map = self.process_m2m_field(obj, _field_name, _column_name, value, _columns)
                            if new_m2m_map:
                                m2m_map.update(new_m2m_map)
                        elif "django_countries" in settings.INSTALLED_APPS and isinstance(model_field, CountryField):
                            self.process_django_countries_field(obj, _field_name, value)
                        else:
                            self.set_model_attr(obj, _field_name, value)
                    else:
                        pass
                        # logger.warning("The model {model} has no field {field}".format(model=self.model,field=self.get_model_field_name(_column_name)))
            # print("Saving obj {title}.... with start_date:{start_date}".format(title=obj.title,start_date=obj.start_date))
            obj.save()
            if m2m_map:
                for _field_name, m2m_objs in m2m_map.items():
                    for m2m_obj in m2m_objs:
                        # print("Saving m2m wiht field_name = {_field_name} and instance {m2m_obj}".format(_field_name=_field_name,m2m_obj=m2m_obj))
                        getattr(obj, _field_name).add(m2m_obj)
        return obj
        # obj.save_m2m()

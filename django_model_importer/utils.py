import codecs
import csv
import logging
from io import StringIO

from django.utils.translation import gettext as _
from numpy import unicode

logger = logging.getLogger("django-model-importer")


# These classes are copied from http://docs.python.org/2/library/csv.html


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data), dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, "utf-8") for cell in row]


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode("utf-8")


class CsvUnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def cast_to_str(self, obj):
        if isinstance(obj, unicode):
            return obj.encode("utf-8")
        elif isinstance(obj, str):
            return obj
        elif hasattr(obj, "__unicode__"):
            return unicode(obj).encode("utf-8")
        elif hasattr(obj, "__str__"):
            return str(obj)
        else:
            raise TypeError(
                "Expecting unicode, str, or object castable"
                " to unicode or string, got: %r" % type(obj)
            )

    def writerow(self, row):
        self.writer.writerow([self.cast_to_str(s) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """

    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class CsvUnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwargs):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwargs)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class CSVImporter:
    delimiter = ";"
    quotechar = '"'
    escapechar = "\\"
    expected_cols = 1
    logger = logger
    from_row = 1

    def __init__(self, **kwargs):
        self.delimiter = kwargs.get("delimiter", self.delimiter)
        self.logger = kwargs.get("logger", self.logger)
        self.set_expected_cols()
        # self.expected_cols = kwargs.get('expected_cols',self.expected_cols)

    def import_csv(self, file_path, **kwargs):
        from_row = kwargs.get("from_row", self.from_row)
        row_number = 0
        imported_number = 0
        error_number = 0
        # Possiamo prevedere che il file non sia un file ma un path
        for row in CsvUnicodeReader(
            file_path,  # open(file_path, 'rb'),
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            escapechar=self.escapechar,
        ):
            row_number += 1
            if row_number >= from_row:
                if self._import_row(row, row_number, **kwargs):
                    imported_number += 1
                else:
                    error_number += 1
        self.logger.info(
            _(
                f"Imported CSV of {row_number} rows of which {error_number} were not processed"
            )
        )
        return {"rows": row_number, "imported": imported_number, "errors": error_number}

    def _import_row(self, row, row_number, **kwargs):
        if len(row) > self.get_expected_cols():
            self.logger.info(
                f"Numero colonne : {len(row)} invece di {self.get_expected_cols()}"
            )
            self.logger.error(
                "Row number %d has an invalid number of fields, skipping..."
                % row_number
            )
            return False
        else:
            callback = kwargs.get("callback", None)
            kwargs = kwargs or {}
            kwargs.update({"items": row[: self.get_expected_cols()]})
            if callback and hasattr(self, callback):
                return getattr(self, callback)(**kwargs)
            else:
                self.process_row(**kwargs)
                return True

    def process_row(self, **kwargs):
        raise NotImplementedError()

    def get_expected_cols(self):
        return self.expected_cols

    def set_expected_cols(self, expected_cols=None):
        self.expected_cols = expected_cols or self.expected_cols

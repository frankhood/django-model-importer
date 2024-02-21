from django_model_importer.controllers import ModelCSVImporter
from tests.example.models import Poll


class PollsImporter(ModelCSVImporter):
    can_update = False
    can_create = True
    can_add_fk = True
    can_add_m2m = True

    model: object | None = Poll

    db_mapping = {
        "Titolo": "title",
        "Utente": "user__username",
        "Categoria": "poll_categories__name",
        "Domanda": "questions__text",
    }

    def get_import_id_column_index(self):
        return None

    def get_import_id_field_name(self):
        return None

    def get_import_id(self, columns):
        return None

import os

from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.test.testcases import TestCase

from tests.example.factories import PollFactory, UserFactory, PollCategoryFactory, QuestionFactory
from tests.example.importer import PollsImporter
from tests.example.models import Poll, Question


class PollImportUnitTest(TestCase):

    def test_poll_import(self):
        first_poll_category = PollCategoryFactory(name="First")
        second_poll_category = PollCategoryFactory(name="Second")
        poll = PollFactory(
            title="Test Title",
            user=UserFactory(username="pippo"),
            poll_categories=[first_poll_category, second_poll_category]
        )
        first_question = QuestionFactory(
            text="Why you are coding?",
            poll=poll
        )
        second_question = QuestionFactory(
            text="Why you are testing?",
            poll=poll
        )
        csv_text = """Titolo;Utente;Categoria;Domanda\nTest Title;pippo;First;Why you are coding?\nTest Title;pluto;Second;Why you are testing?\nNew Title;paperino;Third;Why you are writing?"""

        file_name = "poll_import.csv"
        with open("poll_import.csv", "w") as csv_file:
            csv_file.write(csv_text)
        csv_importer = PollsImporter()
        csv_importer.import_csv(file_name)
        self.assertEqual(
            Poll.objects.all().count(),
            4
        )
        self.assertTrue(
            Poll.objects.get(title="New Title")
        )
        User = apps.get_model(settings.AUTH_USER_MODEL)
        self.assertTrue(
            User.objects.get(username="pluto")
        )
        self.assertTrue(
            User.objects.get(username="paperino")
        )
        self.assertTrue(
            Question.objects.get(text="Why you are writing?")
        )

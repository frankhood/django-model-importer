import factory.django
from django.apps import apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("domain_word")
    first_name = factory.Faker("first_name_nonbinary")
    last_name = factory.Faker("last_name_nonbinary")
    email = factory.Faker("free_email")

    class Meta:
        """UserFactory Meta."""

        model = settings.AUTH_USER_MODEL


class PollFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("sentence", nb_words=6)
    user = factory.SubFactory(UserFactory)

    class Meta:
        """PollFactory Meta."""

        model = apps.get_model("example.Poll")

    @factory.post_generation
    def poll_categories(self, create, m2m_entries, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if m2m_entries:
            for _m2m_entry in m2m_entries:
                self.poll_categories.add(_m2m_entry)


class QuestionFactory(factory.django.DjangoModelFactory):
    text = factory.Faker("paragraph")
    poll = factory.SubFactory(PollFactory)

    class Meta:
        """QuestionFactory Meta."""

        model = apps.get_model("example.Question")


class PollCategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")

    class Meta:
        """PollCategoryFactory Meta."""

        model = apps.get_model("example.PollCategory")

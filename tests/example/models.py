from django.conf import settings
from django.db import models

from django.utils.translation import ugettext_lazy as _


class Poll(models.Model):
    title = models.CharField(
        _("Title"), max_length=255
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.SET_NULL,
        null=True
    )
    poll_categories = models.ManyToManyField(
        "example.PollCategory",
        verbose_name=_("Poll Categories"),
        related_name="polls"
    )

    class Meta:
        """Poll Meta."""

        verbose_name = _("Poll")
        verbose_name_plural = _("Polls")

    def __str__(self):
        return self.title


class Question(models.Model):
    text = models.TextField(
        _("Question Text")
    )
    poll = models.ForeignKey(
        "example.Poll",
        verbose_name=_("Poll"),
        on_delete=models.CASCADE,
        related_name="questions"
    )

    class Meta:
        """Question Meta."""

        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def __str__(self):
        return f"Question n°{self.id} for poll: {self.poll}"


class PollCategory(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=255
    )

    class Meta:
        """PollCategory Meta."""

        verbose_name = _("Poll Category")
        verbose_name_plural = _("Poll Categories")



from django.urls import path
from django.views.generic import TemplateView

app_name = "django_model_importer"
urlpatterns = [
    path("", TemplateView.as_view(template_name="base.html")),
]

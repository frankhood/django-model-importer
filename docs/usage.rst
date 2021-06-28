=====
Usage
=====

To use Django Model Importer in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_model_importer.apps.DjangoModelImporterConfig',
        ...
    )

Add Django Model Importer's URL patterns:

.. code-block:: python

    from django_model_importer import urls as django_model_importer_urls


    urlpatterns = [
        ...
        url(r'^', include(django_model_importer_urls)),
        ...
    ]

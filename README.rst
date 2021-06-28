=============================
Django Model Importer
=============================

.. image:: https://badge.fury.io/py/django-model-importer.svg
    :target: https://badge.fury.io/py/django-model-importer

.. image:: https://travis-ci.org/frankhood/django-model-importer.svg?branch=master
    :target: https://travis-ci.org/frankhood/django-model-importer

.. image:: https://codecov.io/gh/frankhood/django-model-importer/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/frankhood/django-model-importer

This is a utility class for Django ORM Class import

Documentation
-------------

The full documentation is at https://django-model-importer.readthedocs.io.

Quickstart
----------

Install Django Model Importer::

    pip install django-model-importer

Add it to your `INSTALLED_APPS`:

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

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage

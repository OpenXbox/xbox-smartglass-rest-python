====================
Xbox-Smartglass-REST
====================

.. image:: https://pypip.in/version/xbox-smartglass-rest/badge.svg
    :target: https://pypi.python.org/pypi/xbox-smartglass-rest/
    :alt: Latest Version

.. image:: https://travis-ci.com/OpenXbox/xbox-smartglass-rest-python.svg?branch=master
    :target: https://travis-ci.com/OpenXbox/xbox-smartglass-rest-python

.. image:: https://img.shields.io/badge/discord-OpenXbox-blue.svg
    :target: https://discord.gg/E8kkJhQ
    :alt: Discord chat channel

Open-Source Xbox One Smartglass REST server.

For in-depth information, check out the documentation: (https://openxbox.github.io)

Dependencies
------------
* Python >= 3.5
* xbox-smartglass-stump (https://pypi.org/project/xbox-smartglass-stump/)
* Flask (https://pypi.org/project/Flask/)

Install
-------

Via pip:
::

    pip install xbox-smartglass-rest


How to use
----------

Start the server:
::

    $ xbox-rest-server


Authentication
--------------

Authenticate from scratch
::

    For non-2FA enabled account: http://localhost:5557/auth/login
    For 2FA: http://localhost:5557/auth/oauth

    # Store tokens on valid authentication
    http://localhost:5557/auth/store

Load tokens from disk
::

    http://localhost:5557/auth/load
    http://localhost:5557/auth/refresh

2FA OAuth - POST
::

    # Get authorize url
    GET http://localhost:5557/auth/url
    Response-Parameters (JSON): authorization_url

    # Submit redirect url
    POST http://localhost:5557/auth/oauth
    Request-Parameters: redirect_uri

Regular (non-2FA) login - POST
::

    POST http://localhost:5557/auth/login
    Request-Parameters: email, password


General usage
-------------

To see all API endpoints:
::

    http://localhost:5557


Usual usage:
::

    # (Optional) Poweron console
    http://localhost:5557/device/<liveid>/poweron
    # NOTE: You can specify device by ip: /device/<liveid>/poweron?addr=192.168.0.123
    # Enumerate devices on network
    # NOTE: You can enumerate device by specific ip: /device?addr=192.168.0.123
    http://localhost:5557/device
    # Connect to console
    # NOTE: You can connect anonymously: /connect?anonymous=true
    # .. if console allows it ..
    http://localhost:5557/device/<liveid>/connect

    # Use other API endpoints ...


Known issues
------------
* Find, report and/or fix them ;)

Bugreporting
------------
When reporting bugs, please make sure to provide the output of the following endpoint

::

    http://localhost:5557/versions


Contribute
----------
* Report bugs/suggest features
* Improve / add endpoints

Credits
-------
This package uses parts of Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

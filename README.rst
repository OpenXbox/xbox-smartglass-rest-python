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

Authenticate first (Authentication provided by xbox-webapi-python):
::

    $ xbox-authenticate

    # Alternative: Use the ncurses terminal ui, it has authentication integrated
    $ xbox-tui

    # If you want to authenticate via browser, use:
    $ xbox-auth-via-browser


Now, start the server:
::

    $ xbox-rest-server


To see all API endpoints:
::

    http://localhost:5557


Usual usage:
::

    # Read tokens from appdirs location
    http://localhost:5557/authentication/refresh
    # (Optional) Poweron console
    http://localhost:5557/<liveid>/poweron
    # Enumerate devices on network
    http://localhost:5557/devices
    # Connect to console
    http://localhost:5557/<liveid>/connect
    # Use other API endpoints ...


Known issues
------------
* Find, report and/or fix them ;)

Contribute
----------
* Report bugs/suggest features
* Improve / add endpoints

Credits
-------
This package uses parts of Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

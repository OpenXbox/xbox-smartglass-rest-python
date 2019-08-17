#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name="xbox-smartglass-rest",
    version="0.9.8",
    author="OpenXbox",
    description="Xbox One Smartglass REST API",
    long_description=open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
    license="GPL",
    keywords="xbox one smartglass rest api",
    url="https://github.com/OpenXbox/xbox-smartglass-rest-python",
    packages=[
        'xbox.rest',
        'xbox.rest.routes',
        'xbox.rest.scripts'
    ],
    namespace_packages=['xbox'],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    install_requires=[
        'xbox-webapi>=1.1.7',
        'xbox-smartglass-core==1.0.12',
        'urwid==2.0.1',
        'xbox-smartglass-stump>=0.9.5',
        'Flask'
    ],
    tests_require=[
        'pytest',
        'flake8',
        'tox'
    ],
    extras_require={
        'dev': [
            'bumpversion',
            'watchdog',
            'coverage',
            'Sphinx',
            'wheel',
            'twine'
        ]
    },
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'xbox-rest-server=xbox.rest.scripts.rest_server:main'
        ]
    }
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="xbox-smartglass-rest",
    version="1.10.0",
    author="OpenXbox",
    description="Meta package - Xbox One Smartglass REST API",
    long_description=open('README.rst').read(),
    license="GPL",
    keywords="xbox one smartglass rest api",
    url="https://github.com/OpenXbox/xbox-smartglass-core-python",
    zip_safe=False,
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'xbox-smartglass-core',
    ]
)

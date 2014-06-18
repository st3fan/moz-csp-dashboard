#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/

from setuptools import setup

install_requires = [
    'Flask==0.10.1',
    'requests==2.3.0',
    'psycopg2==2.5.3',
    'httpagentparser=1.7.3'
]

setup(name="moz-csp",
      version="0.1",
      description="CSP Reporter",
      url="https://github.com/st3fan/moz-csp",
      author="Stefan Arentz",
      author_email="sarentz@mozilla.com",
      install_requires = install_requires,
      packages=["csp", "csp.frontend", "csp.frontend.static", "csp.frontend.templates"],
      include_package_data=True,
      scripts=["scripts/csp-web"])

# -*- coding: utf-8 -*-#
#
# November 1 2015, Christian Hopps <chopps@gmail.com>
#
# Copyright (c) 2015, Deutsche Telekom AG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from setuptools import setup

required = [
    "BeautifulSoup4",
    "lxml"
]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup (name='wgstatus',
       version='0.9.8',
       description='wgstatus',
       long_description=read("README.rst"),
       author='Christian E. Hopps',
       author_email='chopps@gmail.com',
       license='Apache License, Version 2.0',
       install_requires=required,
       url='https://github.com/choppsv1/wgstatus',
       entry_points={"console_scripts": [ "wgstatus = wgstatus.main:main"]},
       packages=['wgstatus'])

# -*- coding: utf-8 -*-#
# March 19 2016,  <chopps@gmail.com>
#
# Copyright (c) 2016 by Christian E. Hopps.
# All rights reserved.
#
# REDISTRIBUTION IN ANY FORM PROHIBITED WITHOUT PRIOR WRITTEN
# CONSENT OF THE AUTHOR.
#
from __future__ import absolute_import, division, unicode_literals, print_function, nested_scopes
import base64
import datetime
import json
import os
import sys
try:
    import urllib2 as urllib
    from urllib import urlopen
    from urllib import urlencode
except:
    import urllib as urllib
    from urllib.request import urlopen
    from urllib.parse import urlencode


CACHEDIR = "~/.cache/wgstatus"

if sys.version_info[0] >= 3:
    def encodeurl (url):
        return base64.urlsafe_b64encode(bytes(url, "utf-8"))
else:
    def encodeurl (url):
        return base64.urlsafe_b64encode(url)


def flush_caches ():
    os.system("rm -rf {}".format(CACHEDIR))


def get_cache_dir ():
    cachedir = os.path.expanduser(CACHEDIR)
    if not os.path.exists(cachedir):
        os.makedirs(cachedir)
    return cachedir


def url2pathname (url):
    cachedir = get_cache_dir()
    fname = encodeurl(url)
    fname = fname.decode("utf-8")
    return os.path.join(cachedir, fname)


def pathname2url (pname):
    return base64.urlsafe_b64decode(os.path.basename(pname))


def file_age_in_seconds (pname):
    if not os.path.exists(pname):
        return sys.maxsize
    mtime = os.path.getmtime(pname)
    mtime = datetime.datetime.fromtimestamp(mtime)
    nowtime = datetime.datetime.now()
    delta = nowtime - mtime
    return delta.total_seconds()


def get_with_cache(url, payload, cache_seconds):
    if payload:
        parms = urlencode(payload)
        if parms:
            url = url + "?" + parms

    pname = url2pathname(url)
    if file_age_in_seconds(pname) <= cache_seconds:
        with open(pname) as fp:
            return json.load(fp)

    response = urlopen(url)
    data = json.load(response)

    with open(pname, "w") as fp:
        json.dump(data, fp)
    return data


__author__ = ''
__date__ = 'March 19 2016'
__version__ = '1.0'
__docformat__ = "restructuredtext en"

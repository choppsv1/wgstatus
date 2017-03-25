# -*- coding: utf-8 -*-#
# March 25 2017, Christian Hopps <chopps@gmail.com>
#
# Copyright (c) 2017 by Christian E. Hopps.
# All rights reserved.
#
# REDISTRIBUTION IN ANY FORM PROHIBITED WITHOUT PRIOR WRITTEN
# CONSENT OF THE AUTHOR.
#
from __future__ import absolute_import, division, unicode_literals, print_function, nested_scopes

from wgstatus.main import main

def test_00_flush_isis ():
    main(["-f", "idr"])

def test_isis_by_date ():
    main(["-l", "2017-01-01", "isis"])

def test_isis_by_ietf_95 ():
    main(["-l", "95", "isis"])

def test_isis_replaced_dates ():
    main(["--include-replaced", "--include-date", "isis"])

def test_isis_shepherd_status ():
    main(["-S", "-s", "isis"])

def test_idr_all ():
    main(["-d", "-r", "-S", "-s", "idr"])

__author__ = 'Christian Hopps'
__date__ = 'March 25 2017'
__version__ = '1.0'
__docformat__ = "restructuredtext en"

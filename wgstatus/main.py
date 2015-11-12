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
from __future__ import absolute_import, division, unicode_literals, print_function, nested_scopes
import argparse
import datetime
import os
import pdb
import re
import subprocess
from bs4 import BeautifulSoup


def split_nempty (s):
    return [ x.strip() for x in s.split('\n') if x.strip() ]


def parse_date (e):
    datestring = e.span.text.strip()
    try:
        return datetime.datetime.strptime(datestring, "%Y-%m-%d")
    except ValueError:
        return datetime.datetime.strptime(datestring, "%Y-%m")


def get_orignal_date (url_name):
    cachedir = "/tmp/wgstatus.cache"
    if not os.path.exists(cachedir):
        os.system("mkdir -p " + cachedir)
    basename = url_name.split('/')[-2]
    path = os.path.join(cachedir, basename)
    if not os.path.exists(path):
        print("Fetching original publication date of {}".format(url_name.split('/')[-2]))
        cmd = "curl -s -o {} https://datatracker.ietf.org{}00/".format(path, url_name)
        subprocess.check_output(cmd, shell=True)
    output = open(path).read().encode("utf-8")
    if not output:
        # Fake a date
        return datetime.datetime.strptime("2010", "%Y")
    soup = BeautifulSoup(output, "lxml")
    upds = soup.find_all("th")
    if not upds:
        pdb.set_trace()
    for upd in upds:
        if "Last updated" not in upd.text:
            continue

        tr = upd.parent
        td = tr.find_all("td")
        match = re.search(r"latest revision (\d+-\d+-\d+)", td[1].text.strip())
        if match:
            upd = datetime.datetime.strptime(match.group(1), "%Y-%m-%d")
        else:
            upd = td[1].text.strip().split()[0]
            upd = datetime.datetime.strptime(upd, "%Y-%m-%d")
        return upd
    else:
        assert False


def print_doc_summary (args, doc):
    if args.org_mode:
        name = doc[0].div.a.text.strip()
        if name.startswith("RFC"):
            fmt = """ - {name}
   - {title}"""
        else:
            fmt = " - {name}"
    else:
        fmt = ""
        if args.include_date:
            fmt += "{date}: "
        fmt += "{name}"
        if args.include_status:
            fmt += "\t{status}"

    fmt = fmt.format(date=doc[1], title=doc[0].div.b.text.strip(), name=doc[0].div.a.text, status=doc[2])
    print(fmt)


def main (*margs):
    parser = argparse.ArgumentParser("wgstatus")
    # Should be non-optional arg.
    parser.add_argument('--last-meeting', required=True, help='Date (YYYY-MM-DD) of last IETF')
    parser.add_argument('--include-date', action="store_true", help='Include date in summary')
    parser.add_argument('--include-status', action="store_true", help='Include status in summary')
    parser.add_argument('--org-mode', action="store_true", help='Output org mode friendly slides')
    parser.add_argument('--use', help='file to use')
    parser.add_argument('wgname', nargs='?', default='isis', help='Working group name')
    args = parser.parse_args(*margs)

    lastmeeting = datetime.datetime.strptime(args.last_meeting, "%Y-%m-%d")

    if not args.wgname and not args.use:
        return

    if not args.use:
        cmd = "curl -s -o - 'https://datatracker.ietf.org/doc/search/?name={}&sort=&rfcs=on&activedrafts=on'"
        cmd = cmd.format(args.wgname)
        output = subprocess.check_output(cmd, shell=True)
    else:
        output = open(args.use).read().decode("utf-8")
    soup = BeautifulSoup(output, "lxml")
    # <table class="table table-condensed table-striped">
    table = soup.find('table', {'class': 'table table-condensed table-striped'})
    head = table.find("thead")
    body = table.find("tbody")

    # Get the column information
    # To extract href for sorting on column 1
    # table.find("thead").find("tr").find_all("th")[1].find('a').attrs
    header_elms = table.find("thead").find("tr").find_all("th")
    header_names = [ x.attrs['class'][0] if 'class' in x.attrs else '' for x in header_elms ]
    date_idx = header_names.index("date")
    name_idx = header_names.index("document")
    status_idx = header_names.index("status")

    # Get the data
    docs = [x for x in table.find("tbody").find_all("tr") if x.find("td", "doc")]
    docs = [ x.find_all("td") for x in docs ]
    docs = [ (x[name_idx], parse_date(x[date_idx]), split_nempty(x[status_idx].text)) for x in docs ]

    # docs[x][0].div.a.text is the draft name with version
    # docs[x][0].div.a['href'] is the relative url of the doc
    # docs[x][0].div.b.text is the title of the draft
    # docs[x][1].a.text.strip() is the date y-m-d
    # docs[x][2] is a list of status names

    # docs = [ (x[name_idx], x[date_idx], x[status_idx]) for x in docs ]

    rfcs = [ x for x in docs if x[0].div.a.text.startswith("RFC") ]
    rfcs = sorted(rfcs, key=lambda x: int(x[0].div.a.text[4:]))
    drafts = [ x for x in docs if not x[0].div.a.text.startswith("RFC") ]
    drafts = sorted(drafts, key=lambda x: x[1])

    # print("\nRFCS")
    # for doc in rfcs:
    #     print("{}: {}".format(doc[1], doc[0].div.a.text))

    # print("\nIDs")
    # for doc in drafts:
    #     print("{}: {}".format(doc[1], doc[0].div.a.text))

    new_rfcs = [ x for x in rfcs if x[1] >= lastmeeting ]
    existing = [ x for x in drafts if x[1] < lastmeeting ]
    new_or_updated = [ x for x in drafts if x[1] >= lastmeeting ]

    new = []
    updated = []
    for doc in new_or_updated:
        if doc[0].div.a.text.endswith('-00'):
            new.append(doc)
        else:
            origdate = get_orignal_date(doc[0].div.a['href'])
            if origdate >= lastmeeting:
                # print("Original also published ({}) after last meeting ({})".format(origdate, lastmeeting))
                new.append(doc)
            else:
                updated.append(doc)

    # wgdocpfx = "draft-ietf-{}".format(args.wgname)
    wgdocpfx = "draft-ietf-"
    new_wgstatus = [ x for x in new if x[0].a.text.startswith(wgdocpfx) ]
    updated_wgstatus = [ x for x in updated if x[0].a.text.startswith(wgdocpfx) ]
    existing_wgstatus = [ x for x in existing if x[0].a.text.startswith(wgdocpfx) ]
    new_ind = [ x for x in new if x not in new_wgstatus ]
    updated_ind = [ x for x in updated if x not in updated_wgstatus ]
    existing_ind = [ x for x in existing if x not in existing_wgstatus ]

    print("\n** Document Status")

    if new_rfcs:
        print("\n*** New RFCs")
        for doc in new_rfcs:
            print_doc_summary(args, doc)

    if new_wgstatus:
        print("\n*** New WG-Docs")
        for doc in new_wgstatus:
            print_doc_summary(args, doc)

    if updated_wgstatus:
        print("\n*** Updated WG-Docs")
        for doc in updated_wgstatus:
            print_doc_summary(args, doc)

    if existing_wgstatus:
        print("\n*** Existing WG-Docss")
        for doc in existing_wgstatus:
            print_doc_summary(args, doc)

    if new_ind:
        print("\n*** New IDs")
        for doc in new_ind:
            print_doc_summary(args, doc)

    if updated_ind:
        print("\n*** Updated IDs")
        for doc in updated_ind:
            print_doc_summary(args, doc)

    if existing_ind:
        print("\n*** Existing IDs")
        for doc in existing_ind:
            print_doc_summary(args, doc)


if __name__ == "__main__":
    main(["--wgname", "isis"])

__author__ = 'Christian Hopps'
__date__ = 'November 1 2015'
__version__ = '1.0'
__docformat__ = "restructuredtext en"

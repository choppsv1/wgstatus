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
import sys
from bs4 import BeautifulSoup

ORG_LEVEL_OFF = 1

def split_nempty (s):
    return [ x.strip() for x in s.split('\n') if x.strip() ]


def parse_date (e):
    datestring = e.span.text.strip()
    try:
        return datetime.datetime.strptime(datestring, "%Y-%m-%d")
    except ValueError:
        return datetime.datetime.strptime(datestring, "%Y-%m")


def get_shepherd (x):
    "Get the shepherd "
    ad = [e for e in x if "class" in e.attrs and e.attrs["class"][0] == "ad"]
    if not ad:
        return ""
    ad = ad[0]
    shep = ad.find_all("a")
    if len(shep) == 1:
        #return shep[0].text.split()[-1]
        return "[{}]".format(shep[0].text)
    if shep:
        #return ", ".join(reversed([x.text.split()[-1] for x in shep]))
        return "[{}]".format(", ".join(reversed([x.text for x in shep])))
    return ""

def get_url_with_cache (url, basename):
    cachedir = "/tmp/wgstatus.cache"
    if not os.path.exists(cachedir):
        os.system("mkdir -p " + cachedir)

    path = os.path.join(cachedir, basename)
    if not os.path.exists(path):
        print("Fetching {} into cache".format(basename))
        cmd = "curl -s -o {} {}".format(path, url)
        subprocess.check_output(cmd, shell=True)
    return open(path).read().encode("utf-8")


def get_meeting_info ():
    url = "http://www.ietf.org/meeting/past.html"
    output = get_url_with_cache(url, "past.html")

    soup = BeautifulSoup(output, "lxml")
    meetings = soup.find_all("h3")
    if not meetings:
        raise ValueError("No meeting info found in {}".format(url))

    meeting_info = {}
    for meeting in meetings:
        if "IETF" not in meeting.text:
            continue

        match = re.search(r"(\d+)(st|nd|rd|th) IETF", meeting.text)
        if not match:
            continue

        meeting_number = int(match.group(1))
        for sib in meeting.next_siblings:
            # Make sure we don't get to the next heading.
            if "IETF" in sib:
                raise ValueError("No meeting date found for {}".format(meeting_number))

            in_month_re = r"(([A-Z][a-z]+) (\d+)-(\d+), (\d{4}))"
            x_month_re = r"(([A-Z][a-z]+) (\d+)-([A-Z][a-z]+) (\d+), (\d{4}))"
            match = re.search(r"{}|{}".format(in_month_re, x_month_re), str(sib))
            if match:
                groups = match.groups()
                if groups[0]:
                    # Date range in same month
                    date = "{} {} {}".format(groups[1], groups[3], groups[4])
                else:
                    # Date range crosses months
                    assert groups[5]
                    date = "{} {} {}".format(groups[8], groups[9], groups[10])
                date = datetime.datetime.strptime(date, "%B %d %Y")
                meeting_info[meeting_number] = date
                break
        else:
            raise ValueError("No date found for meeting {}".format(meeting_number))
    return meeting_info


def get_orignal_date (url_name):
    url = "https://datatracker.ietf.org{}00/".format(url_name)
    cachename = url_name.split('/')[-2] + "-00"
    try:
        output = get_url_with_cache(url, cachename)
        assert output
    except (IOError, AssertionError):
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


def print_headline (args, headline, level):
    hline = ""
    if args.org_mode:
        hline = "\n" + "*" * (level + ORG_LEVEL_OFF)
    else:
        hline = "\n" + "#" * level
    hline += " " + headline
    print(hline)


def print_doc_summary (args, doc, longest, longest_shep):
    name = doc[0].div.a.text.strip()
    shep = doc[3]
    if args.org_mode or not (args.include_date or args.include_status):
        fmt = " - "
    else:
        fmt = ""
    if args.include_date:
        fmt += "{date}: "
    if name.startswith("RFC"):
        fmt += "{name} - {title}"
    else:
        fmt += "{name}"
    if args.include_shepherd:
        fmt += " "
        fmt += " " * (longest - len(name)) + " {shepherd}"
    if args.include_status:
        if not args.include_shepherd:
            fmt += " " * (longest - len(name))
        else:
            fmt += " " * (longest_shep - len(shep))
        fmt += " {status}"

    fmt = fmt.format(date=doc[1], title=doc[0].div.b.text.strip(), name=name, status=doc[2],
                     shepherd=shep)
    print(fmt)


def main (*margs):
    parser = argparse.ArgumentParser("wgstatus")
    # Should be non-optional arg.
    parser.add_argument('--last-meeting', help='Meeting number or Date (YYYY-MM-DD) of last IETF')
    parser.add_argument('--exclude-existing', action="store_true", help='Exclude unchanged docs in summary')
    parser.add_argument('--include-date', action="store_true", help='Include date in summary')
    parser.add_argument('--include-shepherd', action="store_true", help='Include shepherd in summary')
    parser.add_argument('--include-status', action="store_true", help='Include status in summary')
    parser.add_argument('--org-mode', action="store_true", help='Output org mode friendly slides')
    parser.add_argument('--use', help=argparse.SUPPRESS)
    parser.add_argument('wgname', nargs='?', help='Working group name')
    args = parser.parse_args(*margs)

    if not args.last_meeting:
        meeting_info = get_meeting_info()
        lastidx = sorted(meeting_info.keys())[-1]
        lastmeeting = meeting_info[lastidx]
    else:
        try:
            lastmeeting = datetime.datetime.strptime(args.last_meeting, "%Y-%m-%d")
        except:
            meeting_info = get_meeting_info()
            lastmeeting = meeting_info[int(args.last_meeting)]

    if not args.wgname and not args.use:
        print("Need to specify a WG name (use -h for help)")
        sys.exit(1)

    if not args.use:
        cmd = "curl -s -o - 'https://datatracker.ietf.org/doc/search/?name=-{}-&sort=&rfcs=on&activedrafts=on'"
        cmd = cmd.format(args.wgname)
        output = subprocess.check_output(cmd, shell=True)
    else:
        output = open(args.use).read().decode("utf-8")
    soup = BeautifulSoup(output, "lxml")

    # <table class="table table-condensed table-striped">
    table = soup.find('table', {'class': 'table table-condensed table-striped tablesorter'})
    head = table.find("thead")
    # body = table.find("tbody")

    # Get the column information
    # To extract href for sorting on column 1
    # table.find("thead").find("tr").find_all("th")[1].find('a').attrs
    header_elms = table.find("thead").find("tr").find_all("th")
    header_names = [ x.attrs['data-header'] if 'data-header' in x.attrs else '' for x in header_elms ]
    date_idx = header_names.index("date")
    name_idx = header_names.index("document")
    status_idx = header_names.index("status")
    ipr_idx = header_names.index("ipr")
    shep_idx = header_names.index("ad")

    # Get the data
    # index 0 "Active IDs" index 1 actual docs, index 2 "RFCs", index 3 actual docs
    all_tbody = table.find_all("tbody")
    all_trs = all_tbody[1].find_all("tr")
    if len(all_tbody) > 3:
        all_trs += all_tbody[3].find_all("tr")
    docs = [x for x in all_trs if x.find("td", "doc")]
    docs = [ x.find_all("td") for x in docs ]
    docs = [ (x[name_idx],
              parse_date(x[date_idx]),
              split_nempty(x[status_idx].text),
              get_shepherd(x)
    ) for x in docs ]

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

    print_headline(args, "Document Status Since {}".format(lastmeeting), 1)

    def get_longest (docs):
        longest = reduce(max, [ len(x[0].div.a.text.strip()) for x in docs ], 0)
        longest_shep = reduce(max, [ len(x[3]) for x in docs ], 0)
        return longest, longest_shep

    if new_rfcs:
        print_headline(args, "New RFCs", 2)
        longest, longest_shep = get_longest(new_rfcs)
        for doc in new_rfcs:
            print_doc_summary(args, doc, longest, longest_shep)

    if new_wgstatus:
        print_headline(args, "New WG-Docs", 2)
        longest, longest_shep = get_longest(new_wgstatus)
        for doc in new_wgstatus:
            print_doc_summary(args, doc, longest, longest_shep)

    if updated_wgstatus:
        print_headline(args, "Updated WG-Docs", 2)
        longest, longest_shep = get_longest(updated_wgstatus)
        for doc in updated_wgstatus:
            print_doc_summary(args, doc, longest, longest_shep)

    if existing_wgstatus and not args.exclude_existing:
        print_headline(args, "Existing WG-Docs", 2)
        longest, longest_shep = get_longest(existing_wgstatus)
        for doc in existing_wgstatus:
            print_doc_summary(args, doc, longest, longest_shep)

    if new_ind:
        print_headline(args, "New IDs", 2)
        longest, longest_shep = get_longest(new_ind)
        for doc in new_ind:
            print_doc_summary(args, doc, longest, longest_shep)

    if updated_ind:
        print_headline(args, "Updated IDs", 2)
        longest, longest_shep = get_longest(updated_ind)
        for doc in updated_ind:
            print_doc_summary(args, doc, longest, longest_shep)

    if existing_ind and not args.exclude_existing:
        print_headline(args, "Existing IDs", 2)
        longest, longest_shep = get_longest(existing_ind)
        for doc in existing_ind:
            print_doc_summary(args, doc, longest, longest_shep)


if __name__ == "__main__":
    main()

__author__ = 'Christian Hopps'
__date__ = 'November 1 2015'
__version__ = '1.0'
__docformat__ = "restructuredtext en"

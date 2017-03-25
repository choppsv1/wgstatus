# -*- coding: utf-8 -*-#
#
# When converting to REST api use used Fred Baker's perl code heavily.
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
from functools import reduce
import argparse
import datetime
import json
import os
import pdb
import pkg_resources
import pprint
import re
import subprocess
import sys

from . import rest


class json_dict (dict):
    def __hash__ (self):
        return self['resource_uri'].__hash__()


TIME_LEN_HOUR = 60 * 60
TIME_LEN_DAY = TIME_LEN_HOUR * 24
TIME_LEN_WEEK = TIME_LEN_DAY * 7

ORG_LEVEL_OFF = 1

base_url = r"https://datatracker.ietf.org/api/v1"

states_by_name = {}
states_by_slug = {}
states_by_uri = {}

wg_states = set()
iesg_states = set()
rfc_states = set()


def safelen (v):
    if not v:
        return 0
    return len(v)


# From Fred Bakers get_states(slug, tag):
def get_states():
    payload = {
        "format": "json",
        "limit": 0,
        # "type__slug__in": slug,
    }
    rdict = rest.get_with_cache(base_url + "/doc/state/", payload, TIME_LEN_DAY)
    # we don't handle continuation here.
    assert rdict['meta']['next'] is None

    for state in rdict['objects']:
        if state['used']:
            uri = state['resource_uri']
            state_copy = dict(state)
            # state_copy['type_tag'] = tag

            states_by_name[state['name']] = state_copy
            states_by_slug[state['slug']] = state_copy
            states_by_uri[uri] = state_copy
            # print("slug: {}: uri: {} type: {} state: {}".format(state['slug'], uri, state['type'], state['name']))
            # pprint.pprint(state)
            if state['type'] == "/api/v1/doc/statetype/draft-stream-ietf/":
                wg_states.add(uri)
            elif state['type'] == "/api/v1/doc/statetype/draft-iesg/":
                iesg_states.add(uri)
            elif state['type'] == "/api/v1/doc/statetype/draft-rfceditor/":
                rfc_states.add(uri)


def get_wg (wgname):
    payload = {
        "format": "json",
        "limit": 0,
        "acronym": wgname,
    }
    print("Getting IETF WG {}".format(wgname))
    rdict = rest.get_with_cache(base_url + "/group/group/", payload, TIME_LEN_DAY)
    # we don't handle continuation here.
    assert rdict['meta']['next'] is None
    return rdict['objects'][0]


def get_drafts (wg):
    payload = {
        "format": "json",
        "limit": 0,
        # "rfcs": "on",
        # "activedrafts": "on",
        # "name__contains": wg,
        # "group__acronym__in": wg['acronym'],
        "group__acronym__in": wg,
        "expires__gt": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    print("Getting IETF docs for {}".format(wg))
    # print("Getting IETF docs for {}".format(wg['acronym']))
    rdict = rest.get_with_cache(base_url + "/doc/document/", payload, TIME_LEN_HOUR)
    # we don't handle continuation here.
    assert rdict['meta']['next'] is None
    docs = set()
    for doc in rdict['objects']:
        doc = json_dict(doc)
        doc['time'] = datetime.datetime.strptime(doc['time'], "%Y-%m-%dT%H:%M:%S")
        doc['expires'] = datetime.datetime.strptime(doc['expires'], "%Y-%m-%dT%H:%M:%S")
        doc['states'] = set(doc['states'])
        docs.add(doc)
    return docs


def get_rfcs (wg, after):
    payload = {
        "format": "json",
        "limit": 0,
        # "rfcs": "on",
        # "activedrafts": "on",
        # "name__contains": wg,
        # "group__acronym__in": wg['acronym'],
        # "time__gt": after,
        "group__acronym__in": wg,
        "states__slug__in": "pub",
    }
    print("Getting IETF RFCs for {}".format(wg))
    # print("Getting IETF docs for {}".format(wg['acronym']))
    rdict = rest.get_with_cache(base_url + "/doc/document/", payload, TIME_LEN_HOUR)
    # we don't handle continuation here.
    assert rdict['meta']['next'] is None
    docs = set()
    for doc in rdict['objects']:
        # Rewrite some fields
        doc = json_dict(doc)
        doc['name'] = "RFC" + doc['rfc']
        # print("Got {}".format(doc['name']))
        doc['time'] = datetime.datetime.strptime(doc['time'], "%Y-%m-%dT%H:%M:%S")
        doc['states'] = set(doc['states'])
        docs.add(doc)
    return docs


def get_meetings ():
    payload = {
        "format": "json",
        "limit": 0,
        "type": "ietf",
    }
    rdict = rest.get_with_cache(base_url + "/meeting/meeting/", payload, TIME_LEN_DAY)
    # we don't handle continuation here.
    assert rdict['meta']['next'] is None

    meeting_info = {}
    for meeting in rdict['objects']:
        meeting = meeting_info[meeting['number']] = dict(meeting)
        meeting['date'] = datetime.datetime.strptime(meeting['date'], "%Y-%m-%d")

    return meeting_info


def find_last_meeting (meeting_info):
    now = datetime.datetime.now()
    for key in reversed(sorted(meeting_info.keys())):
        if meeting_info[key]['date'] < now:
            return meeting_info[key]


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


#
# XXX
#
# def get_orignal_date (url_name):
#     url = "https://datatracker.ietf.org{}00/".format(url_name)
#     cachename = url_name.split('/')[-2] + "-00"
#     try:
#         output = get_url_with_cache(url, cachename)
#         assert output
#     except (IOError, AssertionError):
#         # Fake a date
#         return datetime.datetime.strptime("2010", "%Y")

#     soup = BeautifulSoup(output, "lxml")
#     upds = soup.find_all("th")
#     if not upds:
#         pdb.set_trace()

#     for upd in upds:
#         if "Last updated" not in upd.text:
#             continue

#         tr = upd.parent
#         td = tr.find_all("td")
#         match = re.search(r"latest revision (\d+-\d+-\d+)", td[1].text.strip())
#         if match:
#             upd = datetime.datetime.strptime(match.group(1), "%Y-%m-%d")
#         else:
#             upd = td[1].text.strip().split()[0]
#             upd = datetime.datetime.strptime(upd, "%Y-%m-%d")
#         return upd
#     else:
#         assert False


def print_headline (args, headline, level):
    hline = ""
    if args.org_mode:
        hline = "\n" + "*" * (level + ORG_LEVEL_OFF)
    else:
        hline = "\n" + "#" * level
    hline += " " + headline
    print(hline)


def states_to_string (states):
    s = ""
    for state in states:
        if s:
            s += ",{}".format(states_by_uri[state]['name'])
        else:
            s = states_by_uri[state]['name']
    return s


def print_doc_summary (args, doc, longest, longest_shep):
    name = doc['name']
    shep = doc['shepherd']
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

    if not name.startswith("RFC"):
        if args.include_shepherd:
            fmt += " "
            fmt += " " * (longest - len(name)) + " {shepherd}"
        if args.include_status:
            if not args.include_shepherd:
                fmt += " " * (longest - len(name))
            else:
                fmt += " " * (longest_shep - len(shep))
            fmt += " {status}"

    fmt = fmt.format(date=doc['time'], title=doc['title'], name=name,
                     status=states_to_string(doc['states']),
                     shepherd=shep)
    print(fmt)


def get_new_and_updated(docs, lastmeeting):
    existing = [ x for x in docs if x['time'] < lastmeeting ]
    new_or_updated = [ x for x in docs if x['time'] >= lastmeeting ]
    new = set()
    updated = set()
    for doc in docs:
        if int(doc['rev']) == 0:
            new.add(doc)
        else:
            updated.add(doc)
            url = "https://datatracker.ietf.org/api/v1/doc/dochistory/"
            payload = {
                "name": doc['name'],
                "rev": "00"
            }

            print("Getting history for {}".format(doc['name']))
            try:
                rdict = rest.get_with_cache(url, payload, TIME_LEN_HOUR)
                zerodoc = rdict.pop()
                pub_time = datetime.datetime.strptime(zerodoc['time'], "%Y-%m-%dT%H:%M:%S")
                if pub_time >= lastmeeting:
                    new.add(doc)
                else:
                    updated.add(doc)
            except Exception:
                updated.add(doc)


    return new, updated, existing


def main (*margs):
    # from _version import __version__
    __version__ = pkg_resources.get_distribution('wgstatus').version

    parser = argparse.ArgumentParser("wgstatus")
    # Should be non-optional arg.
    parser.add_argument('-l', '--last-meeting', help='Meeting number or Date (YYYY-MM-DD) of last IETF')
    parser.add_argument('-e', '--exclude-existing', action="store_true", help='Exclude unchanged docs in summary')
    parser.add_argument('-f', '--flush', action="store_true", help='Flush the caches')
    parser.add_argument('-d', '--include-date', action="store_true", help='Include date in summary')
    parser.add_argument('-r', '--include-replaced', action="store_true", help='Include replaced drafts')
    parser.add_argument('-S', '--include-shepherd', action="store_true", help='Include shepherd in summary')
    parser.add_argument('-s', '--include-status', action="store_true", help='Include status in summary')
    parser.add_argument('-o', '--org-mode', action="store_true", help='Output org mode friendly slides')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--use', help=argparse.SUPPRESS)

    parser.add_argument('wgname', nargs='?', help='Working group name')
    args = parser.parse_args(*margs)

    if args.flush:
        rest.flush_caches()

    if not args.last_meeting:
        meeting_info = get_meetings()
        meeting = find_last_meeting(meeting_info)
        lastmeeting = meeting['date']
    else:
        try:
            lastmeeting = datetime.datetime.strptime(args.last_meeting, "%Y-%m-%d")
            meeting = None
        except Exception:
            meeting_info = get_meetings()
            meeting = meeting_info[args.last_meeting]
            lastmeeting = meeting['date']

    if not args.wgname:
        print("Need to specify a WG name (use -h for help)")
        sys.exit(1)

    #wg = get_wg(args.wgname)
    print("Getting IETF document states")
    get_states()

    drafts = get_drafts(args.wgname)

    if args.include_shepherd:
        for draft in drafts:
            shep_email_uri = draft['shepherd']
            if not shep_email_uri:
                draft['shepherd'] = ""
                continue
            rdict = rest.get_with_cache("https://datatracker.ietf.org" + shep_email_uri,
                                        None,
                                        TIME_LEN_WEEK)
            person = rdict['person']
            rdict = rest.get_with_cache("https://datatracker.ietf.org/" + person,
                                        None,
                                        TIME_LEN_WEEK)
            draft['shepherd'] = rdict['name']

    docs = set(drafts)

    rfc_uri = states_by_name["RFC"]['resource_uri']
    wgdoc_uri = states_by_name["WG Document"]['resource_uri']
    replaced_uri = states_by_name["Replaced"]['resource_uri']

    rfcs = set([ x for x in docs if rfc_uri in x['states'] ])
    docs -= rfcs
    iesgs = set([ x for x in docs if (x['states'] & (rfc_states | iesg_states)) ])
    docs -= iesgs
    wgdocs = set([ x for x in docs if wgdoc_uri in x['states'] ])
    docs -= wgdocs
    idocs = docs

    if not args.include_replaced:
        idocs = set([ x for x in docs if replaced_uri not in x['states'] ])

    # It seems we don't get RFCs from the normal query due to expired
    rfcs = get_rfcs(args.wgname, str(lastmeeting.date()))
    rfcs = set([ x for x in rfcs if rfc_uri in x['states'] ])
    new_rfcs = [ x for x in rfcs if x['time'] >= lastmeeting ]

    new_wgstatus, updated_wgstatus, existing_wgstatus = get_new_and_updated(wgdocs, lastmeeting)
    new_iesgs, updated_iesgs, existing_iesgs = get_new_and_updated(iesgs, lastmeeting)
    updated_iesgs = new_iesgs | updated_iesgs
    new_ind, updated_ind, existing_ind = get_new_and_updated(idocs, lastmeeting)

    if meeting:
        print_headline(args, "Document Status Since IETF-{} in {} ({})".format(
            meeting['number'], meeting['city'], lastmeeting.date()), 1)
    else:
        print_headline(args, "Document Status Since {}".format(lastmeeting), 1)

    def get_longest (docs):
        longest = reduce(max, [ safelen(x['name']) for x in docs ], 0)
        if not args.include_shepherd:
            return longest, 0
        longest_shep = reduce(max, [ safelen(x['shepherd']) for x in docs ], 0)
        return longest, longest_shep

    for doc_set, desc in [(new_rfcs, "New RFCs"),
                          (updated_iesgs, "Docs in IESG"),
                          (existing_iesgs, "Existing Docs in IESG"),
                          (new_wgstatus, "New WG Docs"),
                          (updated_wgstatus, "Updated WG Docs"),
                          (existing_wgstatus, "Existing WG Docs"),
                          (new_ind, "New Individual Docs"),
                          (updated_ind, "Updated Individual Docs"),
                          (existing_ind, "Existing Individual Docs")]:
        if doc_set:
            print_headline(args, desc, 2)
            longest, longest_shep = get_longest(doc_set)
            for doc in sorted(doc_set, key=lambda x: x['name']):
                print_doc_summary(args, doc, longest, longest_shep)


if __name__ == "__main__":
    main()

__author__ = 'Christian Hopps'
__date__ = 'November 1 2015'
__version__ = '1.0'
__docformat__ = "restructuredtext en"

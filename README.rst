
wgstatus
========


Fetch document status for an IETF working group.

Installing
----------

To install from PyPi:

.. code-block:: sh

    pip install wgstatus

To install a new version from PyPi:

.. code-block:: sh

    pip install --upgrade wgstatus

To install and run from a git repostiory (links into):

.. code-block:: sh

    git clone https://github.com/choppsv1/wgstatus.git
    cd wgstatus
    pip install -e .

Usage
-----

.. code-block:: sh

    usage: wgstatus [-h] [--last-meeting LAST_MEETING] [--exclude-existing]
                    [--include-date] [--include-status] [--org-mode]
                    [wgname]

    positional arguments:
      wgname                Working group name

    optional arguments:
      -h, --help            show this help message and exit
      --last-meeting LAST_MEETING
                            Meeting number or Date (YYYY-MM-DD) of last IETF
      --exclude-existing    Exclude unchanged docs in summary
      --include-date        Include date in summary
      --include-status      Include status in summary
      --org-mode            Output org mode friendly slides


Examples
--------

Here's an exmaple for Netmod wg since IETF 93 meeting (as of 2015-11-06) output in org mode format::

    $ wgstatus --org-mode --last=93 netmod

    Fetching draft-ietf-netmod-routing-cfg-00 into cache

    ** Document Status Since 2015-07-24 00:00:00

    *** New WG-Docs
     - draft-ietf-netmod-opstate-reqs-00

    *** Updated WG-Docs
     - draft-ietf-netmod-yang-metadata-02
     - draft-ietf-netmod-yang-json-06
     - draft-ietf-netmod-routing-cfg-20
     - draft-ietf-netmod-syslog-model-05
     - draft-ietf-netmod-acl-model-05
     - draft-ietf-netmod-rfc6020bis-08
     - draft-ietf-netmod-rfc6087bis-05

    *** New IDs
     - draft-kwatsen-netmod-opstate-00
     - draft-wilton-netmod-opstate-yang-00
     - draft-chen-netmod-enterprise-yang-namespace-00
     - draft-faq-netmod-cpe-yang-profile-00
     - draft-leiba-netmod-regpolicy-update-01
     - draft-dharini-netmod-dwdm-if-yang-00
     - draft-entitydt-netmod-entity-00
     - draft-openconfig-netmod-model-catalog-00

    *** Updated IDs
     - draft-betts-netmod-framework-data-schema-uml-02
     - draft-mansfield-netmod-uml-to-yang-01
     - draft-voit-netmod-peer-mount-requirements-03
     - draft-bogdanovic-netmod-yang-model-classification-05
     - draft-wilton-netmod-intf-ext-yang-01
     - draft-wilton-netmod-intf-vlan-yang-01

    *** Existing IDs
     - draft-vassilev-netmod-yang-direct-must-augment-ext-00
     - draft-asechoud-netmod-diffserv-model-03
     - draft-wwz-netmod-yang-tunnel-cfg-00
     - draft-bierman-netmod-yang-package-00
     - draft-bjorklund-netmod-openconfig-reply-00
     - draft-dharini-netmod-g-698-2-yang-04
     - draft-openconfig-netmod-opstate-01


Here's an exmaple for IS-IS WG since IETF 94 (as of 2015-11-06) excluding non-changed documents::

    $ wgstatus --exclude-existing isis

    # Document Status Since 2015-11-06 00:00:00

    ## Updated WG-Docs
     - draft-ietf-isis-mpls-elc-01
     - draft-ietf-isis-node-admin-tag-05

    ## New IDs
     - draft-chen-isis-rfc5316bis-00

    ## Updated IDs
     - draft-xu-isis-encapsulation-cap-06

Here's and example for OSPF WG since IETF 94 (as of 2015-11-06) including status::

    $ wgstatus  --include-status ospf

    # Document Status Since 2015-11-06 00:00:00

    ## Updated WG-Docs
    draft-ietf-ospf-mpls-elc-01                          [u'I-D Exists', u'WG Document', u'Jun 2016']

    ## Existing WG-Docs
    draft-ietf-ospf-flowspec-extensions-00               [u'I-D Exists', u'WG Document', u'Jun 2017']
    draft-ietf-ospf-ospfv3-segment-routing-extensions-03 [u'I-D Exists', u'WG Document', u'Jun 2017']
    draft-ietf-ospf-segment-routing-extensions-05        [u'I-D Exists', u'WG Document', u'Jun 2016']
    draft-ietf-ospf-ttz-01                               [u'I-D Exists', u'WG Document', u'Jun 2016']
    draft-ietf-ospf-two-part-metric-01                   [u'I-D Exists', u'WG Document', u'Jun 2016']
    draft-ietf-ospf-prefix-link-attr-13                  [u'RFC Ed Queue', u': AUTH48', u'for 84 days', u'Submitted to IESG for Publication:', u'Proposed Standard', u'Dec 2015']
    draft-ietf-ospf-transition-to-ospfv3-02              [u'I-D Exists', u'WG Document', u'Jun 2016']
    draft-ietf-ospf-sbfd-discriminator-02                [u'I-D Exists', u'WG Document', u'Dec 2015']
    draft-ietf-ospf-ospfv3-lsa-extend-08                 [u'I-D Exists', u'WG Document', u'Dec 2016']
    draft-ietf-ospf-encapsulation-cap-00                 [u'I-D Exists', u'WG Document']
    draft-ietf-ospf-rfc4970bis-07                        [u'RFC Ed Queue', u': EDIT', u'for 28 days', u'Submitted to IESG for Publication:', u'Proposed Standard', u'Dec 2015']
    draft-ietf-ccamp-flexible-grid-ospf-ext-03           [u'I-D Exists', u'WG Document']
    draft-ietf-ospf-node-admin-tag-08                    [u'IESG Evaluation::AD Followup', u'for 32 days', u'Submitted to IESG for Publication:', u'Proposed Standard', u'Dec 2015']
    draft-ietf-ccamp-ospf-availability-extension-03      [u'I-D Exists', u'WG Document']
    draft-ietf-ospf-mrt-01                               [u'I-D Exists', u'WG Document', u'Jun 2016']
    draft-ietf-ospf-ospfv2-hbit-00                       [u'I-D Exists', u'WG Document']
    draft-ietf-bier-ospf-bier-extensions-01              [u'I-D Exists', u'WG Document']
    draft-ietf-ospf-link-overload-00                     [u'I-D Exists', u'WG Document']
    draft-ietf-ospf-yang-03                              [u'I-D Exists', u'WG Document', u'Dec 2016']

    ## Existing IDs
    draft-chunduri-ospf-operator-defined-tlvs-01         [u'I-D Exists']
    draft-chen-ospf-tts-00                               [u'I-D Exists']
    draft-ppsenak-ospf-te-link-attr-reuse-00             [u'I-D Exists']
    draft-acee-ospf-admin-tags-03                        [u'I-D Exists']
    draft-chen-ospf-te-ttz-01                            [u'I-D Exists']
    draft-smirnov-ospf-xaf-te-04                         [u'I-D Exists']
    draft-xu-ospf-multi-homing-ipv6-00                   [u'I-D Exists']
    draft-wang-bier-lite-ospf-extension-01               [u'I-D Exists']
    draft-raza-ospf-stub-neighbor-02                     [u'I-D Exists']

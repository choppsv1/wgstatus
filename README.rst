
wgstatus
========

Fetch document status for an IETF working group.

Usage
-----

.. code-block:: sh

    usage: wgstatus [-h] --last-meeting LAST_MEETING [--include-date]
                    [--include-status] [--org-mode] [--use USE]
                    [wgname]

    positional arguments:
      wgname                Working group name

    optional arguments:
      -h, --help            show this help message and exit
      --last-meeting LAST_MEETING
                            Date (YYYY-MM-DD) of last IETF
      --include-date        Include date in summary
      --include-status      Include status in summary
      --org-mode            Output org mode friendly slides
      --use USE             file to use    usage: wgstatus [-h] [--wgname WGNAME] [--last-meeting LAST_MEETING]
                        [--include-date] [--include-status] [--org-mode] [--use USE]

Example
-------

.. code-block:: sh
    $ wgstatus --last-meeting=2015-07-31 --org-mode isis

    ** Document Status

    *** New RFCs
     - RFC 7645
       - The Keying and Authentication for Routing Protocol (KARP) IS-IS Security Analysis

    *** Updated WG-Docs
     - draft-ietf-isis-yang-isis-cfg-06
     - draft-ietf-isis-pcr-02
     - draft-ietf-isis-route-preference-02
     - draft-ietf-bier-isis-extensions-01
     - draft-ietf-isis-mrt-01
     - draft-ietf-isis-mpls-elc-01
     - draft-ietf-isis-node-admin-tag-05

    *** Existing WG-Docss
     - draft-ietf-isis-sbfd-discriminator-02
     - draft-ietf-isis-te-metric-extensions-07
     - draft-ietf-isis-prefix-attributes-01
     - draft-ietf-isis-segment-routing-extensions-05

    *** New IDs
     - draft-ginsberg-isis-remaining-lifetime-00
     - draft-ginsberg-isis-rfc4971bis-00
     - draft-chen-teas-rfc5316bis-00
     - draft-wang-isis-bier-lite-extension-00
     - draft-shen-isis-spine-leaf-ext-00

    *** Updated IDs
     - draft-you-isis-flowspec-extensions-02
     - draft-chen-isis-ttz-03
     - draft-xu-nvo3-isis-cp-01
     - draft-baker-ipv6-isis-dst-src-routing-04
     - draft-franke-isis-over-ipv6-01
     - draft-lamparter-homenet-isis-profile-01
     - draft-lamparter-isis-p2mp-01
     - draft-liu-isis-auto-conf-06
     - draft-xu-isis-encapsulation-cap-06

    *** Existing IDs
     - draft-xu-isis-service-function-adv-03
     - draft-decraene-isis-lsp-lifetime-problem-statement-00
     - draft-ginsberg-isis-l2bundles-00


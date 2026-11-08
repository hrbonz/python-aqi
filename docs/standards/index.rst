Standards archive
=================

The breakpoint tables in ``aqi.algos`` come from official documents. Reference
documents move or disappear (the Chinese government pages especially), so a
copy of each one is kept here, next to the code that implements it.

The PDFs live in ``docs/standards/`` in the git repository. They are **not**
part of the sdist or the wheel, only of the documentation.

.. list-table::
   :header-rows: 1
   :widths: 30 22 48

   * - Document
     - Implemented by
     - Notes
   * - :download:`EPA TAD, September 2012 <epa-tad-2012-09_EPA-454-B-12-001.pdf>`
     - nothing (historical)
     - PM2.5 Good band 0-15.4, ozone 8h 1997 bands. Kept to show what the
       2013 revision changed.
   * - :download:`EPA TAD, December 2013 <epa-tad-2013-12_EPA-454-B-13-001.pdf>`
     - ``aqi.algos.epa.EPA_2012``
     - PM2.5 Good band 0-12.0, ozone 8h 1997 bands (0.059/0.075/0.095/0.115):
       the tables python-aqi has always had.
   * - :download:`Federal Register 78 FR 3286 <epa-fr-2013-01-15_78FR3286.pdf>`
     - ``aqi.algos.epa.EPA_2012``
     - Page 3286 of the PM NAAQS final rule (15 January 2013) with the
       revised 40 CFR 58 Appendix G. The whole rule (203 pages, document
       2012-30946) is not archived.
   * - :download:`EPA TAD, September 2018 <epa-tad-2018-09_EPA-454-B-18-007.pdf>`
     - ``EPA_2015`` (planned, #40)
     - Ozone 8h breakpoints of the 2015 standard (0.054/0.070/0.085/0.105/0.200).
       First revision with the "Beyond the AQI" Q&A.
   * - :download:`EPA TAD, May 2024 <epa-tad-2024-05_EPA-454-B-24-002.pdf>`
     - ``EPA_2024`` (planned, #40)
     - 2024 PM2.5 breakpoints. Table 6 and its footnote 4 define the
       Hazardous band and how values above 500 are computed.
   * - :download:`EPA TAD, May 2026 <epa-tad-2026-05_EPA-403-B-26-003.pdf>`
     - ``EPA_2024`` (planned, #40)
     - Current edition. Same breakpoints as the May 2024 edition, it only
       gets a new document number and corrects the ozone worked example
       (0.78 written for 0.078, 0.14 for 0.014).
   * - :download:`AQI daily report regulation, 2nd draft, 2011 <hj-aqi-daily-2011-03-draft2.pdf>`
     - nothing (historical)
     - 二次征求意见稿 of what became HJ 633-2012, still titled "AQI daily
       report technical regulation". Kept to show where the table came from.
   * - :download:`HJ 633-2012 <hj633-2012.pdf>`
     - ``aqi.algos.mep.MEP_2012``
     - Technical Regulation on Ambient Air Quality Index (on trial).
   * - :download:`HJ 633-2026 <hj633-2026.pdf>`
     - ``MEP_2026`` (planned, #41)
     - Replaces HJ 633-2012. A scan without a text layer, the IAQI table is
       transcribed in :doc:`hj633-2026-table`.
   * - :download:`GB 3095-2012 <gb3095-2012.pdf>`
     - context
     - Ambient air quality standard, the concentration limits the HJ 633-2012
       IAQI 100 values are based on.
   * - :download:`GB 3095-2026 <gb3095-2026.pdf>`
     - context
     - Replaces GB 3095-2012, same date as HJ 633-2026. A scan without a text
       layer.

Provenance
----------

.. list-table::
   :header-rows: 1
   :widths: 24 20 56

   * - File
     - Published / effective
     - Source
   * - ``epa-tad-2012-09_EPA-454-B-12-001.pdf``
     - September 2012
     - EPA, document EPA-454/B-12-001. Copy from the maintainer's archive
       (file dated 2014-09-03). Also at the `UNT web archive
       <https://webarchive.library.unt.edu/web/20121006175057/http://www.epa.gov/airnow/aqi-technical-assistance-document-sep2012.pdf>`_.
   * - ``epa-tad-2013-12_EPA-454-B-13-001.pdf``
     - December 2013
     - EPA, document EPA-454/B-13-001. Copy from the maintainer's archive
       (file dated 2014-11-12), original URL not recorded.
   * - ``epa-fr-2013-01-15_78FR3286.pdf``
     - 2013-01-15
     - Federal Register, Vol. 78, No. 10, p. 3286, extract of the final rule
       2012-30946. Copy from the maintainer's archive (file dated 2014-11-18).
   * - ``epa-tad-2018-09_EPA-454-B-18-007.pdf``
     - September 2018
     - EPA, document EPA-454/B-18-007. Copy from the maintainer's archive
       (file dated 2023-03-03). Also at `airnow.gov
       <https://www.airnow.gov/sites/default/files/2020-05/aqi-technical-assistance-document-sept2018.pdf>`_.
   * - ``epa-tad-2024-05_EPA-454-B-24-002.pdf``
     - May 2024 (the PM2.5 change took effect 2024-05-06)
     - EPA, document EPA-454/B-24-002. Copy from the maintainer's archive
       (added 2026-11-07). Publication page: `AirNow
       <https://www.airnow.gov/publications/air-quality-index/technical-assistance-document-for-reporting-the-daily-aqi/>`_.
   * - ``epa-tad-2026-05_EPA-403-B-26-003.pdf``
     - May 2026
     - EPA, document EPA-403/B-26-003 (the last page still carries
       EPA-454/B-24-002, May 2024). Downloaded 2026-11-08 from `AirNow
       <https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf>`_,
       the URL always serves the current edition, so this copy is the one
       that was there on that date. The publication page is the same as for
       the 2024 edition.
   * - ``hj-aqi-daily-2011-03-draft2.pdf``
     - 2011-02-24 (letter 环办函〔2011〕200号), comments due 2011-03-10
     - Ministry of Environmental Protection, draft sent for comment, `MEE
       page <https://www.mee.gov.cn/gkml/hbb/bgth/201103/t20110301_201301.htm>`_.
       Copy from the maintainer's archive (file dated 2014-09-03), its file
       name ``W020110301385498176520.pdf`` is the page's attachment. The
       explanatory notes (编制说明) are on the same page, not archived.
   * - ``hj633-2012.pdf``
     - 2012-02-29 / 2016-01-01 (dates on the cover)
     - Ministry of Environmental Protection (now MEE), announcement 2012 No. 8,
       electronic edition ("请以中国环境科学出版社出版的正式标准文本为准").
       Copy from the maintainer's archive (file dated 2015-01-28), not
       downloaded from the links below. Official `MEE page
       <https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/201203/t20120302_224166.shtml>`_
       (marked as repealed from 2026-03-01) and its `PDF
       <https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/201203/W020250407406362045613.pdf>`_.
   * - ``hj633-2026.pdf``
     - 2026-02-14 / 2026-03-01 (dates on the cover)
     - Ministry of Ecology and Environment, `publication page
       <https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/202602/t20260225_1144441.shtml>`_
       (the page links the PDF), announced with `this notice
       <http://www.mee.gov.cn/xxgk2018/xxgk/xxgk01/202602/t20260224_1144403.html>`_.
       Copy from the maintainer's archive
       (added 2026-11-07).
   * - ``gb3095-2012.pdf``
     - 2012-02-29 / 2016-01-01 (dates on the cover)
     - Ministry of Environmental Protection and AQSIQ, announcement 2012 No. 7,
       electronic edition. Copy from the maintainer's archive (file dated
       2014-09-03), not downloaded from the links below. Official `MEE page
       <https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqhjzlbz/201203/t20120302_224165.shtml>`_
       (marked as repealed from 2026-03-01), it links a `PDF
       <https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqhjzlbz/201203/W020250407403788086276.pdf>`_.
   * - ``gb3095-2026.pdf``
     - 2026-02-13 / 2026-03-01 (dates on the cover)
     - Ministry of Ecology and Environment and SAMR, `MEE page
       <https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqhjzlbz/202602/t20260225_1144419.shtml>`_
       (the page links the PDF). Copy from the maintainer's archive (added
       2026-11-07).

Other MEE pages
---------------

Not archived, listed so the trail can be followed:

* HJ 633-2012 `announcement
  <http://www.mee.gov.cn/gkml/hbb/bgg/201203/t20120302_224146.htm>`_ (2012-03-02).
* `Letter <http://www.mee.gov.cn/gkml/hbb/bgth/201111/t20111116_220136.htm>`_
  of November 2011 asking for comments on the 2nd draft of GB 3095 and the 3rd
  draft of the AQI daily report regulation.
* `Notice <http://www.mee.gov.cn/xxgk2018/xxgk/xxgk06/202512/t20251215_1137858.html>`_
  of December 2025 asking for comments on the draft GB 3095 and two other
  standards, the step before GB 3095-2026 and HJ 633-2026.
* The `MEE index of ambient air quality standards
  <https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqhjzlbz/>`_ also lists
  the older and related ones, none of them archived: GB 3095-1996 (`page
  <https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqhjzlbz/199612/t19961206_67502.shtml>`_,
  repealed 2016-01-01), GB 9137-88 (protection of crops, repealed
  2016-01-01), GB/T 18883-2002 (indoor air, repealed 2023-02-01) and
  GB/T 27630-2011 (in-vehicle air). The index shows no 1982 or 2000/2002
  version of GB 3095.
* The search used to find them: `环境空气质量指数
  <https://www.mee.gov.cn/searchnew/?searchword=%E7%8E%AF%E5%A2%83%E7%A9%BA%E6%B0%94%E8%B4%A8%E9%87%8F%E6%8C%87%E6%95%B0>`_.

Redistribution
--------------

* The EPA documents and the Federal Register are works of the United States
  government, they are in the public domain.
* The HJ and GB documents are the electronic editions the Chinese ministries
  publish for free on their website. Their redistribution terms are not
  stated in the documents and have not been checked by a lawyer. They are
  archived for reference only, if a rights holder asks for removal, they will
  be removed. The printed editions of the standards are the official texts.

Adding a document
-----------------

Add the PDF to ``docs/standards/``, a row in both tables above, and cite it in
the docstring of the class that implements it. Scanned PDFs get a transcribed
table next to them.

.. toctree::
   :hidden:

   hj633-2026-table

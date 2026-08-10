## Wiki-note

### Properties
title: "Hong Kong FIR: ADS-B, Flight Plans, and ATS/PBN Routes"
type: concept
summary: "This note consolidates requirements for ADS-B Out equipment, flight plan submission, and ATS/PBN route structure within the Hong Kong FIR, including compliance standards, filing procedures, and route specifications."
sources: ["[[raw/sources/AIP_17july2026]]"]
source_count: 1
keywords: ["ADS-B", "Hong Kong FIR", "flight plan", "ATS routes", "PBN routes"]
last_updated: 2026-08-05

## Content
## ADS-B Out Requirements

All aircraft flying within the Hong Kong FIR at or above F290 must be equipped with ADS-B Out complying with RTCA DO-260 (ES Version 0), DO-260A (ES Version 1), or DO-260B (ES Version 2) as per ICAO Annex 10 Volume IV and Doc 9871. Acceptable means of compliance include EASA AMC 20-24, CS-ACNS Subpart D, FAA AC 20-165A, or CASA CAO 20.18 Appendix XI. If equipment does not comply, it must be deactivated or set to transmit zero for NUCp/NIC/NAC/SIL. Non-compliant aircraft are not given priority and may be subject to traffic conditions. If ADS-B becomes unserviceable in flight, ATC must be informed. Operational approval from State of Registry is no longer required. In flight plans, the appropriate ADS-B designator must be indicated in item 10, and the Aircraft Identification (item 7) must be replicated exactly as the Flight ID, either as ICAO three-letter designator plus flight identification (e.g., KLM511) or registration marking (e.g., EIAKO), with no zeros, hyphens, or spaces added if less than 7 characters.

## Flight Plan Submission Requirements

All aircraft conducting IFR flights within the Hong Kong FIR must file a flight plan, except authorized operators may submit a CAD-approved flight notification form for local VFR flights. For flights departing HKIA, there are three filing methods: Private Communication Network, AFTN (scheduled flights only), and Flight Plan Form DCA6a.

- **Private Communication Network**: Most effective and widely used, providing an online form that mimics ICAO format with customizations: default address VHHHZPZA, an 'AD/' field for up to 40 AFTN addresses (VHHHZPZA not allowed), and Field 19 for supplementary info (not transmitted normally, but available as SPL on request). The system performs validity checks including syntactic checks on alpha/digit fields and time format, semantic checks on aircraft type and location indicators, route syntax per ICAO Doc 4444 Appendix 2, AFTN address checking, and Field 18 sorting.
- **AFTN filing**: Only for scheduled operations, addressed to VHHHZPZA, with up to 7 addressees per line in the AD field. Overseas AFTN addresses must be registered with AIMC (email bo@cad.gov.hk) and must match the registered address.
- **Flight Plan Form DCA6a**: Must be printed legibly, no manuscript entries, submitted by hand or fax (2910 1180).

Changes to filed flight plans must be communicated to AIMC by telephone; operators must not send DLA, CHG, or CNL themselves. For inbound or transiting flights, file to VHHKZQZX via AFTN. Flight plans can be filed up to 5 days (120 hours) before EOBT, and at least 3 hours prior is required; less than 3 hours may cause ATFM delay. Delays of 15 minutes beyond EOBT require DLA or new FPL.

## ATS Routes Overview

The Hong Kong FIR ATS routes are detailed in ENR 3.1, with each route defined by a designator (e.g., A1, A202, A461, A470, A583, B330, G581, G86) and a series of significant points with coordinates. Routes have specified upper/lower limits (often UNL to 8000 ft AMSL), airspace classification (mostly Class A, with some segments Class C), lateral limits (typically 50 NM, but 12 NM for some segments), and FL series (Odd/Even). Controlling units are primarily Hong Kong Radar with primary (PRI) and secondary (SRY) frequencies. Compulsory ATS reporting points are designated for all aircraft (e.g., IKELA, ELATO, SIKOU, BEKOL, NOMAN, TAMOT, DOTMI, SABNO, KAPLI) while other waypoints are compulsory for non-jet aircraft only. Routes may have specific remarks such as one-way operations (e.g., A461 northbound only, G86 eastbound only, B330 southbound normally), RVSM airspace references (FL290-410), and PBN route overlays (e.g., P901 above FL285 on A1). For airspace classification within or above Hong Kong CTR/UCARAs, refer to ENR 1.4 and ENR 2.1.

## PBN Routes

PBN routes in Hong Kong FIR are listed in ENR 3.3, with designations like L642 (RNP 4), M750 (RNAV 5), M771 (RNP 4), M772 (RNP 10), P901 (RNP 10), and Q1 (RNP 10). These routes have specific navigation performance requirements: RNP 4 and RNP 10 require on-board performance monitoring and alerting, while RNAV 5 requires basic area navigation. Routes are one-way, with upper limits often UNL and lower limits at 8000 ft AMSL or FL 270/285. Airspace classification is Class A, with FL series (Odd/Even) as specified. Controlling units are Hong Kong Radar with PRI and SRY frequencies. For example, L642 runs from EPKAL to BIGEX via ENBOK and EPDOS, with even FL series. M750 runs from KILOG to ENVAR, applicable only under radar environment with ATC monitoring navigation performance. M771 runs from DOSUT to BIGEX via DULOP and DUMOL, with odd FL series. M772 runs from ASOBA to DULOP, with upper limit FL 460 and lower FL 285. P901 runs from IKELA to BIGEX via IDOSI, with odd/even FL series. Q1 runs from DULOP to CARSO, with specific joining levels from M771 and M772. Compulsory reporting points for all aircraft include EPKAL, DOSUT, DULOP, ASOBA, IKELA, and ENVAR.

## Related References

- [[Aircraft Radio and Navigation Equipment Requirements in Hong Kong FIR]]
- [[Flight Plan Addressing]]
- [[Flight Plan Route Requirements]]

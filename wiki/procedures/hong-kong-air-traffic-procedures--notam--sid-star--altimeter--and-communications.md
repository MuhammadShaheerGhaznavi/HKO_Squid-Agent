## Wiki-note

### Properties
title: "Hong Kong Air Traffic Procedures: NOTAM, SID/STAR, Altimeter, and Communications"
type: procedure
summary: "This note consolidates Hong Kong air traffic procedures covering NOTAM/SNOWTAM distribution, SID/STAR operations, altimeter settings, and communication requirements within the Hong Kong FIR."
sources: ["[[raw/sources/AIP_17july2026]]"]
source_count: 1
keywords: ["NOTAM", "SNOWTAM", "SID", "STAR", "altimeter", "Hong Kong FIR"]
last_updated: 2026-08-11

## Content
## NOTAM and SNOWTAM Procedures

- NOTAMs in Hong Kong are distributed in two series: Series A for international distribution and Series C for local distribution. Each NOTAM has a serial number based on the calendar year. A checklist of NOTAMs in force is issued monthly.
- Foreign NOTAM offices can retrieve Hong Kong NOTAMs by sending a request message (RQN) to VHHHYNYX. Formats: `RQN VHHH A0115/14` for a single NOTAM, or `RQN VHHH A0201/14 - A0205/14` for a series.
- SNOWTAM is issued when the runway at Hong Kong International Airport (HKIA) is wholly or partly contaminated by standing water.

## Standard Instrument Arrival (STAR) Procedures

- IFR arrivals expect a Standard Instrument Arrival (STAR) unless notified. RNP 1 STARs are implemented; see GEN 1.5 para 3.5.3 for requirements.
- Pilots must plan descent profile per published STAR to ensure vertical separation.
- Speed control is in force unless cancelled; arriving aircraft fly at 250 KIAS or less below 10,000 ft. Minimum inter-arrival spacing at HKIA is 3.0 NM.
- Pilots must inform Approach Control on first contact if unable to comply with speeds or if final approach speed is below 125 KIAS.
- If unable RNP or loss of GNSS, revert to RNAV 1 (DME/DME/IRU) and inform ATC using phraseology 'UNABLE RNP 1 [DUE TO (reason)]'. If ground aids unavailable, ATC provides alternative clearance or vectoring.

## Standard Instrument Departure (SID) Procedures

- IFR departures expect a Standard Instrument Departure (SID) unless notified. RNP 1 SIDs are implemented; see GEN 1.5 para 3.5.3.
- On first contact with 'Hong Kong Departure', pilot states call sign, passing altitude to nearest 100 ft, and assigned altitude.
- Speed control is in force unless cancelled; departing aircraft fly at 250 KIAS or less below 10,000 ft.
- Aircraft must follow SID track and connect to appropriate terminal transition route (ENR 3.1).
- Final cruising level notification at least 10 minutes prior to crossing TMA boundary, except via BEKOL where climb to S0480 or above is expected. Aircraft must reach assigned cruising level at or before TMA boundary; failure may result in loss of separation.
- If unable RNP, revert to RNAV 1 and inform ATC; on ground, clearance for non-RF SID using RNAV 1 is issued.

## Altimeter Setting Procedures

- Transition altitude is 9,000 ft; transition level is FL110. When QNH at HKIA is 979 hPa or below, ATC informs pilots of transition level via ATIS or voice. Lowest QNH recorded is 953.2 hPa.
- Aircraft beyond 50 NM from HKIA, or within 50 NM but at or above transition level, use 1013.2 hPa. Within 50 NM and at or below transition altitude, use local QNH.
- Aircraft within 50 NM shall not flight plan to cruise between transition altitude and FL120.
- Arriving aircraft change to QNH when 50 NM from airport if at or below transition altitude, or when vacating transition level on descent. Departing aircraft change to 1013.2 hPa when 50 NM from airport if at or below transition altitude, or when vacating transition altitude on climb.
- QNH reports on ATIS 128.2 MHz and 127.05 MHz; QFE on request. Values in hectopascals, rounded down.
- IFR cruising levels per ICAO Annex 2 Appendix 3. VFR cruising levels above 3,000 ft: magnetic track 000°-179° odd thousands plus 500 ft; 180°-359° even thousands plus 500 ft.
- Vertical separation minima: 1,000 ft at or below FL410, 2,000 ft above FL410. Minimum rate of change 500 ft/min assumed; pilots using lower rate must inform ATC.

## General Rules and Communication Procedures in Hong Kong FIR

- Air traffic rules in Hong Kong FIR conform to Annex 2 and Annex 11, the Air Navigation (Hong Kong) Order 1995, ICAO Doc 4444 PANS/ATM, and Regional Supplementary Procedures MID/ASIA Region, except for differences in GEN 1.7.
- For traffic entering Hong Kong FIR, aircraft must establish two-way radio communication with Hong Kong Radar on specified frequencies at least 10 NM before certain reporting points (or 3 minutes for others). Key reporting points and frequencies (primary/secondary):
  - ELATO (A1(E)/G581) 121.3/128.125
  - SIKOU (A202/R339) 127.1/123.7
  - NOMAN (A461/M501) 132.15/129.9
  - DOTMI (A470) 121.3/128.125
  - SABNO (A583) 128.75/129.9
  - TAMOT (B330) 127.1/123.7
  - KAPLI (G86) 132.15/129.9
  - LELIM (M503) 121.3/128.125
  - DOSUT (M771) 122.95/135.6
  - DUMOL (M771) 128.75/129.9 (at DUMOL)
  - ASOBA (M772) 122.95/135.6
  - IKELA (A1(W)) 125.325/132.775
  - SIERA (R473) 127.55/134.3 (3 min prior)
  - MCU DVOR/DME 123.95/132.225 (3 min prior)
  - ROMEO 123.95/132.225 (3 min prior)
- Initial call must include call sign, position (relative to reporting point), level (including passing and cleared levels), transponder code, and other pertinent info.
- Aircraft entering outside controlled airspace but wishing to join must request clearance and remain clear until received.
- After take-off, on first contact with 'Hong Kong Departure', pilot states call sign, passing altitude (nearest 100 ft), and assigned altitude.
- Approach Control uses phraseology '(Call sign) contact Hong Kong Director 119.5 MHZ with call sign only' to reduce congestion.
- Aircraft leaving Hong Kong FIR remain on control frequency until instructed.
- Position reports are made at reporting points; radar-identified aircraft may omit them when informed.
- Pilots must read back: ATC route clearances, clearances to enter/land/take off/cross/backtrack runway, other clearances including conditional, runway in use, altimeter settings, SSR codes, level instructions, heading and speed instructions, and transition levels when required.

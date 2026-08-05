## Wiki-note

### Properties
title: "Bigtable vs. Related Systems"
type: synthesis
summary: "Bigtable is compared to various distributed storage and database systems, highlighting its unique position in providing a sparse, semi-structured data model with high performance."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["comparison", "distributed storage", "databases", "key-value", "column-oriented"]
last_updated: 2026-08-01

## Content
Bigtable differs from Boxwood, which provides lower-level infrastructure for building higher-level services, while Bigtable directly supports client applications. Unlike distributed hash tables (CAN, Chord, Tapestry, Pastry) that address Internet-scale concerns like variable bandwidth and Byzantine faults, Bigtable focuses on centralized control and fail-stop assumptions. The key-value model of distributed B-trees is considered too limiting; Bigtable's richer model supports sparse semi-structured data with efficient flat-file representation and locality groups for tuning. Compared to parallel databases like Oracle RAC (shared disks) and DB2 Parallel Edition (shared-nothing), Bigtable uses GFS and Chubby instead of shared disks and lock managers, and does not provide full relational transactions. Locality groups achieve compression and read performance similar to column-oriented systems like C-Store and Sybase IQ. Bigtable's memtable/SSTable approach is analogous to Log-Structured Merge Trees, and it shares characteristics with C-Store but differs in API and performance focus.

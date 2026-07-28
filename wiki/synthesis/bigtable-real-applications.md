## Wiki-note

### Properties
title: "Bigtable Real Applications"
type: synthesis
summary: "Bigtable is used by over 60 Google products including Google Analytics, Google Earth, and Personalized Search, handling diverse workloads from batch processing to low-latency serving."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["Google Analytics", "Google Earth", "Personalized Search", "MapReduce", "real-world usage"]
last_updated: 2026-07-29

## Content
Bigtable supports a wide range of applications: [[Google Analytics]] stores raw click data (~200 TB) and summary tables (~20 TB) with high compression; [[Google Earth]] uses tables for imagery preprocessing (~70 TB) and serving (~500 GB) with in-memory column families; [[Personalized Search]] stores per-user data with many column families and uses [[MapReduce]] for profile generation.

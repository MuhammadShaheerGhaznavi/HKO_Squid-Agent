## Wiki-note

### Properties
title: "Google Analytics on Bigtable"
type: entity
summary: "Google Analytics uses Bigtable to store raw click data and summary tables for web traffic analysis."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Google Analytics", "raw click table", "summary table", "MapReduce", "compression"]
last_updated: 2026-08-01

## Content
Google Analytics (analytics.google.com) helps webmasters analyze traffic patterns. It uses two main tables in Bigtable. The raw click table (~200 TB) stores a row per end-user session, with row names as tuples of website name and session creation time, ensuring sessions for the same site are contiguous and chronologically sorted. This table compresses to 14% of its original size. The summary table (~20 TB) contains predefined summaries per website, generated from the raw click table via periodically scheduled MapReduce jobs. The overall system's throughput is limited by GFS throughput. The summary table compresses to 29% of its original size. This shows Bigtable's use for both raw data storage and derived summaries.

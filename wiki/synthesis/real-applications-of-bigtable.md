## Wiki-note

### Properties
title: "Real Applications of Bigtable"
type: synthesis
summary: "Bigtable is used by over sixty Google products including Google Analytics, Google Earth, and Personalized Search, handling diverse workloads from batch processing to low-latency serving."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["Google Analytics", "Google Earth", "Personalized Search", "MapReduce", "real applications"]
last_updated: 2026-07-29

## Content
Bigtable is used by Google Analytics for storing raw click data (~200 TB) and summary tables (~20 TB), Google Earth for imagery preprocessing (~70 TB) and serving (~500 GB), and Personalized Search for per-user data. These applications use MapReduce for data processing and rely on Bigtable's scalability, compression, and low-latency access.

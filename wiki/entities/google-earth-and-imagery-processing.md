## Wiki-note

### Properties
title: "Google Earth and Imagery Processing"
type: entity
summary: "Google Earth uses Bigtable for preprocessing raw imagery and serving high-resolution satellite images."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Google Earth", "imagery", "preprocessing", "serving", "MapReduce"]
last_updated: 2026-08-01

## Content
Google Earth and Google Maps provide access to high-resolution satellite imagery. The system uses one table for preprocessing raw imagery (~70 TB) and a different set of tables for serving client data. The preprocessing table stores raw imagery, which is cleaned and consolidated into final serving data. Since images are already compressed, Bigtable compression is disabled. Each row corresponds to a geographic segment, with row names ensuring adjacent segments are stored near each other. A column family tracks data sources, with many sparse columns. The preprocessing pipeline relies heavily on MapReduce over Bigtable, processing over 1 MB/sec of data per tablet server. The serving system uses a relatively small table (~500 GB) that must serve tens of thousands of queries per second per datacenter with low latency, hosted across hundreds of tablet servers with in-memory column families.

## Wiki-note

### Properties
title: "Bigtable Performance Optimizations"
type: synthesis
summary: "Bigtable uses locality groups, caching, compression, Bloom filters, and efficient commit log handling to improve performance."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["locality group", "scan cache", "block cache", "compression", "Bloom filter", "commit log"]
last_updated: 2026-07-29

## Content
Bigtable optimizations include: locality groups to separate column families into different SSTables; two-level caching (Scan Cache and Block Cache); configurable compression (Bentley-McIlroy + fast compressor); Bloom filters to skip unnecessary SSTable reads; and a single commit log per tablet server with two writing threads to mitigate GFS latency spikes.

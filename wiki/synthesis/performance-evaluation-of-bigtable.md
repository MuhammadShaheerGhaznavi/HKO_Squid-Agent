## Wiki-note

### Properties
title: "Performance Evaluation of Bigtable"
type: synthesis
summary: "Bigtable performance benchmarks show high throughput for sequential writes, scans, and memory reads, with random reads being slower due to disk seeks. Aggregate throughput scales nearly linearly with the number of tablet servers."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["performance", "throughput", "scalability", "random read", "sequential write", "scan"]
last_updated: 2026-07-29

## Content
Performance benchmarks on a cluster with up to 500 tablet servers show that sequential writes, scans, and random reads from memory achieve high throughput (e.g., 8000+ ops/sec per server for memory reads). Random reads are slower (~1200 ops/sec per server) due to disk seeks. Aggregate throughput scales nearly linearly, though per-server throughput drops slightly due to load imbalance and network contention.

## Wiki-note

### Properties
title: "Bigtable Benchmark Workloads"
type: concept
summary: "Details the six benchmarks used to evaluate Bigtable: sequential/random reads and writes, scans, and in-memory random reads."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["benchmark", "random read", "sequential write", "scan", "in-memory"]
last_updated: 2026-08-01

## Content
Bigtable was tested with six benchmarks: sequential writes, random writes, sequential reads, random reads, scans, and random reads from memory. Sequential writes used row keys 0 to R-1, partitioned into 10N ranges assigned dynamically to clients. Random writes hashed row keys modulo R to spread load uniformly. Reads mirrored writes, with scans using the API to fetch ranges in one RPC. In-memory reads used a locality group marked as in-memory, with data reduced to 100 MB per server to fit memory. These benchmarks measure throughput for 1000-byte values, with scans reducing RPC overhead. The workloads are designed to isolate different performance aspects, such as disk I/O, network, and CPU.

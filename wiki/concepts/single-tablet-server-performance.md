## Wiki-note

### Properties
title: "Single Tablet Server Performance"
type: concept
summary: "Analyzes the performance of a single tablet server, highlighting the impact of block size, caching, and commit log on read/write speeds."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["tablet server", "random read", "block cache", "commit log", "scan"]
last_updated: 2026-08-01

## Content
With one tablet server, random reads are an order of magnitude slower than other operations because each read fetches a 64 KB SSTable block from GFS to use a single 1000-byte value, achieving ~1200 reads/sec (75 MB/s), saturating CPU and network. In-memory reads are faster as they avoid GFS. Writes perform well because they are appended to a single commit log and group-committed to GFS, with no difference between random and sequential writes. Sequential reads benefit from the block cache, which stores fetched blocks for subsequent reads. Scans are fastest as they amortize RPC overhead over many values. These results show that block size and caching are critical for read performance, and that write performance is efficient due to log-based writes.

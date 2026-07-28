## Wiki-note

### Properties
title: "Commit Log Implementation"
type: concept
summary: "Bigtable uses a single commit log per tablet server to improve write performance, with log sorting for efficient recovery and dual log threads to handle GFS latency spikes."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["commit log", "group commit", "log sorting", "recovery", "dual log threads"]
last_updated: 2026-07-29

## Content
Each tablet server appends mutations to a single commit log, co-mingling mutations for different tablets. This improves write throughput via group commit. For recovery, log entries are sorted by (table, row name, log sequence number) to allow efficient sequential reads. Two log writing threads are used to mitigate GFS latency spikes; writes switch to the other thread if the active log performs poorly.

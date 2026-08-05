## Wiki-note

### Properties
title: "Bigtable Performance Evaluation Setup"
type: concept
summary: "Describes the hardware and configuration used to benchmark Bigtable, including tablet servers, GFS, and client machines."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Bigtable", "performance", "benchmark", "GFS", "tablet server"]
last_updated: 2026-08-01

## Content
The performance evaluation of Bigtable was conducted in a cluster with tablet servers configured with 1 GB memory, writing to a GFS cell of 1786 machines, each with two 400 GB IDE hard drives. Client machines, equal in number to tablet servers, generated load, each with dual-core Opteron 2 GHz chips and gigabit Ethernet. The network was a two-level tree with 100-200 Gbps aggregate bandwidth at the root, and round-trip times under a millisecond. All machines ran GFS servers, with some also running tablet servers or clients, and shared with other jobs. The benchmarks used 1000-byte values, with R row keys chosen so each server read/wrote ~1 GB. This setup ensures that the results reflect Bigtable's performance under realistic conditions, with network and CPU as potential bottlenecks.

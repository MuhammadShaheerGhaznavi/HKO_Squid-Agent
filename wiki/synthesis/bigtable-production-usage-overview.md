## Wiki-note

### Properties
title: "Bigtable Production Usage Overview"
type: synthesis
summary: "As of August 2006, Bigtable was used in hundreds of Google clusters, handling high request volumes and diverse workloads."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["production", "clusters", "requests", "tablet servers", "Google"]
last_updated: 2026-08-01

## Content
As of August 2006, there were 388 non-test Bigtable clusters running in various Google machine clusters, with a combined total of about 24,500 tablet servers. Many clusters were used for development and idle for significant periods. One group of 14 busy clusters with 8069 total tablet servers saw an aggregate volume of more than 1.2 million requests per second, with incoming RPC traffic of about 741 MB/s and outgoing RPC traffic of about 16 GB/s. Tables varied widely in size, cell size, memory usage, and schema complexity. Some tables served user-facing data, while others supported batch processing. This demonstrates Bigtable's scalability and adaptability to different workloads.

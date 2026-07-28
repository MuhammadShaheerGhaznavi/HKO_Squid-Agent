# Wiki Knowledge Index
*Last Index Sync: 2026-07-29*


## Concepts

| Title | Summary | Keywords | Last Updated |
| :--- | :--- | :--- | :--- |
| [[concepts/bigtable-data-model\|Bigtable Data Model]] | Bigtable is a sparse, distributed, persistent multidimensional sorted map indexed by row key, column key, and timestamp. | `Bigtable`, `data model`, `row key`, `column key`, `timestamp`, `sparse`, `sorted map` | 2026-07-29 |
| [[concepts/bigtable-tablet-location-hierarchy\|Bigtable Tablet Location Hierarchy]] | Bigtable uses a three-level B+ tree-like hierarchy to locate tablets, with a root tablet stored in Chubby. | `tablet location`, `root tablet`, `METADATA table`, `B+ tree`, `Chubby` | 2026-07-29 |
| [[concepts/commit-log-implementation\|Commit Log Implementation]] | Bigtable uses a single commit log per tablet server to improve write performance, with log sorting for efficient recovery and dual log threads to handle GFS latency spikes. | `commit log`, `group commit`, `log sorting`, `recovery`, `dual log threads` | 2026-07-29 |
| [[concepts/locality-groups-and-compression\|Locality Groups and Compression]] | Locality groups allow grouping column families into separate SSTables for efficient reads. Compression can be applied per locality group, using a two-pass scheme that achieves high ratios for clustered data. | `locality group`, `compression`, `Bentley-McIlroy`, `Bloom filter`, `in-memory` | 2026-07-29 |
| [[concepts/tablet-location-hierarchy\|Tablet Location Hierarchy]] | Bigtable uses a three-level B+ tree-like hierarchy for tablet location, with a Chubby file pointing to the root tablet, which points to METADATA tablets, which point to user tablets. | `tablet location`, `root tablet`, `METADATA table`, `Chubby`, `B+ tree` | 2026-07-29 |


## Entities

| Title | Summary | Keywords | Last Updated |
| :--- | :--- | :--- | :--- |
| [[entities/bigtable-api\|Bigtable API]] | The Bigtable API provides functions for creating and deleting tables and column families, as well as reading, writing, and scanning data. | `Bigtable`, `API`, `RowMutation`, `Scanner`, `MapReduce`, `Sawzall` | 2026-07-29 |
| [[entities/bigtable-building-blocks\|Bigtable Building Blocks]] | Bigtable is built on GFS, SSTable, and Chubby for storage, data format, and distributed coordination. | `GFS`, `SSTable`, `Chubby`, `distributed lock service`, `Paxos` | 2026-07-29 |


## Procedures

| Title | Summary | Keywords | Last Updated |
| :--- | :--- | :--- | :--- |
| [[procedures/bigtable-tablet-assignment-and-master-role\|Bigtable Tablet Assignment and Master Role]] | The master assigns tablets to tablet servers, monitors server liveness via Chubby, and handles load balancing and garbage collection. | `master`, `tablet server`, `Chubby`, `tablet assignment`, `load balancing` | 2026-07-29 |
| [[procedures/bigtable-tablet-serving-and-compactions\|Bigtable Tablet Serving and Compactions]] | Tablet state consists of SSTables and a memtable; writes are logged and applied to the memtable, and compactions merge SSTables to maintain performance. | `memtable`, `SSTable`, `commit log`, `minor compaction`, `major compaction`, `merging compaction` | 2026-07-29 |
| [[procedures/tablet-assignment-and-server-membership\|Tablet Assignment and Server Membership]] | Tablet assignment uses Chubby for server discovery and lease management. The master monitors the servers directory, assigns tablets, and handles server failures by reassigning tablets. | `tablet assignment`, `Chubby`, `master`, `tablet server`, `lease`, `failure detection` | 2026-07-29 |
| [[procedures/tablet-serving-and-compactions\|Tablet Serving and Compactions]] | Tablet serving involves a memtable for recent writes and SSTables for persistent data. Compactions (minor, merging, major) convert memtables to SSTables and merge SSTables to reduce read overhead. | `memtable`, `SSTable`, `minor compaction`, `merging compaction`, `major compaction`, `commit log` | 2026-07-29 |


## Synthesis

| Title | Summary | Keywords | Last Updated |
| :--- | :--- | :--- | :--- |
| [[synthesis/bigtable-lessons-learned\|Bigtable Lessons Learned]] | Key lessons include the importance of simple designs, handling diverse failures, delaying features until needed, and thorough monitoring. | `lessons learned`, `failure handling`, `simple design`, `monitoring`, `feature delay` | 2026-07-29 |
| [[synthesis/bigtable-performance-optimizations\|Bigtable Performance Optimizations]] | Bigtable uses locality groups, caching, compression, Bloom filters, and efficient commit log handling to improve performance. | `locality group`, `scan cache`, `block cache`, `compression`, `Bloom filter`, `commit log` | 2026-07-29 |
| [[synthesis/bigtable-real-applications\|Bigtable Real Applications]] | Bigtable is used by over 60 Google products including Google Analytics, Google Earth, and Personalized Search, handling diverse workloads from batch processing to low-latency serving. | `Google Analytics`, `Google Earth`, `Personalized Search`, `MapReduce`, `real-world usage` | 2026-07-29 |
| [[synthesis/lessons-learned-from-bigtable\|Lessons Learned from Bigtable]] | Key lessons include the importance of handling diverse failures, delaying feature additions until needed, proper monitoring, and the value of simple designs. | `lessons learned`, `failure handling`, `monitoring`, `simple design`, `feature creep` | 2026-07-29 |
| [[synthesis/performance-evaluation-of-bigtable\|Performance Evaluation of Bigtable]] | Bigtable performance benchmarks show high throughput for sequential writes, scans, and memory reads, with random reads being slower due to disk seeks. Aggregate throughput scales nearly linearly with the number of tablet servers. | `performance`, `throughput`, `scalability`, `random read`, `sequential write`, `scan` | 2026-07-29 |
| [[synthesis/real-applications-of-bigtable\|Real Applications of Bigtable]] | Bigtable is used by over sixty Google products including Google Analytics, Google Earth, and Personalized Search, handling diverse workloads from batch processing to low-latency serving. | `Google Analytics`, `Google Earth`, `Personalized Search`, `MapReduce`, `real applications` | 2026-07-29 |


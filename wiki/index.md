# Wiki Knowledge Index
*Last Index Sync: 2026-08-01*


## Concepts

| Title | Summary | Keywords | Last Updated |
| :--- | :--- | :--- | :--- |
| [[concepts/bigtable-acknowledgements-and-references\|Bigtable Acknowledgements and References]] | Lists contributors and references for the Bigtable paper. | `Bigtable`, `acknowledgements`, `references`, `OSDI 2006` | 2026-08-01 |
| [[concepts/bigtable-benchmark-workloads\|Bigtable Benchmark Workloads]] | Details the six benchmarks used to evaluate Bigtable: sequential/random reads and writes, scans, and in-memory random reads. | `benchmark`, `random read`, `sequential write`, `scan`, `in-memory` | 2026-08-01 |
| [[concepts/bigtable-data-model\|Bigtable Data Model]] | Bigtable is a sparse, distributed, persistent multidimensional sorted map indexed by row key, column key, and timestamp, with values as uninterpreted byte arrays. | `data model`, `row key`, `column key`, `timestamp`, `sparse map` | 2026-08-01 |
| [[concepts/bigtable-internals--compactions--compression--bloom-filters--and-commit-logs\|Bigtable Internals: Compactions, Compression, Bloom Filters, and Commit Logs]] | This note covers key internal mechanisms of Google's Bigtable: compactions (minor, merging, major), compression schemes, Bloom filters for read optimization, and commit-log implementation for recovery. | `Bigtable`, `compaction`, `compression`, `Bloom filter`, `commit log`, `SSTable` | 2026-08-01 |
| [[concepts/bigtable-overview-and-api\|Bigtable Overview and API]] | Bigtable is a distributed storage system developed at Google for managing structured data at scale. It provides a simple data model, supports a rich API for data manipulation, and integrates with other Google technologies like MapReduce and Sawzall. | `Bigtable`, `distributed storage`, `scalability`, `API`, `MapReduce`, `Sawzall` | 2026-08-01 |
| [[concepts/bigtable-performance-evaluation-setup\|Bigtable Performance Evaluation Setup]] | Describes the hardware and configuration used to benchmark Bigtable, including tablet servers, GFS, and client machines. | `Bigtable`, `performance`, `benchmark`, `GFS`, `tablet server` | 2026-08-01 |
| [[concepts/bigtable-scaling-behavior\|Bigtable Scaling Behavior]] | Examines how Bigtable throughput scales from 1 to 500 tablet servers, noting superlinear gains but sublinear scaling due to load imbalance. | `scaling`, `throughput`, `load balancing`, `tablet servers`, `aggregate` | 2026-08-01 |
| [[concepts/bigtable-system-components\|Bigtable System Components]] | Bigtable has three main components: a client library, a master server, and tablet servers, with the master handling metadata and tablet servers handling data. | `Bigtable`, `master`, `tablet server`, `client library`, `architecture` | 2026-08-01 |
| [[concepts/building-blocks-of-bigtable\|Building Blocks of Bigtable]] | Bigtable is built on GFS, SSTable, Chubby, and a cluster management system, each providing essential infrastructure for storage, locking, and coordination. | `GFS`, `SSTable`, `Chubby`, `cluster management`, `Paxos` | 2026-08-01 |
| [[concepts/caching-for-read-performance-in-bigtable\|Caching for Read Performance in Bigtable]] | Bigtable uses two levels of caching—Scan Cache and Block Cache—to improve read performance by reducing disk accesses. | `Scan Cache`, `Block Cache`, `caching`, `read performance`, `SSTable` | 2026-08-01 |
| [[concepts/exploiting-immutability-in-bigtable\|Exploiting Immutability in Bigtable]] | The immutability of SSTables simplifies concurrency control, garbage collection, and tablet splitting in Bigtable. | `immutability`, `SSTable`, `garbage collection`, `tablet splitting`, `concurrency` | 2026-08-01 |
| [[concepts/locality-groups-in-bigtable\|Locality Groups in Bigtable]] | Locality groups group column families into separate SSTables to improve read efficiency and allow per-group tuning. | `locality group`, `SSTable`, `column family`, `in-memory`, `read efficiency` | 2026-08-01 |
| [[concepts/single-tablet-server-performance\|Single Tablet Server Performance]] | Analyzes the performance of a single tablet server, highlighting the impact of block size, caching, and commit log on read/write speeds. | `tablet server`, `random read`, `block cache`, `commit log`, `scan` | 2026-08-01 |
| [[concepts/tablet-location-hierarchy\|Tablet Location Hierarchy]] | Bigtable uses a three-level B+-tree-like hierarchy to store tablet locations, with a Chubby file at the top, a root tablet, and METADATA tablets. | `tablet location`, `B+-tree`, `METADATA table`, `root tablet`, `Chubby` | 2026-08-01 |
| [[concepts/tablet-serving-and-data-storage\|Tablet Serving and Data Storage]] | Tablet persistent state is stored in GFS, with updates in a commit log and memtable, and reads merging SSTables and memtable. | `tablet serving`, `GFS`, `memtable`, `SSTable`, `commit log` | 2026-08-01 |


## Entities

| Title | Summary | Keywords | Last Updated |
| :--- | :--- | :--- | :--- |
| [[entities/google-analytics-on-bigtable\|Google Analytics on Bigtable]] | Google Analytics uses Bigtable to store raw click data and summary tables for web traffic analysis. | `Google Analytics`, `raw click table`, `summary table`, `MapReduce`, `compression` | 2026-08-01 |
| [[entities/google-earth-and-imagery-processing\|Google Earth and Imagery Processing]] | Google Earth uses Bigtable for preprocessing raw imagery and serving high-resolution satellite images. | `Google Earth`, `imagery`, `preprocessing`, `serving`, `MapReduce` | 2026-08-01 |
| [[entities/personalized-search-storage\|Personalized Search Storage]] | Personalized Search stores user queries and clicks in Bigtable, using per-user rows and column families for different action types. | `Personalized Search`, `user data`, `column families`, `replication`, `quota` | 2026-08-01 |


## Procedures

| Title | Summary | Keywords | Last Updated |
| :--- | :--- | :--- | :--- |
| [[procedures/bigtable-client-api\|Bigtable Client API]] | Bigtable provides a client API for creating and modifying tables, with operations like opening tables, writing data via RowMutation, and applying operations atomically. | `API`, `RowMutation`, `OpenOrDie`, `Apply`, `write` | 2026-08-01 |
| [[procedures/speeding-up-tablet-recovery\|Speeding up Tablet Recovery]] | Tablet recovery is accelerated by performing minor compactions before unloading a tablet, reducing the commit log state that needs to be replayed. | `tablet recovery`, `minor compaction`, `commit log`, `tablet server`, `master` | 2026-08-01 |
| [[procedures/tablet-assignment-and-master-startup\|Tablet Assignment and Master Startup]] | The master assigns tablets to tablet servers using Chubby for coordination, and follows a startup sequence to discover existing assignments. | `tablet assignment`, `master`, `Chubby`, `startup`, `lock` | 2026-08-01 |


## Synthesis

| Title | Summary | Keywords | Last Updated |
| :--- | :--- | :--- | :--- |
| [[synthesis/bigtable-conclusions-and-production-experience\|Bigtable Conclusions and Production Experience]] | Summarizes Bigtable's production history, user adoption, and future directions. | `Bigtable`, `production`, `conclusions`, `future work`, `Google` | 2026-08-01 |
| [[synthesis/bigtable-production-usage-overview\|Bigtable Production Usage Overview]] | As of August 2006, Bigtable was used in hundreds of Google clusters, handling high request volumes and diverse workloads. | `production`, `clusters`, `requests`, `tablet servers`, `Google` | 2026-08-01 |
| [[synthesis/bigtable-table-characteristics-in-production\|Bigtable Table Characteristics in Production]] | Production Bigtable tables vary widely in size, compression, cell count, column families, and memory usage, reflecting diverse use cases. | `table size`, `compression ratio`, `column families`, `locality groups`, `memory` | 2026-08-01 |
| [[synthesis/bigtable-vs--related-systems\|Bigtable vs. Related Systems]] | Bigtable is compared to various distributed storage and database systems, highlighting its unique position in providing a sparse, semi-structured data model with high performance. | `comparison`, `distributed storage`, `databases`, `key-value`, `column-oriented` | 2026-08-01 |
| [[synthesis/lessons-from-bigtable--failure-handling-and-system-design\|Lessons from Bigtable: Failure Handling and System Design]] | Bigtable's development revealed that large distributed systems face diverse failures beyond standard assumptions, and that simplicity in design is crucial for maintainability. | `failures`, `distributed systems`, `simplicity`, `monitoring`, `protocols` | 2026-08-01 |


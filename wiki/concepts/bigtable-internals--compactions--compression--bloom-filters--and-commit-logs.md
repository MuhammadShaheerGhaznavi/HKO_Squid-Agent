## Wiki-note

### Properties
title: "Bigtable Internals: Compactions, Compression, Bloom Filters, and Commit Logs"
type: concept
summary: "This note covers key internal mechanisms of Google's Bigtable: compactions (minor, merging, major), compression schemes, Bloom filters for read optimization, and commit-log implementation for recovery."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Bigtable", "compaction", "compression", "Bloom filter", "commit log", "SSTable"]
last_updated: 2026-08-01

## Content
## Compactions in Bigtable

As writes execute, the memtable grows. When it reaches a threshold, it is frozen, a new memtable is created, and the frozen one is converted to an SSTable and written to GFS. This **minor compaction** shrinks memory usage and reduces data to read from the commit log during recovery. Each minor compaction creates a new SSTable, so to bound the number of SSTables, Bigtable periodically performs a **merging compaction** in the background. A merging compaction reads a few SSTables and the memtable, writes out a new SSTable, and discards the inputs. A **major compaction** rewrites all SSTables into exactly one SSTable. Non-major compactions can contain special deletion entries that suppress deleted data in older SSTables, but major compactions produce SSTables with no deletion information or deleted data. Bigtable cycles through all tablets and regularly applies major compactions to reclaim resources and ensure deleted data disappears timely, which is important for services that store sensitive data.

## Compression in Bigtable

Clients can control compression for SSTables in a locality group, choosing the compression format and block size. The compression is applied per SSTable block, allowing small portions to be read without decompressing the entire file. Many clients use a two-pass custom scheme: the first pass uses Bentley and McIlroy's algorithm to compress long common strings across a large window, and the second uses a fast algorithm for repetitions in a 16 KB window. Both passes are fast, encoding at 100–200 MB/s and decoding at 400–1000 MB/s. This scheme achieves a 10-to-1 space reduction in Webtable, better than typical Gzip's 3-to-1 or 4-to-1, because rows from the same host are stored close together, allowing the algorithm to identify shared boilerplate. Compression ratios improve further when storing multiple versions of the same value. See also [[Locality Groups in Bigtable]].

## Bloom Filters in Bigtable

Read operations in Bigtable must read from all SSTables that constitute a tablet's state, which can cause many disk accesses if those SSTables are not in memory. To reduce this, clients can specify that Bloom filters be created for SSTables in a particular locality group. A Bloom filter allows the system to ask whether an SSTable might contain data for a specified row/column pair. This drastically reduces the number of disk seeks required for read operations, especially for applications where a small amount of tablet server memory is used for the filters. Additionally, most lookups for non-existent rows or columns do not need to touch disk at all. See also [[SSTable]] and [[Locality Groups in Bigtable]].

## Commit-Log Implementation in Bigtable

To avoid many concurrent log files in GFS, Bigtable appends mutations to a single commit log per tablet server, co-mingling mutations for different tablets. This improves performance via group commit but complicates recovery. When a tablet server dies, its tablets are moved to many other servers, each needing to reapply mutations from the original log. To avoid reading the full log multiple times, the log entries are sorted by key ⟨table, row name, log sequence number⟩, making mutations for each tablet contiguous. The sorting is parallelized by partitioning the log into 64 MB segments, sorted on different tablet servers, coordinated by the master. To protect against GFS latency spikes, each tablet server has two log writing threads, each with its own log file, switching if one becomes slow. Log entries contain sequence numbers to elide duplicates from switching. See also [[Speeding up Tablet Recovery]].

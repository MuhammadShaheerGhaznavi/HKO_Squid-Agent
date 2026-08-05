## Wiki-note

### Properties
title: "Tablet Serving and Data Storage"
type: concept
summary: "Tablet persistent state is stored in GFS, with updates in a commit log and memtable, and reads merging SSTables and memtable."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["tablet serving", "GFS", "memtable", "SSTable", "commit log"]
last_updated: 2026-08-01

## Content
The persistent state of a tablet is stored in GFS. Updates are committed to a commit log storing redo records. Recently committed updates are kept in memory in a sorted buffer called a memtable; older updates are stored in a sequence of SSTables. To recover a tablet, a tablet server reads metadata from the METADATA table, which lists the SSTables and redo points (pointers into commit logs). The server reads SSTable indices into memory and reconstructs the memtable by applying committed updates since the redo points. When a write arrives, the server checks well-formedness and authorization (reading permitted writers from a Chubby file, usually cached). A valid mutation is written to the commit log, with group commit to improve throughput of small mutations. After commit, contents are inserted into the memtable. Reads are checked similarly and executed on a merged view of SSTables and memtable, which is efficient because both are lexicographically sorted. Read and write operations can continue during tablet splits and merges.

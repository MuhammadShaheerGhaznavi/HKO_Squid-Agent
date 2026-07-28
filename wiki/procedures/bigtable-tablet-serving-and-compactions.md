## Wiki-note

### Properties
title: "Bigtable Tablet Serving and Compactions"
type: procedure
summary: "Tablet state consists of SSTables and a memtable; writes are logged and applied to the memtable, and compactions merge SSTables to maintain performance."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["memtable", "SSTable", "commit log", "minor compaction", "major compaction", "merging compaction"]
last_updated: 2026-07-29

## Content
Each tablet's persistent state is stored in [[GFS]] as SSTables and a commit log. Recent updates are kept in an in-memory memtable. Reads merge the memtable and SSTables. Minor compactions convert a full memtable to an SSTable. Merging compactions combine multiple SSTables into one, and major compactions produce a single SSTable without deletion markers, reclaiming space.

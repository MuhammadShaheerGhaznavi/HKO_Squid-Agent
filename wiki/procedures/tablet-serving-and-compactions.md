## Wiki-note

### Properties
title: "Tablet Serving and Compactions"
type: procedure
summary: "Tablet serving involves a memtable for recent writes and SSTables for persistent data. Compactions (minor, merging, major) convert memtables to SSTables and merge SSTables to reduce read overhead."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["memtable", "SSTable", "minor compaction", "merging compaction", "major compaction", "commit log"]
last_updated: 2026-07-29

## Content
Tablet persistent state is stored in GFS as SSTables and a commit log. Recent updates are kept in an in-memory memtable. Reads merge SSTables and memtable. Minor compaction converts a frozen memtable to an SSTable. Merging compaction combines several SSTables and memtable into one. Major compaction rewrites all SSTables into one, removing deleted data. Compactions reduce memory usage and improve read performance.

## Wiki-note

### Properties
title: "Speeding up Tablet Recovery"
type: procedure
summary: "Tablet recovery is accelerated by performing minor compactions before unloading a tablet, reducing the commit log state that needs to be replayed."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["tablet recovery", "minor compaction", "commit log", "tablet server", "master"]
last_updated: 2026-08-01

## Content
When the master moves a tablet from one tablet server to another, the source server first performs a minor compaction on that tablet. This reduces recovery time by minimizing the uncompacted state in the commit log. After this compaction, the server stops serving the tablet and performs another (usually fast) minor compaction to eliminate any remaining log entries that arrived during the first compaction. Once this second compaction is complete, the tablet can be loaded on another server without requiring any log recovery. This process ensures that tablet migration is efficient and minimizes downtime. See also [[Commit-Log Implementation in Bigtable]].

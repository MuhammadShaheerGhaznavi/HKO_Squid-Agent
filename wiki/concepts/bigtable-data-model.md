## Wiki-note

### Properties
title: "Bigtable Data Model"
type: concept
summary: "Bigtable is a sparse, distributed, persistent multidimensional sorted map indexed by row key, column key, and timestamp."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["Bigtable", "data model", "row key", "column key", "timestamp", "sparse", "sorted map"]
last_updated: 2026-07-29

## Content
Bigtable is a sparse, distributed, persistent multidimensional sorted map. The map is indexed by a row key, column key, and a timestamp; each value is an uninterpreted array of bytes. Data is stored in lexicographic order by row key. Column keys are grouped into column families, which are the unit of access control and compression. Timestamps allow multiple versions of data per cell, with automatic garbage collection based on version count or age.

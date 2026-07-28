## Wiki-note

### Properties
title: "Bigtable API"
type: entity
summary: "The Bigtable API provides functions for creating and deleting tables and column families, as well as reading, writing, and scanning data."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["Bigtable", "API", "RowMutation", "Scanner", "MapReduce", "Sawzall"]
last_updated: 2026-07-29

## Content
The Bigtable API includes operations for creating and deleting tables and column families, and for reading and writing data. Clients use RowMutation for atomic updates to a single row, and Scanner for iterating over rows and columns. Bigtable supports single-row transactions, integer counters, and client-supplied scripts (Sawzall). It integrates with [[MapReduce]] for large-scale parallel computations.

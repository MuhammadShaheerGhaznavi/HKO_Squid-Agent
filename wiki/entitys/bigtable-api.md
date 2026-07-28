## Wiki-note

### Properties
title: "Bigtable API"
type: entity
summary: "The Bigtable API provides functions for creating and deleting tables and column families, reading and writing data, and performing single-row transactions."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["Bigtable", "API", "RowMutation", "Scanner", "single-row transactions", "MapReduce"]
last_updated: 2026-07-29

## Content
The Bigtable API includes operations for creating and deleting tables and column families, as well as reading and writing data. Clients use RowMutation for atomic updates and Scanner for iterating over data. Bigtable supports single-row transactions, integer counters, and client-supplied scripts via Sawzall. It integrates with MapReduce for large-scale parallel computations.

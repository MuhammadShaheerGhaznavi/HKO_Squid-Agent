## Wiki-note

### Properties
title: "Bigtable Tablet Location Hierarchy"
type: concept
summary: "Bigtable uses a three-level B+ tree-like hierarchy to locate tablets, with a root tablet stored in Chubby."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["tablet location", "root tablet", "METADATA table", "B+ tree", "Chubby"]
last_updated: 2026-07-29

## Content
Tablet location is stored in a three-level hierarchy: a Chubby file points to the root tablet, which is the first tablet of a special METADATA table. The METADATA table stores the location of all user tablets. Clients cache tablet locations and recursively traverse the hierarchy if needed, requiring up to three network round-trips for a cold cache.

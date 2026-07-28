## Wiki-note

### Properties
title: "Tablet Location Hierarchy"
type: concept
summary: "Bigtable uses a three-level B+ tree-like hierarchy for tablet location, with a Chubby file pointing to the root tablet, which points to METADATA tablets, which point to user tablets."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["tablet location", "root tablet", "METADATA table", "Chubby", "B+ tree"]
last_updated: 2026-07-29

## Content
Bigtable uses a three-level hierarchy for tablet location. A Chubby file stores the location of the root tablet. The root tablet contains the location of all METADATA tablets. Each METADATA tablet contains the location of a set of user tablets. The client library caches tablet locations and recursively traverses the hierarchy if needed.

## Wiki-note

### Properties
title: "Tablet Location Hierarchy"
type: concept
summary: "Bigtable uses a three-level B+-tree-like hierarchy to store tablet locations, with a Chubby file at the top, a root tablet, and METADATA tablets."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["tablet location", "B+-tree", "METADATA table", "root tablet", "Chubby"]
last_updated: 2026-08-01

## Content
Bigtable uses a three-level hierarchy analogous to a B+-tree to store tablet location information. The first level is a file in Chubby containing the location of the root tablet. The root tablet contains locations of all tablets in a special METADATA table. Each METADATA tablet contains locations of a set of user tablets. The root tablet is the first METADATA tablet but is never split, ensuring the hierarchy has at most three levels. The METADATA table stores tablet locations under row keys encoding the tablet's table identifier and end row. Each METADATA row stores about 1KB in memory, and with 128 MB METADATA tablets, the scheme can address 2^34 tablets. The client library caches tablet locations; if cache is empty, locating a tablet requires three network round-trips (including one Chubby read); if stale, up to six round-trips. To reduce cost, the client prefetches tablet locations by reading metadata for multiple tablets at once. The METADATA table also stores secondary information like event logs for debugging.

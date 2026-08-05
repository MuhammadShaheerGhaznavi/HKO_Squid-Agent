## Wiki-note

### Properties
title: "Locality Groups in Bigtable"
type: concept
summary: "Locality groups group column families into separate SSTables to improve read efficiency and allow per-group tuning."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["locality group", "SSTable", "column family", "in-memory", "read efficiency"]
last_updated: 2026-08-01

## Content
In Bigtable, clients can group multiple column families into a locality group, and each locality group generates a separate SSTable per tablet. This segregation improves read efficiency because applications that access only certain column families do not need to read through unrelated data. For example, in Webtable, page metadata (like language and checksums) can be in one locality group, while page contents are in another, so metadata reads avoid scanning page contents. Locality groups also allow per-group tuning parameters, such as declaring a group as in-memory. SSTables for in-memory locality groups are loaded lazily into tablet server memory, enabling reads without disk access. This is useful for frequently accessed small data, like the location column family in the METADATA table. See also [[SSTable]] and [[Tablet]].

## Wiki-note

### Properties
title: "Caching for Read Performance in Bigtable"
type: concept
summary: "Bigtable uses two levels of caching—Scan Cache and Block Cache—to improve read performance by reducing disk accesses."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Scan Cache", "Block Cache", "caching", "read performance", "SSTable"]
last_updated: 2026-08-01

## Content
To enhance read performance, tablet servers employ two levels of caching. The Scan Cache is a higher-level cache that stores key-value pairs returned by the SSTable interface, beneficial for applications that repeatedly read the same data. The Block Cache is a lower-level cache that stores SSTable blocks read from GFS, useful for applications reading data close to recently accessed data, such as sequential reads or random reads of different columns in the same locality group within a hot row. These caches reduce the need for disk accesses, improving overall read latency. See also [[SSTable]] and [[Locality Groups in Bigtable]].

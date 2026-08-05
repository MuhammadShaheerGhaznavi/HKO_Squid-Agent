## Wiki-note

### Properties
title: "Bigtable Data Model"
type: concept
summary: "Bigtable is a sparse, distributed, persistent multidimensional sorted map indexed by row key, column key, and timestamp, with values as uninterpreted byte arrays."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["data model", "row key", "column key", "timestamp", "sparse map"]
last_updated: 2026-08-01

## Content
Bigtable is a sparse, distributed, persistent multidimensional sorted map. The map is indexed by a row key, column key, and a timestamp; each value is an uninterpreted array of bytes. The data model was settled after examining various potential uses. A concrete example is the Webtable, which stores web pages and related information. In Webtable, URLs are row keys, various aspects of web pages are column names, and page contents are stored in the contents: column under timestamps when fetched. Row keys are arbitrary strings (up to 64KB, typically 10-100 bytes). Every read or write under a single row key is atomic, regardless of the number of columns. Bigtable maintains data in lexicographic order by row key, and the row range is dynamically partitioned into tablets, which are units of distribution and load balancing. This enables efficient reads of short row ranges. Clients can exploit locality by choosing row keys, e.g., reversing hostnames in URLs to group pages from the same domain. Column keys are grouped into column families, which are the basic unit of access control. A column family must be created before data can be stored under any column key in it. The number of column families is intended to be small (hundreds at most), while the number of columns can be unbounded. Column keys are named as family:qualifier. Timestamps are 64-bit integers, assigned by Bigtable as real time in microseconds or by clients. Different versions of a cell are stored in decreasing timestamp order. Per-column-family settings allow garbage collection of old versions, e.g., keeping only the last n versions or only those written in the last seven days. See [[Bigtable Overview]] for context.

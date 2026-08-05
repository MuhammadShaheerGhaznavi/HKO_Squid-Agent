	## Wiki-note

### Properties
title: "Bigtable Table Characteristics in Production"
type: synthesis
summary: "Production Bigtable tables vary widely in size, compression, cell count, column families, and memory usage, reflecting diverse use cases."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["table size", "compression ratio", "column families", "locality groups", "memory"]
last_updated: 2026-08-01

## Content
Table 2 in the paper shows characteristics of several production Bigtable tables. Sizes range from 0.5 TB (Google Earth serving) to 800 TB (Crawl). Compression ratios vary from 11% to 64%, with some tables having compression disabled (e.g., Google Earth imagery). Cell counts range from 0.9 billion (Orkut) to 1000 billion (Crawl). Column families range from 1 (Google Analytics) to 93 (Personalized Search). Locality groups range from 1 to 11. The percentage of data in memory varies from 0% to 33%, with latency-sensitive tables typically having higher memory percentages. This diversity illustrates Bigtable's flexibility in handling different data types and access patterns.

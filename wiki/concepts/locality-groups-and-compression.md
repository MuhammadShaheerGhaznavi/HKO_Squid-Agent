## Wiki-note

### Properties
title: "Locality Groups and Compression"
type: concept
summary: "Locality groups allow grouping column families into separate SSTables for efficient reads. Compression can be applied per locality group, using a two-pass scheme that achieves high ratios for clustered data."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["locality group", "compression", "Bentley-McIlroy", "Bloom filter", "in-memory"]
last_updated: 2026-07-29

## Content
Clients can group column families into locality groups, each stored in separate SSTables. This allows efficient reads by only accessing relevant SSTables. Locality groups can be marked as in-memory for fast access. Compression is applied per SSTable block using a two-pass scheme (Bentley-McIlroy and fast compression). Bloom filters can be used to reduce disk seeks for non-existent rows/columns.

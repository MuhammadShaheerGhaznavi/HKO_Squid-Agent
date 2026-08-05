## Wiki-note

### Properties
title: "Bigtable Overview and API"
type: concept
summary: "Bigtable is a distributed storage system developed at Google for managing structured data at scale. It provides a simple data model, supports a rich API for data manipulation, and integrates with other Google technologies like MapReduce and Sawzall."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Bigtable", "distributed storage", "scalability", "API", "MapReduce", "Sawzall"]
last_updated: 2026-08-01

## Content
Bigtable is a distributed storage system developed at Google for managing structured data. It is designed to reliably scale to petabytes of data across thousands of machines, achieving wide applicability, scalability, high performance, and high availability. Over 60 Google products use Bigtable, including Google Analytics, Google Finance, Orkut, Personalized Search, Writely, and Google Earth. These products range from throughput-oriented batch processing to latency-sensitive serving. Bigtable clusters vary from a handful to thousands of servers, storing up to several hundred terabytes. Unlike parallel or main-memory databases, Bigtable does not support a full relational data model; instead, it provides a simple data model with dynamic control over data layout and format. Data is indexed by row and column names that are arbitrary strings, and values are uninterpreted byte arrays. Clients can control data locality through schema choices and dynamically decide whether to serve data from memory or disk. See [[Data Model]] for more details.

The Bigtable API offers functions for creating and deleting tables and column families, as well as changing cluster, table, and column family metadata like access control rights. Client applications can write or delete values, look up values from individual rows, or iterate over a subset of data. The API uses a RowMutation abstraction for atomic mutations to a single row, as shown in C++ code that adds and deletes anchors in a Webtable. A Scanner abstraction allows iteration over rows and columns, with mechanisms to limit rows, columns, and timestamps, such as regular expressions on column names or time ranges. Bigtable supports single-row transactions for atomic read-modify-write sequences, but not general transactions across row keys; however, it provides an interface for batching writes across row keys. Cells can be used as integer counters, and client-supplied scripts written in Sawzall can be executed in server address spaces for data transformation, filtering, and summarization, though they cannot write back to Bigtable. Bigtable integrates with MapReduce, a framework for large-scale parallel computations, via wrappers that allow Bigtable to serve as both input source and output target for MapReduce jobs.

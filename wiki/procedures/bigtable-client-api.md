## Wiki-note

### Properties
title: "Bigtable Client API"
type: procedure
summary: "Bigtable provides a client API for creating and modifying tables, with operations like opening tables, writing data via RowMutation, and applying operations atomically."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["API", "RowMutation", "OpenOrDie", "Apply", "write"]
last_updated: 2026-08-01

## Content
The Bigtable client API allows applications to interact with tables. A typical workflow involves opening a table using a function like `OpenOrDie("/bigtable/web/webtable")`. To write data, clients use `RowMutation` objects, which can set or delete cells. For example, `RowMutation r1(T, "com.cnn.www"); r1.Set("anchor:www.c-span.org", "CNN"); r1.Delete("anchor:www.abc.com");` modifies the row with key "com.cnn.www". The `Apply` operation applies the mutation atomically. This API is simple and supports dynamic control over data layout. The API also supports reading data, though not detailed in this section. The API is designed to be used by many Google products, from batch processing to real-time serving. See [[Data Model]] for the underlying structure.

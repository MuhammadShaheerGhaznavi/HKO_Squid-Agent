## Wiki-note

### Properties
title: "Bigtable Building Blocks"
type: entity
summary: "Bigtable is built on GFS, SSTable, and Chubby, which provide distributed file storage, persistent ordered maps, and distributed locking respectively."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["GFS", "SSTable", "Chubby", "distributed storage", "lock service"]
last_updated: 2026-07-29

## Content
Bigtable uses the Google File System (GFS) for storing log and data files. SSTable format provides persistent, ordered immutable maps from keys to values. Chubby is a highly-available distributed lock service used for master election, bootstrap location, tablet server discovery, schema storage, and access control lists.

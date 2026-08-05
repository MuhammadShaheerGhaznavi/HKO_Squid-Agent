## Wiki-note

### Properties
title: "Bigtable System Components"
type: concept
summary: "Bigtable has three main components: a client library, a master server, and tablet servers, with the master handling metadata and tablet servers handling data."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Bigtable", "master", "tablet server", "client library", "architecture"]
last_updated: 2026-08-01

## Content
Bigtable's implementation consists of three major components: a library linked into every client, one master server, and many tablet servers. Tablet servers can be dynamically added or removed to accommodate workload changes. The master is responsible for assigning tablets to tablet servers, detecting server additions/expirations, balancing load, garbage collecting files in GFS, and handling schema changes. Each tablet server manages a set of tablets (typically 10-1000 per server), handling read/write requests and splitting tablets that grow too large. Client data does not flow through the master; clients communicate directly with tablet servers, so the master is lightly loaded. A Bigtable cluster stores tables, each consisting of tablets containing row ranges. Initially, each table has one tablet, which splits automatically into multiple tablets of approximately 100-200 MB each as it grows.

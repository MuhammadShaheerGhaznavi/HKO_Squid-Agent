## Wiki-note

### Properties
title: "Bigtable Implementation Components"
type: entity
summary: "Bigtable implementation consists of a client library, a master server, and many tablet servers. The master assigns tablets, detects server failures, and balances load; tablet servers manage tablets and handle read/write requests."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["master", "tablet server", "tablet", "load balancing", "client library"]
last_updated: 2026-07-29

## Content
The Bigtable implementation has three major components: a client library, one master server, and many tablet servers. The master assigns tablets to tablet servers, detects server additions/expirations, balances load, and handles schema changes. Tablet servers manage a set of tablets, handle read/write requests, and split tablets that grow too large. Clients communicate directly with tablet servers for data operations.

## Wiki-note

### Properties
title: "Building Blocks of Bigtable"
type: concept
summary: "Bigtable is built on GFS, SSTable, Chubby, and a cluster management system, each providing essential infrastructure for storage, locking, and coordination."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["GFS", "SSTable", "Chubby", "cluster management", "Paxos"]
last_updated: 2026-08-01

## Content
Bigtable is built on several Google infrastructure components. It uses the distributed Google File System (GFS) to store log and data files, and typically operates in a shared pool of machines running other distributed applications. A cluster management system handles scheduling, resource management, machine failure detection, and monitoring. The SSTable file format is used internally to store Bigtable data; it provides a persistent, ordered immutable map from keys to values, with operations for lookups and range iterations. Each SSTable contains a sequence of blocks (typically 64KB) with a block index at the end, loaded into memory on open, enabling lookups with a single disk seek via binary search in the index. Optionally, SSTables can be memory-mapped for faster access. Bigtable relies on Chubby, a highly-available distributed lock service with five active replicas using Paxos for consistency. Chubby provides a namespace of directories and files that can be used as locks, with atomic reads and writes. Bigtable uses Chubby for master election, storing bootstrap locations, discovering tablet servers, storing schema information, and access control lists. Chubby unavailability can cause Bigtable unavailability, but measurements show it is rare, with an average of 0.0047% of Bigtable server hours affected.

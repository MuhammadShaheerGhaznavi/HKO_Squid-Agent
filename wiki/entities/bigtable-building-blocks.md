## Wiki-note

### Properties
title: "Bigtable Building Blocks"
type: entity
summary: "Bigtable is built on GFS, SSTable, and Chubby for storage, data format, and distributed coordination."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["GFS", "SSTable", "Chubby", "distributed lock service", "Paxos"]
last_updated: 2026-07-29

## Content
Bigtable uses [[GFS]] to store log and data files. Data is stored in [[SSTable]] format, an immutable ordered map from keys to values. [[Chubby]] provides a highly-available distributed lock service for master election, tablet server discovery, schema storage, and access control. Chubby uses the [[Paxos]] algorithm for consistency.

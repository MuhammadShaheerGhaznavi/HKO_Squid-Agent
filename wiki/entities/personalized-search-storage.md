## Wiki-note

### Properties
title: "Personalized Search Storage"
type: entity
summary: "Personalized Search stores user queries and clicks in Bigtable, using per-user rows and column families for different action types."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Personalized Search", "user data", "column families", "replication", "quota"]
last_updated: 2026-08-01

## Content
Personalized Search (www.google.com/psearch) records user queries and clicks across Google properties. Each user has a unique userid and a row named by that userid. All user actions are stored in a table, with a separate column family for each action type (e.g., web queries). Each data element uses the time of the user action as its Bigtable timestamp. User profiles are generated using MapReduce over Bigtable and used to personalize live search results. Data is replicated across several Bigtable clusters for availability and latency reduction. Originally, client-side replication ensured eventual consistency; now a server-side replication subsystem is used. The design allows other groups to add per-user information in their own columns, leading to an unusually large number of column families. A simple quota mechanism limits storage consumption by any particular client in shared tables, providing isolation between product groups.

## Wiki-note

### Properties
title: "Bigtable Conclusions and Production Experience"
type: synthesis
summary: "Summarizes Bigtable's production history, user adoption, and future directions."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["Bigtable", "production", "conclusions", "future work", "Google"]
last_updated: 2026-08-01

## Content
Bigtable has been in production use at Google since April 2005, with roughly seven person-years of design and implementation before that. As of August 2006, over sixty projects use Bigtable, and users appreciate its performance, high availability, and scalability by simply adding machines. New users sometimes find the interface unusual, especially those accustomed to relational databases with general-purpose transactions, but the success of many Google products validates the design. Future work includes support for secondary indices, infrastructure for cross-data-center replicated Bigtables with multiple master replicas, and deploying Bigtable as a service to product groups. Building a custom storage solution provided significant flexibility and control, allowing removal of bottlenecks as they arise. See also [[Bigtable Overview]] and [[Bigtable Architecture]].

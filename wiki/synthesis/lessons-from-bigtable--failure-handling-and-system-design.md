## Wiki-note

### Properties
title: "Lessons from Bigtable: Failure Handling and System Design"
type: synthesis
summary: "Bigtable's development revealed that large distributed systems face diverse failures beyond standard assumptions, and that simplicity in design is crucial for maintainability."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["failures", "distributed systems", "simplicity", "monitoring", "protocols"]
last_updated: 2026-08-01

## Content
Bigtable encountered many failure types beyond network partitions and fail-stop failures, including memory and network corruption, large clock skew, hung machines, asymmetric network partitions, bugs in Chubby, GFS quota overflows, and hardware maintenance. To address these, they added checksumming to RPCs and removed assumptions about Chubby error sets. Another lesson was to delay adding features until usage is clear; they initially planned general-purpose transactions but only implemented single-row transactions after seeing real needs, with a specialized mechanism for secondary indices planned. System-level monitoring proved vital: they extended RPC tracing to detect issues like lock contention and slow GFS writes, and registered clusters in Chubby for tracking. The most important lesson was the value of simple designs; a complex tablet-server membership protocol was scrapped for a simpler one relying on widely-used Chubby features, reducing debugging time.

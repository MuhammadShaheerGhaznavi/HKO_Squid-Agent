## Wiki-note

### Properties
title: "Lessons Learned from Bigtable"
type: synthesis
summary: "Key lessons include the importance of handling diverse failures, delaying feature additions until needed, proper monitoring, and the value of simple designs."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["lessons learned", "failure handling", "monitoring", "simple design", "feature creep"]
last_updated: 2026-07-29

## Content
Lessons from building Bigtable include: large distributed systems face many failure types beyond network partitions; features should be added only when clearly needed (e.g., single-row transactions sufficed over general transactions); proper monitoring (RPC tracing, cluster registration) is crucial; and simple designs (e.g., tablet server membership protocol) are easier to maintain and debug.

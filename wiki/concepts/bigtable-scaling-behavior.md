## Wiki-note

### Properties
title: "Bigtable Scaling Behavior"
type: concept
summary: "Examines how Bigtable throughput scales from 1 to 500 tablet servers, noting superlinear gains but sublinear scaling due to load imbalance."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["scaling", "throughput", "load balancing", "tablet servers", "aggregate"]
last_updated: 2026-08-01

## Content
Aggregate throughput increases dramatically, over 100x, when scaling from 1 to 500 tablet servers, with in-memory random reads improving almost 300x. However, scaling is not linear; per-server throughput drops significantly from 1 to 50 servers due to load imbalance from other processes and imperfect load balancing. Rebalancing is throttled to minimize tablet movements, which cause brief unavailability. Random reads scale worst (only 100x for 500x servers) because each read transfers a 64 KB block, saturating shared gigabit links. This indicates that while Bigtable scales well, network bandwidth and load balancing are key factors limiting linear scaling.

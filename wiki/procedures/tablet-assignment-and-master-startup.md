## Wiki-note

### Properties
title: "Tablet Assignment and Master Startup"
type: procedure
summary: "The master assigns tablets to tablet servers using Chubby for coordination, and follows a startup sequence to discover existing assignments."
sources: ["[[raw/sources/bigtable]]"]
source_count: 1
keywords: ["tablet assignment", "master", "Chubby", "startup", "lock"]
last_updated: 2026-08-01

## Content
Each tablet is assigned to one tablet server at a time. The master tracks live servers and tablet assignments, including unassigned tablets. When a tablet is unassigned and a server has room, the master sends a load request. Bigtable uses Chubby to track tablet servers: each server creates and acquires an exclusive lock on a uniquely-named file in a Chubby directory. If a server loses its lock (e.g., due to network partition), it stops serving; it tries to reacquire the lock, and if the file no longer exists, it kills itself. The master periodically checks server lock status; if a server has lost its lock or is unreachable, the master tries to acquire the lock itself. If successful, it deletes the server's file to prevent it from serving again and moves its tablets to unassigned. The master kills itself if its Chubby session expires. At startup, the master: (1) grabs a unique master lock in Chubby, (2) scans the servers directory to find live servers, (3) communicates with each live server to discover assigned tablets, and (4) scans the METADATA table to learn all tablets, adding unassigned ones to the set. Before scanning METADATA, it ensures the root tablet is assigned if not already. Tablet splits are initiated by tablet servers, which commit the split in METADATA and notify the master; if notification is lost, the master detects the split when loading the tablet.

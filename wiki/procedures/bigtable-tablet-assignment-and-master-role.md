## Wiki-note

### Properties
title: "Bigtable Tablet Assignment and Master Role"
type: procedure
summary: "The master assigns tablets to tablet servers, monitors server liveness via Chubby, and handles load balancing and garbage collection."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["master", "tablet server", "Chubby", "tablet assignment", "load balancing"]
last_updated: 2026-07-29

## Content
The master assigns tablets to tablet servers. Tablet servers register themselves in a Chubby directory. The master monitors this directory and detects server failures by attempting to acquire the server's lock. If successful, it deletes the server file and reassigns its tablets. The master also handles schema changes and garbage collection of obsolete SSTables.

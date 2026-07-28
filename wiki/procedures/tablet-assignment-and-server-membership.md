## Wiki-note

### Properties
title: "Tablet Assignment and Server Membership"
type: procedure
summary: "Tablet assignment uses Chubby for server discovery and lease management. The master monitors the servers directory, assigns tablets, and handles server failures by reassigning tablets."
sources: ["[[raw/sources/paper]]"]
source_count: 1
keywords: ["tablet assignment", "Chubby", "master", "tablet server", "lease", "failure detection"]
last_updated: 2026-07-29

## Content
Tablet servers create and acquire exclusive locks on files in a Chubby directory. The master monitors this directory to discover servers. If a server loses its lock, the master deletes its file and reassigns its tablets. The master also scans the METADATA table to discover unassigned tablets. At startup, the master acquires a master lock, scans live servers, communicates with them to learn assignments, and scans METADATA to find unassigned tablets.

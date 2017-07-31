# [opsimulate](https://pypi.python.org/pypi/opsimulate)

## Creating Problem Modules

Problem modules have a fairly simple required API. A problem module itself is simply a directory.

### Required Files

In the problem module directory, four files are required:
- `initiate`: executable Bash script to initiate the problem
- `check`: executable Bash script to check if the problem has been fixed yet, returns 0 status code if incident has been resolved, 1 status code if the incident is still ongoing 
- `resolve`: executable Bash script to fix and resolve the problem
- `metadata.yml`: YAML file with metadata about the module and incident, including hints, incident description, a solution for resolving the incident, and an introduction to the incident scenario printed to the student

### Module Metadata Requirements

The following keys and values are required in `metadata.yml`:

```
---
author: "<creator of the module>"
hints: 
- "<helpful hint on how to start>"
- "<hint on what tool to use>"
description: "<here is a description of the scenario and what the module might teach>"
introduction: "<here is the incident scenario that the student should be aware of>"
solution: "<here are some approaches to fixing the incident problem>"
```

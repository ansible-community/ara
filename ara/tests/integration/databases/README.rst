Database migration integration tests
====================================
This directory contains database files of a specific revision to test if
we are able to successfully upgrade from one revision to the latest revision
successfully.

- 000: Unstable database schema (assumed ~0.9.3)
- 001: First stable database schema
- 002: ara_record module data added
- 003: ara_record type added
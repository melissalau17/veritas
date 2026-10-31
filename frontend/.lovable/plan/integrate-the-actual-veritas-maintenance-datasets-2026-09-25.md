# Integrate the actual VERITAS maintenance datasets

## What will change
- Replace the fictional equipment register with the eight assets and work-order summaries from the uploaded sequence dataset.
- Make **EA-5601 — Solvent Heater** the default Asset 360 destination and the central example across navigation.
- Show EA-5601’s complete 25-work-order timeline, actual costs, downtime, disciplines, causes, actions, and personnel.
- Add the two validated EA-5601 Failure Memory relationships as prominent reusable evidence.
- Rework the troubleshooting workspace around tube differential pressure, fouling, and sensing-path verification using the uploaded records.
- Update the review screen with evidence candidates drawn from the same dataset.

## Interaction and presentation
- Keep the existing information-dense navy/yellow industrial interface.
- Preserve filters, tabs, workflow steps, cross-links, and review decisions.
- Clearly label source-derived evidence and avoid savings or addressability claims not supported by the files.

## Technical details
- Convert both CSVs into typed local prototype data so every source record remains available without requiring a backend.
- Derive register totals and EA-5601 metrics from those records rather than duplicating calculated values.
- Keep every existing route and add route-specific social metadata fields required by the app.
- Verify the desktop interface, links, tabs, tables, and error logs after the update.

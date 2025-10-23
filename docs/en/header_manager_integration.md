# Stage 3 Header Manager Integration

- Header normalization, synonym resolution, and location inference now live in `scripts/core/header_manager.py`.
- Stage 1 synchronization and Stage 3 reporting reuse the same semantic matching rules, so adjusting the core registry automatically updates every stage.
- Warehouse/site columns are inferred dynamically via `HeaderRegistry` group metadata, eliminating brittle hard-coded lists.

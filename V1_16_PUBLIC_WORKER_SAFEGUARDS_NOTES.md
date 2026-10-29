# v1.16 — Public worker safeguards (local review)

- Public-only one shared fitting slot per application **process**. Busy requests are declined, not queued.
- Public fitting runs in a spawned child Python process; parent enforces a 60-second wall-clock deadline and terminates/reaps its worker before releasing the slot.
- Existing integration/RHS limits and optimiser settings are enforced within the worker.
- Local (Windows) fitting remains direct/unrestricted.
- Tests: `test_KineticFittingPot_Public_Worker.bat`; existing readiness suite remains available.
- **Limitations:** per-process slot is not distributed across multiple server replicas; timeout covers fitting job rather than post-fit chart/workbook generation; Streamlit platform-level CPU/memory safety is not guaranteed. Worker creation can be costly, and actual cloud testing remains required.
- Not approved for deployment until Windows local public-mode worker tests and cloud trial pass.

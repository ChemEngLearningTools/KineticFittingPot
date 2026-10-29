from __future__ import annotations
import concurrent.futures
import threading
from pathlib import Path
from utils.public_fit_worker import run_public_fit, PublicFitBusy, PublicFitTimeout, PublicFitStopped
from utils.kinetic_fitting_engine import parse_fitting_workbook

ROOT = Path(__file__).resolve().parents[1]

def main():
    sample = ROOT / 'data/templates/KineticFittingPot_Kinetic_Fitting_Catalytic_Saturation_Synthetic_Data.xlsx'
    raw = sample.read_bytes()
    problem = parse_fitting_workbook(raw)
    kwargs = dict(weighting='species_scaled', n_starts=1, random_seed=20260904, max_nfev=25)
    # Occupy a separate test semaphore; verify nonblocking rejection without needing two slow fits.
    slot = threading.BoundedSemaphore(1)
    assert slot.acquire(blocking=False)
    try:
        try:
            run_public_fit(raw, problem.fit_parameter_ids, slot=slot, **kwargs)
            raise AssertionError('Busy admission not rejected')
        except PublicFitBusy:
            print('PASS concurrent busy request rejected')
    finally:
        slot.release()
    # The hard deadline is intentionally shorter than process spawn overhead.
    try:
        run_public_fit(raw, problem.fit_parameter_ids, timeout_s=0.01, **kwargs)
        raise AssertionError('Timeout was not enforced')
    except PublicFitTimeout:
        print('PASS worker hard timeout enforced and process reaped')
    # Retry must be possible after hard timeout; budget stop is also acceptable for this test.
    try:
        outcome = run_public_fit(raw, problem.fit_parameter_ids, timeout_s=55, **kwargs)
        assert 'best' in outcome.fit_result
        assert outcome.budget_summary['integrations'] > 0
        print('PASS subsequent worker fit and budget telemetry')
    except PublicFitStopped as exc:
        assert exc.summary.get('integrations', 0) > 0
        print('PASS subsequent worker ran and cooperatively stopped at numerical budget')
    print('PUBLIC WORKER SAFEGUARDS: PASS')

if __name__ == '__main__':
    main()

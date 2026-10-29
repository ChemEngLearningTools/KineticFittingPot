"""Bounded public kinetic fitting in a killable subprocess.

One slot is held for the entire process lifecycle in the Streamlit app process.
This protects one application instance; replicas require an external coordinator.
"""
from __future__ import annotations
import multiprocessing as mp
import threading
import time
from dataclasses import dataclass
from utils.deployment import PUBLIC_FITTING_LIMITS


class PublicFitBusy(RuntimeError):
    pass


class PublicFitTimeout(RuntimeError):
    pass


class PublicFitStopped(RuntimeError):
    def __init__(self, reason, summary=None):
        super().__init__(reason)
        self.summary = summary or {}


@dataclass
class PublicFitOutcome:
    fit_result: dict
    budget_summary: dict


# App owns this one semaphore per interpreter, not per browser session.
_FITTING_SLOT = threading.BoundedSemaphore(1)


def _child_main(connection, workbook_bytes, selected_parameters, weighting, n_starts, random_seed, max_nfev):
    from utils.kinetic_fitting_engine import FittingBudget, FittingBudgetExceeded, fit_multistart, evaluate_validation, parse_fitting_workbook, problem_with_fit_parameters
    budget = FittingBudget(max_integrations=PUBLIC_FITTING_LIMITS['max_integrations'],
                           max_rhs_evaluations=PUBLIC_FITTING_LIMITS['max_rhs_evaluations'],
                           max_wall_time_s=PUBLIC_FITTING_LIMITS['max_wall_time_s'])
    try:
        problem = problem_with_fit_parameters(parse_fitting_workbook(workbook_bytes), selected_parameters)
        fit_result = fit_multistart(problem, weighting=weighting, n_starts=n_starts,
                                   random_seed=random_seed, max_nfev=max_nfev, budget=budget)
        fit_result["validation"] = evaluate_validation(problem, fit_result, budget=budget)
        connection.send(('ok', fit_result, budget.summary()))
    except FittingBudgetExceeded as exc:
        connection.send(('stopped', str(exc), budget.summary()))
    except Exception as exc:
        connection.send(('error', f'{type(exc).__name__}: {exc}', budget.summary()))
    finally:
        connection.close()


def run_public_fit(workbook_bytes, selected_parameters, *, weighting, n_starts, random_seed, max_nfev,
                   timeout_s=None, slot=None):
    """Run one fit with admission control, deadline and forced worker termination.

    Must be called from the Streamlit script, not a spawned worker.
    Timeout includes spawn overhead. Always reap/kill before releasing the slot.
    """
    guard = slot if slot is not None else _FITTING_SLOT
    if not guard.acquire(blocking=False):
        raise PublicFitBusy('Another public kinetic fit is currently running. Please retry shortly.')
    proc = None
    parent = child = None
    try:
        timeout = float(timeout_s if timeout_s is not None else PUBLIC_FITTING_LIMITS['max_wall_time_s'])
        if timeout <= 0:
            raise ValueError('The public timeout must be positive.')
        ctx = mp.get_context('spawn')
        parent, child = ctx.Pipe(duplex=False)
        proc = ctx.Process(target=_child_main,
                           args=(child, workbook_bytes, tuple(selected_parameters), weighting, int(n_starts), int(random_seed), int(max_nfev)),
                           daemon=False)
        deadline = time.monotonic() + timeout
        proc.start()
        child.close()
        child = None
        remaining = max(0.0, deadline - time.monotonic())
        if not parent.poll(remaining):
            if proc.is_alive():
                raise PublicFitTimeout(f'The public fitting time limit of {timeout:g} seconds was reached. The worker was stopped; no fitted result is reported.')
            raise RuntimeError(f'The fitting worker exited without reporting a result (exit code {proc.exitcode}).')
        try:
            status, payload, summary = parent.recv()
        except EOFError as exc:
            raise RuntimeError('The fitting worker closed without a result.') from exc
        if status == 'ok':
            return PublicFitOutcome(payload, summary)
        if status == 'stopped':
            raise PublicFitStopped(payload, summary)
        raise RuntimeError(f'Public fitting worker failed: {payload}')
    finally:
        if proc is not None and proc.pid is not None:
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=3.0)
                if proc.is_alive():
                    proc.kill()
                    proc.join(timeout=3.0)
            else:
                proc.join(timeout=1.0)
        if child is not None:
            child.close()
        if parent is not None:
            parent.close()
        guard.release()

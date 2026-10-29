from __future__ import annotations
"""KineticFittingPot v1.15 public-readiness checks. Does not alter the app."""
import argparse
from datetime import datetime, timezone
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REPORT_DIR = ROOT / 'validation_reports'


def run_subprocess(path: str, timeout: int):
    t = time.perf_counter()
    try:
        proc = subprocess.run([sys.executable, str(ROOT / 'tools' / path)], cwd=ROOT,
                              capture_output=True, text=True, timeout=timeout,
                              env=dict(os.environ, PYTHONUNBUFFERED='1'))
        return {'status':'PASS' if proc.returncode == 0 else 'FAIL', 'seconds':round(time.perf_counter()-t, 3),
                'detail': (proc.stdout + '\n' + proc.stderr)[-5000:].strip()}
    except subprocess.TimeoutExpired:
        return {'status':'TIMEOUT', 'seconds':round(time.perf_counter()-t, 3),
                'detail':f'Test subprocess exceeded {timeout} seconds (subprocess terminated).'}
    except Exception as e:
        return {'status':'FAIL','seconds':round(time.perf_counter()-t,3),'detail':repr(e)}


def check_invalid_inputs():
    from openpyxl import load_workbook
    from utils.general_batch_model import parse_model_workbook
    from utils.kinetic_fitting_engine import parse_fitting_workbook
    template = ROOT/'data/templates/KineticFittingPot_Isothermal_Batch_Model_Template.xlsx'
    fitting = ROOT/'data/templates/KineticFittingPot_Kinetic_Fitting_Catalytic_Saturation_Synthetic_Data.xlsx'
    good_model = parse_model_workbook(template.read_bytes())
    good_fit = parse_fitting_workbook(fitting.read_bytes())
    assert good_model.species_ids and good_fit.observations
    checks = 0
    for source, parser, sheet in [(template,parse_model_workbook,'Species'),(fitting,parse_fitting_workbook,'Experimental_Data')]:
        wb = load_workbook(source)
        del wb[sheet]
        b = BytesIO(); wb.save(b)
        try: parser(b.getvalue())
        except (ValueError, KeyError, TypeError): checks+=1
        else: raise AssertionError(f'Missing {sheet} worksheet was accepted')
    return {'status':'PASS', 'seconds':0, 'detail':f'{checks} missing-worksheet mutants rejected; supplied model and fitting templates parsed.'}


def check_public_limits():
    from dataclasses import replace
    from utils.deployment import PUBLIC_FITTING_LIMITS, public_fitting_violations, public_cloud_workbook_violations
    from utils.kinetic_fitting_engine import parse_fitting_workbook, FittingBudget, FittingBudgetExceeded, fit_multistart
    book = (ROOT/'data/templates/KineticFittingPot_Kinetic_Fitting_Catalytic_Saturation_Synthetic_Data.xlsx').read_bytes()
    prob = parse_fitting_workbook(book)
    assert not public_fitting_violations(prob)
    assert not public_cloud_workbook_violations(book)
    assert PUBLIC_FITTING_LIMITS['max_fitted_parameters']==8 and PUBLIC_FITTING_LIMITS['max_datasets']==6
    assert public_fitting_violations(replace(prob, observations=prob.observations*8))
    budget = FittingBudget(max_integrations=1, max_rhs_evaluations=1000, max_wall_time_s=60)
    t=time.perf_counter()
    stopped=False
    try: fit_multistart(prob, weighting='species_scaled', n_starts=1, max_nfev=15, budget=budget)
    except FittingBudgetExceeded: stopped=True
    assert stopped, 'Computational budget was not enforced'
    return {'status':'PASS','seconds':round(time.perf_counter()-t,3),
            'detail':f'Current public limits verified; oversized observation request rejected; budget interrupted fit after {budget.integrations} integrations.'}


def benchmark_catalytic():
    from utils.kinetic_fitting_engine import parse_fitting_workbook, fit_multistart, FittingBudget, synthetic_truth
    from utils.deployment import PUBLIC_FITTING_LIMITS
    book = (ROOT/'data/templates/KineticFittingPot_Kinetic_Fitting_Catalytic_Saturation_Synthetic_Data.xlsx').read_bytes()
    problem = parse_fitting_workbook(book)
    v=PUBLIC_FITTING_LIMITS
    budget=FittingBudget(max_integrations=v['max_integrations'],max_rhs_evaluations=v['max_rhs_evaluations'],max_wall_time_s=v['max_wall_time_s'])
    t=time.perf_counter()
    try:
        result=fit_multistart(problem,weighting='species_scaled',n_starts=v['max_starts'],
                              max_nfev=v['max_nfev_per_start'],budget=budget)
        met=budget.summary()
        return {'status':'PASS' if result['status']=='converged' else 'WARN', 'seconds':round(time.perf_counter()-t,3),
                'detail':f"status={result['status']}, SSE={result['best']['sse']:.8g}, "
                         f"parameters={dict(zip(problem.fit_parameter_ids, [round(float(x), 9) for x in result['best_values']]))}, "
                         f"integrations={met['integrations']}, RHS={met['rhs_evaluations']}, "
                         f"failed_forward={met['failed_forward_evaluations']}; convergence does not establish parameter identifiability."}
    except Exception as e:
        return {'status':'FAIL','seconds':round(time.perf_counter()-t,3),'detail':repr(e)}


def extended_public_case(case: str, timeout_s: int=100):
    start=time.perf_counter()
    try:
        proc=subprocess.run([sys.executable,str(ROOT/'tools/public_fitting_extended_v115.py'),'--case',case],
                            cwd=ROOT,capture_output=True,text=True,timeout=timeout_s,
                            env=dict(os.environ,PYTHONUNBUFFERED='1',KINETICFITTINGPOT_MODE='public_cloud'))
        if proc.returncode:
            return {'status':'FAIL','seconds':round(time.perf_counter()-start,3),
                    'detail':proc.stderr[-2000:] or proc.stdout[-2000:]}
        obj=json.loads(proc.stdout.strip().splitlines()[-1])
        # A budget stop is an expected, correctly enforced outcome, but not a fitting pass.
        status=('PASS' if obj['status']=='converged' else
                'LIMIT_REACHED' if obj['status']=='BUDGET_STOP' else
                'NON_CONVERGED' if obj['status']=='non_converged' else 'FAIL')
        return {'status':status,'seconds':round(time.perf_counter()-start,3),'detail':json.dumps(obj,indent=2), 'measurements':obj}
    except subprocess.TimeoutExpired:
        return {'status':'TIMEOUT','seconds':round(time.perf_counter()-start,3),
                'detail':f'External benchmark process terminated after {timeout_s} seconds; no app hard-timeout claim.'}
    except Exception as exc:
        return {'status':'FAIL','seconds':round(time.perf_counter()-start,3),'detail':repr(exc)}

def main():
    p=argparse.ArgumentParser(description='KineticFittingPot v1.15 validation and benchmark reporter')
    p.add_argument('--full', action='store_true', help='Run slower legacy diagnostics smoke test as well')
    p.add_argument('--timeout',type=int,default=180,help='Timeout per legacy smoke test in seconds')
    args=p.parse_args()
    REPORT_DIR.mkdir(exist_ok=True)
    results={}
    checks=[('batch_simulation','smoke_test_batch_simulator.py'),
            ('general_batch','smoke_test_general_batch_model.py'),
            ('initial_rate','test_initial_rate_validation.py'),
            ('fitting_regression','smoke_test_kinetic_fitting_engine.py'),
            ('reaction_stoichiometry','smoke_test_reaction_stoichiometry_fundamentals.py'),
            ('model_diagnostics_fundamentals','smoke_test_model_diagnostics_fundamentals.py')]
    if args.full: checks.append(('advanced_diagnostics','smoke_test_model_diagnostics_engine.py'))
    for name,filename in checks:
        print(f'Running {name}...',flush=True)
        results[name]=run_subprocess(filename, args.timeout)
        print('  '+results[name]['status'],flush=True)
    for name,fn in [('invalid_workbooks',check_invalid_inputs),('public_limits_and_stop',check_public_limits),('public_catalytic_benchmark',benchmark_catalytic)]:
        print(f'Running {name}...',flush=True)
        t=time.perf_counter()
        try: results[name]=fn()
        except Exception as e: results[name]={'status':'FAIL','seconds':round(time.perf_counter()-t,3),'detail':repr(e)+'\n'+traceback.format_exc()[-3000:]}
        print('  '+results[name]['status'],flush=True)
    for case in ['biodiesel_6p','synthetic_8p_6ds']:
        name='public_'+case
        print(f'Running {name}...',flush=True)
        results[name]=extended_public_case(case)
        print('  '+results[name]['status'],flush=True)
    limitations=[
        'The 8-parameter/6-dataset case uses synthetic concentration modifiers and duplicated observations; it tests workload, not parameter identifiability.',
        'A LIMIT_REACHED result demonstrates the cooperative guard, not a successful fit.',
        'Cooperative time budgets cannot guarantee a hard timeout or safe multiuser concurrency.',
        'A converged least-squares result does not establish parameter identifiability.',
        'Public Streamlit UI and concurrent workload testing remain necessary before deployment.',
    ]
    payload={'title':'KineticFittingPot v1.15 validation report','generated_utc':datetime.now(timezone.utc).isoformat(),
             'python':sys.version,'full_suite':args.full,'results':results,'limitations':limitations}
    (REPORT_DIR/'KineticFittingPot_v1_15_results.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    lines=['# KineticFittingPot v1.15 — Validation report','',f"Generated (UTC): {payload['generated_utc']}",'',
           '| Test | Result | Seconds |','|---|---|---:|']
    for name,r in results.items():lines.append(f"| {name} | {r['status']} | {r['seconds']} |")
    for name,r in results.items():lines+=['',f'## {name}','',r['detail'] or '(no output)']
    lines+=['','## Outstanding validation limitations','']+[f'- {x}' for x in limitations]
    (REPORT_DIR/'KineticFittingPot_v1_15_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    bad=[n for n,r in results.items() if r['status'] not in ('PASS',)]
    print('\nReport:', REPORT_DIR/'KineticFittingPot_v1_15_results.md')
    print('Result:', 'CHECK REQUIRED: '+', '.join(bad) if bad else 'SELECTED TESTS PASS; NOT YET DEPLOYMENT CERTIFIED')
    return 1 if bad else 0

if __name__=='__main__': raise SystemExit(main())

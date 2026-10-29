from __future__ import annotations
"""Isolated public-mode workloads. All stress-case extensions are synthetic."""
import argparse
from dataclasses import replace
from io import BytesIO
import json
from pathlib import Path
import sys
from time import perf_counter
import traceback
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from utils.kinetic_fitting_engine import parse_fitting_workbook, fit_multistart, FittingBudget, FittingBudgetExceeded
from utils.deployment import PUBLIC_FITTING_LIMITS, public_fitting_violations

BASE=ROOT/'data/case_studies/KineticFittingPot_kinetic_fit_results_Biodiesel.xlsx'

def stress_bytes():
    """Extend the 6-parameter biodiesel model with two concentration modifiers;
    duplicate its A/B/C conditions under fresh IDs for a workload test.
    These are NOT six independent experimental datasets and do not validate identifiability.
    """
    w=load_workbook(BASE)
    s=w['Parameters']
    s.append(['kmod_f',0.01,'m³ kmol⁻¹','Yes',1e-5,0.1,'Synthetic rate modifier, stress testing only'])
    s.append(['kmod_r',0.01,'m³ kmol⁻¹','Yes',1e-5,0.1,'Synthetic rate modifier, stress testing only'])
    r=w['Reactions'];r['C2']='(k1f*c_TG*c_MeOH)*(1+kmod_f*c_TG)';r['C3']='(k1r*c_DG*c_ME)*(1+kmod_r*c_DG)'
    ds=w['Datasets'];rows=list(ds.values)[1:]; ids={str(row[0]):str(row[0])+'_replica' for row in rows}
    for row in rows:
        rr=list(row);rr[0]=ids[str(row[0])];rr[1]='SYNTHETIC REPLICA of '+str(row[1]);ds.append(rr)
    obs=w['Experimental_Data']; old=list(obs.values)[1:]
    for row in old:
        rr=list(row);rr[0]=ids[str(row[0])];rr[-1]='SYNTHETIC REPLICA (same measurement, not independent)';obs.append(rr)
    out=BytesIO();w.save(out);return out.getvalue()

def run(case):
    blob=BASE.read_bytes() if case=='biodiesel_6p' else stress_bytes()
    problem=parse_fitting_workbook(blob)
    issues=public_fitting_violations(problem)
    if issues: raise ValueError('Public limits rejected case: '+str(issues))
    limits=PUBLIC_FITTING_LIMITS
    budget=FittingBudget(max_integrations=limits['max_integrations'],max_rhs_evaluations=limits['max_rhs_evaluations'],max_wall_time_s=limits['max_wall_time_s'])
    start=perf_counter()
    output={'case':case,'source':'original Biodiesel fit-results workbook' if case=='biodiesel_6p' else 'synthetically extended Biodiesel workbook; duplicated observations, not independent evidence',
            'fitted_parameters':len(problem.fit_parameter_ids),'datasets':len(problem.datasets),'observations':len(problem.observations),
            'settings':{'multistart':limits['max_starts'],'max_nfev':limits['max_nfev_per_start']}}
    try:
        result=fit_multistart(problem,weighting='species_scaled',n_starts=limits['max_starts'],max_nfev=limits['max_nfev_per_start'],budget=budget)
        output.update({'status':result['status'],'sse':float(result['best']['sse']),
                       'estimates':dict(zip(problem.fit_parameter_ids,map(float,result['best_values']))),
                       'start_records':[{'start':r['start'],'success':r['success'],'nfev':r['nfev'],'sse':float(r['sse']),'message':r['message']} for r in result['records']]})
    except FittingBudgetExceeded as exc:
        output.update(status='BUDGET_STOP',detail=str(exc))
    except Exception as exc:
        output.update(status='ERROR',detail=repr(exc),traceback=traceback.format_exc()[-1200:])
    output.update(elapsed_s=round(perf_counter()-start,3),budget=budget.summary())
    print(json.dumps(output,allow_nan=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['biodiesel_6p','synthetic_8p_6ds'],required=True)
    args=ap.parse_args();run(args.case)

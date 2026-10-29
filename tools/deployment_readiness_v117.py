from __future__ import annotations
"""Predeployment verification, not a substitute for a browser/cloud acceptance test."""
import argparse, ast, importlib.metadata, json, os, pathlib, platform, subprocess, sys, time
from datetime import datetime, timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
REPORT=ROOT/'validation_reports'
TESTS=[
 ('batch_simulation','smoke_test_batch_simulator.py',60),
 ('general_batch','smoke_test_general_batch_model.py',60),
 ('initial_rate','test_initial_rate_validation.py',60),
 ('fitting_regression','smoke_test_kinetic_fitting_engine.py',120),
 ('reaction_stoichiometry','smoke_test_reaction_stoichiometry_fundamentals.py',60),
 ('model_diagnostics_fundamentals','smoke_test_model_diagnostics_fundamentals.py',60),
 ('model_diagnostics_engine','smoke_test_model_diagnostics_engine.py',100),
 ('biodiesel_case_study','smoke_test_kinetic_fitting_case_study.py',90),
 ('public_worker','test_public_worker_v116.py',110),
]
def check(name, fn):
 t=time.perf_counter()
 try:
  detail=fn(); return dict(test=name,status='PASS',seconds=round(time.perf_counter()-t,3),detail=str(detail))
 except Exception as exc: return dict(test=name,status='FAIL',seconds=round(time.perf_counter()-t,3),detail=f'{type(exc).__name__}: {exc}')
def subprocess_check(item):
 name,filename,limit=item; t=time.perf_counter()
 try:
  p=subprocess.run([sys.executable,str(ROOT/'tools'/filename)],cwd=ROOT,capture_output=True,text=True,timeout=limit,env={**os.environ,'PYTHONUNBUFFERED':'1','PYTHONPATH':str(ROOT)+os.pathsep+os.environ.get('PYTHONPATH','')})
  return dict(test=name,status='PASS' if p.returncode==0 else 'FAIL',seconds=round(time.perf_counter()-t,3),detail=(p.stdout+'\n'+p.stderr).strip()[-4500:])
 except subprocess.TimeoutExpired as exc:
  return dict(test=name,status='TIMEOUT',seconds=round(time.perf_counter()-t,3),detail=f'Exceeded independent test deadline: {limit} s')
def mode_check():
 from utils.deployment import deployment_mode, PUBLIC_FITTING_LIMITS, public_cloud_workbook_violations
 previous=os.environ.get('KINETICFITTINGPOT_MODE')
 try:
  for alias,expected in [('local','local'),('cloud','public_cloud')]:
   os.environ['KINETICFITTINGPOT_MODE']=alias
   assert deployment_mode()==expected
 finally:
  if previous is None: os.environ.pop('KINETICFITTINGPOT_MODE',None)
  else: os.environ['KINETICFITTINGPOT_MODE']=previous
 assert PUBLIC_FITTING_LIMITS['max_wall_time_s']==60
 assert PUBLIC_FITTING_LIMITS['max_rhs_evaluations']==400000
 assert public_cloud_workbook_violations(b'not-an-xlsx')
 return 'Both local/cloud overrides and workbook rejection verified; computational limits unchanged. Public fit and diagnostics routing also checked separately.'
def route_check():
 source=(ROOT/'app.py').read_text(encoding='utf-8')
 tree=ast.parse(source)
 assigned={}
 for n in ast.walk(tree):
  if isinstance(n,ast.Assign):
   for target in n.targets:
    if isinstance(target,ast.Name): assigned[target.id]=n.value
 diag=assigned.get('DIAG'); fit=assigned.get('FIT')
 assert isinstance(diag,ast.IfExp) and isinstance(diag.test,ast.Call) and isinstance(diag.test.func,ast.Name) and diag.test.func.id=='is_public_cloud'
 assert isinstance(diag.body,ast.Name) and diag.body.id=='_locked_diag'
 assert isinstance(diag.orelse,ast.Attribute) and diag.orelse.attr=='render'
 assert isinstance(fit,ast.Attribute) and fit.attr=='render'
 source_fit=(ROOT/'modules'/'kinetic_fitting.py').read_text(encoding='utf-8')
 assert 'if cloud:' in source_fit and 'run_public_fit(' in source_fit and 'fit_multistart(' in source_fit
 return 'Source-level Streamlit routing: public fit enabled; public Advanced Diagnostics locked; local Advanced Diagnostics enabled. Browser behaviour NOT exercised.'
def dependency_check():
 pins={}
 for line in (ROOT/'requirements.txt').read_text().splitlines():
  line=line.strip()
  if not line or line.startswith('#'):continue
  name,sep,version=line.partition('==')
  assert sep and name and version, 'Unpinned dependency: '+line
  pins[name]=version
 for name in ('streamlit','numpy','pandas','scipy','openpyxl','plotly'):assert name in pins, f'Missing {name}'
 installed=[]
 for name,expected in pins.items():
  try: actual=importlib.metadata.version(name)
  except importlib.metadata.PackageNotFoundError: actual='NOT INSTALLED'
  installed.append(f'{name} pinned={expected}, current={actual}')
 return 'Pinned dependencies verified. Environment: '+platform.platform()+'; '+ '; '.join(installed)
def package_check():
 assert (ROOT/'.streamlit'/'config.toml').is_file()
 assert (ROOT/'run_KineticFittingPot.bat').is_file()
 forbidden=[x for x in ROOT.rglob('*') if x.is_file() and x.name in {'secrets.toml','.env'}]
 assert not forbidden, 'Private/runtime files in package: '+str(forbidden[:5])
 return 'Deployment config present; no secrets.toml/.env found. Runtime __pycache__ files will be excluded from ZIP packaging.'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true',help='Skip separate numerical smoke scripts');args=parser.parse_args()
 REPORT.mkdir(exist_ok=True)
 results=[check('mode_and_input_restrictions',mode_check),check('page_access_routing_static',route_check),check('dependency_manifest',dependency_check),check('package_hygiene',package_check)]
 if not args.quick:
  for test in TESTS:
   r=subprocess_check(test); results.append(r)
   print(f"{r['test']}: {r['status']} ({r['seconds']:.2f}s)",flush=True)
 else: print('Quick mode: numerical and worker tests intentionally NOT RUN.',flush=True)
 stamp=datetime.now(timezone.utc).isoformat()
 full=not args.quick
 verdict='PASS_LOCAL_AUTOMATED' if full and all(x['status']=='PASS' for x in results) else ('INCOMPLETE_QUICK' if not full else 'REVIEW_REQUIRED')
 data={'version':'1.17','generated_utc':stamp,'verdict':verdict,'environment':{'python':sys.version,'platform':platform.platform()},'results':results,'manual_checks_pending':['Run actual Streamlit in forced public mode (Windows launcher included): upload & fit, busy, timeout, budget-stop UI, Basic Diagnostics, Advanced Diagnostics lock.','Run normal local mode: Advanced Diagnostics and biodiesel case study.','Review full content and styling in browser; inspect iPad after initial cloud deployment.','Cloud instance process management, concurrent users and memory behaviour cannot be certified from local checks.']}
 (REPORT/'KineticFittingPot_v1_17_results.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 lines=['# KineticFittingPot v1.17 — Technical readiness','',f'Generated UTC: {stamp}',f'**Automated verdict: {verdict}**','', '| Test | Status | Seconds |','|---|---|---:|']
 lines += [f"| {r['test']} | {r['status']} | {r['seconds']:.3f} |" for r in results]
 for r in results: lines.extend(['',f"## {r['test']} — {r['status']}",'','```text',r['detail'],'```'])
 lines+=['','## Manual/browser and cloud checks remain outstanding'] + [f'- {x}' for x in data['manual_checks_pending']]
 (REPORT/'KineticFittingPot_v1_17_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print('AUTOMATED VERDICT:',verdict,flush=True)
 print('Report:',REPORT/'KineticFittingPot_v1_17_results.md',flush=True)
 return 0 if verdict!='REVIEW_REQUIRED' else 1
if __name__=='__main__':raise SystemExit(main())

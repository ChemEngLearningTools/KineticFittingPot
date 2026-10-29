"""Pre-run rate evaluation regression (run with installed project dependencies)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.general_batch_model import parse_model_workbook, model_volume_m3, evaluate_rates
import numpy as np
p = Path(__file__).resolve().parents[1]/'data/templates/KineticFittingPot_Isothermal_Batch_Model_Template.xlsx'
m = parse_model_workbook(p.read_bytes())
v = model_volume_m3(m, m.initial_moles_kmol)
r = evaluate_rates(m, m.initial_moles_kmol/v)
assert len(r)==len(m.reaction_ids) and np.all(np.isfinite(r))
print('Initial rate evaluation: PASS')

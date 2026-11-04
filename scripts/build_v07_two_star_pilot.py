"""Create an UNEXECUTED reproducible IRSA plan for two real Taurus catalog stars."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stellarforge.observational_plan import make_pilot_plan, save_pilot_plan

if __name__=='__main__':
    seed=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'
    destination=ROOT/'reports/observational_readiness_v0.7/TWO_STAR_PILOT_NOT_EXECUTED.json'
    plan=make_pilot_plan(seed)
    save_pilot_plan(destination,plan)
    print(json.dumps({'pilot_stars':[t['catalog_name'] for t in plan['pilot_targets']],
                      'pilot_status':plan['status'],
                      'observed_ztf_rows':0,
                      'manifest':str(destination)},indent=2))
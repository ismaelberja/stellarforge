import json
from pathlib import Path
from scripts.run_v10_pilot import execute_pilot


def test_offline_summary_never_makes_discovery_claims(tmp_path):
    seed=Path(__file__).resolve().parents[1]/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'
    def fake(*, seed, output, execute):
        assert not execute
        return {'acquisition':[{'target':'FT Tau','raw_response_present':False,
                                'result':'NOT_ATTEMPTED_OFFLINE_MODE'}]}
    v=execute_pilot(output=tmp_path,seed=seed,runner=fake)
    assert v['gaia_ztf_associations_independently_verified']==0
    assert not v['scientific_publication_ready']
    assert 'FT Tau' in (tmp_path/'V10_INTAKE_REPORT.md').read_text()
    assert json.loads((tmp_path/'V10_TRIAGE.json').read_text())['network_requested'] is False


def test_network_mode_does_not_promote_raw_response_to_science(tmp_path):
    seed=Path(__file__).resolve().parents[1]/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'
    def fake(*, seed, output, execute):
        assert execute
        return {'acquisition':[{'target':'CIDA 11','raw_response_present':True,
                                'result':'RAW_RESPONSE_SAVED_NOT_AUTHENTICATED_OR_CROSSMATCHED'}]}
    v=execute_pilot(output=tmp_path,seed=seed,runner=fake,execute=True)
    assert v['raw_responses_present']==1
    assert v['physical_dipper_or_burster_confirmations']==0
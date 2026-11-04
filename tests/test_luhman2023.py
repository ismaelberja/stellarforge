"""Luhman 2023 MRT parser tests; synthetic records remain explicitly synthetic."""
import csv
import hashlib
import io
import json
from pathlib import Path
from unittest.mock import patch
import pytest
from stellarforge.luhman2023 import (
    parse_membership_mrt, validate_technical_seed, audit_seed_against_full_mrt,
    git_blob_sha1, MIRROR_URL, MIRROR_BLOB_SHA1, CatalogValidationError,
    download_pinned_mirror,
)

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv'


def fixed_line(gaia='123456789012345678',ra=60.123456,dec=25.234567,
               group='L1495/B209',mag='14.500',reference='Gaia'):
    chars=[' ']*361
    def insert(a,b,v):
        v=str(v)
        assert len(v) <= b-a+1
        chars[a-1:a-1+len(v)]=list(v)
    insert(1,19,gaia)
    insert(21,37,'J04001234+2523456')
    insert(59,81,'SYNTHETIC TEST STAR')
    insert(83,91,f'{ra:.6f}')
    insert(93,101,f'{dec:.6f}')
    insert(103,109,reference)
    insert(169,173,'M4.5')
    insert(175,180,'11.234')
    insert(188,194,'-21.221')
    insert(297,302,mag)
    insert(345,360,group)
    return ''.join(chars)


def raw_mrt(*rows):
    return ('Title: A Census of the Taurus Star-forming Region and Neighboring Associations with Gaia\n'
            'Table: Adopted Members of Taurus\n'
            'Byte-by-byte Description of file: ajac9da3t2_mrt.txt\n'
            + '\n'.join(rows) + '\n').encode('utf-8')


def test_pinned_mirror_url_is_immutable_and_hash_fixed():
    assert '7b6a5c83eca81fc66e50cb4889ee35cb28861367' in MIRROR_URL
    assert len(MIRROR_BLOB_SHA1) == 40
    assert git_blob_sha1(b'hello') == 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0'


def test_parser_preserves_64_bit_id_and_membership_column():
    raw=raw_mrt(fixed_line())
    results=parse_membership_mrt(raw,enforce_reference_counts=False)
    assert results['record_count'] == 1
    assert results['with_gaia_dr3_source_id'] == 1
    star=results['members'][0]
    assert star['gaia_dr3_source_id'] == '123456789012345678'
    assert star['ra_deg'] == 60.123456
    assert star['dec_deg'] == 25.234567
    assert star['gmag'] == 14.5
    assert star['pmra_mas_per_year'] == 11.234
    assert star['pmdec_mas_per_year'] == -21.221
    assert star['position_reference'] == 'Gaia'
    assert star['kinematic_group'] == 'L1495/B209'
    assert results['source_git_blob_sha1'] == git_blob_sha1(raw)


def test_parser_keeps_missing_gaia_member_as_member():
    raw=raw_mrt(fixed_line(gaia='',reference='2MASS'))
    out=parse_membership_mrt(raw,enforce_reference_counts=False)
    assert out['record_count'] == 1
    assert out['with_gaia_dr3_source_id'] == 0
    assert out['without_gaia_dr3_source_id'] == 1


def test_full_catalog_counts_gate_rejects_partial_table():
    with pytest.raises(CatalogValidationError,match='Unexpected population'):
        parse_membership_mrt(raw_mrt(fixed_line()))


def test_source_identity_gate():
    with pytest.raises(CatalogValidationError,match='Wrong table'):
        parse_membership_mrt(b'Taurus fake content\n' + fixed_line().encode())


def test_duplicate_gaia_ids_rejected():
    raw=raw_mrt(fixed_line(),fixed_line(ra=62))
    with pytest.raises(CatalogValidationError,match='Duplicate Gaia'):
        parse_membership_mrt(raw,enforce_reference_counts=False)


def test_invalid_ra_rejected():
    raw=raw_mrt(fixed_line(ra=-1))
    with pytest.raises(CatalogValidationError,match='Invalid sky'):
        parse_membership_mrt(raw,enforce_reference_counts=False)


def test_canonical_real_coordinate_seed_is_validated_but_not_science_approved():
    audit=validate_technical_seed(SEED)
    assert audit['rows'] == 24
    assert audit['named_groups'] == 13
    assert audit['scientific_pilot_frozen'] is False
    assert audit['disk_class_strata_verified'] is False


def test_seed_preserves_real_gaia_identifiers_as_strings():
    with SEED.open(newline='') as f:
        rows=list(csv.DictReader(f))
    ids=[r['gaia'] for r in rows]
    assert len(ids)==len(set(ids))==24
    assert '164800235906366976' in ids
    assert '3406270362673330944' in ids
    assert {r['reference'] for r in rows} == {'Gaia'}
    assert {r['group'] for r in rows} == {
        'B209N','HD28354','L1489/L1498','L1495/B209','L1517','L1521/B213',
        'L1524/L1529/B215','L1527','L1536','L1544','L1551','L1558','TTau'}


def test_seed_corruption_is_detected(tmp_path):
    broken=tmp_path/'subset.csv'
    broken.write_text(SEED.read_text().replace('164800235906366976','not_an_identifier'))
    with pytest.raises(CatalogValidationError,match='Duplicate or invalid'):
        validate_technical_seed(broken)


def test_seed_data_are_never_allowed_to_claim_disk_class():
    with SEED.open() as f:
        fieldnames=csv.DictReader(f).fieldnames
    assert 'disk_class' not in fieldnames
    assert 'is_dipper' not in fieldnames


def test_download_fails_closed_if_mirror_byte_hash_does_not_match(tmp_path):
    class MockResponse:
        def __enter__(self): return self
        def __exit__(self,*_): pass
        def read(self,n): return raw_mrt(fixed_line())
    with patch('stellarforge.luhman2023.urlopen',return_value=MockResponse()):
        with pytest.raises(CatalogValidationError,match='checksum mismatch'):
            download_pinned_mirror(tmp_path/'table.txt')
    assert not (tmp_path/'table.txt').exists()
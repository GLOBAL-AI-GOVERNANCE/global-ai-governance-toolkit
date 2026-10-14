"""Adversarial tests for the bounded synthetic reference, not operational assessment."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from witness import InvalidInput, parse_json, run, evaluate, utc
EVAL='2026-10-14T12:00:00Z'

class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.fixture=HERE/'fixtures/valid.json'
        self.root=HERE/'fixtures'
        self.raw=self.fixture.read_bytes()
        self.data=json.loads(self.raw)
    def result(self, change=None):
        case=copy.deepcopy(self.data)
        if change: change(case)
        raw=json.dumps(case,sort_keys=True).encode()
        return evaluate(case,raw,EVAL,self.root)
    def codes(self,change):
        return {x['id'].split(':',1)[1] for x in self.result(change)['findings']}
    def test_clean_declared_record_is_bounded_pass(self):
        r=self.result()
        self.assertEqual(r['status'],'PASS')
        self.assertEqual(r['authority_effect'],'NONE')
        self.assertFalse(r['details']['independent_assessment'])
        self.assertEqual(r['details']['review_disposition'],'PENDING_HUMAN_DECISION')
    def test_deterministic_bytes_and_exit(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'out'
            x,first=run(self.fixture,dest,EVAL,evidence_root=self.root)
            raw=(dest/'profile-result.json').read_bytes()
            y,second=run(self.fixture,dest,EVAL,evidence_root=self.root)
            self.assertEqual(x,0);self.assertEqual(y,0)
            self.assertEqual(raw,(dest/'profile-result.json').read_bytes())
            self.assertEqual(first,second)
    def test_undeclared_executed(self):
        self.assertIn('UNAUTHORIZED_TOOL_EXECUTED',self.codes(lambda x:x['actions'][0].update(tool='admin_shell')))
    def test_denied_but_executed(self):
        self.assertIn('ACTION_EXECUTED_WITHOUT_ALLOW',self.codes(lambda x:x['actions'][0].update(control_decision='DENY')))
    def test_missing_approval(self):
        self.assertIn('MISSING_REQUIRED_APPROVAL',self.codes(lambda x:x['actions'][0].update(tool='publish')))
    def test_denied_approval(self):
        self.assertIn('DENIED_APPROVAL_EXECUTED',self.codes(lambda x:x['actions'][0].update(approval='DENIED')))
    def test_policy_mismatch(self):
        self.assertIn('POLICY_ID_MISMATCH',self.codes(lambda x:x['actions'][0].update(policy_id='other')))
    def test_revoked_policy(self):
        self.assertIn('EXECUTED_OUTSIDE_AUTHORITY_WINDOW',self.codes(lambda x:x['policy'].update(revoked_at='2026-10-12T11:00:00Z')))
    def test_expired_policy(self):
        self.assertIn('POLICY_NOT_CURRENT',self.codes(lambda x:x['policy'].update(valid_until='2026-10-13T00:00:00Z')))
    def test_monitor_disabled(self):
        self.assertIn('MONITOR_NOT_ACTIVE',self.codes(lambda x:x.update(monitor_status='DISABLED')))
    def test_coverage_unknown(self):
        self.assertIn('COVERAGE_GAP',self.codes(lambda x:x.update(observation_coverage='UNKNOWN')))
    def test_execution_unknown(self):
        self.assertIn('UNKNOWN_EXECUTION',self.codes(lambda x:x['actions'][0].update(execution_observation='UNKNOWN')))
    def test_not_observed_is_conditional(self):
        r=self.result(lambda x:x['actions'][0].update(execution_observation='NOT_OBSERVED',control_decision='DENY'))
        self.assertEqual(r['status'],'CONDITIONAL')
    def test_unbound_evidence(self):
        self.assertIn('UNBOUND_ACTION_EVIDENCE',self.codes(lambda x:x['actions'][0].update(evidence_ref='missing.txt')))
    def test_tampered_evidence_digest(self):
        self.assertIn('EVIDENCE_DIGEST_MISMATCH',self.codes(lambda x:x['evidence'][0].update(sha256='sha256:'+'0'*64)))
    def test_traversal_rejected(self):
        self.assertIn('EVIDENCE_MISSING_OR_UNSAFE',self.codes(lambda x:x['evidence'][0].update(reference='../secret.txt')))
    def test_duplicate_keys_rejected(self):
        with self.assertRaises(InvalidInput):parse_json(b'{"a":1,"a":2}')
    def test_nonfinite_number_rejected(self):
        with self.assertRaises(InvalidInput):parse_json(b'{"x":NaN}')
    def test_unknown_enum_rejected(self):
        with self.assertRaises(InvalidInput):self.result(lambda x:x['actions'][0].update(control_decision='MAGIC'))
    def test_future_action_fails(self):
        self.assertIn('FUTURE_ACTION',self.codes(lambda x:x['actions'][0].update(at='2026-10-20T00:00:00Z')))
    def test_utc_calendar(self):
        with self.assertRaises(InvalidInput):utc('2026-02-30T00:00:00Z')
    def test_evidence_missing(self):
        self.assertIn('EVIDENCE_MISSING_OR_UNSAFE',self.codes(lambda x:x['evidence'][0].update(reference='not-there.txt')))

if __name__=='__main__':unittest.main()

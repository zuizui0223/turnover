#!/usr/bin/env python3
"""Regression for independently rounded observed K and log(K) artifacts.

A0003 is a genuine frozen archive row.  No OU simulation outcome is needed:
we test only that K-scale identity is maintained and that distinct K values
cannot slip through a log-scale rounding tolerance.
"""
from pathlib import Path
from types import SimpleNamespace
import math
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'/'analysis'))
from aggregate_austraits_k_shared_ou_v0_1 import verify_archived_K_identity

def raises(message,fn):
    try:
        fn()
    except ValueError as e:
        assert message in str(e), str(e)
        return
    raise AssertionError('Expected to reject corrupted OU K reference: '+message)

def main():
    row=SimpleNamespace(S3_K=0.1183,S3_logK=-2.1349,
                        prune_K=0.2424,prune_logK=-1.4174)
    # Old validator rejected this because |log(.1183)-(-2.1349)|>.00021.
    assert abs(math.log(row.S3_K)-row.S3_logK)>.00021
    verify_archived_K_identity('A0003','S3',
                               {'observed_logK':math.log(row.S3_K)},row,'S3_logK')
    verify_archived_K_identity('A0003','prune_only',
                               {'observed_logK':math.log(row.prune_K)},row,'prune_logK')
    raises('OU logK differs from archived K',
           lambda:verify_archived_K_identity('A0003','S3',
                     {'observed_logK':math.log(row.S3_K)+.0003},row,'S3_logK'))
    bad=SimpleNamespace(S3_K=.1183,S3_logK=-2.131,
                        prune_K=.2424,prune_logK=-1.4174)
    raises('inconsistent archived K and logK',
           lambda:verify_archived_K_identity('A0003','S3',
                    {'observed_logK':math.log(bad.S3_K)},bad,'S3_logK'))
    bad=SimpleNamespace(S3_K=-.1183,S3_logK=-2.1349,
                        prune_K=.2424,prune_logK=-1.4174)
    raises('nonfinite',lambda:verify_archived_K_identity('A0003','S3',
                         {'observed_logK':0},bad,'S3_logK'))
    print('PASS: frozen A0003 independent-rounding regression and hard identity failures')

if __name__=='__main__':
    main()

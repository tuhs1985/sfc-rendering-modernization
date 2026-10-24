import copy
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/m1_component'))
from identity_census import analyze,COLUMNS


class IdentityCensusTests(unittest.TestCase):
    def fixture(self):
        entries=[]
        for owner in (1,2,3):
            key=[0]*19;key[0]=1;key[2]=100+owner;key[3]=200;key[6]=owner
            entries.append(dict(key=key,first_frame=600,last_frame=600,first_ms=10000,last_ms=10000,observations=1))
            key=[0]*19;key[0]=3;key[3]=200;key[4]=300;key[6]=1;key[7]=100+owner;key[8]=200;key[9]=key[11]=owner
            entries.append(dict(key=key,first_frame=600,last_frame=600,first_ms=10000,last_ms=10000,observations=1))
        return dict(schema='m1.identity-census.v1',enabled=True,capacity=256,storage_bytes=25632,
                    observations=6,omitted_observations=0,columns=list(COLUMNS),entries=entries)

    def test_three_instances_and_choice_mismatch_beyond_detail_window(self):
        report=analyze(self.fixture())
        self.assertEqual(report['native_ship_epoch_pairs'],3)
        self.assertEqual(len(report['shared_visuals']),1)
        self.assertEqual([r['context_owner'] for r in report['context_choice_mismatches']],[2,3])
        self.assertEqual(report['first_ms'],10000)

    def test_correct_same_asset_instances_do_not_imply_wrong_owner(self):
        data=self.fixture()
        for entry in data['entries']:
            k=entry['key']
            if k[0]==3:k[6]=k[11]
        self.assertEqual(analyze(data)['context_choice_mismatches'],[])

    def test_omission_is_explicit_partial(self):
        data=self.fixture();data['observations']+=20;data['omitted_observations']=20
        self.assertEqual(analyze(data)['result'],'IDENTITY_CENSUS_PARTIAL')

    def test_invalid_counter_tuple_and_time_rejected(self):
        cases=[]
        for field,value in [('observations',7),('capacity',257),('storage_bytes',32768)]:
            d=self.fixture();d[field]=value;cases.append(d)
        d=self.fixture();d['entries'][0]['key'][2]=-1;cases.append(d)
        d=self.fixture();d['entries'][0]['first_ms']=20000;cases.append(d)
        d=self.fixture();d['entries'].append(copy.deepcopy(d['entries'][0]));d['observations']+=1;cases.append(d)
        for data in cases:
            with self.assertRaises(ValueError):analyze(data)

    def test_context_must_be_qualified_before_naming_mismatch(self):
        data=self.fixture()
        for entry in data['entries']:
            if entry['key'][0]==3:entry['key'][8]=999
        report=analyze(data)
        self.assertEqual(report['context_choice_mismatches'],[])
        self.assertEqual(report['model_observations_without_qualified_context'],3)

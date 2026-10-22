import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from lifecycle_capture import PHASES, RECOVERY_PHASES, analyze


class LifecycleCaptureTests(unittest.TestCase):
    def exercise(self, dropped=0, malformed=False, missing=False):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)
            rows=[]
            for owner,status,revision,ms in ((2,1,2,100),(2,2,2,31000),(4,1,4,45000),(4,2,4,72000)):
                row=[0]*96;row[0]=len(rows)+1;row[1]=owner;row[3]=ms;row[4]=status;row[7]=revision;rows.append(row)
            (path/'LIVE-SCENE-001-updates.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
            (path/'LIFECYCLE-001-events.jsonl').write_text(json.dumps([1] if malformed else rows[1])+'\n')
            worker=dict(lifecycle_capture=True,stopped=True,io_failed=False,saturated=False,dropped=dropped,
                        lifecycle_dropped=0,lifecycle_omitted=0,lifecycle_pending=0,lifecycle_records=1)
            if missing:worker.pop('lifecycle_pending')
            (path/'LIVE-SCENE-001-worker.json').write_text(json.dumps(worker))
            return analyze(path)

    def test_alive_gap_and_retirement_never_infer_death(self):
        result=self.exercise()
        self.assertEqual(result['result'],'OBSERVATIONS_READY_NOT_DEATH_PROOF')
        self.assertFalse(result['native_death_signal_qualified'])
        self.assertEqual(sorted(result['owners']),['2','4'])
        self.assertEqual(result['owners']['4']['last_ms'],72000)

    def test_lost_record_or_missing_counter_is_partial(self):
        for kwargs in (dict(dropped=1),dict(missing=True)):
            self.assertEqual(self.exercise(**kwargs)['result'],'PARTIAL')

    def test_malformed_event_rejected(self):
        with self.assertRaises(ValueError):self.exercise(malformed=True)

    def test_cues_allow_setup_and_alive_return_before_destruction(self):
        self.assertEqual([p[0] for p in PHASES],[15,25,40,60])
        self.assertEqual([p[1] for p in PHASES],[1,2,3,4])
        self.assertLess(PHASES[-1][0],90)
    def test_recovery_cues_repeat_alive_return_without_destroy_instruction(self):
        self.assertEqual([p[0] for p in RECOVERY_PHASES],[15,25,40,55,70,80])
        self.assertEqual([p[1] for p in RECOVERY_PHASES],[1,2,3,2,3,1])
        self.assertFalse(any('destroy' in message.lower() for _,_,message in RECOVERY_PHASES))


if __name__=='__main__':unittest.main()

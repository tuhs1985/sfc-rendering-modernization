import hashlib,json,os,stat,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools/asset_diagnostics"))
import share_evidence as tool

class SharingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);(self.root/"artifacts").mkdir()
        self.a=self.root/"artifacts/a.raw";self.b=self.root/"artifacts/b.raw"
        self.a.write_bytes(b"original pixels");self.b.write_bytes(self.a.read_bytes())
        self.group=dict(bytes=self.a.stat().st_size,sha256=hashlib.sha256(self.a.read_bytes()).hexdigest(),files=["artifacts/a.raw","artifacts/b.raw"])
    def tearDown(self):
        for p in (self.root/"artifacts").iterdir():
            if p.is_file():p.chmod(stat.S_IREAD|stat.S_IWRITE)
        self.temp.cleanup()
    def test_dry_run_does_not_rewrite_or_freeze_files(self):
        result=tool.share(self.root,[self.group],apply=False)
        self.assertFalse(os.path.samefile(self.a,self.b));self.assertEqual(result["shareable_bytes"],15)
        self.assertFalse(result["linked"])
    def test_actual_links_preserve_pixels_and_repeat_is_idempotent(self):
        result=tool.share(self.root,[self.group],apply=True)
        self.assertTrue(os.path.samefile(self.a,self.b));self.assertEqual(self.a.read_bytes(),b"original pixels")
        self.assertEqual(result["linked"],1)
        if os.name=="nt":
            self.assertTrue(self.a.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY)
            self.assertTrue(self.b.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY)
        self.assertEqual(tool.share(self.root,[self.group],apply=True)["linked"],0)
    def test_changed_input_refused_without_replacing_it(self):
        self.b.write_bytes(b"different bytes")
        with self.assertRaises(ValueError):tool.share(self.root,[self.group],apply=True)
        self.assertFalse(os.path.samefile(self.a,self.b));self.assertEqual(self.b.read_bytes(),b"different bytes")
    def test_failed_atomic_replace_preserves_original(self):
        with patch.object(tool.os,"replace",side_effect=OSError("simulated")):
            with self.assertRaises(OSError):tool.share(self.root,[self.group],apply=True)
        self.assertEqual(self.b.read_bytes(),b"original pixels");self.assertFalse(os.path.samefile(self.a,self.b))
        self.assertEqual(len(list((self.root/"artifacts").iterdir())),2)
    def test_inventory_only_selects_duplicate_images_in_completed_older_runs(self):
        base=self.root/"artifacts/remix-runtime/runs";base.mkdir(parents=True)
        for name,error in (("20260101-one",None),("20260102-two",None),("20260103-failed","failed"),("20990101-future",None)):
            run=base/name;run.mkdir();(run/"result.json").write_text(json.dumps(dict(error=error)))
            (run/"texture-0.bin").write_bytes(b"x"*9000)
            (run/"private.txt").write_bytes(b"x"*9000)
        report=tool.inventory(self.root,"2026-02-01")
        self.assertEqual(len(report["groups"]),1);self.assertEqual(len(report["groups"][0]["files"]),2)
        self.assertEqual(report["potential_shared_bytes"],9000)

    def test_outside_artifacts_is_refused(self):
        external=self.root/"private.raw";external.write_bytes(b"original pixels");self.group["files"][1]="private.raw"
        with self.assertRaises(ValueError):tool.share(self.root,[self.group],apply=True)
        self.assertEqual(external.read_bytes(),b"original pixels")

if __name__=="__main__":unittest.main()

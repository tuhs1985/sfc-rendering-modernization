"""In-memory Git protocol fixtures;never create a remote or publish test data."""
from pathlib import Path
import hashlib
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/recon'))
import audit_git_publication as audit

def fixture(files):
    rows=[(hashlib.sha1(raw).hexdigest(),path,raw) for path,raw in files]
    def git(*args,stdin=None):
        if args[0]=='rev-parse':return b'a'*40+b'\n'
        if args[0]=='-c':return ('\n'.join(path for _,path,_ in rows)+'\n').encode()
        if args[:2]==('rev-list','--objects'):return ('\n'.join(oid+' '+path for oid,path,_ in rows)+'\n').encode()
        if args[:2]==('rev-list','--count'):return b'2\n'
        if args[0]=='cat-file' and args[1].startswith('--batch-check'):
            return b''.join(f'{oid} blob {len(raw)}\n'.encode() for oid,_,raw in rows)
        if args[:2]==('cat-file','--batch'):
            return b''.join(f'{oid} blob {len(raw)}\n'.encode()+raw+b'\n' for oid,_,raw in rows)
        raise AssertionError(args)
    return git

class PublicationTests(unittest.TestCase):
    def test_clean_history_and_image_require_visual_review(self):
        with patch.object(audit,'git',side_effect=fixture([('README.md',b'Project documentation\n'),('docs/evidence.png',b'\x89PNG\r\n\x1a\nfixture')])):
            result=audit.audit()
        self.assertEqual(result['commits'],2);self.assertEqual(result['unique_blobs'],2)
        self.assertFalse(result['blocked']);self.assertEqual(len(result['images_to_review']),1)
    def test_credentials_and_proprietary_binary_are_blocked_without_value_leak(self):
        secret=b'ghp_'+b'x'*36
        with patch.object(audit,'git',side_effect=fixture([('old.txt',secret),('Game Assets/client.exe',b'MZ\0binary')])):
            result=audit.audit()
        self.assertIn('github_token',{r['rule'] for r in result['blocked']})
        self.assertIn('excluded_or_sensitive_historical_path',{r['rule'] for r in result['blocked']})
        self.assertNotIn(secret.decode(),str(result))
    def test_non_utf8_and_literal_assignments_require_review(self):
        assignment=b'password='+b'"'+b'notarealcredential123'+b'"'
        with patch.object(audit,'git',side_effect=fixture([('data.txt',b'\xff'),('example.py',assignment)])):
            result=audit.audit()
        self.assertTrue(result['blocked']);self.assertEqual(len(result['manual_text_review']),1)
    def test_explicit_branch_only(self):
        for ref in ('HEAD','--all','refs/heads/../private','refs/tags/v1'):
            with self.subTest(ref=ref),self.assertRaises(ValueError):audit.audit(ref)
    def test_removed_desktop_path_cannot_be_reintroduced(self):
        with patch.object(audit,'git',side_effect=fixture([(audit.REMOVED_DESKTOP_PATH,b'\x89PNG\r\n\x1a\nfixture')])):
            result=audit.audit()
        self.assertIn('removed_private_desktop_path',{row['rule'] for row in result['blocked']})

if __name__=='__main__':unittest.main()

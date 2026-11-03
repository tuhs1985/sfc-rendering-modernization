"""Actual Windows reader compatibility and publication recovery checks."""
import ctypes as C
import mmap
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
import material_library as lib


@unittest.skipUnless(os.name=='nt','Windows material publication contract')
class PublicationTests(unittest.TestCase):
    def shared_reader(self,path):
        import msvcrt
        kernel=C.WinDLL('kernel32',use_last_error=True)
        kernel.CreateFileW.argtypes=[C.c_wchar_p,C.c_uint32,C.c_uint32,C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p]
        kernel.CreateFileW.restype=C.c_void_p
        handle=kernel.CreateFileW(str(path),0x80000000,7,None,3,128,None)
        if handle==C.c_void_p(-1).value:raise C.WinError(C.get_last_error())
        return os.fdopen(msvcrt.open_osfhandle(handle,os.O_RDONLY|os.O_BINARY),'rb')

    def test_held_reader_and_mapping_keep_old_bytes_new_read_gets_new(self):
        for mapped in (False,True):
            with self.subTest(mapped=mapped),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);lib.publish_remix_revision(root,'old')
                with self.shared_reader(root/'mod.usda') as reader:
                    mapping=mmap.mmap(reader.fileno(),0,access=mmap.ACCESS_READ) if mapped else None
                    try:
                        before=(root/'mod.usda').stat().st_mtime_ns
                        receipt=lib.publish_remix_revision(root,'new é material')
                        self.assertEqual(receipt['exchange'],'ReplaceFileW')
                        self.assertEqual(reader.read(),b'old')
                        if mapping:self.assertEqual(mapping[:],b'old')
                        self.assertEqual((root/'mod.usda').read_text(encoding='utf-8'),'new é material')
                        self.assertGreater(receipt['published_mtime_ns']//10**9,before//10**9)
                        self.assertFalse((root/'mod.usda.pending').exists())
                    finally:
                        if mapping:mapping.close()

    def test_reader_without_delete_sharing_is_not_bypassed_and_retry_works(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lib.publish_remix_revision(root,'old')
            with (root/'mod.usda').open('rb') as reader:
                with self.assertRaises(PermissionError) as caught:lib.publish_remix_revision(root,'new')
                self.assertEqual(caught.exception.winerror,32)
                self.assertEqual(reader.read(),b'old')
            lib.publish_remix_revision(root,'new')
            self.assertEqual((root/'mod.usda').read_text(),'new')

    def test_exact_packaged_arch_reader(self):
        runtime=ROOT/'artifacts/remix-runtime/deps/candidate-1.6.1/runtime'
        if not (runtime/'usd_arch.dll').exists():self.skipTest('Pinned optional runtime unavailable')
        with os.add_dll_directory(str(runtime)):
            arch=C.CDLL(str(runtime/'usd_arch.dll'))
            open_file=getattr(arch,'?ArchOpenFile@pxrInternal_v0_25_11__pxrReserved__@@YAPEAU_iobuf@@PEBD0@Z')
            open_file.argtypes=[C.c_char_p,C.c_char_p];open_file.restype=C.c_void_p
            crt=C.CDLL('ucrtbase.dll');crt.fclose.argtypes=[C.c_void_p]
            crt.fread.argtypes=[C.c_void_p,C.c_size_t,C.c_size_t,C.c_void_p];crt.fread.restype=C.c_size_t
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);lib.publish_remix_revision(root,'old')
                reader=open_file(str(root/'mod.usda').encode('utf-8'),b'rb');self.assertTrue(reader)
                try:
                    r=lib.publish_remix_revision(root,'new');self.assertEqual(r['exchange'],'ReplaceFileW')
                    buffer=C.create_string_buffer(3);self.assertEqual(crt.fread(buffer,1,3,reader),3)
                    self.assertEqual(buffer.raw,b'old');self.assertEqual((root/'mod.usda').read_bytes(),b'new')
                finally:crt.fclose(reader)

    def test_first_creation_and_repeated_revision(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);receipts=[lib.publish_remix_revision(root,str(i)) for i in range(20)]
            self.assertEqual(receipts[0]['exchange'],'rename-new')
            self.assertTrue(all(r['exchange']=='ReplaceFileW' for r in receipts[1:]))
            self.assertEqual((root/'mod.usda').read_text(),'19')
            self.assertTrue(all(b['published_mtime_ns']//10**9>a['published_mtime_ns']//10**9 for a,b in zip(receipts,receipts[1:])))

    def test_access_denial_preserves_prior_complete_file_and_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lib.publish_remix_revision(root,'old')
            def deny(*args):C.set_last_error(5);return 0
            with patch.object(lib,'_windows_replace_file',return_value=deny):
                with self.assertRaises(PermissionError) as caught:lib.publish_remix_revision(root,'new')
            self.assertEqual(caught.exception.winerror,5)
            self.assertEqual((root/'mod.usda').read_text(),'old')
            self.assertEqual((root/'mod.usda.pending').read_text(),'new')

    def test_documented_partial_errors_preserve_or_restore_public_name(self):
        for code in (1175,1176,1177):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);target=root/'mod.usda';lib.publish_remix_revision(root,'old')
                def partial(*args):
                    if code in (1176,1177):target.replace(root/'old-retained')
                    C.set_last_error(code);return 0
                with patch.object(lib,'_windows_replace_file',return_value=partial):
                    with self.assertRaises(OSError) as caught:lib.publish_remix_revision(root,'new')
                self.assertEqual(caught.exception.winerror,code)
                self.assertEqual(target.read_text(),'old' if code==1175 else 'new')
                if code!=1175:self.assertEqual((root/'old-retained').read_text(),'old')

    def test_read_only_is_not_bypassed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lib.publish_remix_revision(root,'old');target=root/'mod.usda'
            target.chmod(stat.S_IREAD)
            try:
                with self.assertRaises(PermissionError):lib.publish_remix_revision(root,'new')
                self.assertEqual(target.read_text(),'old')
            finally:target.chmod(stat.S_IWRITE)

    def test_same_content_and_timestamp_survive_extended_path(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for i in range(8):root=root/('material-library-path-'+str(i)+'-'*12)
            root.mkdir(parents=True);self.assertGreater(len(str(root)),260)
            lib.publish_remix_revision(root,'old');r=lib.publish_remix_revision(root,'new')
            self.assertEqual((root/'mod.usda').read_bytes(),b'new')
            self.assertEqual((root/'mod.usda').stat().st_mtime_ns,r['published_mtime_ns'])


if __name__=='__main__':unittest.main()

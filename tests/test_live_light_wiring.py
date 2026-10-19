import json
from pathlib import Path
import struct
import sys
import tempfile
import ctypes as C
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import live_lights
import light_controls
import run_report
from native_light_state import decode
from test_native_light_controls import packet as native_packet


class LiveLightTests(unittest.TestCase):
    def setup_packet(self):
        raw=native_packet();raw[4297]=1
        struct.pack_into('<3f',raw,204,1,0,0);struct.pack_into('<3f',raw,228,1,1,1);struct.pack_into('<f',raw,240,1.5)
        struct.pack_into('<3f',raw,268,0,0,1);struct.pack_into('<3f',raw,292,1,1,1);struct.pack_into('<f',raw,304,.25)
        row=decode(raw)
        # Deterministic defaults,not the sponsor's actively edited tuning file.
        controls={r['id']:r for r in light_controls.validate(dict(schema_version=1,backend='remix_sdk_0_6_4',
            lights=[dict(id='native_directional_0'),dict(id='native_directional_1')]),live_lights.REGISTRY)}
        return row,controls

    def test_native_ratio_packet_and_checksum(self):
        row,controls=self.setup_packet()
        result=live_lights.packet(row,{'owner_epoch':2},row['session_words'],controls,1,.5,1,123,1)
        self.assertEqual(len(result),200)
        self.assertEqual(struct.unpack_from('<3f',result,92),(.75,.75,.75))
        self.assertEqual(struct.unpack_from('<3f',result,156),(.125,.125,.125))
        self.assertEqual(struct.unpack_from('<Q',result,192)[0],live_lights.fnv(result[:192]))
        half=live_lights.packet(row,{'owner_epoch':2},row['session_words'],controls,1,.25,2,123,2)
        self.assertEqual(struct.unpack_from('<f',half,92)[0],.375)
        self.assertEqual(struct.unpack_from('<Q',half,48)[0],123) # config edit does not freshen native observation

    def test_unqualified_state_rejected(self):
        row,controls=self.setup_packet();row['slots'][0]['native_type']=5
        with self.assertRaises(ValueError):live_lights.packet(row,{'owner_epoch':2},row['session_words'],controls,1,.5,1,123,1)

    def test_shadow_softness_is_independent_of_strength(self):
        row,controls=self.setup_packet()
        controls['native_directional_0']['angular_diameter_degrees']=2
        result=live_lights.packet(row,{'owner_epoch':2},row['session_words'],controls,1,.5,1,123,1)
        self.assertEqual(struct.unpack_from('<f',result,104)[0],2)
        self.assertEqual(struct.unpack_from('<3f',result,92),(.75,.75,.75))

    def test_reload_keeps_last_valid_after_partial_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);config=folder/'config.toml';config.write_bytes(live_lights.DEFAULT.read_bytes())
            receiver=SimpleNamespace(name='Local\\SFCBridge_'+'1'*32,selected=None)
            relay=live_lights.Relay(folder,receiver,config)
            with mock.patch('builtins.print'):
                relay.reload();before=relay.controls;config.write_text('broken = [');relay.reload()
            self.assertIs(relay.controls,before);self.assertEqual(relay.accepted,1);self.assertEqual(relay.rejected,1)

    def test_scale_invalid_even_without_relay(self):
        with self.assertRaises(ValueError):light_controls.validate(dict(schema_version=1,backend='remix_sdk_0_6_4',master_multiplier=float('nan')),live_lights.REGISTRY)

    def test_tuning_repeated_snapshot_does_not_refresh_age(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);(folder/'gate').mkdir()
            row,controls=self.setup_packet();raw=native_packet();raw[4297]=1
            decoded=decode(raw);owner=decoded['owner_epoch']
            (folder/f'gate/native-light-latest-{owner}.bin').write_bytes(raw)
            current=[0]*96;current[1]=owner;current[3]=decoded['elapsed_ms'];current[4]=1
            channel=SimpleNamespace(sample_owner=lambda i:current if i==0 else None)
            name='Local\\SFCBridge_'+''.join(f'{x:08x}' for x in decoded['session_words'])
            receiver=SimpleNamespace(name=name,selected={'owner_epoch':owner},channel=channel)
            relay=live_lights.Relay(folder,receiver,tuning=True)
            relay.last_native=decoded;relay.observed=123;relay.last_config=10
            # No Windows timer call is needed for a repeated snapshot.
            with mock.patch('live_lights.time.monotonic',return_value=10):relay.poll()
            self.assertEqual(relay.observed,123)

    def test_busy_output_replace_drops_without_waiting(self):
        row,controls=self.setup_packet()
        with tempfile.TemporaryDirectory() as directory:
            name='Local\\SFCBridge_'+''.join(f'{x:08x}' for x in row['session_words'])
            receiver=SimpleNamespace(name=name,selected={'owner_epoch':2})
            relay=live_lights.Relay(directory,receiver,tuning=True)
            relay.last_config=10;relay.controls=controls;relay.last_native=row;relay.observed=123
            with mock.patch('live_lights.time.monotonic',return_value=10),mock.patch.object(Path,'replace',side_effect=PermissionError('busy')):
                relay.poll()
            self.assertEqual(relay.publish_busy,1)
            self.assertEqual(relay.observed,123)

    def test_busy_source_does_not_abort_or_refresh_native_age(self):
        row,controls=self.setup_packet()
        with tempfile.TemporaryDirectory() as directory:
            name='Local\\SFCBridge_'+''.join(f'{x:08x}' for x in row['session_words'])
            receiver=SimpleNamespace(name=name,selected={'owner_epoch':2})
            relay=live_lights.Relay(directory,receiver,tuning=True)
            relay.last_config=10;relay.controls=controls;relay.last_native=row;relay.observed=123
            with mock.patch('live_lights.time.monotonic',return_value=10),mock.patch('live_lights.read_latest',side_effect=PermissionError('busy')),mock.patch('builtins.print'):
                relay.poll()
            self.assertEqual(relay.read_busy,1);self.assertTrue(relay.read_pending)
            self.assertEqual(relay.observed,123)
            output=(Path(directory)/'live-lights.bin').read_bytes()
            self.assertEqual(struct.unpack_from('<Q',output,48)[0],123)

    @unittest.skipUnless(sys.platform=='win32','Windows share policy')
    def test_actual_exclusive_lock_recovers_without_waiting(self):
        from ctypes import wintypes as W
        kernel=C.WinDLL('kernel32',use_last_error=True)
        kernel.CreateFileW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,C.c_void_p,W.DWORD,W.DWORD,W.HANDLE]
        kernel.CreateFileW.restype=W.HANDLE;kernel.CloseHandle.argtypes=[W.HANDLE]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'native-light-latest-2.bin';raw=bytes(native_packet());path.write_bytes(raw)
            receiver=SimpleNamespace(name='Local\\SFCBridge_'+'1'*32,selected=None)
            relay=live_lights.Relay(directory,receiver,tuning=True);relay.observed=123
            handle=kernel.CreateFileW(str(path),0x80000000,0,None,3,0x80,None)
            self.assertNotEqual(handle,C.c_void_p(-1).value)
            try:
                with mock.patch('builtins.print'):self.assertEqual(list(relay.records(path)),[])
                self.assertEqual(relay.read_busy,1)
            finally:kernel.CloseHandle(handle)
            with mock.patch('builtins.print'):self.assertEqual(list(relay.records(path)),[raw])
            self.assertEqual(relay.read_recoveries,1);self.assertFalse(relay.read_pending)
            self.assertEqual(relay.observed,123)

    @unittest.skipUnless(sys.platform=='win32','Windows share policy')
    def test_windows_snapshot_size_and_handle_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'snapshot-é.bin';path.write_bytes(b'bad')
            with self.assertRaises(ValueError):live_lights.read_latest(path)
            path.write_bytes(bytes(native_packet()))
            self.assertEqual(live_lights.read_latest(path),bytes(native_packet()))
            path.unlink() # reader must not retain a handle after either path


class RunReportTests(unittest.TestCase):
    def tearDown(self):run_report.current_folder=None
    def test_exception_leaves_report_and_bad_json_is_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'result.json'
            run_report.save(directory,dict(result='IN_PROGRESS'))
            run_report.failure(ValueError('test failure'))
            self.assertEqual(json.loads(path.read_text())['result'],'PARTIAL')
            run_report.save(directory,dict(result='GOOD',bad=float('nan')))
            self.assertEqual(json.loads(path.read_text())['result'],'PARTIAL')


if __name__=='__main__':unittest.main()

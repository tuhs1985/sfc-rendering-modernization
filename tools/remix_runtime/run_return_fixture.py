"""Bounded offline same-proxy image-compositor validation. NEVER launches SFC."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess as sp
import time
from return_channel import Channel,valid_name
import depth_search_channel
import broad_capture

ROOT=Path(__file__).resolve().parents[2]
DLL=ROOT/'artifacts/remix-runtime/deps/remix-1.5.2/.trex/d3d9.dll'
BIN=ROOT/'artifacts/remix-runtime/return-bin'
TEST=Path(r'C:\Project\SFC-Remix-Return-Test')
ENV={'DXVK_LOG_LEVEL':'error','DXVK_GRAPHICS_PRESET_TYPE':'4','RTX_INTEGRATE_INDIRECT_MODE':'0','DXVK_UPSCALER_TYPE':'0','DXVK_RAY_RECONSTRUCTION':'False','RTX_DLSS_PRESET':'0','RTX_ENABLE_ASYNC_COMPILATION':'False'}
def digest(p):
    with open(p,'rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest().upper()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--graceful',action='store_true',help='Signal stop instead of intentional renderer crash')
    inspect=parser.add_mutually_exclusive_group()
    inspect.add_argument('--inspect-visibility',action='store_true',help='Exercise read-only late depth-binding observation')
    inspect.add_argument('--inspect-early-depth',action='store_true',help='Exercise supported pre-effects Present observation')
    inspect.add_argument('--search-depth',action='store_true',help='Expanded six-phase engine/presentation search')
    inspect.add_argument('--broad-capture',action='store_true',help='Full-support public event capture,10seconds,2GB ceiling')
    inspect.add_argument('--depth-snapshots',action='store_true',help='Three read-only 8sample depth snapshots, no SFC')
    parser.add_argument('--slow-end-scene',action='store_true',help='Offline only: detach while simulated original COM call sleeps')
    parser.add_argument('--with-depth',action='store_true',help='Bind known synthetic D24S8 descriptor, not actual scene depth')
    parser.add_argument('--observation-only',action='store_true',help='No Remix runtime/image; control channel and depth observations only')
    args=parser.parse_args()
    inspect_requested=args.inspect_visibility or args.inspect_early_depth
    if args.with_depth and not (args.inspect_early_depth or args.search_depth or args.broad_capture or args.depth_snapshots):parser.error('--with-depth requires --inspect-early-depth or --search-depth or --broad-capture or --depth-snapshots')
    if args.observation_only and (not (args.inspect_early_depth or args.search_depth or args.broad_capture or args.depth_snapshots) or not args.graceful):parser.error('--observation-only requires --inspect-early-depth or --search-depth or --broad-capture or --depth-snapshots and --graceful')
    if args.depth_snapshots and not (args.observation_only and args.graceful):parser.error('--depth-snapshots requires --observation-only and --graceful')
    if args.broad_capture and not (args.observation_only and args.graceful):parser.error('--broad-capture requires --observation-only and --graceful')
    if args.search_depth and not args.observation_only:parser.error('--search-depth requires --observation-only')
    if args.slow_end_scene and not args.search_depth:parser.error('--slow-end-scene requires --search-depth')
    if digest(DLL)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise RuntimeError('Pinned Remix changed')
    if digest(TEST/'dxgi.dll')!='E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7':raise RuntimeError('Copied proxy changed')
    work=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-return-fixture');work.mkdir()
    for source,name in [(broad_capture.qualified_full() if args.broad_capture or args.depth_snapshots else TEST/'dxgi.dll','dxgi.dll'),(BIN/'d3d11_return_fixture.exe','d3d11_return_fixture.exe'),(BIN/'SFCRemixReturn.dll','SFCRemixReturn.dll')]:shutil.copyfile(source,work/name)
    # No existing game config changed. Disable fixture menu/input capture only.
    (work/'ReShade.ini').write_text('[GENERAL]\nEffectSearchPaths=./no-effects\nPresetPath=./fixture.ini\n[OVERLAY]\nTutorialProgress=4\nShowFPS=0\nShowFrameTime=0\n[INPUT]\nInputProcessing=0\n')
    env={**os.environ,**ENV,'DXVK_LOG_PATH':str(work)}
    host=fixture=channel=None;streams=[];start=time.monotonic();error=None;history=[]
    try:
        def output(name):
            f=open(work/name,'wb');streams.append(f);return f
        host=sp.Popen([str(BIN/'return_host.exe'),'--observe-only' if args.observation_only else str(DLL)],cwd=work,env=env,stdout=output('host.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        session=None
        while time.monotonic()-start<60:
            if host.poll() is not None:raise RuntimeError('Runtime host exited before session ready')
            text=(work/'host.log').read_text(errors='replace')
            session=next((line[8:] for line in text.splitlines() if line.startswith('SESSION ')),None)
            if session:break
            time.sleep(.1)
        if not session or not valid_name(session):raise RuntimeError('Runtime session startup failed')
        channel=Channel(session)
        env.update(SFC_REMIX_RETURN_SESSION=session,SFC_REMIX_EXPECTED_IMAGE=str(work/'d3d11_return_fixture.exe'),SFC_REMIX_PRELOAD_REQUIRED='1')
        env.pop('SFC_REMIX_BROAD_OUTPUT',None)
        env.pop('SFC_REMIX_DEPTH_OUTPUT',None)
        if args.depth_snapshots:env['SFC_REMIX_DEPTH_OUTPUT']=str(work)
        if args.broad_capture:env['SFC_REMIX_BROAD_OUTPUT']=str(work/'broad.bin')
        env['SFC_REMIX_INSPECT_VISIBILITY']='3' if args.search_depth else ('2' if args.inspect_early_depth else ('1' if args.inspect_visibility else '0'))
        env.pop('SFC_RETURN_FIXTURE_DEPTH',None)
        env.pop('SFC_RETURN_OBSERVATION_ONLY',None)
        env.pop('SFC_RETURN_EXPANDED_SEARCH',None)
        env.pop('SFC_RETURN_SLOW_END',None)
        if args.with_depth:env['SFC_RETURN_FIXTURE_DEPTH']='1'
        if args.observation_only:env['SFC_RETURN_OBSERVATION_ONLY']='1'
        if args.search_depth:env['SFC_RETURN_EXPANDED_SEARCH']='1'
        if args.slow_end_scene:env['SFC_RETURN_SLOW_END']='1'
        fixture=sp.Popen([str(BIN/'return_launcher.exe'),'--fixture',str(work/'d3d11_return_fixture.exe'),str(work/'SFCRemixReturn.dll'),digest(work/'d3d11_return_fixture.exe'),digest(work/'SFCRemixReturn.dll')],cwd=work,env=env,stdout=output('fixture.log'),stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        disabled_at=None;reenabled=False;killed=False;last=0
        while fixture.poll() is None:
            elapsed=time.monotonic()-start
            size=sum(p.stat().st_size for p in work.rglob('*') if p.is_file())
            if elapsed>100 or size>(broad_capture.HARD+32*1024*1024 if args.broad_capture else (96*1024*1024 if args.depth_snapshots else 32*1024*1024)):raise RuntimeError('Fixture time/output cap')
            text=(work/'fixture.log').read_text(errors='replace')
            state=channel.snapshot()
            if args.search_depth and elapsed>8:channel.set('stop',1)
            if args.slow_end_scene and state['ready'] and depth_search_channel.snapshot(channel.address)['reserved']==1:channel.set('stop',1)
            if state['ready'] and not disabled_at:
                channel.set('armed',1);channel.set('enabled',int(not args.observation_only))
            if 'SAMPLE enabled ' in text and disabled_at is None:
                channel.set('enabled',0);disabled_at=time.monotonic()
            if disabled_at and 'SAMPLE disabled ' in text and time.monotonic()-disabled_at>1 and not reenabled:
                channel.set('enabled',1);reenabled=True
            if 'SAMPLE recreated ' in text and not killed and (not inspect_requested or state['visibilitySamples']>=8):
                if args.graceful:
                    channel.set('stop',1)
                else:
                    host.kill();host.wait(timeout=5) # Explicit owned-renderer crash test.
                killed=True
            if elapsed-last>.25:history.append({'seconds':elapsed,**state});last=elapsed
            time.sleep(.05)
        fixture.wait(timeout=5)
        if fixture.returncode:raise RuntimeError('Native fixture failed: '+str(fixture.returncode))
        text=(work/'fixture.log').read_text(errors='replace')
        if args.broad_capture:
            broad=broad_capture.save_analysis(work/'broad.bin')
            if 'BROAD_END ' not in text or 'state_errors=0' not in text or broad['header']['error']:raise RuntimeError('Broad fixture failed')
            if not broad['counts'].get('resource') or not broad['counts'].get('view') or not broad['counts'].get('targets'):raise RuntimeError('Full-support events not delivered')
            if args.with_depth and not broad['depth_candidates']:raise RuntimeError('Known transient depth missing')
            if not args.with_depth and broad['depth_candidates']:raise RuntimeError('Unexpected depth in negative fixture')
            channel.set('stop',1)
        elif args.search_depth:
            search=depth_search_channel.snapshot(channel.address)
            if 'SEARCH_END ' not in text or 'state_errors=0 restored=15 seen=63' not in text:raise RuntimeError('Expanded fixture restoration/state evidence incomplete')
            if search['error'] or search['status']!=4 or search['restoredMask']!=15:raise RuntimeError('Expanded search cleanup not confirmed')
            if args.with_depth and not search['resourceCount']:raise RuntimeError('Known depth missing from expanded search')
            if not args.with_depth and search['resourceCount']:raise RuntimeError('Unexpected depth in negative fixture')
            channel.set('stop',1)
        elif args.depth_snapshots:
            if 'DEPTH_SNAPSHOT_END ' not in text or 'state_errors=0' not in text:raise RuntimeError('Depth snapshot fixture state evidence incomplete')
            channel.set('stop',1)
            from depth_snapshot_analysis import analyze_run
            report=analyze_run(work,images=True)
            if bool(report['complete'])!=args.with_depth:raise RuntimeError('Depth snapshot positive/negative evidence failed')
            if not args.with_depth and report['snapshots']:raise RuntimeError('Unexpected depth without candidate')
        elif args.observation_only:
            if 'OBSERVATION_END ' not in text or 'state_errors=0 samples=8 resized=1 recreated=1' not in text:raise RuntimeError('Observation fixture state evidence incomplete')
            channel.set('stop',1)
        elif 'phases=11111' not in text or 'state_errors=0' not in text or not killed:raise RuntimeError('Fixture phase/state evidence incomplete')
        if not channel.state.startupRestored or not channel.state.startupVerified:raise RuntimeError('Startup preload/path evidence incomplete')
        if inspect_requested:
            s=channel.state
            if s.visibilitySamples!=8 or s.depthPresentSamples!=(8 if args.with_depth else 0) or s.visibilityScope!=(2 if args.inspect_early_depth else 1):raise RuntimeError('Unexpected fixture visibility count/scope')
            if args.with_depth:
                # Existing proxy may expose a shader-readable typeless resource
                # behind a typed D24S8 view. Compare exact independently logged
                # native descriptor, not the originally requested resource format.
                known=re.findall(r'KNOWN_FIXTURE_DEPTH width=(\d+) height=(\d+) resource_format=(\d+) view_format=(\d+) flags=(\d+)',text)
                observed=(s.depthWidth,s.depthHeight,s.depthFormat,s.depthViewFormat,s.depthBindFlags)
                if not known or observed!=tuple(map(int,known[-1])) or s.depthViewFormat!=45 or not(s.depthBindFlags&64) or s.depthMultisamples!=1:raise RuntimeError('Known fixture depth descriptor mismatch')
        if args.graceful:
            host.wait(timeout=8)
            if host.returncode:raise RuntimeError('Graceful host shutdown failed')
    except Exception as exc:error=str(exc)
    finally:
        if channel:
            channel.set('enabled',0);channel.set('stop',1)
        for p in (fixture,host):
            if p and p.poll() is None:
                p.terminate()
                try:p.wait(timeout=5)
                except sp.TimeoutExpired:p.kill();p.wait(timeout=5)
        final=channel.snapshot() if channel else None
        search=None
        if channel and args.search_depth:
            try:search=depth_search_channel.snapshot(channel.address)
            except ValueError:pass
        if channel:channel.close()
        for f in streams:f.close()
        (work/'result.json').write_text(json.dumps({'probe':'REMIX-RETURN-001-FIXTURE','expanded_search':search,'observation_only':args.observation_only,'graceful':args.graceful,'inspect_early_depth':args.inspect_early_depth,'inspect_visibility':args.inspect_visibility,'known_fixture_depth':args.with_depth,'error':error,'seconds':time.monotonic()-start,'host_exit':host.returncode if host else None,'fixture_exit':fixture.returncode if fixture else None,'history':history,'final':final,'runtime_environment':ENV,'source_files':{p.name:digest(p) for p in (BIN/'return_host.exe',BIN/'SFCRemixReturn.dll',BIN/'d3d11_return_fixture.exe',BIN/'return_launcher.exe')}},indent=2))
    print(f'Evidence: {work}')
    if (work/'fixture.log').exists():print((work/'fixture.log').read_text(errors='replace'))
    if error:raise RuntimeError(error)
if __name__=='__main__':main()

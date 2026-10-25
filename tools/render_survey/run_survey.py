"""Prepared metadata-only survey; no SFC unless --execute explicitly given."""
import argparse,json,os,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from survey_capture import digest,reserve_capture_budget,FULL,FULL_SHA

def locks():
    files=[p for p in (ROOT/'tools/render_survey').rglob('*') if p.is_file() and p.suffix in ('.py','.cpp','.h','.ps1')]
    files += [ROOT/'artifacts/render-survey/bin'/name for name in ('SFCRemixReturn.dll','trace_tests.exe','native_tests.exe','d3d11_return_fixture.exe','survey_fixture_launcher.exe')]+[FULL]
    files += [ROOT/'artifacts/remix-runtime/deps/reshade/include'/name for name in ('reshade.hpp','reshade_events.hpp','reshade_api_pipeline.hpp')]
    files += [ROOT/'artifacts/remix-runtime/return-bin'/name for name in ('return_launcher.exe','return_host.exe','d3d11_return_fixture.exe')]
    files += [ROOT/'artifacts/m1/bin'/name for name in ('m1_gate.dll','m1_controller.exe')]
    files += [ROOT/'tools/remix_runtime'/name for name in ('return_wire.h','return_channel.py','broad_capture.py','recover_broad_session.py')]
    detours=ROOT/'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833'
    files += [detours/'include/detours.h',detours/'lib.X86/detours.lib']
    return {p.relative_to(ROOT).as_posix():digest(p) for p in files}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',action='store_true');p.add_argument('--fixture-seconds',type=int,choices=(10,90),default=10);p.add_argument('--execute',action='store_true');p.add_argument('--record-build',action='store_true');a=p.parse_args()
    receipt=ROOT/'artifacts/render-survey/build.json'
    if a.record_build:receipt.write_text(json.dumps(locks(),indent=2));print('Survey build lock recorded;not GPU qualification');return
    if json.loads(receipt.read_text())!=locks():raise ValueError('Survey source/build lock stale')
    if digest(FULL)!=FULL_SHA:raise ValueError('Pinned full-support proxy changed')
    reserve_capture_budget()
    os.environ['SFC_SURVEY_DURATION_MS']=str(a.fixture_seconds*1000) if a.fixture else '90000'
    frozen=locks();original_copy=shutil.copyfile
    def copy(source,destination,*args,**kwargs):
        result=original_copy(source,destination,*args,**kwargs)
        if Path(source).resolve()==ROOT/'artifacts/render-survey/bin/SFCRemixReturn.dll':
            target=Path(destination).resolve()
            if target.parent.parent==ROOT/'artifacts/remix-runtime/runs':
                (target.parent/'survey-control.json').write_text(json.dumps(dict(probe='RENDER-FAMILY-SURVEY-001',wire_version=2,locks=frozen,duration_ms=int(os.environ['SFC_SURVEY_DURATION_MS']),geometry_payload=False,image_payload=False,native_lights=True,native_effect_list_census=True,total_run_cap_bytes=2*1024**3,origin_stride=8,origin_budget_per_present=64),indent=2))
        return result
    shutil.copyfile=copy
    if a.fixture:
        import fixture_driver as driver
        sys.argv=[str(Path(driver.__file__)),'--broad-capture','--observation-only','--graceful','--with-depth']
    else:
        if a.execute:
            q=json.loads((ROOT/'artifacts/render-survey/qualification.json').read_text())
            if q['locks']!=locks() or q['result']!='OFFLINE_SURVEY_EVENTS_STATE_CLEANUP_PASS':raise ValueError('Actual-proxy survey qualification missing/stale')
        import game_driver as driver
        sys.argv=[str(Path(driver.__file__)),'--broad-capture','--observation-only']+(['--execute'] if a.execute else [])
    driver.main()

if __name__=='__main__':main()

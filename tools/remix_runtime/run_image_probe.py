"""Bounded actual-Remix image controls test. No SFC launch or injection."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess as sp
import time
from run_return_fixture import ROOT,DLL,ENV,digest

def analyze(text):
    cases={m[1]:[float(m[i]) for i in (2,3,4)] for m in re.finditer(r'IMAGE_CASE (\w+) rgb=([\d.]+),([\d.]+),([\d.]+) samples=16',text)}
    names={'startup','local_auto','local_manual','local_exposure','local_brightness','local_saturation','local_contrast','local_gamma','global_manual','global_saturation','global_contrast','global_exposure','global_brightness','global_auto','restored','local_boost','global_boost'}
    if set(cases)!=names or 'IMAGE_GPU_ORACLE_PASS' not in text:raise ValueError('Image cases/GPU oracle incomplete')
    def avg(n):return sum(cases[n])/3
    for mode in ('local','global'):
        for control in ('exposure','brightness'):
            if avg(mode+'_'+control)>=avg(mode+'_manual')-2:raise ValueError(mode+' '+control+' had no measured dimming')
        if max(cases[mode+'_saturation'])-min(cases[mode+'_saturation'])>1:raise ValueError(mode+' saturation did not produce grey')
        if max(cases[mode+'_contrast'])-min(cases[mode+'_contrast'])>1:raise ValueError(mode+' zero contrast not neutral-grey')
        if abs(avg(mode+'_auto')-avg(mode+'_manual'))<2:raise ValueError(mode+' auto exposure effect not distinguished')
        if max(cases[mode+'_boost'])-min(cases[mode+'_boost'])<=max(cases[mode+'_manual'])-min(cases[mode+'_manual'])+2:raise ValueError(mode+' boosted grade had no measured effect')
    if avg('local_gamma')<=avg('local_manual')+2:raise ValueError('Gamma did not brighten midtones')
    if max(abs(a-b) for a,b in zip(cases['startup'],cases['local_auto']))>4:raise ValueError('Enabled-neutral drift from startup')
    if max(abs(a-b) for a,b in zip(cases['local_auto'],cases['restored']))>4:raise ValueError('Restored baseline drift')
    return cases

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--quality',action='store_true');p.add_argument('--native-emission-bloom',action='store_true');p.add_argument('--candidate',action='store_true');a=p.parse_args()
    if a.native_emission_bloom and a.quality:p.error('Separate native bloom and quality controls')
    if a.candidate and not a.native_emission_bloom:p.error('Candidate probe restricted to native emission/bloom control')
    if not a.execute:print('Offline only. --execute starts owned GPU probe, never SFC.');return
    if digest(DLL)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise ValueError('Pinned runtime mismatch')
    work=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-image-controls');work.mkdir()
    exe=ROOT/'artifacts/remix-runtime/live-return-bin/image_controls_probe.exe'
    runtime=DLL
    if a.candidate:
        from runtime_candidate import verify
        runtime=verify()['runtime'];exe=ROOT/'artifacts/remix-runtime/candidate-1.6.1-bin/native_emission_bloom_probe.exe'
    sources={n:digest(Path(__file__).parent/n) for n in ('image_controls_probe.cpp','remix_image_adjust.h','remix_image_controls.h','remix_quality_controls.h','image_controls.py','quality_controls.py','run_image_probe.py')}
    result=dict(probe='REMIX-IMAGE-CONTROLS-001',source_hashes=sources,executable_sha256=digest(exe),runtime_sha256=digest(DLL),sfc_launched=False,limits=dict(seconds=75,warning_bytes=16*1024*1024,hard_bytes=32*1024*1024),environment=ENV)
    started=time.monotonic();error=None;child=None
    env={**os.environ,**ENV,'DXVK_LOG_PATH':str(work)};env.pop('SFC_QUALITY_PROBE',None)
    env.pop('SFC_NATIVE_EMISSION_BLOOM_PROBE',None)
    if a.native_emission_bloom:env['SFC_NATIVE_EMISSION_BLOOM_PROBE']='1'
    result.update(runtime_sha256=digest(runtime),candidate=a.candidate,native_emission_bloom=a.native_emission_bloom)
    if a.native_emission_bloom:
        # Match the existing process-local NRC-off policy explicitly. Old env
        # aliases alone do not establish the candidate's actual config baseline.
        config=work/'rtx.conf'
        config.write_text('rtx.integrateIndirectMode = 0\nrtx.enableRayReconstruction = False\nrtx.upscalerType = 0\n')
        env['DXVK_CONFIG_FILE']=str(config)
        from PIL import Image
        Image.new('RGBA',(128,128),(220,40,8,255)).save(work/'emission-probe.dds')
        result['native_probe_config']=config.read_text()
    if a.quality:
        # Synthetic checker with a complete original-resolution mip chain.
        import struct
        from PIL import Image
        image=Image.new('RGBA',(128,128));image.putdata([(255,210,100,255) if ((x//8)^(y//8))&1 else (8,20,60,255) for y in range(128) for x in range(128)])
        raw=bytearray(b'DDS '+struct.pack('<7I11I8I5I',124,0x2100f,128,128,512,0,8,*([0]*11),32,0x41,0,32,0xff,0xff00,0xff0000,0xff000000,0x401008,0,0,0,0))
        for level in range(8):raw.extend(image.resize((128>>level,128>>level),Image.Resampling.BOX).tobytes())
        (work/'quality-checker.dds').write_bytes(raw);env['SFC_QUALITY_PROBE']='1'
        result['synthetic_texture_sha256']=digest(work/'quality-checker.dds');result['quality_mode']=True
    try:
        with (work/'probe.log').open('wb') as f:
            child=sp.Popen([str(exe),str(runtime)],cwd=work,env=env,stdout=f,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
            warned=False
            while child.poll() is None:
                size=sum(x.stat().st_size for x in work.rglob('*') if x.is_file())
                if size>16*1024*1024 and not warned:print('Image probe16MiB warning',flush=True);warned=True
                if size>32*1024*1024 or time.monotonic()-started>75:raise RuntimeError('Image probe time/output cap')
                time.sleep(.25)
        result['exit_code']=child.returncode
        if child.returncode:raise RuntimeError('Image GPU probe failed')
        text=(work/'probe.log').read_text()
        if a.native_emission_bloom:
            rgb={m[1]:[float(m[i]) for i in (2,3,4)] for m in re.finditer(r'IMAGE_CASE (\w+) rgb=([\d.]+),([\d.]+),([\d.]+) samples=16',text)}
            halos={m[1]:float(m[2]) for m in re.finditer(r'NATIVE_EMISSION_BLOOM_CASE (\w+) halo=([\d.eE+-]+)',text)}
            if len(rgb)!=11 or set(rgb)!=set(halos) or 'IMAGE_GPU_ORACLE_PASS' not in text:raise ValueError('Native emission/bloom cases incomplete')
            result['global_emission_visible_effect_measured']=sum(rgb['emission_four'])>sum(rgb['emission_one'])+3>sum(rgb['emission_zero'])+6
            # Not a user control unless independently demonstrated effective.
            if halos['bloom_on']<=halos['bloom_off']+.01 or halos['bloom_strong']<=halos['bloom_on']+.01:raise ValueError('Bloom enable/intensity did not change halo pixels')
            if abs(halos['bloom_zero']-halos['bloom_off'])>.2:raise ValueError('Zero bloom intensity did not restore no-halo image')
            if halos['bloom_threshold_high']>=halos['bloom_strong']-.01:raise ValueError('Bloom threshold had no measured suppression')
            if abs(halos['bloom_wide']-halos['bloom_narrow'])<.01:raise ValueError('Bloom steps had no measured effect')
            result.update(result='OFFLINE_NATIVE_BLOOM_PASS',cases=rgb,halo=halos)
        elif a.quality:
            cases={m[1]:dict(spatial=float(m[2]),temporal=float(m[3])) for m in re.finditer(r'QUALITY_CASE (\w+) spatial=([\d.eE+-]+) temporal=([\d.eE+-]+)',text)}
            if set(cases)!={'aniso16','trilinear','aniso1','mip_sharp','mip_soft','temporal','denoise_off','denoise_on','restored','point_reference'}:raise ValueError('Quality pixel cases missing')
            result['cases']=cases;result['result']='OFFLINE_QUALITY_OPTIONS_EXERCISED'
            # Small changes in noisy output are not proof of texture sharpness.
            result['filtering_measured']=abs(cases['aniso16']['spatial']-cases['aniso1']['spatial'])>max(1,cases['aniso16']['spatial']*.01)
            result['mip_bias_measured']=abs(cases['mip_sharp']['spatial']-cases['mip_soft']['spatial'])>max(1,cases['aniso16']['spatial']*.01)
            result['temporal_aa_measured']=abs(cases['temporal']['temporal']-cases['aniso16']['temporal'])>.1 or abs(cases['temporal']['spatial']-cases['aniso16']['spatial'])>1
            result['denoising_measured']=abs(cases['denoise_off']['temporal']-cases['denoise_on']['temporal'])>.1
            result['linear_sampler_measured']=abs(cases['point_reference']['spatial']-cases['restored']['spatial'])>max(1,cases['restored']['spatial']*.01)
        else:result['cases']=analyze(text);result['result']='OFFLINE_IMAGE_CONTROLS_PASS'
    except Exception as exc:error=str(exc);result.update(result='PARTIAL',error=error)
    finally:
        if child and child.poll() is None:child.terminate();child.wait(timeout=5)
        result['seconds']=time.monotonic()-started
        result['output_bytes']=sum(x.stat().st_size for x in work.rglob('*') if x.is_file())
        (work/'result.json').write_text(json.dumps(result,indent=2))
    print('Evidence: '+str(work))
    if error:raise RuntimeError(error)

if __name__=='__main__':main()

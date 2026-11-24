"""Inspect actual Slate window pixels, independently of target RGB readback."""
import argparse
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from PIL import Image
from qualify_stream import runtime_exe


def run(exe,scene,output,width=1280,height=800):
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    args=[str(runtime_exe(exe)),'-windowed',f'-ResX={width}',f'-ResY={height}','-nosound','-nolog',
        f'-SFCScene={scene.resolve()}','-SFCDiagnostics',f'-SFCOutput={output}','-SFCExit','-SFCInspectionCheck']
    result=subprocess.run(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=90)
    if result.returncode or (output/'rejected.txt').exists():raise ValueError('Packaged inspection failed')
    window=output/'inspection.bmp'
    if not window.exists():raise ValueError('Missing actual inspection-widget pixels')
    source=Image.open(output/'ship.bmp').convert('RGB');actual=np.asarray(Image.open(window).convert('RGB'))
    h,w=actual.shape[:2];scale=min(w/source.width,h/source.height)
    sw,sh=round(source.width*scale),round(source.height*scale);x,y=(w-sw)//2,(h-sh)//2
    expected=np.zeros_like(actual);expected[y:y+sh,x:x+sw]=np.asarray(source.resize((sw,sh),Image.Resampling.BILINEAR))
    wanted=expected.max(axis=2)>25;seen=actual.max(axis=2)>25
    # Exit button is deliberately separate UI; exclude only its top strip.
    wanted[:64]=False;seen[:64]=False
    intersection=np.count_nonzero(wanted&seen);union=np.count_nonzero(wanted|seen)
    iou=intersection/union if union else 0
    if wanted.sum()<100 or iou<.88:raise ValueError(f'Inspection lost textured surface or aspect-fit placement: IoU={iou:.4f}')
    report=dict(actual_widget_pixels=True,window=[w,h],target=[source.width,source.height],coverage_iou=iou,opaque_surface_visible=True)
    (output/'qualified.json').write_text(json.dumps(report,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('exe','scene','output'):p.add_argument(key,type=Path)
    p.add_argument('--width',type=int,default=1280);p.add_argument('--height',type=int,default=800);a=p.parse_args()
    print(json.dumps(run(a.exe,a.scene,a.output,a.width,a.height),indent=2))

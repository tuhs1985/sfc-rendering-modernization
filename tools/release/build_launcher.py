"""Developer-only build of the native application entry point."""
import os
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]
if __name__=='__main__':
    vc=Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Auxiliary/Build/vcvars64.bat')
    output=ROOT/'artifacts/alpha/launcher-bin';output.mkdir(parents=True,exist_ok=True)
    command=f'"{vc}" && cl /nologo /std:c++20 /EHsc /W4 /WX /O2 /MT "{ROOT / "tools/release/launcher.cpp"}" /Fe:launcher.exe /Fo:launcher.obj /link /Brepro shell32.lib advapi32.lib'
    # cmd's /s quoting differs from the CRT argument grammar used by list2cmdline.
    subprocess.run(f'"{os.environ["COMSPEC"]}" /d /s /c "{command}"',cwd=output,check=True)

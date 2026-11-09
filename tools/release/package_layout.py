"""Build-only exclusions for the x64 alpha. Never trim the upstream source cache."""
from pathlib import Path,PurePosixPath
import shutil

PYTHON_BUILD_DIRS=frozenset({'include','libs','Scripts'})
ARM_RUNTIME='runtime/remix-runtime/deps/candidate-1.6.1/runtime/d3d9_a64ec.dll'


def excluded(name):
    name=PurePosixPath(name).as_posix().casefold()
    return (name==ARM_RUNTIME.casefold() or
            any(name==('python/'+part).casefold() or name.startswith(('python/'+part+'/').casefold())
                for part in PYTHON_BUILD_DIRS))


def copy_python(source,target):
    source=Path(source).resolve()
    def ignore(folder,names):
        skipped=set(shutil.ignore_patterns('__pycache__','*.pyc')(folder,names))
        if Path(folder).resolve()==source:skipped.update(PYTHON_BUILD_DIRS.intersection(names))
        return skipped
    shutil.copytree(source,target,ignore=ignore)


def copy_remix(source,target):
    source=Path(source).resolve()
    def ignore(folder,names):
        return {'d3d9_a64ec.dll'} if Path(folder).resolve()==source and 'd3d9_a64ec.dll' in names else set()
    shutil.copytree(source,target,dirs_exist_ok=True,ignore=ignore)

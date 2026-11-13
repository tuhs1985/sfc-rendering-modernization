"""Release-only ReShade writable base using its documented path override.

Keep effects/preset inputs in the tester's game copy; generated configuration,
logs, screenshots and shader cache belong to this session's application data.
No game configuration is edited by this helper.
"""
import configparser
from pathlib import Path


def prepare(context,work):
    if not context.release:raise ValueError('Portable ReShade requires release context')
    root=(Path(work)/'reshade').resolve()
    if not root.is_relative_to(context.data_root.resolve()):raise ValueError('ReShade output must stay under package data')
    profile=configparser.RawConfigParser(strict=True)
    profile.optionxform=str
    try:
        profile.read_string((context.game_root/'ReShade.ini').read_text(encoding='utf-8-sig'))
    except FileNotFoundError:
        pass  # ReShade can start with defaults in its private session directory.
    root.mkdir();(root/'cache').mkdir();(root/'screenshots').mkdir();(root/'addons').mkdir()
    for section in ('GENERAL','SCREENSHOT','ADDON'):
        if not profile.has_section(section):profile.add_section(section)
    # Paths were relative to the game directory before changing ReShade's base.
    for name in ('EffectSearchPaths','TextureSearchPaths','PresetPath','StartupPresetPath'):
        value=profile.get('GENERAL',name,fallback='')
        if value:
            paths=[]
            for item in value.split(','):
                path=Path(item.strip())
                path=(context.game_root/path).resolve()
                if not path.is_relative_to(context.game_root.resolve()):raise ValueError('ReShade input outside game copy: '+name)
                paths.append(str(path))
            profile.set('GENERAL',name,','.join(paths))
    profile.set('GENERAL','IntermediateCachePath',str(root/'cache'))
    profile.set('SCREENSHOT','SavePath',str(root/'screenshots'))
    profile.set('ADDON','AddonPath',str(root/'addons'))
    with (root/'ReShade.ini').open('x',encoding='utf-8') as out:profile.write(out,space_around_delimiters=False)
    return {'RESHADE_BASE_PATH_OVERRIDE':str(root)}

"""Serial, bounded offline UE qualification. Never launches or changes SFC."""
import argparse
import ctypes
from ctypes import wintypes
import importlib.util
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('ue_pixels', ROOT / 'tools/ue5_proof/verify.py')
pixels = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pixels)


def runtime_exe(exe):
    exe = exe.resolve()
    for name in ('SFCUEWrapper.exe', 'SFCUEWrapper-Win64-Shipping.exe'):
        direct = exe.parent / 'SFCUEWrapper/Binaries/Win64' / name
        if direct.is_file():
            return direct
    return exe


def run(exe, scene, output, *, frame=0, procedural=False, shared=False, expect_reject=False, world_restart=False, gpu_exchange=False, gpu_consumer=None, gpu_depth=False):
    exe, scene, output = exe.resolve(), scene.resolve(), output.resolve()
    # Use the actual runtime process: terminating a bootstrap on timeout leaves its child alive.
    exe = runtime_exe(exe)
    output.mkdir(parents=True, exist_ok=False)
    args = [str(exe), '-windowed', '-ResX=1920', '-ResY=1080', '-nosound',
            f'-SFCScene={scene}', f'-SFCOutput={output}', '-SFCDiagnostics', '-SFCExit',
            f'-SFCFrame={frame}']
    if procedural:
        args.append('-SFCProcedural')
    if shared:
        args.append('-SFCSharedOwner')
    if world_restart:
        args.append('-SFCWorldRestart')
    if gpu_exchange:
        args.append('-SFCGpuExchange')
    if gpu_depth:
        if not gpu_exchange or not gpu_consumer:
            raise ValueError('Depth qualification requires the external GPU consumer')
        args.append('-SFCGpuDepth')
    if gpu_consumer:
        if not gpu_exchange:
            raise ValueError('An external GPU consumer requires --gpu-exchange')
        args.append(f'-SFCGpuConsumer={gpu_consumer.resolve()}')
    start = time.perf_counter()
    with (output / 'process.log').open('w', encoding='utf-8') as log:
        result = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, timeout=120)
    elapsed = time.perf_counter() - start
    if expect_reject:
        if result.returncode not in (0, 2) or not (output / 'rejected.txt').is_file() or (output / 'result.json').exists():
            raise ValueError(f'Missing recoverable rejection: {output}, exit={result.returncode}')
        return dict(rejected=(output / 'rejected.txt').read_text(encoding='utf-8-sig'), process_seconds=elapsed)
    if result.returncode:
        raise ValueError(f'UE failed, exit={result.returncode}: {output}')
    if (output / 'rejected.txt').is_file():
        raise ValueError((output / 'rejected.txt').read_text(encoding='utf-8-sig'))
    if 'Ensure condition failed:' in (output / 'process.log').read_text(encoding='utf-8', errors='replace'):
        raise ValueError(f'UE ensure in standalone fixture: {output}')
    report = json.loads((output / 'result.json').read_text(encoding='utf-8-sig'))
    if gpu_exchange:
        from PIL import Image
        with Image.open(output / 'ship.bmp') as source_image, Image.open(output / 'd3d11.bmp') as received_image:
            if source_image.size != received_image.size or source_image.convert('RGB').tobytes() != received_image.convert('RGB').tobytes():
                raise ValueError('D3D11 received pixels differ from the UE reference')
        report['gpu_exchange_pixels_equal'] = True
    source = json.loads(scene.read_text(encoding='utf-8'))
    if gpu_depth:
        import numpy as np
        _, coverage, interior, ndc = pixels.reference(source, scene.parent, frame, include_depth=True,image_origin='bottom')
        actual = np.fromfile(output / 'depth.raw', dtype='<f4').reshape(ndc.shape)
        projection = np.asarray(source['frames'][frame]['projection'])
        selected = coverage & interior
        if not selected.any():
            raise ValueError('Depth fixture has no qualified interior pixels')
        expected = projection[2, 3] / (ndc[selected] + projection[2, 2])
        relative_error = np.abs(actual[selected] - expected) / np.maximum(expected, 1e-6)
        # Hardware subpixel rounding can select the adjacent surface exactly
        # at an occlusion edge. Qualify those pixels against nearby reference
        # surfaces instead of accepting arbitrary outliers.
        converted = -projection[2, 2] + projection[2, 3] / actual[selected]
        boundary = (relative_error > .002) | (np.abs(converted - ndc[selected]) > 1e-4)
        accepted_boundary = np.zeros(boundary.shape, dtype=bool)
        ys, xs = np.where(selected)
        for index in np.flatnonzero(boundary):
            y, x = ys[index], xs[index]
            nearby = ndc[max(0, y-1):y+2, max(0, x-1):x+2]
            finite = nearby[np.isfinite(nearby)]
            edge = finite.size < nearby.size or np.ptp(finite) > 1e-4
            depths = projection[2, 3] / (finite + projection[2, 2])
            accepted_boundary[index] = edge and np.any(np.abs(depths - actual[y, x]) / depths <= .002)
        if not selected.any() or not np.isfinite(relative_error).all() or np.any(boundary & ~accepted_boundary):
            raise ValueError(f'UE depth differs from source geometry: {relative_error.max()}')
        stable = selected.copy()
        stable[ys[accepted_boundary], xs[accepted_boundary]] = False
        report['gpu_depth'] = dict(compared_pixels=int(stable.sum()),
                                   raster_boundary_pixels=int(accepted_boundary.sum()),
                                   max_relative_error=float(relative_error[~accepted_boundary].max()))
        native = np.fromfile(output / 'depth.raw.native', dtype='<f4').reshape(ndc.shape)
        owners = np.fromfile(output / 'depth.raw.owners', dtype='<u4').reshape(ndc.shape)
        if not np.all(owners[selected] == source['frames'][frame]['owner']):
            raise ValueError('Owner bits did not survive GPU conversion')
        depth_error = np.abs(native[stable] - ndc[stable])
        if depth_error.max() > 1e-4:
            raise ValueError(f'Native depth conversion error: {depth_error.max()}')
        report['gpu_depth']['native_max_error'] = float(depth_error.max())
        report['gpu_depth']['owner_pixels'] = int(np.count_nonzero(owners))
        report['gpu_depth']['background_false_owners'] = int(np.count_nonzero(owners[~coverage]))
        padded = np.pad(coverage, 1)
        adjacent = np.logical_or.reduce([
            padded[y:y+coverage.shape[0], x:x+coverage.shape[1]]
            for y in range(3) for x in range(3)
        ])
        if np.any(owners[~adjacent]):
            raise ValueError(f'Background wrongly assigned to owner: {report["gpu_depth"]}')
    if report['source_packet_sha256'] != source['source_packet_sha256'] or report['source_frame'] != source['frames'][frame]:
        raise ValueError('Rendered receipt lost source provenance')
    if not report['constructed_arrays_checked'] or report['transform_updates'] != 101:
        raise ValueError('Constructed arrays or retained transforms not verified')
    if shared and not procedural and not report['shared_geometry']:
        raise ValueError('Owners do not share the retained mesh')
    if world_restart and (report.get('world_activations') != 2 or report.get('asset_builds') != 1):
        raise ValueError('World recreation did not reuse its session asset')
    if not shared:
        report['pixels'] = pixels.verify(scene, output / 'ship.bmp', output, frame,image_origin='bottom')
        if report['pixels']['within_three_levels'] < .97:
            raise ValueError(f'Source pixel comparison failed: {output}')
    report['process_seconds'] = elapsed
    (output / 'qualified.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def close_normally(exe, scene, output, *, escape=False):
    """Send normal Windows close to this owned process, then verify no capture files."""
    exe, scene, output = exe.resolve(), scene.resolve(), output.resolve()
    exe = runtime_exe(exe)
    output.mkdir(parents=True, exist_ok=False)
    p = subprocess.Popen([str(exe), '-windowed', '-ResX=1920', '-ResY=1080', '-nosound',
                          '-nolog', f'-SFCScene={scene}', f'-SFCOutput={output}'])
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    callback = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    deadline = time.monotonic() + 45
    try:
        while time.monotonic() < deadline and p.poll() is None:
            handles = []
            @callback
            def visit(hwnd, _):
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value == p.pid and user32.IsWindowVisible(hwnd):
                    handles.append(hwnd)
                return True
            user32.EnumWindows(visit, 0)
            if handles:
                time.sleep(2)
                for hwnd in handles:
                    if escape:
                        user32.PostMessageW(hwnd, 0x0100, 0x1B, 0x00010001)  # WM_KEYDOWN Escape
                        user32.PostMessageW(hwnd, 0x0101, 0x1B, 0xC0010001)
                    else:
                        user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE, not forced termination
                break
            time.sleep(.1)
        code = p.wait(timeout=30)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
            raise RuntimeError('Normal close failed; terminated only this owned fixture')
    if code or list(output.iterdir()):
        raise ValueError('Normal close or diagnostics-off capture check failed')
    return dict(normal_exit=True, diagnostic_files=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe', type=Path)
    parser.add_argument('scene', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--frame', type=int, default=0)
    parser.add_argument('--procedural', action='store_true')
    parser.add_argument('--shared', action='store_true')
    parser.add_argument('--reject', action='store_true')
    parser.add_argument('--close', action='store_true')
    parser.add_argument('--gpu-exchange', action='store_true')
    parser.add_argument('--gpu-consumer', type=Path)
    parser.add_argument('--gpu-depth', action='store_true')
    args = parser.parse_args()
    if args.close:
        result = close_normally(args.exe, args.scene, args.output)
    else:
        result = run(args.exe, args.scene, args.output, frame=args.frame, procedural=args.procedural,
                     shared=args.shared, expect_reject=args.reject, gpu_exchange=args.gpu_exchange,
                     gpu_consumer=args.gpu_consumer, gpu_depth=args.gpu_depth)
    print(json.dumps(result, indent=2))

#!/usr/bin/env python3
"""Reusable image processing CLI powered by Python orchestration and ImageMagick.

This script intentionally keeps dependencies minimal:
- Python standard library only
- ImageMagick available as `magick` on PATH, or in common Windows install paths
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}
TOOL_VERSION = "0.2.0"
PROFILE_PRESETS = {
    "avatar": {
        "description": "Centered square JPG output for avatars or profile photos.",
        "defaults": {
            "action": "crop-square",
            "format": "jpg",
            "suffix": "_avatar",
            "quality": 92,
        },
    },
    "social-square": {
        "description": "Centered square JPG output for social media posts or covers.",
        "defaults": {
            "action": "crop-square",
            "format": "jpg",
            "suffix": "_social",
            "quality": 90,
        },
    },
    "square-pad": {
        "description": "Keep full frame and pad to a square PNG canvas.",
        "defaults": {
            "action": "pad-square",
            "format": "png",
            "suffix": "_square",
            "background": "white",
        },
    },
    "thumbnail": {
        "description": "Create compact thumbnails for galleries or lists.",
        "defaults": {
            "action": "resize",
            "width": 427,
            "height": 240,
            "suffix": "_thumb",
            "quality": 85,
        },
    },
    "webp-web": {
        "description": "Convert images to WEBP for web delivery.",
        "defaults": {
            "action": "convert",
            "format": "webp",
            "suffix": "_web",
            "quality": 85,
        },
    },
    "wallpaper-fhd": {
        "description": "Resize to 1920x1080 for Full HD wallpapers.",
        "defaults": {
            "action": "resize",
            "width": 1920,
            "height": 1080,
            "suffix": "_fhd",
            "quality": 90,
            "fill": True,
        },
    },
}


@dataclass
class ProcessResult:
    source: Path
    output: Path | None
    ok: bool
    message: str = ""


def resolve_magick() -> str:
    magick = shutil.which("magick")
    if magick:
        return magick

    common_windows_dirs = [
        Path(r"C:\Program Files"),
        Path(r"C:\Program Files (x86)"),
        Path(r"D:\APP\Develop"),
    ]
    for base in common_windows_dirs:
        if not base.exists():
            continue
        candidates = sorted(base.glob("ImageMagick-*/magick.exe"))
        if candidates:
            return str(candidates[-1])

    raise RuntimeError(
        "ImageMagick not found. Install ImageMagick on Windows and ensure magick.exe is on PATH."
    )


def run_magick(magick: str, args: list[str]) -> str:
    result = subprocess.run(
        [magick, *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "magick failed")
    return result.stdout


def parse_color(value: str) -> str:
    return value.strip() or "white"


def parse_quality(value: int) -> int:
    if value < 1 or value > 100:
        raise argparse.ArgumentTypeError("quality must be between 1 and 100")
    return value


def parse_positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return parsed


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise RuntimeError(f"config must be a JSON object: {path}")
    return data


def ensure_output_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTS


def write_json(path: Path, payload: object) -> None:
    ensure_output_parent(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def iter_images(input_path: Path, recursive: bool, pattern: str | None = None) -> Iterable[Path]:
    if input_path.is_file():
        if is_image_file(input_path):
            yield input_path
        return

    if not input_path.exists():
        return

    if recursive:
        iterator = input_path.rglob(pattern or "*")
    else:
        iterator = input_path.glob(pattern or "*")

    for path in iterator:
        if is_image_file(path):
            yield path


def get_dimensions(magick: str, image_path: Path) -> tuple[int, int]:
    output = run_magick(magick, ["identify", "-format", "%w,%h", str(image_path)]).strip()
    width, height = output.split(",")
    return int(width), int(height)


def get_basic_info(magick: str, image_path: Path) -> dict[str, object]:
    output = run_magick(
        magick,
        ["identify", "-format", "%f|%m|%w|%h|%b", str(image_path)],
    ).strip()
    filename, fmt, width, height, size = output.split("|", 4)
    return {
        "file": filename,
        "path": str(image_path),
        "format": fmt,
        "width": int(width),
        "height": int(height),
        "size": size,
    }


def get_verbose_info(magick: str, image_path: Path) -> str:
    return run_magick(magick, ["identify", "-verbose", str(image_path)])


def maybe_change_suffix(path: Path, output_format: str | None) -> Path:
    if not output_format:
        return path
    return path.with_suffix("." + output_format.lower().lstrip("."))


def derive_output_path(
    src: Path,
    input_root: Path,
    output_root: Path,
    output_format: str | None = None,
    suffix: str = "",
) -> Path:
    try:
        relative = src.relative_to(input_root)
    except ValueError:
        relative = Path(src.name)

    if suffix:
        relative = relative.with_name(relative.stem + suffix + relative.suffix)

    dst = output_root / relative
    if output_format:
        dst = maybe_change_suffix(dst, output_format)
    return dst


def output_exists_message(dst: Path) -> str:
    return f"skipped: output exists ({dst})"


def should_skip_existing(dst: Path, overwrite: bool) -> bool:
    return dst.exists() and not overwrite


def convert_image(
    magick: str,
    src: Path,
    dst: Path,
    quality: int = 90,
    background: str = "white",
) -> None:
    args = [str(src)]
    if src.suffix.lower() == ".png" and dst.suffix.lower() in {".jpg", ".jpeg"}:
        args += ["-background", background, "-alpha", "remove", "-alpha", "off"]
    args += ["-quality", str(quality), str(dst)]
    run_magick(magick, args)


def resize_image(
    magick: str,
    src: Path,
    dst: Path,
    width: int,
    height: int,
    force: bool = False,
    fill: bool = False,
    quality: int | None = None,
) -> None:
    geometry = f"{width}x{height}"
    if force:
        geometry += "!"
    elif fill:
        geometry += "^"

    args = [str(src), "-resize", geometry]
    if quality is not None:
        args += ["-quality", str(quality)]
    args += [str(dst)]
    run_magick(magick, args)


def crop_square(magick: str, src: Path, dst: Path, quality: int | None = None) -> None:
    args = [
        str(src),
        "-gravity",
        "center",
        "-crop",
        "%[fx:min(w,h)]x%[fx:min(w,h)]+0+0",
        "+repage",
    ]
    if quality is not None:
        args += ["-quality", str(quality)]
    args += [str(dst)]
    run_magick(magick, args)


def pad_square(
    magick: str,
    src: Path,
    dst: Path,
    background: str = "white",
    quality: int | None = None,
) -> None:
    args = [
        str(src),
        "-background",
        background,
        "-gravity",
        "center",
        "-extent",
        "%[fx:max(w,h)]x%[fx:max(w,h)]",
    ]
    if quality is not None:
        args += ["-quality", str(quality)]
    args += [str(dst)]
    run_magick(magick, args)


def print_results(results: list[ProcessResult]) -> int:
    ok_count = sum(1 for r in results if r.ok)
    fail_count = len(results) - ok_count
    print(json.dumps(
        {
            "total": len(results),
            "ok": ok_count,
            "failed": fail_count,
            "results": [
                {
                    "source": str(r.source),
                    "output": str(r.output) if r.output else None,
                    "ok": r.ok,
                    "message": r.message,
                }
                for r in results
            ],
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0 if fail_count == 0 else 1


def results_payload(results: list[ProcessResult]) -> dict[str, object]:
    ok_count = sum(1 for r in results if r.ok)
    fail_count = len(results) - ok_count
    return {
        "tool_version": TOOL_VERSION,
        "total": len(results),
        "ok": ok_count,
        "failed": fail_count,
        "results": [
            {
                "source": str(r.source),
                "output": str(r.output) if r.output else None,
                "ok": r.ok,
                "message": r.message,
            }
            for r in results
        ],
    }


def save_manifest(path: Path | None, payload: dict[str, object]) -> None:
    if path:
        write_json(path, payload)


def print_single_result(source: Path, output: Path | None, ok: bool, message: str = "") -> int:
    print(json.dumps(
        {
            "source": str(source),
            "output": str(output) if output else None,
            "ok": ok,
            "message": message,
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0 if ok else 1


def require_output(path: str | None) -> Path:
    if not path:
        raise SystemExit("--output is required for this command")
    return Path(path)


def handle_doctor(_: argparse.Namespace) -> int:
    info = {
        "tool_version": TOOL_VERSION,
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
    }
    try:
        magick = resolve_magick()
        version_line = run_magick(magick, ["-version"]).splitlines()[0]
        info.update({
            "magick_found": True,
            "magick_path": magick,
            "magick_version": version_line,
        })
    except Exception as exc:
        info.update({
            "magick_found": False,
            "magick_error": str(exc),
        })
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def handle_profiles(_: argparse.Namespace) -> int:
    payload = {
        "tool_version": TOOL_VERSION,
        "profiles": [
            {
                "name": name,
                "description": profile["description"],
                "defaults": profile["defaults"],
            }
            for name, profile in PROFILE_PRESETS.items()
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def handle_init_config(args: argparse.Namespace) -> int:
    profile_name = args.profile or "thumbnail"
    if profile_name not in PROFILE_PRESETS:
        raise SystemExit(f"unknown profile: {profile_name}")

    payload = {
        "tool_version": TOOL_VERSION,
        "profile": profile_name,
        "input": r"D:\images",
        "output": r"D:\images_out",
        "recursive": True,
        "pattern": "*.png",
        "manifest": r"D:\images_out\manifest.json",
    }
    payload.update(PROFILE_PRESETS[profile_name]["defaults"])
    output_path = Path(args.output)
    write_json(output_path, payload)
    print(json.dumps(
        {
            "ok": True,
            "message": "config created",
            "message_zh": "配置文件已创建",
            "output": str(output_path),
            "profile": profile_name,
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


def merge_batch_settings(args: argparse.Namespace) -> argparse.Namespace:
    merged: dict[str, object] = {
        "action": None,
        "format": None,
        "suffix": "",
        "quality": 90,
        "background": "white",
        "width": None,
        "height": None,
        "force": False,
        "fill": False,
        "min_width": None,
        "min_height": None,
        "overwrite": False,
        "dry_run": False,
        "fail_fast": False,
        "manifest": None,
        "pattern": None,
        "recursive": False,
        "input": None,
        "output": None,
        "profile": None,
    }

    if args.config:
        config_path = Path(args.config)
        config = load_json(config_path)
        profile_name = config.get("profile")
        if profile_name:
            if profile_name not in PROFILE_PRESETS:
                raise SystemExit(f"unknown profile in config: {profile_name}")
            merged.update(PROFILE_PRESETS[str(profile_name)]["defaults"])
            merged["profile"] = str(profile_name)

        alias_map = {
            "min_width": "min_width",
            "min_height": "min_height",
        }
        for key, value in config.items():
            target_key = alias_map.get(key, key)
            if target_key in merged and value is not None:
                merged[target_key] = value

    if args.profile:
        if args.profile not in PROFILE_PRESETS:
            raise SystemExit(f"unknown profile: {args.profile}")
        merged.update(PROFILE_PRESETS[args.profile]["defaults"])
        merged["profile"] = args.profile

    cli_values = {
        "input": args.input,
        "output": args.output,
        "action": args.action,
        "recursive": args.recursive,
        "pattern": args.pattern,
        "format": args.format,
        "suffix": args.suffix,
        "quality": args.quality,
        "background": args.background,
        "width": args.width,
        "height": args.height,
        "force": args.force,
        "fill": args.fill,
        "min_width": args.min_width,
        "min_height": args.min_height,
        "overwrite": args.overwrite,
        "dry_run": args.dry_run,
        "fail_fast": args.fail_fast,
        "manifest": args.manifest,
    }
    for key, value in cli_values.items():
        if value is not None:
            merged[key] = value

    for key, value in merged.items():
        setattr(args, key, value)
    return args


def validate_resolved_batch_args(args: argparse.Namespace) -> None:
    if not args.input:
        raise SystemExit("resolved batch input is empty")
    if not args.output:
        raise SystemExit("resolved batch output is empty")
    if not args.action:
        raise SystemExit("resolved batch action is empty")
    if args.action == "resize" and (not args.width or not args.height):
        raise SystemExit("resolved resize batch requires width and height")
    if args.force and args.fill:
        raise SystemExit("--force and --fill cannot be used together")


def handle_info(args: argparse.Namespace) -> int:
    magick = resolve_magick()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"input not found: {input_path}")

    if input_path.is_file():
        if args.verbose:
            print(get_verbose_info(magick, input_path))
        else:
            print(json.dumps(get_basic_info(magick, input_path), ensure_ascii=False, indent=2))
        return 0

    rows = []
    for image in iter_images(input_path, recursive=args.recursive, pattern=args.pattern):
        rows.append(get_basic_info(magick, image))
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def handle_convert(args: argparse.Namespace) -> int:
    magick = resolve_magick()
    src = Path(args.input)
    dst = require_output(args.output)
    if should_skip_existing(dst, args.overwrite):
        return print_single_result(src, dst, True, output_exists_message(dst))
    ensure_output_parent(dst)
    convert_image(magick, src, dst, quality=args.quality, background=args.background)
    return print_single_result(src, dst, True, "processed")


def handle_resize(args: argparse.Namespace) -> int:
    magick = resolve_magick()
    src = Path(args.input)
    dst = require_output(args.output)
    if should_skip_existing(dst, args.overwrite):
        return print_single_result(src, dst, True, output_exists_message(dst))
    ensure_output_parent(dst)
    resize_image(
        magick,
        src,
        dst,
        width=args.width,
        height=args.height,
        force=args.force,
        fill=args.fill,
        quality=args.quality,
    )
    return print_single_result(src, dst, True, "processed")


def handle_crop_square(args: argparse.Namespace) -> int:
    magick = resolve_magick()
    src = Path(args.input)
    dst = require_output(args.output)
    if should_skip_existing(dst, args.overwrite):
        return print_single_result(src, dst, True, output_exists_message(dst))
    ensure_output_parent(dst)
    crop_square(magick, src, dst, quality=args.quality)
    return print_single_result(src, dst, True, "processed")


def handle_pad_square(args: argparse.Namespace) -> int:
    magick = resolve_magick()
    src = Path(args.input)
    dst = require_output(args.output)
    if should_skip_existing(dst, args.overwrite):
        return print_single_result(src, dst, True, output_exists_message(dst))
    ensure_output_parent(dst)
    pad_square(magick, src, dst, background=args.background, quality=args.quality)
    return print_single_result(src, dst, True, "processed")


def apply_batch_action(magick: str, args: argparse.Namespace, src: Path, dst: Path) -> None:
    if args.action == "convert":
        convert_image(magick, src, dst, quality=args.quality, background=args.background)
    elif args.action == "resize":
        resize_image(
            magick,
            src,
            dst,
            width=args.width,
            height=args.height,
            force=args.force,
            fill=args.fill,
            quality=args.quality,
        )
    elif args.action == "crop-square":
        crop_square(magick, src, dst, quality=args.quality)
    elif args.action == "pad-square":
        pad_square(magick, src, dst, background=args.background, quality=args.quality)
    else:
        raise RuntimeError(f"unsupported action: {args.action}")


def handle_batch(args: argparse.Namespace) -> int:
    args = merge_batch_settings(args)
    validate_resolved_batch_args(args)
    magick = resolve_magick()
    input_dir = Path(args.input)
    output_dir = require_output(args.output)
    if not input_dir.exists():
        raise SystemExit(f"input not found: {input_dir}")
    ensure_directory(output_dir)

    results: list[ProcessResult] = []
    for src in iter_images(input_dir, recursive=args.recursive, pattern=args.pattern):
        dst = derive_output_path(
            src=src,
            input_root=input_dir if input_dir.is_dir() else src.parent,
            output_root=output_dir,
            output_format=args.format,
            suffix=args.suffix,
        )
        try:
            if should_skip_existing(dst, args.overwrite):
                results.append(ProcessResult(src, dst, True, output_exists_message(dst)))
                continue

            if args.min_width or args.min_height:
                width, height = get_dimensions(magick, src)
                if args.min_width and width < args.min_width:
                    results.append(ProcessResult(src, None, True, "skipped: width below threshold"))
                    continue
                if args.min_height and height < args.min_height:
                    results.append(ProcessResult(src, None, True, "skipped: height below threshold"))
                    continue

            if args.dry_run:
                results.append(ProcessResult(src, dst, True, "dry-run: planned"))
                continue

            ensure_output_parent(dst)
            apply_batch_action(magick, args, src, dst)
            results.append(ProcessResult(src, dst, True, "processed"))
        except Exception as exc:
            if args.fail_fast:
                raise
            results.append(ProcessResult(src, dst, False, str(exc)))

    payload = results_payload(results)
    payload["profile"] = args.profile
    payload["action"] = args.action
    payload["input"] = str(input_dir)
    payload["output"] = str(output_dir)
    if args.manifest:
        save_manifest(Path(args.manifest), payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["failed"] == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reusable image processing CLI powered by Python and ImageMagick.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="Check Python and ImageMagick availability.")
    doctor_parser.set_defaults(func=handle_doctor)

    profiles_parser = subparsers.add_parser("profiles", help="List built-in processing profiles.")
    profiles_parser.set_defaults(func=handle_profiles)

    init_config_parser = subparsers.add_parser("init-config", help="Create a starter JSON config file.")
    init_config_parser.add_argument("--output", required=True, help="Output JSON config path.")
    init_config_parser.add_argument("--profile", choices=sorted(PROFILE_PRESETS), help="Built-in profile for starter config.")
    init_config_parser.set_defaults(func=handle_init_config)

    info_parser = subparsers.add_parser("info", help="Inspect image dimensions and metadata.")
    info_parser.add_argument("--input", required=True, help="Input image file or directory.")
    info_parser.add_argument("--recursive", action="store_true", help="Scan directories recursively.")
    info_parser.add_argument("--pattern", help="Glob pattern for directory scanning, e.g. '*.png'.")
    info_parser.add_argument("--verbose", action="store_true", help="Use identify -verbose for single file input.")
    info_parser.set_defaults(func=handle_info)

    convert_parser = subparsers.add_parser("convert", help="Convert one image to another format.")
    convert_parser.add_argument("--input", required=True, help="Input image file.")
    convert_parser.add_argument("--output", required=True, help="Output image file.")
    convert_parser.add_argument("--quality", type=parse_quality, default=90, help="Output quality (1-100).")
    convert_parser.add_argument("--background", type=parse_color, default="white", help="Background used when removing alpha.")
    convert_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file.")
    convert_parser.set_defaults(func=handle_convert)

    resize_parser = subparsers.add_parser("resize", help="Resize one image.")
    resize_parser.add_argument("--input", required=True, help="Input image file.")
    resize_parser.add_argument("--output", required=True, help="Output image file.")
    resize_parser.add_argument("--width", type=parse_positive_int, required=True, help="Target width.")
    resize_parser.add_argument("--height", type=parse_positive_int, required=True, help="Target height.")
    resize_parser.add_argument("--quality", type=parse_quality, default=90, help="Output quality (1-100).")
    resize_parser.add_argument("--force", action="store_true", help="Force exact dimensions with ! geometry.")
    resize_parser.add_argument("--fill", action="store_true", help="Use ^ geometry for fill-before-crop style resizing.")
    resize_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file.")
    resize_parser.set_defaults(func=handle_resize)

    crop_parser = subparsers.add_parser("crop-square", help="Crop one image to a centered square.")
    crop_parser.add_argument("--input", required=True, help="Input image file.")
    crop_parser.add_argument("--output", required=True, help="Output image file.")
    crop_parser.add_argument("--quality", type=parse_quality, default=90, help="Output quality (1-100).")
    crop_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file.")
    crop_parser.set_defaults(func=handle_crop_square)

    pad_parser = subparsers.add_parser("pad-square", help="Pad one image to a square canvas.")
    pad_parser.add_argument("--input", required=True, help="Input image file.")
    pad_parser.add_argument("--output", required=True, help="Output image file.")
    pad_parser.add_argument("--quality", type=parse_quality, default=90, help="Output quality (1-100).")
    pad_parser.add_argument("--background", type=parse_color, default="white", help="Canvas background color.")
    pad_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file.")
    pad_parser.set_defaults(func=handle_pad_square)

    batch_parser = subparsers.add_parser("batch", help="Batch process images in a directory.")
    batch_parser.add_argument("--input", help="Input directory or one image file.")
    batch_parser.add_argument("--output", help="Output directory.")
    batch_parser.add_argument(
        "--action",
        choices=["convert", "resize", "crop-square", "pad-square"],
        help="Transformation to apply.",
    )
    batch_parser.add_argument("--config", help="JSON config file describing a batch job.")
    batch_parser.add_argument("--profile", choices=sorted(PROFILE_PRESETS), help="Built-in processing profile.")
    batch_parser.add_argument("--recursive", action="store_true", help="Scan directories recursively.")
    batch_parser.add_argument("--pattern", help="Glob pattern for directory scanning, e.g. '*.png'.")
    batch_parser.add_argument("--format", help="Optional output format, e.g. jpg, png, webp.")
    batch_parser.add_argument("--suffix", help="Optional filename suffix, e.g. _square.")
    batch_parser.add_argument("--quality", type=parse_quality, help="Output quality (1-100).")
    batch_parser.add_argument("--background", type=parse_color, help="Background color for alpha removal or padding.")
    batch_parser.add_argument("--width", type=parse_positive_int, help="Target width for resize.")
    batch_parser.add_argument("--height", type=parse_positive_int, help="Target height for resize.")
    batch_parser.add_argument("--force", action="store_true", help="Force exact resize dimensions.")
    batch_parser.add_argument("--fill", action="store_true", help="Use fill-before-crop resize geometry (^).")
    batch_parser.add_argument("--min-width", type=parse_positive_int, help="Skip images narrower than this.")
    batch_parser.add_argument("--min-height", type=parse_positive_int, help="Skip images shorter than this.")
    batch_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files.")
    batch_parser.add_argument("--dry-run", action="store_true", help="Preview planned outputs without writing files.")
    batch_parser.add_argument("--manifest", help="Write JSON manifest/report to this file.")
    batch_parser.add_argument("--fail-fast", action="store_true", help="Stop at the first processing error.")
    batch_parser.set_defaults(func=handle_batch)

    return parser


def validate_args(args: argparse.Namespace) -> None:
    if getattr(args, "command", None) == "batch":
        if not args.input and not args.config:
            raise SystemExit("--input is required unless --config is provided")
        if not args.output and not args.config:
            raise SystemExit("--output is required unless --config is provided")
        if not args.action and not args.profile and not args.config:
            raise SystemExit("--action is required unless --profile or --config is provided")
    if getattr(args, "command", None) == "batch" and args.action == "resize":
        if not args.width or not args.height:
            raise SystemExit("--width and --height are required when --action resize")
    if getattr(args, "command", None) == "resize" and args.force and args.fill:
        raise SystemExit("--force and --fill cannot be used together")
    if getattr(args, "command", None) == "batch" and args.action == "resize" and args.force and args.fill:
        raise SystemExit("--force and --fill cannot be used together")
    if getattr(args, "command", None) == "batch" and args.config:
        config = load_json(Path(args.config))
        action = args.action or config.get("action")
        profile = args.profile or config.get("profile")
        if not action and not profile:
            raise SystemExit("batch config must define action or profile")
        if action == "resize":
            width = args.width or config.get("width")
            height = args.height or config.get("height")
            if not width or not height:
                raise SystemExit("resize batch config must define width and height")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

from __future__ import annotations

import argparse
import re
from pathlib import Path, PurePosixPath
from zipfile import ZIP_STORED, ZipFile, ZipInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = "yunoe"

DIRECTORIES = (
    "yunoe/",
    "yunoe/agents/",
    "yunoe/references/",
    "yunoe/scripts/",
)
PACKAGE_FILES = (
    "LICENSE",
    "README.md",
    "SKILL.md",
    "agents/openai.yaml",
    "references/backend.md",
    "references/typography.md",
    "references/wechat-boundary.md",
    "scripts/wechat_console.py",
)


def project_version() -> str:
    version = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise RuntimeError(f"VERSION is invalid: {version!r}")
    return version


def archive_name(relative_name: str) -> str:
    return f"{PACKAGE_ROOT}/{PurePosixPath(relative_name).as_posix()}"


def package_entries() -> list[tuple[Path, str]]:
    entries = [
        (PROJECT_ROOT / relative_name, archive_name(relative_name))
        for relative_name in PACKAGE_FILES
    ]
    missing = [name for source, name in entries if not source.is_file()]
    if missing:
        raise FileNotFoundError("package files are missing: " + ", ".join(missing))
    symlinks = [name for source, name in entries if source.is_symlink()]
    if symlinks:
        raise RuntimeError("package files must not be symlinks: " + ", ".join(symlinks))
    return entries


def zip_info(name: str, *, directory: bool = False) -> ZipInfo:
    info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = (0o40755 if directory else 0o100644) << 16
    return info


def source_bytes(source: Path) -> bytes:
    text = source.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def build_archive(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_suffix(f"{output.suffix}.tmp")
    try:
        with ZipFile(temporary_output, "w") as archive:
            for directory in DIRECTORIES:
                archive.writestr(zip_info(directory, directory=True), b"")
            for source, name in package_entries():
                archive.writestr(zip_info(name), source_bytes(source))
        verify_archive(temporary_output)
        temporary_output.replace(output)
    finally:
        temporary_output.unlink(missing_ok=True)


def verify_archive(archive_path: Path) -> None:
    expected_files = {name: source for source, name in package_entries()}
    expected_names = set(DIRECTORIES) | set(expected_files)
    with ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError("archive contains duplicate paths")
        if set(names) != expected_names:
            missing = expected_names.difference(names)
            unexpected = set(names).difference(expected_names)
            details = []
            if missing:
                details.append("missing: " + ", ".join(sorted(missing)))
            if unexpected:
                details.append("unexpected: " + ", ".join(sorted(unexpected)))
            raise RuntimeError("invalid package whitelist (" + "; ".join(details) + ")")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                raise RuntimeError(f"unsafe archive path: {name}")
        for name, source in expected_files.items():
            if archive.read(name) != source_bytes(source):
                raise RuntimeError(f"archive content does not match source: {name}")


def default_output() -> Path:
    return PROJECT_ROOT / "artifacts" / f"yunoe-v{project_version()}.zip"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or verify the Yunoe skill ZIP")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path, help="output ZIP path")
    group.add_argument("--verify-only", type=Path, help="verify an existing ZIP")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verify_only:
        verify_archive(args.verify_only.resolve())
        print(f"Verified Yunoe skill release: {args.verify_only}")
        return 0

    output = args.output or default_output()
    output = output if output.is_absolute() else PROJECT_ROOT / output
    build_archive(output.resolve())
    print(f"Built and verified Yunoe skill release: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

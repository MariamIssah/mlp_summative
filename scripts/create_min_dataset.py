import argparse
import os
import shutil
from pathlib import Path
from typing import Iterable


def iter_image_files(folder: Path) -> Iterable[Path]:
    """Yield image file paths under folder in sorted order."""
    if not folder.exists():
        return []
    return sorted(
        [
            path
            for path in folder.iterdir()
            if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]
    )


def copy_subset(source_root: Path, target_root: Path, limit: int) -> int:
    """
    Copy up to `limit` images per class directory from source_root to target_root.

    Returns number of files copied.
    """
    copied = 0
    for class_dir in sorted(source_root.iterdir()):
        if not class_dir.is_dir():
            continue
        images = iter_image_files(class_dir)[:limit]
        if not images:
            continue
        dest_dir = target_root / class_dir.name
        dest_dir.mkdir(parents=True, exist_ok=True)
        for image_path in images:
            shutil.copy2(image_path, dest_dir / image_path.name)
            copied += 1
    return copied


def main():
    parser = argparse.ArgumentParser(description="Create a smaller dataset subset.")
    parser.add_argument("--train-count", type=int, default=30, help="Images per class for training set")
    parser.add_argument("--val-count", type=int, default=10, help="Images per class for validation set")
    parser.add_argument("--source-root", default="data", help="Base data directory containing train/validation")
    parser.add_argument("--target-suffix", default="_min", help="Suffix for subset directories")
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    train_src = source_root / "train"
    val_src = source_root / "validation"

    if not train_src.exists() or not val_src.exists():
        raise FileNotFoundError(f"Expected train/validation under {source_root}, but directories are missing.")

    train_target = source_root / f"train{args.target_suffix}"
    val_target = source_root / f"validation{args.target_suffix}"

    shutil.rmtree(train_target, ignore_errors=True)
    shutil.rmtree(val_target, ignore_errors=True)

    train_target.mkdir(parents=True, exist_ok=True)
    val_target.mkdir(parents=True, exist_ok=True)

    train_copied = copy_subset(train_src, train_target, args.train_count)
    val_copied = copy_subset(val_src, val_target, args.val_count)

    print(f"Copied {train_copied} training images into {train_target}")
    print(f"Copied {val_copied} validation images into {val_target}")


if __name__ == "__main__":
    main()


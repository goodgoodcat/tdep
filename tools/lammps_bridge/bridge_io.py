#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtXYZFrame:
    symbols: list[str]
    positions: list[tuple[float, float, float]]
    lattice: list[list[float]]
    comment: str


_FLOAT_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _parse_lattice(comment: str) -> list[list[float]]:
    m = re.search(r'Lattice="([^"]+)"', comment)
    if m:
        vals = [float(x) for x in m.group(1).split()]
        if len(vals) == 9:
            return [vals[0:3], vals[3:6], vals[6:9]]
    if "CELL{H}:" in comment:
        vals = [float(x) for x in _FLOAT_RE.findall(comment.split("CELL{H}:", 1)[1])][:9]
        if len(vals) == 9:
            return [vals[0:3], vals[3:6], vals[6:9]]
    raise ValueError("Cannot parse lattice from extxyz comment")


def read_extxyz(path: str | Path) -> list[ExtXYZFrame]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    i = 0
    frames: list[ExtXYZFrame] = []
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        n = int(lines[i].strip())
        comment = lines[i + 1]
        lattice = _parse_lattice(comment)
        block = lines[i + 2 : i + 2 + n]
        if len(block) != n:
            raise ValueError("Truncated extxyz frame")
        symbols: list[str] = []
        positions: list[tuple[float, float, float]] = []
        for row in block:
            f = row.split()
            symbols.append(f[0])
            positions.append((float(f[1]), float(f[2]), float(f[3])))
        frames.append(ExtXYZFrame(symbols, positions, lattice, comment))
        i += 2 + n
    if not frames:
        raise ValueError("No extxyz frame parsed")
    return frames

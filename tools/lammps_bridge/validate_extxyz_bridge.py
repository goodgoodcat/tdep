#!/usr/bin/env python3
from __future__ import annotations

import argparse

from bridge_io import read_extxyz


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-extxyz", required=True)
    ap.add_argument("--strict-lattice", action="store_true")
    args = ap.parse_args()

    frames = read_extxyz(args.in_extxyz)
    n0 = len(frames[0].symbols)
    s0 = frames[0].symbols
    l0 = frames[0].lattice

    for i, fr in enumerate(frames):
        if len(fr.symbols) != n0:
            raise SystemExit(f"Frame {i}: atom count mismatch")
        if fr.symbols != s0:
            raise SystemExit(f"Frame {i}: atom order/species mismatch")
        if args.strict_lattice and fr.lattice != l0:
            raise SystemExit(f"Frame {i}: lattice mismatch")

    print(f"OK: {len(frames)} frame(s), {n0} atoms/frame")


if __name__ == "__main__":
    main()

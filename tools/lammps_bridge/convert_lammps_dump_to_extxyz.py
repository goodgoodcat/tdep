#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _bounds_to_lattice(bounds: list[str]) -> tuple[list[list[float]], tuple[float, float, float]]:
    if len(bounds[0].split()) == 3:
        xlo_b, xhi_b, xy = map(float, bounds[0].split())
        ylo_b, yhi_b, xz = map(float, bounds[1].split())
        zlo_b, zhi_b, yz = map(float, bounds[2].split())
        xlo = xlo_b - min(0.0, xy, xz, xy + xz)
        xhi = xhi_b - max(0.0, xy, xz, xy + xz)
        ylo = ylo_b - min(0.0, yz)
        yhi = yhi_b - max(0.0, yz)
        zlo = zlo_b
        zhi = zhi_b
        lat = [[xhi - xlo, 0.0, 0.0], [xy, yhi - ylo, 0.0], [xz, yz, zhi - zlo]]
        return lat, (xlo, ylo, zlo)
    xlo, xhi = map(float, bounds[0].split()[:2])
    ylo, yhi = map(float, bounds[1].split()[:2])
    zlo, zhi = map(float, bounds[2].split()[:2])
    lat = [[xhi - xlo, 0.0, 0.0], [0.0, yhi - ylo, 0.0], [0.0, 0.0, zhi - zlo]]
    return lat, (xlo, ylo, zlo)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dump", required=True)
    ap.add_argument("--type-map", required=True)
    ap.add_argument("--out-extxyz", required=True)
    args = ap.parse_args()

    sym_to_id = json.loads(Path(args.type_map).read_text(encoding="utf-8"))
    id_to_sym = {int(v): k for k, v in sym_to_id.items()}

    lines = Path(args.in_dump).read_text(encoding="utf-8").splitlines()
    i = 0
    out: list[str] = []

    while i < len(lines):
        if not lines[i].startswith("ITEM: TIMESTEP"):
            i += 1
            continue
        step = int(lines[i + 1].strip())
        natoms = int(lines[i + 3].strip())
        bounds = lines[i + 5 : i + 8]
        lattice, origin = _bounds_to_lattice(bounds)
        cols = lines[i + 8].split()[2:]
        col = {c: n for n, c in enumerate(cols)}
        for c in ["id", "type", "x", "y", "z"]:
            if c not in col:
                raise SystemExit(f"Missing ATOMS column: {c}")

        atom_rows = lines[i + 9 : i + 9 + natoms]
        ox, oy, oz = origin
        atoms = []
        for row in atom_rows:
            f = row.split()
            aid = int(f[col["id"]])
            typ = int(f[col["type"]])
            x = float(f[col["x"]]) - ox
            y = float(f[col["y"]]) - oy
            z = float(f[col["z"]]) - oz
            atoms.append((aid, typ, x, y, z))
        atoms.sort(key=lambda t: t[0])

        flat = [*lattice[0], *lattice[1], *lattice[2]]
        lstr = " ".join(f"{v:.16g}" for v in flat)
        out.append(str(natoms))
        out.append(f'Lattice="{lstr}" Properties=species:S:1:pos:R:3 Time={step} pbc="T T T"')
        for _, typ, x, y, z in atoms:
            if typ not in id_to_sym:
                raise SystemExit(f"Unknown type id {typ}")
            out.append(f"{id_to_sym[typ]} {x:.16g} {y:.16g} {z:.16g}")

        i += 9 + natoms

    if not out:
        raise SystemExit("No frame parsed from dump")
    Path(args.out_extxyz).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote {args.out_extxyz}")


if __name__ == "__main__":
    main()

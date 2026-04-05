# LAMMPS bridge tools (extxyz-first)

These scripts provide an external bridge between TDEP and LAMMPS while
prioritizing **extxyz** as the intermediate format.

## Scripts

- `convert_tdep_extxyz_to_lammps.py`
  - extxyz -> LAMMPS `data` file
  - also writes `type_map.json` for reverse conversion
- `convert_lammps_dump_to_extxyz.py`
  - LAMMPS dump (`lammpstrj`) -> extxyz trajectory
- `validate_extxyz_bridge.py`
  - checks atom count/order and optional strict lattice consistency

## Quick start

```bash
python tools/lammps_bridge/validate_extxyz_bridge.py \
  --in-extxyz infile.ssposcar.xyz --strict-lattice

python tools/lammps_bridge/convert_tdep_extxyz_to_lammps.py \
  --in-extxyz infile.ssposcar.xyz \
  --out-data lammps.data \
  --frame 0 \
  --type-map-out type_map.json

python tools/lammps_bridge/convert_lammps_dump_to_extxyz.py \
  --in-dump dump.lammpstrj \
  --type-map type_map.json \
  --out-extxyz md.extxyz
```

## Notes

- extxyz -> LAMMPS currently expects prism-compatible lattice orientation
  (`a=(ax,0,0), b=(xy,by,0), c=(xz,yz,cz)`).
- dump parser currently requires columns: `id type x y z`.

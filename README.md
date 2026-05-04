# magnetron-mode--dark-photon
parameter space for DPDM detected by penning trap magnetron modes.

## Files

- `units.py`: natural-unit conversion factors.
- `parameter_relations.py`: symbolic list of parameter relations.
- `sensitivity_calculator.py`: command-line calculator for minimum detectable epsilon.
- `sensitivity_slider.html`: browser slider UI for visual tuning.

## Run the command-line calculator

Default point:

```bash
python3 sensitivity_calculator.py
```

Example with custom parameters:

```bash
python3 sensitivity_calculator.py \
  --omega-m 0.1 --omega-m-unit neV \
  --omega-c 0.1 --omega-c-unit meV \
  --t-ave 1e-6 --t-ave-unit sec \
  --t-obs 6 --t-obs-unit sec
```

If `--omega-z` is supplied, the code keeps resonance and computes `omega_c`.
Otherwise it uses `omega_c` and computes `omega_z`.

Interactive mode:

```bash
python3 sensitivity_calculator.py --interactive
```

Then use commands like:

```text
wm 0.2 neV
wc 0.5 meV
wz 2e-7 eV
tave 1e-6 sec
tobs 6 sec
show
quit
```

## Run the slider UI

Start a local static server from this directory:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/sensitivity_slider.html
```

The slider UI lets you tune `omega_m`, `omega_c`, `omega_z`, `R`, `t_ave`,
and `t_obs`. It shows the current point and the mass-scan curve in the
`omega_m`-`epsilon_min` plane.

## Check the relation table

```bash
python3 parameter_relations.py
```

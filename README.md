# auto_gjf

Utilities for generating Gaussian input (`.gjf`) files from existing Gaussian inputs, Gaussian log files, or XYZ coordinate files.

## Files

- `gjf2gjf.py`: rebuild a `.gjf` file with a new task type, functional, and basis set while preserving coordinates and checkpoint-related settings.
- `log2gjf.py`: extract coordinates from a Gaussian `.log` file and write a new `.gjf` file.
- `xyz2gjf.py`: convert an `.xyz` file into a `.gjf` file.
- `common_gjf.py`: shared task definitions, functional definitions, argument handling, and GJF writer logic.

## Requirements

- Python 3.10+
- `periodictable` for `log2gjf.py`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Convert XYZ to GJF

```bash
python xyz2gjf.py molecule.xyz -task opt
```

The input file can be passed either as `molecule.xyz` or `molecule`.

Example with explicit settings:

```bash
python xyz2gjf.py molecule.xyz -task freq -func B3BJ -basis def2TZVP -cs "0 1"
```

### 2. Convert Gaussian log to GJF

```bash
python log2gjf.py job.log -task opt
```

### 3. Regenerate GJF from an existing GJF

```bash
python gjf2gjf.py input.gjf -task freq
```

If the selected task requires `%oldchk`, pass it explicitly:

```bash
python gjf2gjf.py input.gjf -task optchk -old previous_job
```

## Common Arguments

- `-task`: calculation task, such as `opt`, `freq`, `TS`, `IRC`
- `-func`: functional shortcut, default is `B3BJ`
- `-basis`: basis set, default is `def2SVP`
- `-nproc`: number of cores, default is `96`
- `-mem`: memory string, default is `400GB`
- `-out`: output file name
- `-old`: base name used to build `%oldchk=...`
- `-cs`: charge and spin multiplicity, for example `"0 1"`
- `-add`: additional keywords appended to the route section
- `-end`: additional input in the end of the file, eg geometric constraints or orbital swapping requirement

## Notes

- Generated `.gjf`, `.chk`, `.log`, and `.xyz` files are ignored by Git in this repository.
- Some defaults in these scripts are tuned for a high-resource environment (`96` cores and `400GB` memory). Adjust them for your machine or cluster before running jobs.

## License

This project is released under the MIT License. See `LICENSE` for details.

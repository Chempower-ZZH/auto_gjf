# auto_gjf

`auto_gjf` is a small toolkit for creating and rewriting Gaussian input files (`.gjf`). It can generate new Gaussian input files from existing `.gjf` files, Gaussian `.log` files, or `.xyz` coordinate files, and it provides predefined task templates and functional shortcuts for common computational workflows.

## Download

Clone the repository from GitHub:

```bash
git clone https://github.com/Chempower-ZZH/auto_gjf.git
cd auto_gjf
```

Install the Python dependency:

```bash
pip install -r requirements.txt
```

The dependency list is intentionally small. `log2gjf.py` uses `periodictable` to convert atomic numbers from Gaussian log files into element symbols.

## Files

| File | Purpose |
| --- | --- |
| `gjf2gjf.py` | Rebuild a `.gjf` file from an existing `.gjf`, preserving coordinates and charge/spin while replacing the task, functional, basis set, and related keywords |
| `xyz2gjf.py` | Convert an `.xyz` coordinate file into a `.gjf` file |
| `log2gjf.py` | Extract coordinates from a Gaussian `.log` file and write a new `.gjf` file |
| `common_gjf.py` | Shared task templates, functional shortcuts, argument definitions, and GJF read/write logic |
| `requirements.txt` | Python dependencies |

## Basic Usage

All scripts can be called directly with `python`. The examples below assume you are already inside the `auto_gjf` directory.

### Convert XYZ to GJF

```bash
python xyz2gjf.py molecule.xyz -task opt
```

The input file may be passed with or without the `.xyz` suffix:

```bash
python xyz2gjf.py molecule -task freq -func B3BJ -basis def2TZVP -cs "0 1"
```

### Convert Gaussian Log to GJF

```bash
python log2gjf.py job.log -task opt -func B3BJ -basis def2SVP
```

`log2gjf.py` first tries to read coordinates from the `Standard orientation` block. If that block is unavailable, it falls back to the older coordinate format after `Normal termination`.

### Rewrite an Existing GJF

```bash
python gjf2gjf.py input.gjf -task freq -func B3BJ -basis def2SVP
```

If the input name is given without the `.gjf` suffix, the script adds it automatically:

```bash
python gjf2gjf.py input -task opt
```

### Use `%oldchk`

Some tasks read geometry, basis, or wavefunction information from a checkpoint file. Examples include `optchk`, `TSchk`, `IRC`, and `spechk`. For these tasks, explicitly pass `-old`:

```bash
python gjf2gjf.py input.gjf -task spechk -old input -out input-spe.gjf
```

This writes the following line to the output file:

```text
%oldchk=input.chk
```

`-old` supports name tokens:

| Token | Meaning |
| --- | --- |
| `$infile` | Input file name without path or suffix |
| `$task` | Current task name |
| `$func` | Current functional shortcut |
| `$basis` | Current basis set |

Example:

```bash
python gjf2gjf.py mol.gjf -task spechk -old "$infile-$func" -func w
```

### Output File Names

If `-out` is omitted, the output name defaults to the input base name with a `.gjf` suffix. In day-to-day use, it is safer to specify `-out` explicitly to avoid overwriting files:

```bash
python gjf2gjf.py mol.gjf -task freq -out mol-freq.gjf
```

`-out` supports the same `$infile`, `$task`, `$func`, and `$basis` tokens:

```bash
python gjf2gjf.py mol.gjf -task opt -func CAM -basis def2TZVP -out "$infile-$task-$func.gjf"
```

### Add Extra Gaussian Keywords

Use `-add` to append extra keywords to the route section:

```bash
python gjf2gjf.py mol.gjf -task spechk -old mol -add "scrf=(SMD,solvent=Dichloromethane)"
```

Example for a TDDFT single-point input:

```bash
python gjf2gjf.py mol.gjf -task spechk -old mol -func w -basis def2tzvp -add "td=(nstates=50)"
```

### Append Extra Text at the End

Use `-end` to append text at the end of the generated `.gjf` file. This is useful for constraints, GIC scan definitions, NBO input, orbital alteration instructions, and similar Gaussian sections:

```bash
python xyz2gjf.py mol.xyz -task scan -end "B 1 2 S 20 1.800000"
```

### Common Arguments

| Argument | Description | Default |
| --- | --- | --- |
| `-task` | Calculation task template. Must be one of the keys in `TASK_TYPES` from `common_gjf.py` | Required |
| `-func` | Functional shortcut. Must be one of the keys in `FUNCTIONALS` from `common_gjf.py` | `B3BJ` |
| `-basis` | Basis set | `def2SVP` |
| `-nproc` | Value for `%nprocshared` | `96` |
| `-mem` | Value for `%mem` | `400GB` |
| `-out` | Output `.gjf` file name | Same as input base name |
| `-old` | Base name for `%oldchk`; do not include `.chk` | None |
| `-cs` | Charge and spin multiplicity, for example `"0 1"` | `gjf2gjf.py` reads it from the input file; other scripts use their defaults |
| `-add` | Extra keywords appended to the route section | Empty |
| `-end` | Extra text appended at the end of the `.gjf` file | Empty |

## Recommended Setup

The recommended workflow is to add aliases or wrapper functions to `~/.bashrc`, and to keep a `methods.sh` file in each computational project directory. This keeps daily commands short and makes the computational settings for each project explicit and reproducible.

### Add Aliases

Add the following lines to `~/.bashrc`. Adjust `AUTO_GJF_HOME` to match your installation path:

```bash
export AUTO_GJF_HOME="/mnt/d/4-Area/Python/tools/Coordinate-Manipulating/auto_gjf"

alias gjf2gjf='python "$AUTO_GJF_HOME/gjf2gjf.py"'
alias xyz2gjf='python "$AUTO_GJF_HOME/xyz2gjf.py"'
alias log2gjf='python "$AUTO_GJF_HOME/log2gjf.py"'
```

Reload your shell configuration:

```bash
source ~/.bashrc
```

Then the scripts can be called from any working directory:

```bash
gjf2gjf mol.gjf -task freq
xyz2gjf mol.xyz -task opt
log2gjf mol.log -task opt
```

### Create a `methods.sh` for Each Project

For each computational project, prepare a local `methods.sh` file:

```bash
func=B3BJ
basis=def2SVP
sfunc=w
solvent=Dichloromethane
```

Suggested meaning of these variables:

| Variable | Recommended use |
| --- | --- |
| `func` | Functional shortcut for main calculations such as optimization, frequency, TS, and IRC jobs |
| `basis` | Basis set for the main calculations |
| `sfunc` | Functional shortcut for follow-up calculations such as single-point, solvent, and TDDFT jobs |
| `solvent` | Solvent name used by SMD or PCM jobs |

### Add `methods.sh`-Aware Wrappers

The following `gg` and `xg` functions read `methods.sh` from the current directory and automatically pass `func` and `basis` to `gjf2gjf` or `xyz2gjf`:

```bash
gg() {
    if [[ ! -r ./methods.sh ]]; then
        echo "Error: ./methods.sh is missing or not readable."
        return 1
    fi

    (
        source ./methods.sh
        gjf2gjf "$@" -func "$func" -basis "$basis"
    )
}

xg() {
    if [[ ! -r ./methods.sh ]]; then
        echo "Error: ./methods.sh is missing or not readable."
        return 1
    fi

    (
        source ./methods.sh
        xyz2gjf "$@" -func "$func" -basis "$basis"
    )
}
```

Examples:

```bash
xg mol.xyz -task opt -out mol-opt.gjf
gg mol-opt.gjf -task freq -out mol-freq.gjf
```

These commands automatically append:

```bash
-func "$func" -basis "$basis"
```

### Additional Shortcut Functions

The following examples are based on the author's personal `~/.bashrc` workflow and are useful for common follow-up calculations.

#### IRC

```bash
IRC() {
    base="${1##*/}"
    func="${base##*-}"
    func="${func%%.gjf}"
    out_file="${base%TS*}TS-IRC${base##*TS}"
    gjf2gjf "$1" -out "${out_file}.gjf" -task IRC -old "$1" -func "$func"
}

IRCR() {
    base="${1##*/}"
    func="${base##*-}"
    func="${func%%.gjf}"
    out_file="${base%TS*}TS-IRCR${base##*TS}"
    gjf2gjf "$1" -out "${out_file}.gjf" -task IRCR -old "$1" -func "$func"
}

IRCF() {
    base="${1##*/}"
    func="${base##*-}"
    func="${func%%.gjf}"
    out_file="${base%TS*}TS-IRCF${base##*TS}"
    gjf2gjf "$1" -out "${out_file}.gjf" -task IRCF -old "$1" -func "$func"
}
```

Examples:

```bash
IRC TS-example-B3BJ.gjf
IRCR TS-example-B3BJ.gjf
IRCF TS-example-B3BJ.gjf
```

#### SMD and PCM Single-Point Jobs

```bash
SMD() {
    base="${1##*/}"
    default_func="${base##*-}"
    default_func="${default_func%%.gjf}"
    func="${3:-$default_func}"
    solvent="${2:-Dichloromethane}"

    if [ -z "$3" ]; then
        output_file="${1%.gjf}-S.gjf"
    else
        output_file="${1%.gjf}-$3-S.gjf"
    fi

    gjf2gjf "$1" \
        -out "$output_file" \
        -task spechk \
        -old "${1%.gjf}" \
        -add "scrf=(SMD,solvent=$solvent)" \
        -basis def2tzvp \
        -func "$func"
}

PCM() {
    base="${1##*/}"
    default_func="${base##*-}"
    default_func="${default_func%%.gjf}"
    func="${3:-$default_func}"

    if [ -z "$3" ]; then
        output_file="${1%.gjf}-P.gjf"
    else
        output_file="${1%.gjf}-$3-P.gjf"
    fi

    gjf2gjf "$1" \
        -out "$output_file" \
        -task spechk \
        -old "${1%.gjf}" \
        -add "scrf=(PCM,solvent=$2)" \
        -basis def2tzvp \
        -func "$func"
}
```

Examples:

```bash
SMD mol-B3BJ.gjf Dichloromethane
SMD mol-B3BJ.gjf Toluene w
PCM mol-B3BJ.gjf Dichloromethane
```

If you use `methods.sh`, you can add one more wrapper layer:

```bash
SMD1() {
    if [[ ! -r ./methods.sh ]]; then
        echo "Error: methods.sh is missing or not readable in the current directory."
        return 1
    fi

    source ./methods.sh
    SMD "$1" "$solvent" "$sfunc"
}

PCM1() {
    if [[ ! -r ./methods.sh ]]; then
        echo "Error: methods.sh is missing or not readable in the current directory."
        return 1
    fi

    source ./methods.sh
    PCM "$1" "$solvent" "$sfunc"
}
```

#### TS and TDDFT

```bash
TS() {
    base="${1##*/}"
    func="${base##*-}"
    func="${func%%.gjf}"
    out_file="${base%fix*}fix-TS${base##*fix}"
    gjf2gjf "$1" \
        -out "${out_file%.gjf}.gjf" \
        -task TSchk \
        -old "${1%.gjf}" \
        -func "$func"
}

TD() {
    gjf2gjf "$1.gjf" -out "TD-${1}-w.gjf" -task spechk -old "$1" -add "td=(nstates=50)" -func w -basis def2tzvp
}

TDS() {
    gjf2gjf "$1.gjf" -out "TD-${1}-w-S.gjf" -task spechk -old "$1" -add "td=(nstates=50) SCRF=(SMD,solvent=$2)" -func w -basis def2tzvp
}

TDC() {
    gjf2gjf "$1.gjf" -out "TD-${1}-CAM.gjf" -task spechk -old "$1" -add "td=(nstates=50)" -func CAM -basis def2tzvp
}

TDCS() {
    gjf2gjf "$1.gjf" -out "TD-${1}-CAM-S.gjf" -task spechk -old "$1" -add "td=(nstates=50) SCRF=(SMD,solvent=$2)" -func CAM -basis def2tzvp
}
```

Examples:

```bash
TS mol-fix-B3BJ.gjf
TD mol
TDS mol Dichloromethane
TDC mol
TDCS mol Dichloromethane
```

## Functional Shortcuts

The `-func` argument must use one of the shortcuts defined in `FUNCTIONALS` in `common_gjf.py`.

| Shortcut | Gaussian keyword |
| --- | --- |
| `B3` | `B3LYP` |
| `B3D3` | `B3LYP em=GD3` |
| `B3BJ` | `B3LYP em=GD3BJ` |
| `CAM` | `CAM-B3LYP` |
| `w` | `wB97XD` |
| `TPh` | `TPSSh` |
| `TPhD3` | `TPSSh em=GD3BJ IOp(3/174=1000000,3/175=2238200,3/177=452900,3/178=4655000)` |
| `TPD3` | `TPSSTPSS em=GD3BJ` |
| `PBE0` | `PBE1PBE` |
| `PBE0D3` | `PBE1PBE em=GD3BJ` |
| `M06` | `M06` |
| `M06L` | `M06L` |
| `M062X` | `M062X` |
| `MN15` | `MN15` |
| `MN15L` | `MN15L` |

## Available Tasks

The `-task` argument must use one of the task templates defined in `TASK_TYPES` in `common_gjf.py`.

| Task | Route section template |
| --- | --- |
| `fix` | `#p opt=(addred,loose) freq nosymm pop=NPA int=ultrafine` |
| `fixchk` | `#p opt=(addred,loose) freq nosymm pop=NPA int=ultrafine guess=read chkbas geom=check` |
| `fixread` | `#p opt=(addred,loose) freq nosymm pop=NPA int=ultrafine guess=read chkbas` |
| `freq` | `#p freq nosymm pop=NPA int=ultrafine` |
| `freqchk` | `#p freq nosymm pop=NPA int=ultrafine guess=read chkbas geom=check` |
| `freqread` | `#p freq nosymm pop=NPA int=ultrafine guess=read chkbas` |
| `addTS` | `#p opt=(calcfc,ts,noeigen,maxstep=5,addred) freq pop=nboread int=ultrafine symm=follow` |
| `TS` | `#p opt=(calcfc,ts,noeigen,maxstep=5) freq pop=nboread int=ultrafine` |
| `TSchk` | `#p chkbasis opt=(readfc,ts,noeigen,nofreeze,maxstep=5) freq pop=nboread guess=read nosymm geom=allcheck int=ultrafine` |
| `IRC` | `#p chkbasis geom=allcheck guess=read IRC=(maxpoint=30,CALCFC) nosymm int=ultrafine pop=(npa,always)` |
| `IRCR` | `#p chkbasis geom=allcheck guess=read IRC=(maxpoint=30,CALCFC,reverse) nosymm int=ultrafine pop=(npa,always)` |
| `IRCF` | `#p chkbasis geom=allcheck guess=read IRC=(maxpoint=30,CALCFC,forward) nosymm int=ultrafine pop=(npa,always)` |
| `opt` | `#p opt freq pop=nboread nosymm int=ultrafine` |
| `optread` | `#p opt freq pop=nboread nosymm int=ultrafine guess=read chkbas` |
| `optchk` | `#p chkbasis opt freq pop=nboread guess=read nosymm int=ultrafine geom=check` |
| `gicscan` | `#p opt=(addgic,loose) nosymm pop=(npa,always)` |
| `gicscanchk` | `#p opt=(addgic,loose) nosymm pop=(npa,always) geom=check guess=read` |
| `scan` | `#p opt=(addred,loose) nosymm pop=(npa,always)` |
| `scanchk` | `#p opt=(addred,loose) nosymm chkbasis guess=read geom=check pop=(npa,always)` |
| `spe` | `#p pop=(NPA,orbitals,ThreshOrbitals=5)` |
| `spe-nbo` | `#p pop=nboread nosymm` |
| `speread` | `#p pop=(NPA,orbitals,ThreshOrbitals=5) guess=read` |
| `spechk` | `#p pop=(NPA,orbitals,ThreshOrbitals=5) geom=allcheck guess=read` |
| `mix` | `#p pop=NPA geom=chk guess=(read,mix) chkbas` |
| `mixread` | `#p pop=NPA guess=(read,mix) chkbas` |
| `alt` | `#p pop=NPA geom=chk guess=(read,alter) chkbas` |
| `stable` | `#p pop=NPA geom=chk chkbas stable=opt` |

## Notes

- The default resource settings are `%nprocshared=96` and `%mem=400GB`. They are intended for a high-resource environment. Adjust `-nproc` and `-mem` before submitting jobs on a different machine or cluster.
- Tasks containing `geom=check`, `geom=allcheck`, or `guess=read` usually require `%oldchk`. Passing `-old` explicitly is recommended, especially for batch workflows.
- `gjf2gjf.py` reads coordinates and charge/spin from the input `.gjf`; `xyz2gjf.py` writes `0 1` when charge/spin is not provided; `log2gjf.py` defaults to `0 1`.
- Generated `.gjf`, `.chk`, `.log`, and `.xyz` calculation files are usually not meant to be committed. The current `.gitignore` ignores these file types.

## License

This project is released under the MIT License. See `LICENSE` for details.

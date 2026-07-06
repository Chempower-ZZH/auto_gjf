import os
import argparse

TASK_TYPES = {
    "fix": "#p opt=(addred,loose) freq nosymm pop=NPA int=ultrafine",
    "fixchk": "#p opt=(addred,loose) freq nosymm pop=NPA int=ultrafine guess=read chkbas geom=check",
    "fixread": "#p opt=(addred,loose) freq nosymm pop=NPA int=ultrafine guess=read chkbas",
    "freq": "#p freq nosymm pop=NPA int=ultrafine",
    "freqchk": "#p freq nosymm pop=NPA int=ultrafine guess=read chkbas geom=check",
    "freqread": "#p freq nosymm pop=NPA int=ultrafine guess=read chkbas",
    "addTS": "#p opt=(calcfc,ts,noeigen,maxstep=5,addred) freq pop=nboread int=ultrafine symm=follow",
    "TS": "#p opt=(calcfc,ts,noeigen,maxstep=5) freq pop=nboread int=ultrafine",
    "TSchk": "#p chkbasis opt=(readfc,ts,noeigen,nofreeze,maxstep=5) freq pop=nboread guess=read nosymm geom=allcheck int=ultrafine",
    "IRC": "#p chkbasis geom=allcheck guess=read IRC=(maxpoint=30,CALCFC) nosymm int=ultrafine pop=(npa,always)",
    "IRCR": "#p chkbasis geom=allcheck guess=read IRC=(maxpoint=30,CALCFC,reverse) nosymm int=ultrafine pop=(npa,always)",
    "IRCF": "#p chkbasis geom=allcheck guess=read IRC=(maxpoint=30,CALCFC,forward) nosymm int=ultrafine pop=(npa,always)",
    "opt": "#p opt freq pop=nboread nosymm int=ultrafine",
    "optread": "#p opt freq pop=nboread nosymm int=ultrafine guess=read chkbas",
    "optchk": "#p chkbasis opt freq pop=nboread guess=read nosymm int=ultrafine geom=check",
    "gicscan": "#p opt=(addgic,loose) nosymm pop=(npa,always)",
    "gicscanchk": "#p opt=(addgic,loose) nosymm pop=(npa,always) geom=check guess=read",
    "scan": "#p opt=(addred,loose) nosymm pop=(npa,always)",
    "scanchk": "#p opt=(addred,loose) nosymm chkbasis guess=read geom=check pop=(npa,always)",
    "spe": "#p pop=(NPA,orbitals,ThreshOrbitals=5)",
    "spe-nbo": "#p pop=nboread nosymm",
    "speread": "#p pop=(NPA,orbitals,ThreshOrbitals=5) guess=read",
    "spechk": "#p pop=(NPA,orbitals,ThreshOrbitals=5) geom=allcheck guess=read",
    "mix": "#p pop=NPA geom=chk guess=(read,mix) chkbas",
    "mixread": "#p pop=NPA guess=(read,mix) chkbas",
    "alt": "#p pop=NPA geom=chk guess=(read,alter) chkbas",
    "stable": "#p pop=NPA geom=chk chkbas stable=opt",
}

FUNCTIONALS = {
    "B3": "B3LYP",
    "B3D3": "B3LYP em=GD3",
    "B3BJ": "B3LYP em=GD3BJ",
    "CAM": "CAM-B3LYP",
    "w": "wB97XD",
    "TPh": "TPSSh",
    "TPhD3": "TPSSh em=GD3BJ IOp(3/174=1000000,3/175=2238200,3/177=452900,3/178=4655000)",
    "TPD3": "TPSSTPSS em=GD3BJ",
    "PBE0": "PBE1PBE",
    "PBE0D3": "PBE1PBE em=GD3BJ",
    "M06": "M06",
    "M06L": "M06L",
    "M062X": "M062X",
    "MN15": "MN15",
    "MN15L": "MN15L",
}

OLDCHK_KEYWORDS = (
    "geom=chk",
    "geom=check",
    "geom=allchk",
    "geom=allcheck",
    "guess=read",
    "guess=(read",
)

GEOM_CHECK_KEYWORDS = ("geom=chk", "geom=check", "geom=allchk", "geom=allcheck")


def ensure_gjf_suffix(filename):
    if filename.lower().endswith(".gjf"):
        return filename
    return f"{filename}.gjf"


def ensure_file_suffix(filename, suffix):
    if filename.lower().endswith(suffix.lower()):
        return filename
    return f"{filename}{suffix}"


def apply_name_tokens(value, infile_base, task, func, basis):
    return (
        value.replace("$func", func)
        .replace("$task", task)
        .replace("$basis", basis)
        .replace("$infile", infile_base)
    )


def resolve_output_file(input_file, output_arg, task, func, basis):
    infile_base = os.path.splitext(os.path.basename(input_file))[0]
    output_file = output_arg if output_arg else infile_base
    output_file = ensure_gjf_suffix(output_file)
    return apply_name_tokens(output_file, infile_base, task, func, basis)


def prepare_gjf_job(input_file, output_arg, task, func, basis, add_arg, old_arg, cs_arg):
    infile_base = os.path.splitext(os.path.basename(input_file))[0]
    output_file = resolve_output_file(input_file, output_arg, task, func, basis)
    task_type = TASK_TYPES[task]
    if add_arg:
        task_type += " " + add_arg
    functional = FUNCTIONALS[func]
    oldchk_line = build_oldchk_line(old_arg, infile_base, task, func, basis)
    oldchk_line = prompt_for_oldchk(task_type, oldchk_line)
    charge_and_spin = cs_arg if cs_arg else "0 1"
    return output_file, task_type, functional, oldchk_line, charge_and_spin


def add_gjf_output_args(
    parser,
    *,
    require_task=True,
    default_func="B3BJ",
    default_basis="def2SVP",
    default_nproc=96,
    default_mem="400GB",
    default_cs=None,
    include_add=True,
    include_end=True,
):
    parser.add_argument(
        "-out", type=str, default=None,
        help="Output GJF file name (default: same as input file name)"
    )
    parser.add_argument(
        "-task", type=str, choices=TASK_TYPES.keys(), required=require_task,
        help="Task type for the calculation"
    )
    parser.add_argument(
        "-func", type=str, choices=FUNCTIONALS.keys(), default=default_func,
        help="Functional for the calculation (default: B3LYP em=GD3BJ)"
    )
    parser.add_argument(
        "-basis", type=str, default=default_basis,
        help=f"Basis set for the calculation (default: {default_basis})"
    )
    parser.add_argument(
        "-nproc", type=int, default=default_nproc,
        help=f"Number of processors to use (default: {default_nproc})"
    )
    parser.add_argument(
        "-mem", type=str, default=default_mem,
        help=f"Memory to use (default: {default_mem})"
    )
    if include_add:
        parser.add_argument(
            "-add", type=str, default="",
            help="Additional keywords to add to the task line (default: None)"
        )
    if include_end:
        parser.add_argument(
            "-end", type=str, default="",
            help="Text to append at the end of the GJF file (default: None)"
        )
    parser.add_argument(
        "-old", type=str, default=None,
        help="Specify the base name for %oldchk (default: None)"
    )
    parser.add_argument(
        "-cs", type=str, default=default_cs,
        help=(
            f"Specify the charge and spin multiplicity (default: {default_cs})"
            if default_cs is not None
            else "Specify the charge and spin multiplicity (default: None)"
        )
    )
    return parser


def needs_oldchk(task_type):
    return any(keyword in task_type for keyword in OLDCHK_KEYWORDS)


def uses_allcheck_geometry(task_type):
    return "geom=allchk" in task_type or "geom=allcheck" in task_type


def uses_checkpoint_geometry(task_type):
    return any(keyword in task_type for keyword in GEOM_CHECK_KEYWORDS)


def build_oldchk_line(old_value, infile_base, task, func, basis):
    if not old_value:
        return None
    resolved = apply_name_tokens(old_value, infile_base, task, func, basis)
    return f"%oldchk={resolved}.chk"


def prompt_for_oldchk(task_type, oldchk_line):
    if needs_oldchk(task_type) and oldchk_line is None:
        oldchk_filename = input(
            "Please enter the %oldchk file base name (e.g., 'example'): "
        )
        return f"%oldchk={oldchk_filename}.chk"
    return oldchk_line


def read_xyz(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    num_atoms = int(lines[0].strip())
    atoms = []
    for line in lines[2:2 + num_atoms]:
        parts = line.split()
        atoms.append((parts[0], float(parts[1]), float(parts[2]), float(parts[3])))
    return lines[1].strip(), atoms


def read_gjf(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    oldchk_line = None
    chk_index = None
    for index, line in enumerate(lines):
        if line.startswith("%chk"):
            chk_index = index
        if line.startswith("%oldchk"):
            oldchk_line = line.strip()

    charge_and_spin = "0 1"
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 2 and parts[0].lstrip("-").isdigit() and parts[1].isdigit():
            charge_and_spin = f"{parts[0]} {parts[1]}"
            break

    atoms = []
    coordinates_start = False
    for line in lines:
        if line.strip() == charge_and_spin:
            coordinates_start = True
            continue
        if not coordinates_start:
            continue
        parts = line.split()
        if len(parts) != 4:
            break
        try:
            atoms.append((parts[0], float(parts[1]), float(parts[2]), float(parts[3])))
        except ValueError:
            continue

    return oldchk_line, atoms, chk_index, charge_and_spin, lines


def write_gjf(
    filename,
    oldchk_line,
    atoms,
    task_type,
    functional,
    basis_set,
    nproc,
    mem,
    chk_index,
    charge_and_spin,
    lines,
    end_text,
):
    del chk_index, lines

    with open(filename, "w") as file:
        file.write(f"%nprocshared={nproc}\n")
        file.write(f"%mem={mem}\n")

        if needs_oldchk(task_type) and oldchk_line:
            file.write(oldchk_line + "\n")

        file.write(f"%chk={os.path.splitext(filename)[0]}.chk\n")

        if not any(keyword in task_type for keyword in ("chkbas", "chkbasis")):
            file.write(f"{task_type} {functional} {basis_set}\n\n")
        elif any(keyword in task_type for keyword in ("mix", "alter", "stable")):
            file.write(f"{task_type} U{functional}\n\n")
        else:
            file.write(f"{task_type} {functional}\n\n")

        file.write("title\n\n")

        if not uses_allcheck_geometry(task_type):
            file.write(f"{charge_and_spin}\n")

        if not uses_checkpoint_geometry(task_type):
            for atom in atoms:
                file.write(
                    f" {atom[0]:<4} {atom[1]:>12.6f} {atom[2]:>12.6f} {atom[3]:>12.6f}\n"
                )

        if task_type != "scanchk":
            file.write("\n")

        if end_text:
            file.write(end_text.replace("\\", "\n") + "\n")
            file.write("\n")

        if "pop=nboread" in task_type:
            gjf_base_name = os.path.splitext(filename)[0]
            file.write(f"$nbo archive file={gjf_base_name} bndidx $end\n")


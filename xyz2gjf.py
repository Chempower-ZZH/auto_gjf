import argparse
from common_gjf import (
    add_gjf_output_args,
    ensure_file_suffix,
    prepare_gjf_job,
    read_xyz,
    write_gjf,
)


def main():
    parser = argparse.ArgumentParser(
        description="Convert XYZ file to GJF file with specified task types, functionals, and basis sets."
    )

    parser.add_argument("xyz_file", help="Input XYZ file")
    add_gjf_output_args(parser, default_cs=None)

    args = parser.parse_args()
    args.xyz_file = ensure_file_suffix(args.xyz_file, ".xyz")

    _comment, atoms = read_xyz(args.xyz_file)
    output_file, task_type, functional, oldchk_line, charge_and_spin = prepare_gjf_job(
        args.xyz_file, args.out, args.task, args.func, args.basis, args.add, args.old, args.cs
    )

    # 写入 GJF 文件
    write_gjf(
        output_file, oldchk_line, atoms, task_type, functional, args.basis,
        args.nproc, args.mem, None, charge_and_spin, [], args.end
    )

    print(f"GJF file '{output_file}' has been created.")


if __name__ == "__main__":
    main()

import argparse
import os
import re
import sys
import periodictable
from common_gjf import (
    FUNCTIONALS,
    TASK_TYPES,
    add_gjf_output_args,
    prepare_gjf_job,
    write_gjf,
)


def extract_coordinates(log_content):
    std_orient_pattern = re.compile(
        r'\s*\d+\s+(\d+)\s+\d+\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)')
    old_coord_pattern = re.compile(
        r'([A-Za-z]+),0,([-\d.]+),([-\d.]+),([-\d.]+)')

    std_orient_index = log_content.find("Standard orientation")
    if std_orient_index != -1:
        content_below_std_orient = log_content[std_orient_index:]
        std_orient_block = content_below_std_orient.split(
            '---------------------------------------------------------------------')[2]
        matches = std_orient_pattern.findall(std_orient_block)
        coordinates = []
        for match in matches:
            atomic_number = int(match[0])
            element_symbol = periodictable.elements[atomic_number].symbol
            x, y, z = float(match[1]), float(match[2]), float(match[3])
            coordinates.append((element_symbol, x, y, z))
        return coordinates

    normal_termination_index = log_content.find("Normal termination")
    if normal_termination_index == -1:
        raise ValueError(
            "Neither 'Standard orientation' nor 'Normal termination' field found in the log file.")

    content_below_termination = log_content[normal_termination_index:]
    matches = old_coord_pattern.findall(content_below_termination)
    coordinates = [(match[0], float(match[1]), float(
        match[2]), float(match[3])) for match in matches]

    return coordinates


def main():
    parser = argparse.ArgumentParser(
        description="Convert Gaussian log files to GJF format.")
    parser.add_argument("log_file", help="Input Gaussian log file")
    add_gjf_output_args(parser, default_cs="0 1")

    args = parser.parse_args()

    with open(args.log_file, 'r') as f:
        log_content = f.read()

    try:
        coordinates = extract_coordinates(log_content)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_file, task_type, functional, oldchk_line, charge_and_spin = prepare_gjf_job(
        args.log_file, args.out, args.task, args.func, args.basis, args.add, args.old, args.cs
    )

    write_gjf(
        output_file,
        oldchk_line,
        coordinates,
        task_type,
        functional,
        args.basis,
        args.nproc,
        args.mem,
        None,
        charge_and_spin,
        [],
        args.end,
    )

    print(f"GJF file '{output_file}' has been created.")


if __name__ == "__main__":
    main()

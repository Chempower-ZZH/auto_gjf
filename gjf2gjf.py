import argparse
import os
from common_gjf import (
    FUNCTIONALS,
    TASK_TYPES,
    add_gjf_output_args,
    build_oldchk_line,
    ensure_gjf_suffix,
    prompt_for_oldchk,
    read_gjf,
    resolve_output_file,
    write_gjf,
)


def main():
    parser = argparse.ArgumentParser(
        description="Modify GJF file with new task types, functionals, and basis sets, "
                    "keeping original %oldchk and coordinates."
    )

    parser.add_argument("gjf_file", help="Input GJF file")
    add_gjf_output_args(parser, default_cs=None)

    args = parser.parse_args()

    # 检查输入文件名是否有后缀，如果没有则添加 .gjf
    args.gjf_file = ensure_gjf_suffix(args.gjf_file)

    # 获取输入文件名（去掉路径和后缀）
    infile_base = os.path.splitext(os.path.basename(args.gjf_file))[0]
    print("Input file base name (infile_base):", infile_base)  # 调试输出

    # 如果未提供输出文件名，则将其设为输入文件名
    output_file = resolve_output_file(
        args.gjf_file, args.out, args.task, args.func, args.basis
    )

    task_type = TASK_TYPES[args.task]
    functional = FUNCTIONALS[args.func]
    oldchk_line, atoms, chk_index, charge_and_spin, lines = read_gjf(
        args.gjf_file)

    # 确保 -old 参数优先覆盖 oldchk_line
    if args.old:
        oldchk_line = build_oldchk_line(
            args.old, infile_base, args.task, args.func, args.basis
        )
        print("Updated oldchk_line from -old argument:", oldchk_line)  # 调试输出
    else:
        print("Using oldchk_line from input file:", oldchk_line)  # 调试输出

    # 调试输出，确保最终传递的 oldchk_line 是正确的
    print("Final oldchk_line to be passed to write_gjf:", oldchk_line)

    # 如果任务类型需要 %oldchk 但 oldchk_line 为空，则提示用户输入
    oldchk_line = prompt_for_oldchk(task_type, oldchk_line)

    # 如果有附加关键字 (-add 选项)，将其添加到任务类型行
    if args.add:
        task_type += " " + args.add

    # 如果用户通过 -cs 指定了电荷和自旋多重度，则覆盖原来的值
    if args.cs:
        charge_and_spin = args.cs

    write_gjf(
        output_file, oldchk_line, atoms, task_type, functional, args.basis,
        args.nproc, args.mem, chk_index, charge_and_spin, lines, args.end
    )

    print(f"GJF file '{output_file}' has been created.")


# 运行主程序
if __name__ == "__main__":
    main()

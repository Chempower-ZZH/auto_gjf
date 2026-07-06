# auto_gjf

`auto_gjf` 用于批量生成和改写 Gaussian 输入文件 (`.gjf`)。它可以从已有 `.gjf`、Gaussian `.log` 或 `.xyz` 坐标文件生成新的 `.gjf`，并通过预设的 `task`、泛函缩写、基组、电荷自旋、溶剂模型等参数快速组织常见计算任务。

## 下载方式

从 GitHub 克隆项目：

```bash
git clone https://github.com/Chempower-ZZH/auto_gjf.git
cd auto_gjf
```

安装依赖：

```bash
pip install -r requirements.txt
```

目前依赖较少，`log2gjf.py` 需要 `periodictable` 用于根据原子序数恢复元素符号。

## 文件说明

| 文件 | 用途 |
| --- | --- |
| `gjf2gjf.py` | 从已有 `.gjf` 生成新的 `.gjf`，保留坐标、电荷自旋等信息，并按新 task/泛函/基组重写 route section |
| `xyz2gjf.py` | 从 `.xyz` 坐标文件生成 `.gjf` |
| `log2gjf.py` | 从 Gaussian `.log` 文件提取坐标并生成 `.gjf` |
| `common_gjf.py` | 存放通用参数、task 模板、泛函缩写、读写 `.gjf` 的公共逻辑 |
| `requirements.txt` | Python 依赖 |

## 常规使用方式

所有脚本都可以直接用 `python` 调用。下面示例假设你已经在 `auto_gjf` 目录中。

### 从 XYZ 生成 GJF

```bash
python xyz2gjf.py molecule.xyz -task opt
```

输入文件可以写完整后缀，也可以省略 `.xyz`：

```bash
python xyz2gjf.py molecule -task freq -func B3BJ -basis def2TZVP -cs "0 1"
```

### 从 Gaussian log 生成 GJF

```bash
python log2gjf.py job.log -task opt -func B3BJ -basis def2SVP
```

`log2gjf.py` 会优先读取 `Standard orientation` 坐标；如果没有该字段，会尝试从 `Normal termination` 后的旧式坐标格式读取。

### 从已有 GJF 改写 GJF

```bash
python gjf2gjf.py input.gjf -task freq -func B3BJ -basis def2SVP
```

如果输入文件名省略 `.gjf` 后缀，脚本会自动补齐：

```bash
python gjf2gjf.py input -task opt
```

### 使用 `%oldchk`

部分任务需要读取旧 checkpoint，例如 `optchk`、`TSchk`、`IRC`、`spechk` 等。推荐显式传入 `-old`：

```bash
python gjf2gjf.py input.gjf -task spechk -old input -out input-spe.gjf
```

会在输出文件中写入：

```text
%oldchk=input.chk
```

`-old` 支持变量替换：

| 变量 | 含义 |
| --- | --- |
| `$infile` | 输入文件去掉路径和后缀后的名称 |
| `$task` | 当前 task 名称 |
| `$func` | 当前泛函缩写 |
| `$basis` | 当前基组名称 |

示例：

```bash
python gjf2gjf.py mol.gjf -task spechk -old "$infile-$func" -func w
```

### 输出文件名

不指定 `-out` 时，默认输出文件名与输入文件同名，并自动补 `.gjf` 后缀。为了避免覆盖原文件，实际使用中建议显式指定 `-out`：

```bash
python gjf2gjf.py mol.gjf -task freq -out mol-freq.gjf
```

`-out` 同样支持 `$infile`、`$task`、`$func`、`$basis`：

```bash
python gjf2gjf.py mol.gjf -task opt -func CAM -basis def2TZVP -out "$infile-$task-$func.gjf"
```

### 添加额外关键词

使用 `-add` 可以在 route section 后追加额外 Gaussian 关键词：

```bash
python gjf2gjf.py mol.gjf -task spechk -old mol -add "scrf=(SMD,solvent=Dichloromethane)"
```

生成 TDDFT 单点的例子：

```bash
python gjf2gjf.py mol.gjf -task spechk -old mol -func w -basis def2tzvp -add "td=(nstates=50)"
```

### 在文件末尾追加内容

使用 `-end` 可以在 `.gjf` 末尾追加额外输入，例如约束、GIC 扫描定义、NBO 读取内容等：

```bash
python xyz2gjf.py mol.xyz -task scan -end "B 1 2 S 20 1.800000"
```

### 常用参数

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-task` | 计算任务模板，必须从 `common_gjf.py` 的 `TASK_TYPES` 中选择 | 必填 |
| `-func` | 泛函缩写，必须从 `common_gjf.py` 的 `FUNCTIONALS` 中选择 | `B3BJ` |
| `-basis` | 基组 | `def2SVP` |
| `-nproc` | `%nprocshared` 核数 | `96` |
| `-mem` | `%mem` 内存 | `400GB` |
| `-out` | 输出 `.gjf` 文件名 | 与输入同名 |
| `-old` | `%oldchk` 的基础文件名，不需要写 `.chk` | 无 |
| `-cs` | 电荷和自旋多重度，例如 `"0 1"` | `gjf2gjf.py` 读取原文件；其他脚本按默认值 |
| `-add` | 追加到 route section 的关键词 | 空 |
| `-end` | 追加到 `.gjf` 文件末尾的文本 | 空 |

## 推荐的使用设置

更推荐把脚本路径写入 `~/.bashrc`，并在每个计算项目目录中准备一个 `methods.sh`，这样日常命令可以更短，也能保证同一项目使用一致的泛函、基组和溶剂设置。

### 添加 alias

把下面内容加入 `~/.bashrc`。请按你的实际安装位置修改 `AUTO_GJF_HOME`：

```bash
export AUTO_GJF_HOME="/mnt/d/4-Area/Python/tools/Coordinate-Manipulating/auto_gjf"

alias gjf2gjf='python "$AUTO_GJF_HOME/gjf2gjf.py"'
alias xyz2gjf='python "$AUTO_GJF_HOME/xyz2gjf.py"'
alias log2gjf='python "$AUTO_GJF_HOME/log2gjf.py"'
```

使设置立即生效：

```bash
source ~/.bashrc
```

之后可以直接运行：

```bash
gjf2gjf mol.gjf -task freq
xyz2gjf mol.xyz -task opt
log2gjf mol.log -task opt
```

### 为每个项目准备 `methods.sh`

推荐每个计算项目目录都放一个 `methods.sh`，用于集中记录该项目采用的方法：

```bash
func=B3BJ
basis=def2SVP
sfunc=w
solvent=Dichloromethane
```

其中：

| 变量 | 推荐用途 |
| --- | --- |
| `func` | 结构优化、频率、TS、IRC 等主计算使用的泛函缩写 |
| `basis` | 主计算使用的基组 |
| `sfunc` | 单点、溶剂、TDDFT 等后续计算使用的泛函缩写 |
| `solvent` | SMD/PCM 使用的溶剂名称 |

### 添加基于 `methods.sh` 的快捷函数

下面的 `gg` 和 `xg` 会读取当前目录的 `methods.sh`，自动把 `func` 和 `basis` 传给 `gjf2gjf` 或 `xyz2gjf`：

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

使用示例：

```bash
xg mol.xyz -task opt -out mol-opt.gjf
gg mol-opt.gjf -task freq -out mol-freq.gjf
```

这相当于自动补上：

```bash
-func "$func" -basis "$basis"
```

### 推荐的快捷函数示例

下面这些函数参考了实际 `.bashrc` 中的用法，适合处理常见后续任务。

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

示例：

```bash
IRC TS-example-B3BJ.gjf
IRCR TS-example-B3BJ.gjf
IRCF TS-example-B3BJ.gjf
```

#### SMD/PCM 单点

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

示例：

```bash
SMD mol-B3BJ.gjf Dichloromethane
SMD mol-B3BJ.gjf Toluene w
PCM mol-B3BJ.gjf Dichloromethane
```

如果配合 `methods.sh`，还可以再包装一层：

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

#### TS 和 TDDFT

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

示例：

```bash
TS mol-fix-B3BJ.gjf
TD mol
TDS mol Dichloromethane
TDC mol
TDCS mol Dichloromethane
```

## 泛函缩写

`-func` 参数使用 `common_gjf.py` 中定义的缩写。当前包含：

| 缩写 | Gaussian 写法 |
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

## 已包含的 task

`-task` 参数使用 `common_gjf.py` 中定义的任务模板。当前包含：

| task | route section 模板 |
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

## 注意事项

- 默认资源设置是 `%nprocshared=96` 和 `%mem=400GB`，适合高资源环境。提交任务前请根据机器或集群实际情况调整 `-nproc` 和 `-mem`。
- 涉及 `geom=check`、`geom=allcheck`、`guess=read` 的 task 通常需要 `%oldchk`。建议总是显式传入 `-old`，避免交互式提示中断批处理。
- `gjf2gjf.py` 会读取原 `.gjf` 的坐标和电荷自旋；`xyz2gjf.py` 默认电荷自旋为空时会写为 `0 1`；`log2gjf.py` 默认也是 `0 1`。
- 生成的 `.gjf`、`.chk`、`.log`、`.xyz` 等计算文件通常不建议提交到 Git，当前 `.gitignore` 已忽略这些类型。

## License

This project is released under the MIT License. See `LICENSE` for details.

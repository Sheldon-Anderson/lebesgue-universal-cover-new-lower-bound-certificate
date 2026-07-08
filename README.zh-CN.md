# Lebesgue 万有覆盖问题认证下界证书

当前发布版本：`v0.15.4`。

本仓库提供随包发布的有限证书记录，以及用于复验这些记录的确定性 Python 验证程序。证书对应凸 Brass-Sharifi 三测试集框架下的精确十进制阈值 `0.833`。本仓库定位为证书复验包：它复验已经打包进仓库的有限记录，不重新运行原始几何搜索，也不从零生成证书归档。

## 1. 认证结论

本仓库验证归一化 Brass-Sharifi 三测试集下界问题中的阈值 $\tau=0.833$。结合 Brass-Sharifi 归一化原理，可得到凸万有覆盖问题中的证书结论：

```math
\alpha_{\mathrm{cvx}} \ge 0.833.
```

这里 $\alpha_{\mathrm{cvx}}$ 是凸万有覆盖面积的下确界。证明使用容许归一化参数域上的有限覆盖、支撑型局部记录、见证域多边形记录、外向舍入区间估计，以及最终聚合检查。

## 2. 声明范围

本仓库声明：

- 在凸 Brass-Sharifi 三测试集证书框架内，对 $\tau=0.833$ 进行有限记录复验；
- 给出相应的凸版本证书结论，即 $\alpha_{\mathrm{cvx}}$ 的认证下界；
- 对随仓库打包的、与定理相关的证书记录进行确定性复验。

本仓库不声明：

- 得到非凸版本结论；
- 已完成交互式定理证明器形式化；
- 已完成独立外部验证；
- 重新运行原始几何搜索，或重新生成证书归档。

## 3. 仓库目录结构

| 路径 | 作用 |
|---|---|
| `certificate/final_chain/` | 四个与定理相关的证书链归档，供公开复验命令使用。 |
| `certificate/manifest/` | 与关键产物（artifact）对应的 SHA256 清单和校验说明。 |
| `certificate/public/` | 展开的公开证书台账、状态文件和证明边界说明。 |
| `ucbs/config/` | 发布元数据、证书数据列结构与记录数配置、归档成员路径、日志策略和仓库检查策略。 |
| `ucbs/certificate/` | 证书链读取和分组件复验逻辑。 |
| `ucbs/verification/` | 仓库级检查、声明边界规则检查、产物哈希校验、归档与公开展开文件一致性检查和版本一致性检查。 |
| `ucbs/cli/` | 命令行入口和基于 loguru 的日志辅助模块。 |
| `scripts/` | 供源码目录直接运行的公开命令包装脚本。 |
| `tests/` | 开发者回归测试，覆盖命令行帮助信息、校验辅助函数、日志、版本元数据、README 命令、归档副本一致性、声明边界和论文计数一致性。 |
| `docs/` | 复验说明、输出字段、产物策略、数据字典、验证设计和审稿人检查清单。 |
| `paper/` | 编译后的论文 PDF 和 LaTeX 源码。 |

公开复验所需的证书数据已经包含在仓库中，不需要额外下载。

## 4. 验证设计

公开验证器工作在有限记录层面。它检查证书归档成员、CSV/JSON 数据列结构、记录数量、pass/status 字段、适用位置的正 surplus 字段、最终台账分类计数、最终 blocker 为零、SHA256 哈希，以及凸版本声明边界。它不执行产生这些记录的原始搜索流程。

仓库发布检查还会覆盖工程层面的发布质量：Python 编译、包元数据、发布版本一致性、LaTeX 源码、PDF 元数据来源、`CITATION.cff` 和英文 README 之间的论文标题一致性、脚本入口、目录结构、Python 字节码产物排除、编译中间产物排除、文本文件末尾换行、空目录、Python 注释和 docstring 的英文约束、直接 `print` 调用规避、公开 Markdown 数学片段、叙事用语规则检查、README/docs 声明边界、论文声明边界、产物哈希、归档与公开展开文件一致性，以及主证书验证。

日志文件统一使用 `loguru` 写入，代码入口采用 `from loguru import logger`。人类可读日志位于 `runs/<run-id>/log/`。命令行标准输出仍保留简洁 JSON 摘要，便于脚本调用。

## 5. 运行环境

需要 Python `>=3.10`。

在新的运行环境中，先安装运行时依赖：

```bash
python -m pip install -r requirements.txt
```

当前唯一运行时依赖是：

```text
loguru>=0.7.0
```

## 6. 快速验证

在干净解压的仓库根目录运行：

```bash
python scripts/check_repository.py --root . --log-level INFO
```

仓库发布检查会在内部调用主证书验证。使用 `python scripts/...` 形式运行时，不需要先执行 editable install。

推荐复验顺序：

1. 先在干净解压的源码树中运行仓库发布检查。
2. 如需更细的诊断，再运行主证书验证或分组件复验。
3. 如需运行开发者回归测试，请使用 `python -B`，避免生成 `__pycache__` 或 `.pyc` 文件。
4. 最终打包时不要包含自动生成的 `runs/` 目录。

## 7. 命令说明

下面的源码目录直运行命令是推荐的审稿复验路径。执行 editable install 后，也可以使用等价的安装后生成的命令行入口：`ucbs-verify-certificate`、`ucbs-check-repository`、`ucbs-replay-certificate-chain`、`ucbs-replay-per-record-evidence`、`ucbs-replay-construction-audit`、`ucbs-replay-witness-construction` 和 `ucbs-replay-final-verification`。

### 7.1 主证书验证

```bash
python scripts/verify_certificate.py --root . --log-level INFO
```

该命令复验证书链记录，包括固定 SHA256 清单，并在 `runs/certificate_verification/` 下写出状态文件和诊断文件。

### 7.2 仓库发布检查

```bash
python scripts/check_repository.py --root . --log-level INFO
```

该命令检查公开发布包，检查范围包括版本一致性、论文标题一致性、归档与公开展开文件一致性、论文声明边界、编译中间产物排除、文本文件末尾换行、产物哈希和主证书验证。

### 7.3 仅复验证书链

```bash
python scripts/replay_certificate_chain.py --root . --log-level INFO
```

该命令复验四个证书链组件并检查固定 SHA256 清单，不检查 README、docs、仓库目录结构或版本一致性。

### 7.4 分组件复验

```bash
python scripts/replay_per_record_evidence.py --root . --log-level INFO
python scripts/replay_construction_audit.py --root . --log-level INFO
python scripts/replay_witness_construction.py --root . --log-level INFO
python scripts/replay_final_adjudication.py --root . --log-level INFO
```

这些命令用于单独定位四个复验组件。更详细的输出位置和字段说明见 `docs/reproducibility.md`。

### 7.5 开发者回归测试

```bash
python -B -m unittest discover -s tests
```

这些测试不是数学证书复验的必要步骤，但属于发布维护检查。`-B` 用于阻止 Python 写入 `__pycache__` 目录和 `.pyc` 文件；仓库发布检查会主动拒绝这些字节码产物。当前覆盖内容包括：

- 公开脚本的命令行帮助信息；
- 证书校验辅助函数；
- GitHub 可渲染 Markdown 数学片段规则检查；
- 公开叙事用语规则检查；
- 基于 loguru 的文件日志；
- 发布版本、依赖、引用信息和论文标题一致性，包括 `ucbs.__version__`；
- README 命令覆盖情况；
- 展开 CSV/JSON 证书记录的归档与公开展开文件一致性；
- `paper/source/main.tex` 的论文声明边界检查；
- 配置中的证书计数与 LaTeX 论文表格的一致性。

## 8. 成功输出

主证书验证应包含：

```json
{
  "status": "passed",
  "certificate_verified": true,
  "threshold_proved": true,
  "certified_threshold": "0.833",
  "artifact_hashes_verified": true,
  "failed_component_count": 0
}
```

仓库发布检查应包含：

```json
{
  "status": "passed",
  "failed_step_count": 0
}
```

详细输出字段见 `docs/expected_outputs.md` 和 `docs/data_dictionary.md`。

## 9. 证书记录与哈希

证书链归档位于 `certificate/final_chain/`。关键产物的哈希记录在 `certificate/manifest/key_artifacts_sha256.txt`，结构化清单为 `certificate/manifest/final_certificate_manifest.json`。

`python scripts/verify_certificate.py --root . --log-level INFO`、`python scripts/replay_certificate_chain.py --root . --log-level INFO` 和 `python scripts/check_repository.py --root . --log-level INFO` 都会在接受随包证书记录前校验这些哈希。仓库发布检查还会逐字节确认 `certificate/public/` 下展开的公开 CSV/JSON 文件与 ZIP 归档中的对应成员一致。

## 10. 论文与引用

编译后的论文位于：

`paper/A_Certified_Lower_Bound_for_Lebesgues_Universal_Cover_Problem.pdf`

LaTeX 源码位于 `paper/source/`。仓库发布检查要求 `paper/source/main.tex`、`paper/source/macros.tex` 和 `paper/source/figures/fig_placement.tex` 存在。最终发布包不应包含 `.aux`、`.log`、`.out`、`.fls`、`.fdb_latexmk`、`.synctex.gz` 等 LaTeX 编译中间文件。

引用信息见 `CITATION.cff`。

## 11. Markdown 数学公式渲染

为提高 GitHub 页面渲染稳定性，本 README 的块级公式统一使用 fenced `math` 代码块，行内数学只保留短公式片段。仓库的 Markdown 规则检查会在发布前拒绝不稳定的块级公式分隔符和 GitHub 不支持的算子宏。

## 12. 故障排查

复验说明见 `docs/reproducibility.md`。常见问题和声明边界见 `docs/faq.md` 与 `docs/claim_scope.md`。

如果开发者测试之后仓库发布检查失败，请删除生成的 `__pycache__` 目录、`.pyc` 文件、LaTeX 编译中间文件和 `runs/` 目录，或使用 `python -B -m unittest discover -s tests` 重新运行开发者测试。

## 13. 许可

代码和公开文档采用 MIT 许可，见 `LICENSE`。

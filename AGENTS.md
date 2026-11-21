# TriVAL

通用科研思维与沟通内核继承自大本营 [AGENTS.md](../AGENTS.md)。

## 项目约定
- 已发表论文（arXiv:2605.23966）官方实现与 NL4COP 基准仓库；核心术语对齐 [GLOSSARY.md](GLOSSARY.md)，基准数据许可口径见 [benchmark/DATA_LICENSES.md](benchmark/DATA_LICENSES.md)。
- 环境固定 **Python 3.13** 与 `uv`（`uv sync --locked --python 3.13`，编译 `ecos` 需本机 C 编译器）；修改保持复现口径清晰，不破坏已发布基准数据。

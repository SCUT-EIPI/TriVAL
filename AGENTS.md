# TriVAL

在共享工作区中，同时遵循上级目录的 `AGENTS.md`。

## 项目约定
- 方法与术语以 [TriVAL 论文](https://arxiv.org/abs/2605.23966) 为准，基准数据许可口径见 [benchmark/DATA_LICENSES.md](benchmark/DATA_LICENSES.md)。
- 环境固定 **Python 3.13** 与 `uv`（`uv sync --locked --python 3.13`，编译 `ecos` 需本机 C 编译器）；修改保持复现口径清晰，不破坏已发布基准数据。

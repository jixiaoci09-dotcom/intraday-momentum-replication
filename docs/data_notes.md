# 数据使用说明

这个项目使用 Databento 的 CME 期货一分钟数据。由于这类行情数据有授权限制，GitHub 仓库里只保留代码、说明文档、下载记录和整理后的结果表，不上传原始行情数据。

## 不上传的内容

以下内容只保存在本地电脑，不放进 GitHub：

- Databento API key
- `.env` 或其他包含密钥的文件
- 原始行情数据
- 处理后的 parquet 数据
- 大型中间文件
- 账户、账单或付款相关信息

## 可以保留在 GitHub 的内容

仓库中可以保留：

- Python 代码
- README 和方法说明
- 数据下载记录
- 不含原始行情的 summary 文件
- 回归结果和策略结果表
- 最终总结报告

## 本地数据目录

实际运行项目时，数据文件一般放在这些目录下：

- `data/raw/`：原始 Databento 数据
- `data/interim/`：中间处理文件
- `data/processed/`：整理后的每日数据表
- `data/manifests/`：数据下载记录和简要说明

其中 `data/raw/`、`data/interim/` 和 `data/processed/` 已经在 `.gitignore` 中排除，不会上传到 GitHub。

## 记录数据来源

每次下载完整数据后，我会在 `data/manifests/` 中记录数据来源、品种、时间范围、文件大小、下载成本和 SHA-256 hash。这样即使原始数据不上传，也能说明结果是基于哪些数据生成的。

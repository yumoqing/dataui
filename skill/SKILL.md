---
name: dataui-repo
version: 1.0.0
description: dataui 仓库：31 个文件，主语言Python 9，JSON 3，Shell 1
trigger_conditions:
  - 需要理解、修改或排障 dataui 的代码
  - 在 dataui 里定位入口、数据表、对外契约或构建方式
---

# dataui 仓库技能

> 由仓库实际内容生成的骨架（README/目录/模型定义/契约/构建脚本逐项取证）。新增判断与坑位请直接在下面对应小节补充。

## 定位

**dataui**

A set of tools which auto generates frontend ui and backend data operation for data in table in database. crud module generates crud UI for data in table in database. base on a description json file, this module wll generate code by a parameter: tree module generates tree UI for hierarchy data in ta

- 远端：`https://github.com/yumoqing/dataui.git`
- 默认分支：`main`（共 6 个提交）
- 最近提交：2023-03-11 `796c750` bugfix
- 规模：31 个文件；Python 9，JSON 3，Shell 1

## 目录结构

- `dataui/` — Python 包源码（模块本体）（18 个文件）
- `crud/` — 5 个文件
- `models/` — 表定义（`models/*.json`，DDL/表结构唯一源）（4 个文件）
- `docs/` — 文档（1 个文件）
- 根文件：`README.md`、`requirements.txt`、`setup.py`

## 代码入口（顶层 Python）

- `setup.py`
- `dataui/crud_parser.py`
- `dataui/uitypes.py`

## 构建与运行

- `setup.py`：`dataui` v0.1.1，依赖 1 项
- `requirements.txt`：0 项
- Python 包 `dataui/`：`__init__.py`、`crud_parser.py`、`uitypes.py`

## README 要点与注意（摘自 `README.md`）

- 章节：crud、tree

## 建议阅读顺序

1. `README.md`
2. `docs/`
3. `models/`


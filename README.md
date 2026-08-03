# Bing Wallpaper Fetcher 本地部署与自动化指南

## 📋 目录
1. [项目概述](#项目概述)
2. [环境准备](#环境准备)
3. [克隆项目](#克隆项目)
4. [首次运行](#首次运行)
5. [配置自动提交](#配置自动提交)
6. [设置定时任务](#设置定时任务)
7. [代码核心逻辑说明](#代码核心逻辑说明)
8. [常见问题](#常见问题)

---

## 项目概述

**Bing Wallpaper Fetcher** 是一个自动抓取必应（Bing）每日壁纸的工具，支持：
- 自动获取必应 4K+ 高清壁纸
- 数据持久化存储（`source_list.csv`）
- 生成 JSON 数据供前端和 API 使用
- 支持 Windows 定时任务自动运行

**项目地址**：`https://github.com/chnbsdan/bw`

---

## 环境准备

### 1. 安装 Python 3

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载最新的 Python 3.x 安装包
3. **安装时务必勾选** `Add Python to PATH`
4. 验证安装：
```bash
python --version
```

### 2. 安装 Git

1. 访问 [Git 官网](https://git-scm.com/download/win)
2. 下载 Windows 版本并安装（默认选项即可）
3. 验证安装：
```bash
git --version
```

### 3. 安装 Python 依赖包

打开命令提示符（CMD）或 Git Bash，执行：
```bash
pip install requests pandas
```

**依赖说明**：

| 包名 | 用途 |
|------|------|
| `requests` | 发送 HTTP 请求，调用必应 API 和下载图片 |
| `pandas` | 处理 CSV 数据，实现数据的读取、合并和去重 |

---

## 克隆项目

```bash
# 进入存放项目的目录（如 D:\）
cd /d

# 克隆项目（使用 HTTPS 方式）
git clone https://github.com/chnbsdan/bw.git

# 进入项目目录
cd bw
```

**克隆方式对比**：

| 方式 | 优点 | 适用场景 |
|------|------|----------|
| HTTPS | 兼容性好，无需额外配置 | 大多数网络环境 |
| SSH | 免密码推送 | 配置好 SSH 密钥后更方便 |

---

## 首次运行

### 基础运行

```bash
python main.py --no-html
```

**参数说明**：

| 参数 | 作用 |
|------|------|
| `--no-html` | 跳过 HTML 生成，只下载图片和更新数据 |
| `--no-image` | 跳过图片下载，只更新 `source_list.csv` |
| `--use-wget` | 使用系统 `wget` 工具下载图片（网络不稳定时推荐） |
| `--update` | 仅更新数据库，不下载图片和生成 HTML |

### 完整运行输出示例

```
-> (16:42:06) Created directory: ./wallpaper/images
-> (16:42:06) Created directory: ./wallpaper/subpages
-> (16:42:06) Created directory: ./cache
-> (16:42:06) Created directory: ./backup
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
         Mon Aug  3 16:42:06 2026
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
-> (16:42:06) Requesting Bing API...
-> (16:42:08) API response received successfully
-> (16:42:08) Added 8 new records, total count: 2009
-> (16:42:11) BW-260803.jpg downloaded
-> (16:42:13) BW-260802.jpg downloaded
...
```

**输出解读**：

| 信息 | 含义 |
|------|------|
| `Added X new records, total count: Y` | 新增 X 条记录，当前共 Y 条壁纸数据 |
| `BW-260803.jpg downloaded` | 成功下载了 2026-08-03 的壁纸图片 |
| `Created directory` | 自动创建了所需的目录结构 |

---

## 配置自动提交

### 1. 配置 Git 用户信息

```bash
git config user.name "你的GitHub用户名"
git config user.email "你的GitHub注册邮箱"
```

### 2. 配置远程仓库地址（SSH 方式，可选）

```bash
# 切换为 SSH 地址（免密码推送）
git remote set-url origin git@github.com:chnbsdan/bw.git

# 测试 SSH 连接
ssh -T git@github.com
# 看到 "Hi 用户名! You've successfully authenticated..." 即成功
```

### 3. 创建自动运行脚本

在项目根目录（`D:\bw\`）创建 `run_and_commit.bat` 文件：

```batch
@echo off
cd /d "%~dp0"

echo [%date% %time%] 开始抓取壁纸... >> log.txt

:: 运行抓取脚本（跳过HTML生成，跳过图片下载以加快速度）
python main.py --no-html --no-image >> log.txt 2>&1

:: 检查 source_list.csv 是否有变化
git diff --quiet source_list.csv
if errorlevel 1 (
    echo [%date% %time%] 检测到新壁纸，正在提交... >> log.txt
    git add source_list.csv data\wallpapers.json >> log.txt 2>&1
    git commit -m "Daily Update: source_list.csv %date:~0,4%/%date:~5,2%/%date:~8,2%" >> log.txt 2>&1
    git push origin main >> log.txt 2>&1
    echo [%date% %time%] 提交完成！ >> log.txt
) else (
    echo [%date% %time%] 今天没有新的壁纸更新。 >> log.txt
)
```

**脚本逻辑说明**：

| 步骤 | 命令 | 作用 |
|------|------|------|
| 1 | `cd /d "%~dp0"` | 切换到脚本所在目录 |
| 2 | `python main.py --no-html --no-image` | 抓取壁纸数据，不下载图片，不生成 HTML |
| 3 | `git diff --quiet source_list.csv` | 检查 CSV 是否有变更 |
| 4 | `git add/commit/push` | 如果有变更，提交并推送到 GitHub |
| 5 | 写入 `log.txt` | 记录每次运行的日志，便于排查问题 |

**为什么使用 `--no-image`？**
- 网站 `https://bing.hangdn.com/` 的数据源是 `data/wallpapers.json`，它由 `source_list.csv` 生成
- 图片本身不提交到 Git，只存储在本地 `wallpaper/images/` 目录
- 跳过图片下载可以大幅加快运行速度，减少网络问题

### 4. 手动测试脚本

双击运行 `run_and_commit.bat`，检查：
1. 是否生成了 `log.txt` 文件
2. `log.txt` 中是否有 "提交完成！" 或 "没有新的壁纸更新" 的记录
3. 访问 GitHub 仓库，确认 `source_list.csv` 是否有更新

---

## 设置定时任务

### Windows 任务计划程序配置步骤

1. **打开任务计划程序**
   - 按 `Win + R`
   - 输入 `taskschd.msc`
   - 回车

2. **创建基本任务**
   - 点击右侧 **"创建基本任务..."**

3. **填写任务信息**

   | 字段 | 内容 |
   |------|------|
   | 名称 | `BingWallpaperFetcher` |
   | 描述 | `每天自动抓取必应壁纸并提交到GitHub` |

4. **设置触发器**
   - 选择 **"每天"**
   - 设置时间：`03:00`（凌晨3点，此时必应已更新当天壁纸）

5. **设置操作**

   | 字段 | 内容 |
   |------|------|
   | 程序或脚本 | `C:\Windows\System32\cmd.exe` |
   | 添加参数 | `/c "D:\bw\run_and_commit.bat"` |
   | 起始于 | `D:\bw` |

6. **完成创建**

### 配置建议

| 设置项 | 建议 | 原因 |
|--------|------|------|
| 运行时间 | 凌晨 3:00 | 必应壁纸通常在 UTC 15:00-16:00（北京时间 23:00-24:00）更新，凌晨运行确保数据最新 |
| 电脑状态 | 保持开机 | 定时任务只在电脑开机时执行 |
| 网络状态 | 保持联网 | 需要连接必应 API 和 GitHub |

---

## 代码核心逻辑说明

### 1. 数据流架构

```
必应 API → main.py → source_list.csv → generate_data.py → data/wallpapers.json → 网站/API
```

### 2. 数据累加机制（`update_database` 函数）

```python
# 加载历史数据
existing_df = pd.read_csv(database)

# 获取 API 最新数据
new_df = pd.DataFrame(new_records)

# 合并新旧数据
combined_df = pd.concat([existing_df, new_df], ignore_index=True)

# 按日期去重，保留首次记录
combined_df = combined_df.drop_duplicates(subset=['date'], keep='first')

# 保存回 CSV
combined_df.to_csv(database, index=False)
```

**去重逻辑**：
- 使用 `date` 字段作为唯一标识
- `keep='first'` 保留已有的记录，丢弃重复的新数据
- 确保每天只保留一条壁纸记录

### 3. 图片下载去重（`download_images_task` 函数）

```python
# 获取已下载的图片列表
downloaded_imgs = os.listdir(img_dir)

for date_str, url in zip(src_df['date'], src_df['url']):
    target_file = f'{img_prefix}-{date_str[2:]}.jpg'
    
    # 如果文件已存在，跳过下载
    if target_file in downloaded_imgs:
        continue
    
    # 否则执行下载
    response = requests.get(url)
    # ... 保存文件
```

### 4. 关键参数说明

| 参数 | 说明 | 风险等级 |
|------|------|----------|
| `--no-history` | **清空历史数据，只保留最新10条** | ⚠️ **极度危险** |
| `--no-cache` | 代码中已废弃，无实际作用 | ✅ 安全 |
| `--no-fetch` | 跳过 API 更新，使用现有数据 | ✅ 安全 |
| `--update` | 仅更新数据库 | ✅ 安全 |
| `--no-html` | 不生成 HTML | ✅ 安全 |
| `--no-image` | 不下载图片 | ✅ 安全 |

**⚠️ 特别注意**：`--no-history` 会清空所有历史数据，**生产环境绝对不要使用**！

### 5. 项目目录结构

```
D:\bw\
├── .gitignore              # Git 忽略规则
├── main.py                 # 主程序：抓取壁纸数据
├── generate_data.py        # 数据转换：CSV → JSON
├── FileOperations.py       # 文件操作工具
├── HTMLGenerator.py        # HTML 生成器
├── source_list.csv         # 核心数据：所有壁纸元数据
├── run_and_commit.bat      # 自动运行脚本（需创建）
├── log.txt                 # 运行日志（自动生成）
├── wallpaper/
│   └── images/             # 壁纸图片（不提交到 Git）
├── data/
│   └── wallpapers.json     # JSON 数据源（供前端/API 使用）
├── cache/                  # 临时缓存（自动清理）
└── backup/                 # 备份目录（`--update` 时自动创建）
```

---

## 常见问题

### 1. 图片下载失败（网络超时）

**现象**：程序卡在下载图片时，或报错 `Connection was reset`

**解决方案**：

```bash
# 方案1：跳过图片下载
python main.py --no-html --no-image

# 方案2：使用 wget 下载
python main.py --no-html --use-wget
```

### 2. Git 推送失败

**现象**：`fatal: unable to access ...`

**解决方案**：

```bash
# 方案1：使用 SSH 方式
git remote set-url origin git@github.com:chnbsdan/bw.git

# 方案2：配置凭证缓存（HTTPS 方式）
git config credential.helper store
# 然后手动执行一次 git push，输入用户名和令牌
```

### 3. 定时任务没有执行

**排查步骤**：
1. 确认电脑在设定时间处于开机状态
2. 确认网络连接正常
3. 检查任务计划程序中的任务状态
4. 查看 `D:\bw\log.txt` 日志文件

### 4. 历史数据被覆盖

**原因**：误用了 `--no-history` 参数

**解决方案**：
1. 检查 GitHub 仓库的历史提交，找回旧的 `source_list.csv`
2. 检查备份目录 `backup/` 是否有备份文件
3. **确保所有自动任务中不使用 `--no-history` 参数**

---

## 📊 运行状态验证

运行成功后，可以通过以下方式验证：

1. **检查本地数据**：
   ```bash
   # 查看 CSV 记录数
   wc -l source_list.csv
   ```

2. **检查 GitHub 仓库**：
   - 查看 `source_list.csv` 的提交记录
   - 确认文件内容已更新

3. **访问网站**：
   - `https://bing.hangdn.com/`
   - 确认显示最新的壁纸

---



## 📊 数据存储容量

### 1. CSV 文件大小
| 数据量 | 文件大小（估算） | 状态 |
|--------|-----------------|------|
| 当前（2009条） | ~500 KB | ✅ 正常 |
| 10年（~3650条） | ~1 MB | ✅ 完全没问题 |
| 100年（~36500条） | ~10 MB | ✅ 仍然很小 |
| 1000年（~365000条） | ~100 MB | ⚠️ 可能略慢但可用 |

**结论**：CSV 是纯文本格式，每条约 200-300 字节，**几乎不会成为瓶颈**。即使运行 100 年，文件也才 100MB 左右。

### 2. 图片存储（本地）
| 数据量 | 存储空间（估算） | 说明 |
|--------|-----------------|------|
| 1年（365张） | ~2-5 GB | 每张 4K 图片约 5-15MB |
| 10年（3650张） | ~20-50 GB | 需要较大硬盘空间 |

**注意**：图片**不提交到 GitHub**，只存储在本地 `wallpaper/images/` 目录。

### 3. GitHub 仓库限制
| 限制项 | 限制值 | 当前状态 |
|--------|--------|----------|
| 单文件大小 | 100 MB | ✅ `source_list.csv` 远小于此 |
| 仓库总大小（推荐） | 5 GB | ✅ 不存储图片，完全安全 |

---

## 🔍 历史数据抓取范围

### 必应 API 限制
```python
re_url = "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=10&..."
```

| 参数 | 含义 | 限制 |
|------|------|------|
| `idx=0` | 从今天开始 | 0 = 今天，1 = 昨天，以此类推 |
| `n=10` | 返回数量 | **最多返回 10 条** |

**关键限制**：`idx=7` 以后（即 8 天前）的数据，API 返回的是占位图片而非真实壁纸。因此，**每天运行最多只能新增 1 条有效记录**。

### 数据获取策略
```python
# 每次运行：获取从今天往前推 10 天的数据
# 但实际有效的新数据只有 1 条（当天壁纸）
# 其他 9 条与历史数据对比，通过去重机制过滤掉
```

---

## 📈 实际运行效果

### 你的项目数据统计
```
当前总记录：2009 条
数据时间跨度：约 5.5 年（从 2021 年初至今）
```

这说明项目**已经持续运行了 5 年以上**，数据累积完全正常。

### 未来预测
| 时间 | 预计记录数 | 运行状态 |
|------|-----------|----------|
| 1年后 | ~2365 条 | ✅ 正常运行 |
| 5年后 | ~3835 条 | ✅ 正常运行 |
| 10年后 | ~5660 条 | ✅ 正常运行 |
| 50年后 | ~18460 条 | ✅ 仍然正常 |

---

## ⚠️ 唯一需要注意的限制

### 必应壁纸本身
- 必应每日壁纸功能**理论上会持续运营**
- 如果微软停止该服务，项目将无法继续抓取新数据
- 但已抓取的历史数据**永久保留**

### 存储空间（本地）
如果你长期使用 `--no-image`（不下载图片），则完全没有存储压力。如果需要下载图片：
- 每张 4K 壁纸约 5-15 MB
- 1年约 2-5 GB
- 可以根据需求定期清理旧图片

---

## 💡 建议

1. **长期运行**：项目可以**无限制运行**，CSV 数据永远不会满。
2. **建议使用 `--no-image`**：如果你只需要网站展示数据，不需要在本地保存图片，用 `--no-image` 可以节省大量硬盘空间。
3. **定期检查**：偶尔查看 `log.txt`，确认任务正常运行。











+++++++++++++++++++++++

# Bing Wallpaper Fetcher

<p align="center">
    <a href="README_ZH.md">中文文档</a>
</p>

A tool to automatically download Bing wallpapers in 4K+ resolution.

> **Note:** Some images may only be available in 1080p due to Bing's limitations.

---

## Requirements
- Python 3
- Python packages: `requests`, `argparse`, `pandas`

## Usage
- Run `python3 main.py` to download images and generate the HTML gallery.
- To skip HTML generation, add `--no-html` or `--image-only`.
- To only update the `source_list.csv` database without downloading images or generating HTML, use both `--no-image` and `--no-html`.
- The `--update` option updates `source_list.csv` and creates a backup without downloading images or generating HTML.
- **Warning:** Using `--no-cache` will **delete** and rebuild the `source_list.csv` database, resulting in loss of history. Use with caution!
- The `--use-wget` option uses the system's `wget` tool instead of Python's `requests` package for downloading.
- The `--no-fetch` option prevents updating `source_list.csv` and uses the existing file.
- Other parameters are self-explanatory based on their names.

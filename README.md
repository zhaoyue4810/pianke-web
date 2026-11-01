# 片刻 (Pianke) · 开源网页版

> **让 AI 协助初筛与分组，把最终的审美决定权留给自己。**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey.svg)](#快速开始)
[![License: Pianke v2](https://img.shields.io/badge/license-Pianke%20v2-cc785c.svg)](LICENSE)

这是片刻最早的**开源网页版**：在自己电脑上运行的本地选片工具，把相似照片归成“同一个瞬间”，再用左右 A/B 擂台两两比较，挑出最满意的一张。它免费、开源，会继续保留在这里。

片刻现在已经发展成独立安装的 **Mac / Windows 桌面 App**，选片更准、步骤更少，还能接着做交付。如果你是职业摄影师，推荐直接用新版 App。

---

## 下载最新版片刻 App

| | 入口 |
| :--- | :--- |
| **Mac 版**（Apple 芯片，M1 Pro 或更高，16 GB 内存，macOS 15 及以上） | [下载 Mac 版](https://pianke.kongbaige.xyz/web/v1/download) · [安装与使用说明](https://pianke.kongbaige.xyz/assets/install-guide.html) |
| **Windows 版**（Windows 10/11 64 位，建议 16 GB 内存） | [下载 Windows 版](https://pianke.kongbaige.xyz/web/v1/download/windows) · [安装说明](https://pianke.kongbaige.xyz/assets/windows-install-guide.html) |
| **官网** | [pianke.kongbaige.xyz](https://pianke.kongbaige.xyz/) · [套餐与价格](https://pianke.kongbaige.xyz/pricing/) · [English](https://pianke.kongbaige.xyz/en/) |

下载链接始终指向当前最新版本。

## 新版 App 和开源网页版有什么不同

| | 开源网页版（本仓库） | 片刻 App（Mac / Windows） |
| :--- | :--- | :--- |
| **上手** | 需要 Python 环境，首次安装依赖可达 2–3 GB，在浏览器里使用 | 下载安装包直接打开。Mac 版是 Mac 原生应用 |
| **选片方式** | 每组相似照片由你左右两两 PK，一张张比下来 | 片刻引擎先给出整场建议保留的照片，你只需复核和调整 |
| **判断准确度** | 本地通用规则：模糊、过曝、欠曝、闭眼 | 片刻引擎专为人像、婚礼、活动等拍摄场景做选片判断：虚焦、逐只眼睛判断睁闭、后期难以救回的过曝和偏暗；连拍和重复构图里推荐更值得留的一张 |
| **整理维度** | 按“瞬间”分组 | 按瞬间分组之外，还能按人物、按场景查看和筛选，可单独筛出空镜 |
| **复核** | 初筛复核页里点击召回 | 被建议跳过的照片随时可以找回。Mac 版复核页可以直接调整保留张数，悬停一行就能整行移出或选入，按空格放大鼠标所在的照片 |
| **速度** | 专家模式首次需下载数据，之后逐张在本机计算 | 不用配置环境，开箱即用；Mac 版从 1.3.3 起首次进入复核更流畅，初筛也更快 |
| **衔接后期** | 原片移动或复制到 `winners/`、`losers/` | 星级、色标和留用旗标写进照片，Lightroom、Capture One 打开就能看到；也可以只写标记、不移动原片 |
| **交付** | 相机参数水印（10 种样式） | 水印、边框、批量压缩永久免费；Mac 版可以从成片页生成客户看片页，客户在手机上看片、选片，选择自动回到片刻 |
| **越用越懂你** | — | 年付与创始终身版会根据你对建议的调整，学习你的取舍偏好；可随时关闭或删除 |
| **其他** | — | 合照里标出每个人表情最好的一帧（Mac）；插上存储卡即可导入（Mac）；已完成的项目断网也能重新打开、复核和出图 |
| **隐私** | 除云端模式外，照片只在本机处理 | 原图、缩略图、文件名和人脸信息都留在你的电脑上；AI 选片只上传选片所需的分析信息 |
| **价格** | 免费 | 新用户 ¥1.9 / 14 天，月付 ¥9.9，年付 ¥99，创始终身版 ¥128；一次付款，不自动续费 |

---

## 关于授权（请在使用前阅读）

> **本项目完全免费！不收一分钱！**
>
> **摄影师可以用它处理付费拍摄的客户照片；但绝对禁止把软件本身拿去卖钱。**

### 允许
- 个人使用——爱好者、学生、个人摄影师整理自己的照片
- **摄影师 / 工作室在日常拍摄业务中使用，包括处理付费客户的照片**（拍摄服务是你卖的，软件只是你用的工具）
- 自由修改源码自用、提交 PR
- 在保留原始版权与许可的前提下，免费分享给朋友、同事、摄影社群

### 禁止
- **销售本软件**（原版、改名、汉化、二次打包、上架商店——一律不行）
- **把本软件作为付费服务对外提供**（付费 SaaS / 在线选片网站 / 收费小程序等）
- 转售、转授权、再许可
- 移除或隐藏“片刻”品牌、版权、作者联系方式
- 用“片刻”或近似名称分发改版软件

### 商业合作 / 二次开发授权

如果你想做的事情超出上面“允许”范围（比如把片刻嵌入你的付费产品、做付费 SaaS 等），请联系作者协商单独授权：

**微信 `15828377122`**

> 完整条款见 [LICENSE](LICENSE)（中文为准、附英文摘要）。
>
> 如果你发现有人在卖片刻 / 把它包装成付费服务，欢迎私信举报。

---

## 开源网页版的功能

- **照片不出本地**：除“云端模式”外，所有分析、初筛、分组都在你自己的电脑里完成。
- **自动剔除明显废片**：模糊、过曝、欠曝、闭眼，自动识别并归到一边，担心错杀可一键复核召回。
- **把同一瞬间的连拍归到一组**：同一个人、同一个场景、同一段时间，自动放在一起对比。
- **左右擂台两两对决**：按 `←` / `→` 选哪边更好，一组里只留一张（或几张），节奏极快。
- **支持 RAW**：
  - **RAW+JPG 同名双拍**：以 JPG 显示与分析，归档时 RAW 跟着一起搬走（含 `.xmp` 伴随文件）。
  - **纯 RAW**：直接取出内嵌预览图，读图很快。
- **随时反悔、随时续做**：多级撤销；进度自动保存，下次启动接着上次继续。

### 四种工作模式

| 模式 | 适合谁 | 上手成本 | 联网要求 |
| :--- | :--- | :--- | :--- |
| **极速** | 拍物 / 风景 / 低配电脑 | 装一次约 200 MB | 完全不需要 |
| **专家** | 拍人像 / 婚礼 / 活动 / 主流性能电脑 | 装一次约 2–3 GB | 仅第一次联网下载，之后纯离线 |
| **云端** | 想看到“为什么退这张”的文字解释 | 装一次约 5 MB + 自己配置一个 API Key | 每张图都要联网（缩略图会发到你配置的服务商） |
| **本地视觉** | 想要文字理由、但不想上传照片 | 装一次约 2–3 GB + 本机自行运行的本地视觉服务 | 只访问本机服务 |

> **选择建议**：
> - **拍物 / 风景 / 旧电脑** ➔ **极速**，对静物、产品、多角度连拍很稳。
> - **拍人 / 婚礼 / 活动** ➔ **专家**，能把“同一个人不同姿势不同背景”归为一组。
> - **需要文字退片理由、接受上传缩略图** ➔ **云端**，会用大白话告诉你“左边小孩闭眼了”这类原因。
> - **需要文字退片理由、照片不出本机** ➔ **本地视觉**，需要你先在本机运行一个本地视觉服务。

---

## 快速开始

> 国内网络建议先把 pip 换成阿里云源（`https://mirrors.aliyun.com/pypi/simple/`）或清华源（`https://pypi.tuna.tsinghua.edu.cn/simple`），专家模式依赖较大，不换源容易超时。不熟悉命令行的话，可以用带 AI 助手的编辑器（如 [Trae](https://www.trae.com.cn/)）打开本项目，让它帮你换源、安装依赖并运行。

### 方式一：一键启动（推荐非开发者）

1. [下载项目 ZIP 压缩包](https://github.com/zhaoyue4810/pianke/archive/refs/heads/main.zip) 并解压到本地。
2. 双击运行对应的启动器脚本：

| 系统 | 启动脚本 | 首次运行安全提示 |
| :--- | :--- | :--- |
| **macOS** | `启动_macOS.command` | 若提示“身份不明的开发者”：**按住 Control 键**点击脚本 ➔ **打开** ➔ 弹窗中再次点击 **打开**。 |
| **Windows** | `启动_Windows.bat` | 若弹出“Windows 已保护你的电脑”：点击 **更多信息** ➔ **仍要运行**。 |

*启动器会在项目目录下单独准备 Python 环境，不影响系统环境。国内用户默认使用镜像，设置环境变量 `PIANKE_NO_MIRROR=1` 可改走官方源。*

### 方式二：手动启动（适合开发者）

```bash
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安装项目依赖（包含所有模式）
pip install -r requirements.txt

# 3. 运行服务（默认端口 5057，自动打开浏览器）
python app.py

# 常用参数：
python app.py --port 8080 --no-browser
```

### 本地视觉模式准备

先在本机运行一个本地视觉服务，再在启动前用环境变量指定地址和名称：

```bash
LOCAL_VLM_BASE_URL=http://127.0.0.1:11434/v1
LOCAL_VLM_MODEL=<本机服务中的名称>
LOCAL_VLM_TIMEOUT=180
```

首页“更多选项”里可以关闭本地美学评分，只保留文字判图和基础分组，以减少本机资源占用。

---

## 选片工作流

1. **导入与配置**：在首页选择工作模式，输入或拖入照片文件夹的绝对路径，点击 **开始整理**。
2. **分析与进度**：实时显示扫描进度和预估剩余时间。
3. **初筛复核**：平铺展示被自动淘汰的废片及原因，**点击任意照片即可放回待分组列表**，未点击的归入淘汰区。
4. **分组预览与调参**：分组过细或过粗时，拖动滑块调节并点击 **重新分组**。
5. **左右擂台 PK**：在相似组内两两对比。
   - `←` / `→`：保留左侧 / 保留右侧（对侧淘汰）
   - `↑` / `↓`：全要 / 全不要
   - `[` / `]`：仅淘汰左侧 / 仅淘汰右侧（处理单张坏图）
   - `S`：跳过本组（放到队尾最后处理）
   - `Z`：切换缩放（1x ➔ 2x ➔ 4x），两图同步平移
   - `Shift + Z`：撤销当前组的上一步
6. **完成与导出**：展示所有胜出照片，一键打开结果文件夹。

---

## 输出与目录

在你指定的**照片目录**下生成：

```text
你的照片文件夹/
├── winners/                 # 胜出保留的照片
├── losers/                  # 被淘汰的照片
├── .pic_selecter_state.json # 进度文件（可随时中断并继续）
└── _pic_selecter/           # 缓存与日志
    ├── thumbs/              # 缩略图缓存
    ├── log.txt              # 处理日志
    └── skipped.log          # 无法读取的文件清单
```

**归档模式**（首页“更多选项”）：
- **移动模式（默认）**：原片直接移到 `winners/` 或 `losers/`，最省空间；反悔时无损搬回原位。
- **复制模式**：原片不动，在 `winners/`、`losers/` 中创建副本，需要双倍空间。

**初筛强度**：
- **标准**：只剔除明显废片。
- **进阶（默认）**：阈值更严，进入擂台的照片更少。被淘汰的照片都可以在复核页或完成页召回。

---

## 相机水印

选片完成后，在胜出总览页点击 **相机水印**，为照片批量加上相机品牌、机型、镜头、焦距、光圈、快门、ISO、拍摄时间等信息，并自动匹配品牌 Logo。

| ID | 名称 | 风格 |
| :--- | :--- | :--- |
| **A** | 标准底栏 | 白色信息条，左机型/镜头 ｜ 中品牌 Logo ｜ 右参数/时间 |
| **B_full / B_clean** | 极简底栏-详尽 / 极简 | 顶/左/右贴边窄白 + 底部居中 Logo + 信息 |
| **C_full / C_clean** | 毛玻璃悬浮-详尽 / 极简 | 原图模糊作背景 + 缩小照片悬浮居中带阴影 |
| **D_full / D_clean** | 经典白边相框-详尽 / 极简 | 顶/左/右窄白 + 底部大白边居中放品牌 |
| **F_full / F_clean** | 杂志风-详尽 / 极简 | 左下色卡（从图中提取）+ 右下品牌信息 |
| **G** | 极简白边 | 四周均匀窄白边，无文字 |

输出到 `winners/watermarked_<时间戳>/`，保留原 EXIF（旋转标志归位）。

---

## 常见问题

<details>
<summary><b>1. 启动后浏览器没有自动打开？</b></summary>
手动访问 <code>http://localhost:5057</code>。
</details>

<details>
<summary><b>2. 5057 端口被占用？</b></summary>
一键启动器读取环境变量 <code>PIC_SELECTER_PORT</code>：
<ul>
  <li>macOS: <code>export PIC_SELECTER_PORT=8080</code></li>
  <li>Windows: <code>set PIC_SELECTER_PORT=8080</code></li>
</ul>
手动启动时直接传 <code>--port 8080</code>。
</details>

<details>
<summary><b>3. 专家模式首次启动卡在“加载中”？</b></summary>
第一次需要下载几百兆的辅助数据，视网速 1–3 分钟，之后启动很快。长时间无响应请看终端日志或检查网络。
</details>

<details>
<summary><b>4. 云端模式如何配置 API Key？</b></summary>
启动后在网页弹窗里贴入 Key，只保存在本机 <code>~/.config/pic_selecter/ark_key</code>（仅你可读）。也可以在启动前设置环境变量 <code>ARK_API_KEY</code>。
</details>

<details>
<summary><b>5. 极速模式和专家模式剔除废片有什么区别？</b></summary>
<ul>
  <li><b>极速模式</b>：擅长整张模糊、手抖、失焦。</li>
  <li><b>专家模式</b>：擅长背景清楚但人脸糊了、眼睛闭了这类人像废片。</li>
</ul>
</details>

<details>
<summary><b>6. 如何卸载和清理缓存？</b></summary>
<ul>
  <li><b>清理照片缓存</b>：删除照片目录下的 <code>winners/</code>、<code>losers/</code>、<code>.pic_selecter_state.json</code> 和 <code>_pic_selecter/</code>（移动模式下请先把照片移回）。</li>
  <li><b>卸载程序</b>：删除项目文件夹，并清理启动器安装的工具缓存：
    <ul>
      <li>macOS: <code>rm -rf ~/.local/bin/uv ~/.local/share/uv/</code></li>
      <li>Windows: 删除 <code>%USERPROFILE%\.local\bin\uv.exe</code> 和 <code>%USERPROFILE%\.local\share\uv\</code></li>
    </ul>
  </li>
</ul>
</details>

<details>
<summary><b>7. HEIC 图片在网页上无法预览？</b></summary>
Windows 可能需要安装微软官方的 HEIF 扩展才能在浏览器里预览；后台分析不受影响。
</details>

<details>
<summary><b>8. 遇到报错？</b></summary>
见 <a href="TROUBLESHOOTING.md">故障排查指南</a>。
</details>

---

## 隐私与安全

1. 极速、专家与本地视觉模式下，照片只在你的电脑或本机服务里处理，不发往外部。
2. 服务只监听本机回环地址（127.0.0.1），局域网和外网访问不到。
3. 接口做了来源校验，防止外部网站调用；需要额外鉴权时，启动前设置环境变量 `PIC_SELECTER_TOKEN`。
4. **云端模式例外**：缩略图会发送到你配置的服务商接口。对隐私要求高的场景请只用极速、专家或本地视觉模式。

---

## 反馈

- 开源网页版：[GitHub Issues](https://github.com/zhaoyue4810/pianke/issues)
- 片刻 App：[官网支持页](https://pianke.kongbaige.xyz/support/)
- 微信：15828377122

---

## English (short)

**Pianke Web** is the original open-source, run-it-yourself version of Pianke: a local photo culling tool that groups near-identical shots into "moments" and lets you pick the best one with fast left/right A/B comparisons. It stays free under the [Pianke License v2](LICENSE) (free to use, including for paid client work; selling the software itself is not allowed).

Pianke is now a desktop app for **Mac** (native, Apple silicon M1 Pro or later, 16 GB, macOS 15+) and **Windows** (10/11, 64-bit). Compared with this web version, the app installs without any Python setup, suggests a full keep set for the whole shoot so you only review and adjust, checks focus, each eye and unrecoverable exposure, recommends the best frame in bursts, sorts photos by person and scene, writes star ratings and labels that Lightroom and Capture One read, and adds free watermark, border and batch-compression tools. On Mac it can also publish a client viewing page where clients pick favourites on their phone and the picks flow back into Pianke. Originals, thumbnails, file names and face data stay on your computer.

- [Download for Mac](https://pianke.kongbaige.xyz/web/v1/download)
- [Download for Windows](https://pianke.kongbaige.xyz/web/v1/download/windows)
- [Website](https://pianke.kongbaige.xyz/en/) · [Pricing](https://pianke.kongbaige.xyz/en/pricing/)

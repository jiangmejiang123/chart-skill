# visual-explain

**让 AI 在能画图的时候，不再写一大段文字。**

这不是一个"图表库"，是一个 **agent 技能**：装进你的 AI 助手的技能目录后，
它遇到能用图讲清的事情时，会先想"这块能不能画出来"，而不是先铺三段话。

![12 种图表总览](examples/overview.png)

---

## 它改变的是什么

一段文字是**线性**的：读者要读到最后才知道重点，还得自己在脑子里拼出结构。
一张图是**并行**的：结构、比例、流向、先后，一眼全在。

所以判断标准不是"能不能画"，而是：

> **这块信息本来是不是就长成图的样子？**

是的话，画出来比写出来省一半时间。不是的话，硬做一张图只是浪费。
这个技能里写死了这两条：**该画的时候必须画，不该画的时候不许画。**

## 装上之后会发生什么

同样是回答"服务起不来怎么办"，差别是这样：

**以前**——五段文字，读者要自己排优先级：

> 这个报错通常有三个原因。第一是端口被占用，可以先看看 8080 有没有别的进程……
> 第二是配置文件路径写错了，配置文件必须放在工作目录下……
> 第三是依赖没装全，缺哪个会报 module not found……
> 三个里最常见的是第一个……

**现在**——一张判断流程图，三条分支一眼看完，还知道先查哪条。

技能不是让 AI"多画图"，是让它**在正确的地方换成图**。它同时被要求克制：
三个数以内的对比、两句话能说清的事，用表格或一行字，不许硬画。

## 安装

克隆下来，把整个目录放进你的 agent 技能目录：

```bash
git clone https://github.com/jiangmejiang123/visual-explain
pip install -r visual-explain/requirements.txt

# 然后整目录放进技能目录，按你的宿主选一个：
#   Claude Code  → ~/.claude/skills/visual-explain/
#   其他 agent   → 各自的 skills 目录（如 ~/.dsh/skills/、项目内 .agents/skills/）
```

装完开新会话，问它一件需要讲结构的事，看它是不是换了表达方式。

> 它认的是 `SKILL.md`（给模型看的判断规则）+ `scripts/`（执行脚本）。
> 少了 SKILL.md 就只是一个画图工具，少了脚本就只是些建议——两个都要。

## 自己跑一下

不想装也能当命令行工具用：

```bash
python scripts/viz.py --demo out          # 一次出全部 12 张
python scripts/viz.py bar --data '{"周一":12,"周二":19,"周三":15}' --title "每周提交" --out a.png
```

## 12 种图

| 命令 | 画什么 | 数据格式 |
|---|---|---|
| `bar` | 柱状 / 条形对比 | `{"A":12,"B":19}` |
| `line` | 折线，多系列 | `{"系列1":[1,2,3],"系列2":[3,2,1]}` |
| `pie` | 占比 | `{"开发":38,"会议":16}` |
| `scatter` | 两个量的关系 | `{"x":[...],"y":[...]}` |
| `heatmap` | 矩阵热力 | `{"matrix":[[..]],"rows":[..],"cols":[..]}` |
| `flow` | 流程图 / 判断分支 | `{"nodes":[{"id":"a","label":"开始"}],"edges":[["a","b"]]}` |
| `mind` | 脑图 / 层级拆分 | `{"root":"主题","children":{"分支":["叶子"]}}` |
| `gantt` | 甘特图 / 排期 | `{"unit":"小时","tasks":[{"name":"改造","start":0,"dur":1.2}]}` |
| `sankey` | 流向 / 转化漏斗 | `{"left":[["搜索",40]],"right":[["安装",38]],"flows":[["搜索","安装",16]]}` |
| `treemap` | 构成占比（块多时更省地方） | `{"代码":45,"文档":22}` |
| `network` | 关系网络 / 依赖 | `{"edges":[["A","B"]]}` |
| `formula` | LaTeX 公式 | `--expr "E=mc^2"`，多条用 `;;` 分隔 |

全部效果见 `examples/`——都是 `--demo` 的原图，没有后期修。

## CLI

```
python scripts/viz.py <kind> [options]

  --data JSON        内联 JSON，或 - 从 stdin 读
  --json-file PATH   数据文件
  --expr LaTeX       仅 formula；多条用 ;; 分隔
  --title TEXT       图标题
  --out PATH         输出图片（必填，除非用 --demo）
  --width / --height 英寸
  --dpi N            默认 150
  --demo DIR         一次生成全部 12 张示例图
```

## 依赖

Python 包见 `requirements.txt`：`matplotlib` `seaborn` `networkx` `squarify` `graphviz`。

其中 `flow` 和 `mind` 还要 **Graphviz 的系统二进制**（Python 的 `graphviz` 包只是调用它的壳）：

| 系统 | 安装 |
|---|---|
| Windows | `winget install graphviz` 或到 [graphviz.org/download](https://graphviz.org/download/) |
| macOS | `brew install graphviz` |
| Debian / Ubuntu | `apt install graphviz` |

装完不用重启终端——脚本会在 `PATH` 之外再去几个常见目录找一次 `dot`。

## 中文字体

自动按平台探测：**微软雅黑 → 苹方 → Noto Sans CJK → 思源黑体 → 文泉驿 → 黑体**。
一个都没有时会向 stderr 提示，此时中文显示为方块。补一个即可：

```bash
apt install fonts-noto-cjk            # Debian / Ubuntu
brew install font-noto-sans-cjk-sc    # macOS
```

配色和字体都在 `scripts/vizlib.py` 顶部，改常量就行。超过 7 个系列时颜色自动循环。

## 边界

- 只管**结构、比例、流向**。照片质感插画、封面海报 → 用生图模型
- 视频、动图 → 用 ffmpeg 类工具；3D → 用 3D 工具；文档/PPT/Excel → 用 office 类工具
- 只要交互（筛选、点击）→ 写 HTML，别画静态图

## License

MIT

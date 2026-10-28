# visual-explain

**一行命令，一张图。中文不会变成方块。**

一个 ~400 行的 Python 脚本，把常用的 12 种图表封装成命令行工具。
不写 matplotlib 样板代码，不再折腾中文字体。

![12 种图表总览](examples/overview.png)

---

## 它解决什么

用 matplotlib 画中文图的人，基本都踩过这三个坑：

**1. 中文全是方块。**
要手动指定字体文件，换台机器又得重来一遍。这个工具按 Windows（微软雅黑）→ macOS（苹方）→ Linux（Noto CJK / 思源黑体 / 文泉驿）的顺序自动找，找到一个就装上。

**2. 默认配色放不进汇报材料。**
matplotlib 的默认蓝橙，放进 PPT 里像上个世纪的截图。这里用一套低饱和配色——深靛标题、灰蓝辅助线、蓝绿橙紫青粉七色循环，白底、去右边框，截图直接能用。

**3. 八行样板代码只为一个柱状图。**
建图、设标题、去边框、存文件——现在压缩成一条命令，数据用 JSON 直接给。

## 快速开始

```bash
pip install -r requirements.txt
python scripts/viz.py --demo out
```

打开 `out/`，里面是 12 张图，就是上面那张总览。

画一张自己的：

```bash
python scripts/viz.py bar \
  --data '{"周一":12,"周二":19,"周三":15,"周四":23,"周五":26}' \
  --title "每周提交次数" \
  --out chart.png
```

数据也可以从文件或 stdin 给：

```bash
python scripts/viz.py line --json-file trend.json --title "周访问量" --out trend.png
echo '{"开发":38,"会议":16,"排障":25}' | python scripts/viz.py pie --data - --out t.png
```

## 12 种图

| 命令 | 画什么 | 数据格式 |
|---|---|---|
| `bar` | 柱状 / 条形对比 | `{"A":12,"B":19}` |
| `line` | 折线，多系列 | `{"系列1":[1,2,3],"系列2":[3,2,1]}` |
| `pie` | 占比 | `{"开发":38,"会议":16}` |
| `scatter` | 两个量的关系 | `{"x":[...],"y":[...]}` |
| `heatmap` | 矩阵热力 | `{"matrix":[[..],[..]],"rows":[..],"cols":[..]}` |
| `flow` | 流程图 / 分支判断 | `{"nodes":[{"id":"a","label":"开始"},{"id":"b","label":"判断?","shape":"diamond"}],"edges":[["a","b"]]}` |
| `mind` | 脑图 / 层级拆分 | `{"root":"主题","children":{"分支":["叶子1","叶子2"]}}` |
| `gantt` | 甘特图 / 排期 | `{"unit":"小时","tasks":[{"name":"改造","start":0,"dur":1.2}]}` |
| `sankey` | 流向 / 转化 | `{"left":[["搜索",40]],"right":[["安装",38]],"flows":[["搜索","安装",16]]}` |
| `treemap` | 构成占比（块多时更省地方） | `{"代码":45,"文档":22}` |
| `network` | 关系网络 / 依赖 | `{"edges":[["A","B"],["A","C"]]}` |
| `formula` | LaTeX 公式 | `--expr "E=mc^2"`，多条用 `;;` 分隔 |

每种图的效果见 `examples/`，都是 `--demo` 直接产出的原图，没有后期修饰。

## CLI

```
python scripts/viz.py <kind> [options]

  --data JSON        内联 JSON，或 `-` 从 stdin 读
  --json-file PATH   数据文件
  --expr LaTeX       仅 formula；多条用 ;; 分隔
  --title TEXT       图标题
  --out PATH         输出图片（必填，除非用 --demo）
  --width / --height 英寸，覆盖默认尺寸
  --dpi N            默认 150
  --demo DIR         一次生成全部 12 张示例图
```

## 依赖

Python 包（`requirements.txt` 已列）：

```
matplotlib  seaborn  networkx  squarify  graphviz
```

其中 `flow` 和 `mind` 还需要 **Graphviz 的系统二进制**（Python 的 `graphviz` 包只是调用它的壳子）：

| 系统 | 安装 |
|---|---|
| Windows | `winget install graphviz`，或到 [graphviz.org/download](https://graphviz.org/download/) 下载安装包 |
| macOS | `brew install graphviz` |
| Debian / Ubuntu | `apt install graphviz` |

装完不用重启终端——脚本会在 `PATH` 之外，再去几个常见安装目录里找一次 `dot`。

## 字体

自动探测顺序：

```
微软雅黑 → 苹方 → Noto Sans CJK SC → 思源黑体 → 文泉驿微米黑 → 黑体
```

一个都找不到时会向 stderr 打一行提示，此时中文会显示成方块。装一个就行：

```bash
apt install fonts-noto-cjk          # Debian / Ubuntu
brew install font-noto-sans-cjk-sc  # macOS
```

## 自定义

配色和字体都在 `scripts/vizlib.py` 顶部，改常量即可：

```python
INK, MUTED, BLUE, GREEN, ... = "#0F172A", "#64748B", "#2563EB", "#059669", ...
PALETTE = [BLUE, GREEN, ORANGE, PURPLE, CYAN, PINK, SLATE]
```

超过 7 个系列时颜色自动循环，不会报错。

## 边界

- 这是一个给自己省事的工具，不是绘图库。要精细控制就自己写 matplotlib。
- 只做静态 PNG，不做交互图表（要交互直接用 HTML）。
- 三个数以内的对比不值得画图，用表格更快。

## License

MIT

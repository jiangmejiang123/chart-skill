# -*- coding: utf-8 -*-
r"""visual-explain 出图 CLI —— 一行命令出图，不用每次手写 matplotlib。

用法：
  python viz.py bar   --data '{"周一":80,"周二":60}' --title 标题 --out a.png
  python viz.py flow  --json-file flow.json --out a.png
  python viz.py mind  --json-file mind.json --out a.png
  python viz.py gantt --json-file gantt.json --out a.png
  python viz.py sankey|treemap|network|heatmap|scatter|line|pie 同上
  python viz.py formula --expr "E=mc^2;;\sum_{i=1}^{n} x_i" --out a.png

数据也可以从 stdin 给：--data -  然后管道传入。
所有子命令共有：--title / --out / --width / --height
"""
import argparse
import json
import sys
import os

from vizlib import (plt, save, bare, colors, color, FONT_NAME, HAS_CJK_FONT,
                    HAS_GRAPHVIZ, INK, MUTED, LINE,
                    BLUE, GREEN, ORANGE, PURPLE, CYAN, PINK, SLATE)


# ---------- 数据读取 ----------
def load(args):
    if args.json_file:
        with open(args.json_file, encoding="utf-8") as f:
            return json.load(f)
    raw = args.data
    if raw == "-":
        raw = sys.stdin.read()
    if not raw:
        raise SystemExit("缺少数据：用 --data 或 --json-file")
    return json.loads(raw)


def figsize(args, w=None, h=None):
    return (args.width or w or 8, args.height or h or 4.4)


# ---------- 数据类图表 ----------
def cmd_bar(args, d):
    fig, ax = plt.subplots(figsize=figsize(args))
    keys = list(d.keys())
    vals = [float(v) for v in d.values()]
    bars = ax.bar(keys, vals, color=colors(len(keys)), width=0.62)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:g}", ha="center", va="bottom",
                fontsize=9, color=MUTED)
    ax.set_title(args.title or "", fontsize=13, pad=12, color=INK)
    ax.grid(axis="y", alpha=0.25)
    bare(ax)
    ax.tick_params(axis="x", labelsize=11)
    return save(_finish(ax), args.out)


def cmd_line(args, d):
    fig, ax = plt.subplots(figsize=figsize(args))
    if all(isinstance(v, (list, tuple)) for v in d.values()):
        for i, (k, vs) in enumerate(d.items()):
            ax.plot(range(len(vs)), vs, marker="o", ms=4, lw=2,
                    color=color(i), label=k)
        ax.legend(frameon=False, fontsize=9)
    else:
        ax.plot(list(d.keys()), [float(v) for v in d.values()], marker="o", ms=4,
                lw=2, color=BLUE)
    ax.set_title(args.title or "", fontsize=13, pad=12, color=INK)
    ax.grid(alpha=0.25)
    return save(_finish(ax), args.out)


def cmd_pie(args, d):
    fig, ax = plt.subplots(figsize=figsize(args, 6.4, 4.6))
    ax.pie([float(v) for v in d.values()], labels=list(d.keys()), autopct="%1.0f%%",
           colors=colors(len(d)), startangle=90, textprops={"fontsize": 10, "color": INK})
    ax.set_title(args.title or "", fontsize=13, pad=12, color=INK)
    ax.axis("equal")
    return save(_finish(ax), args.out)


def cmd_scatter(args, d):
    fig, ax = plt.subplots(figsize=figsize(args))
    ax.scatter(d["x"], d["y"], s=18, alpha=0.55, color=BLUE, edgecolors="none")
    ax.set_title(args.title or "", fontsize=13, pad=12, color=INK)
    ax.grid(alpha=0.25)
    return save(_finish(ax), args.out)


def cmd_heatmap(args, d):
    import seaborn as sns
    fig, ax = plt.subplots(figsize=figsize(args, 7.5, 4.4))
    m = d["matrix"]
    sns.heatmap(m, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax,
                xticklabels=d.get("cols", "auto"), yticklabels=d.get("rows", "auto"),
                cbar_kws={"label": d.get("unit", "")}, annot_kws={"fontsize": 8})
    ax.set_title(args.title or "", fontsize=13, pad=12, color=INK)
    return save(_finish(ax), args.out)


def _finish(ax):
    """柱/线/饼之外收尾；对 pie 无副作用。"""
    return ax.figure


# ---------- graphviz 结构图 ----------
def _gv(args, rankdir):
    from graphviz import Digraph
    g = Digraph("g", format="png")
    g.attr(rankdir=rankdir, dpi=str(args.dpi or 150), fontname=FONT_NAME, bgcolor="white")
    g.attr("node", fontname=FONT_NAME, fontsize="12", shape="box",
           style="rounded,filled", fillcolor="#EFF6FF", color=BLUE)
    g.attr("edge", fontname=FONT_NAME, fontsize="10", color=MUTED)
    return g


def cmd_flow(args, d):
    g = _gv(args, d.get("rankdir", "LR"))
    for n in d["nodes"]:
        shape = n.get("shape", "box")
        attr = {"label": n["label"]}
        if shape == "diamond":
            attr.update(shape="diamond", fillcolor="#FEF3C7", color=ORANGE)
        elif shape == "circle":
            attr.update(shape="circle")
        g.node(n["id"], **attr)
    for e in d.get("edges", []):
        if isinstance(e, dict):
            g.edge(e["from"], e["to"], label=e.get("label", ""))
        else:
            g.edge(e[0], e[1], label=e[2] if len(e) > 2 else "")
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    g.render(os.path.splitext(out)[0], cleanup=True)
    print(out)
    return out


def cmd_mind(args, d):
    g = _gv(args, "LR")
    g.attr("edge", color="#A78BFA", penwidth="1.2")
    g.attr("node", fillcolor="#F5F3FF", color=PURPLE)
    g.node("root", d["root"], fillcolor=PURPLE, fontcolor="white", fontsize="14")
    for i, (branch, leaves) in enumerate(d.get("children", {}).items()):
        bid = f"b{i}"
        g.node(bid, branch, fontsize="12")
        g.edge("root", bid)
        for j, leaf in enumerate(leaves):
            lid = f"{bid}_{j}"
            g.node(lid, leaf, fontsize="11")
            g.edge(bid, lid)
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    g.render(os.path.splitext(out)[0], cleanup=True)
    print(out)
    return out


# ---------- 甘特 ----------
def cmd_gantt(args, d):
    tasks = d["tasks"]
    fig, ax = plt.subplots(figsize=figsize(args, 11, 0.62 * len(tasks) + 1.8))
    colors = {"blue": BLUE, "green": GREEN, "orange": ORANGE,
              "purple": PURPLE, "cyan": CYAN, "pink": PINK}
    for i, t in enumerate(tasks):
        c = colors.get(t.get("color", "blue"), BLUE)
        ax.barh(i, t["dur"], left=t["start"], height=0.55, color=c, alpha=0.88,
                edgecolor="white")
        ax.text(t["start"] + t["dur"] + (t.get("pad") or 0.08), i, f"{t['dur']:g}",
                va="center", fontsize=9, color=MUTED)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([t["name"] for t in tasks], fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel(d.get("unit", "小时"), fontsize=10, color=MUTED)
    ax.set_title(args.title or "", fontsize=13, pad=12, color=INK)
    ax.grid(axis="x", alpha=0.25)
    return save(bare(ax).figure, args.out)


# ---------- 桑基 ----------
def cmd_sankey(args, d):
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch, Rectangle
    fig, ax = plt.subplots(figsize=figsize(args))
    left, right, flows = d["left"], d["right"], d["flows"]
    total = sum(v for _, v in left)
    gap, height = 0.06, 2.2
    lpos, rpos, y = {}, {}, 0.0
    for n, v in left:
        h = v / total * height; lpos[n] = (y, h); y += h + gap
    y = 0.0
    for n, v in right:
        h = v / total * height; rpos[n] = (y, h); y += h + gap
    color_of = {n: color(i) for i, (n, _) in enumerate(left)}
    lcur = {k: v[0] for k, v in lpos.items()}
    rcur = {k: v[0] for k, v in rpos.items()}
    lsum = dict(left); rsum = dict(right)
    for s, t, v in flows:
        lh = lpos[s][1] * v / lsum[s]
        rh = rpos[t][1] * v / rsum[t]
        y0a, y0b, y1a, y1b = lcur[s], lcur[s] + lh, rcur[t], rcur[t] + rh
        verts = [(0.12, y0a), (0.5, y0a), (0.5, y1a), (0.88, y1a),
                 (0.88, y1b), (0.5, y1b), (0.5, y0b), (0.12, y0b), (0.12, y0a)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
                 Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), facecolor=color_of[s], alpha=0.35,
                               edgecolor="none"))
        lcur[s] += lh; rcur[t] += rh
    for n, (yy, h) in lpos.items():
        ax.add_patch(Rectangle((0.08, yy), 0.04, h, color=color_of[n]))
        ax.text(0.06, yy + h / 2, n, ha="right", va="center", fontsize=11, color=INK)
    for n, (yy, h) in rpos.items():
        ax.add_patch(Rectangle((0.88, yy), 0.04, h, color=INK, alpha=0.8))
        ax.text(0.94, yy + h / 2, n, ha="left", va="center", fontsize=11, color=INK)
    ax.set_xlim(0, 1); ax.set_ylim(-0.1, height + 0.2); ax.axis("off")
    ax.set_title(args.title or "", fontsize=13, pad=8, color=INK)
    return save(fig, args.out)


# ---------- 矩形树 ----------
def cmd_treemap(args, d):
    import squarify
    fig, ax = plt.subplots(figsize=figsize(args))
    names = list(d.keys()); vals = [float(v) for v in d.values()]
    total = sum(vals) or 1
    labels = [f"{n}\n{v / total * 100:.0f}%" if v / total >= 0.06 else n
              for n, v in zip(names, vals)]
    squarify.plot(sizes=vals, label=labels,
                  color=colors(len(names)), alpha=0.88, ax=ax,
                  text_kwargs={"fontsize": 9, "color": "white"})
    ax.axis("off")
    ax.set_title(args.title or "", fontsize=13, pad=10, color=INK)
    return save(_finish(ax), args.out)


# ---------- 网络 ----------
def cmd_network(args, d):
    import networkx as nx
    G = nx.Graph()
    for e in d["edges"]:
        G.add_edge(e[0], e[1])
    pos = nx.spring_layout(G, seed=d.get("seed", 4))
    fig, ax = plt.subplots(figsize=figsize(args, 8.5, 5.6))
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#CBD5E1", width=1.4)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=BLUE, node_size=2600, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_color="white",
                            font_family=FONT_NAME)
    ax.axis("off")
    ax.set_title(args.title or "", fontsize=13, color=INK)
    return save(_finish(ax), args.out)


# ---------- 公式 ----------
def cmd_formula(args, d=None):
    exprs = [e.strip() for e in args.expr.split(";;") if e.strip()]
    n = max(1, len(exprs))
    fig, ax = plt.subplots(figsize=figsize(args, 7, 0.75 * n + 0.8))
    ax.axis("off")
    for i, e in enumerate(exprs):
        y = 1 - (i + 0.5) / n
        ax.text(0.5, y, f"${e}$", ha="center", va="center",
                fontsize=26 if n == 1 else 20)
    fig.tight_layout()
    return save(fig, args.out)


# ---------- demo: one command, twelve charts ----------
DEMOS = {
    "bar": dict(title="每周提交次数",
        data={"周一": 12, "周二": 19, "周三": 15, "周四": 23, "周五": 26, "周六": 8, "周日": 5}),
    "line": dict(title="三条渠道的周访问量",
        data={"小程序": [30, 42, 38, 55, 61], "官网": [22, 26, 31, 29, 35], "App": [50, 48, 60, 72, 80]}),
    "pie": dict(title="一周时间分配",
        data={"开发": 38, "会议": 16, "评审": 12, "文档": 9, "排障": 25}),
    "scatter": dict(title="改动行数 vs 缺陷数", data={"x": [20, 35, 40, 55, 60, 70, 85, 90, 105, 120, 130, 140, 155, 170, 190, 210, 225, 240, 260, 280, 300, 320, 340, 360, 380, 400, 430, 460, 500, 540], "y": [1, 1, 2, 2, 3, 2, 4, 3, 5, 4, 6, 7, 6, 8, 9, 8, 10, 9, 12, 11, 13, 12, 15, 14, 16, 18, 17, 20, 19, 24]}),
    "heatmap": dict(title="每周各时段活跃度",
        data={"matrix": [[12, 18, 25, 22, 30], [35, 40, 38, 45, 50], [48, 52, 44, 60, 65], [70, 66, 72, 68, 80], [55, 60, 58, 62, 70], [30, 35, 28, 40, 45]],
              "rows": ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00"],
              "cols": ["周一", "周二", "周三", "周四", "周五"], "unit": "次"}),
    "flow": dict(title="一个 issue 的处理路径",
        data={"rankdir": "LR",
              "nodes": [{"id": "in", "label": "收到 issue"},
                        {"id": "rep", "label": "能否复现？", "shape": "diamond"},
                        {"id": "fix", "label": "定位并修复"},
                        {"id": "ask", "label": "追问最小复现"},
                        {"id": "done", "label": "关闭", "shape": "circle"}],
              "edges": [["in", "rep"], ["rep", "fix", "能"], ["rep", "ask", "不能"], ["ask", "rep", "补信息"], ["fix", "done"]]}),
    "mind": dict(title="",
        data={"root": "发布流程",
              "children": {"准备": ["写 README", "生成示例图", "加 LICENSE"],
                           "发布": ["建仓库", "推代码", "打 tag"],
                           "推广": ["写一段话", "发到社区", "回评论"]}}),
    "gantt": dict(title="今晚的工作排期",
        data={"unit": "小时",
              "tasks": [{"name": "跨平台改造", "start": 0, "dur": 1.2, "color": "blue"},
                        {"name": "生成 12 张图", "start": 1.2, "dur": 0.5, "color": "green"},
                        {"name": "写 README", "start": 1.7, "dur": 0.8, "color": "orange"},
                        {"name": "推 GitHub", "start": 2.5, "dur": 0.3, "color": "purple"},
                        {"name": "发帖推广", "start": 2.8, "dur": 0.4, "color": "cyan"}]}),
    "sankey": dict(title="流量从哪来、到哪去",
        data={"left": [["搜索", 40], ["社交", 35], ["直链", 25]],
              "right": [["安装", 38], ["看文档", 42], ["离开", 20]],
              "flows": [["搜索", "安装", 16], ["搜索", "看文档", 18], ["搜索", "离开", 6],
                        ["社交", "安装", 12], ["社交", "看文档", 16], ["社交", "离开", 7],
                        ["直链", "安装", 10], ["直链", "看文档", 8], ["直链", "离开", 7]]}),
    "treemap": dict(title="一个仓库的体积构成",
        data={"代码": 45, "文档": 22, "测试": 12, "示例图": 8, "配置": 5, "许可": 3}),
    "network": dict(title="模块依赖",
        data={"edges": [["CLI", "字体"], ["CLI", "配色"], ["CLI", "保存"], ["字体", "系统字体目录"], ["配色", "调色板"], ["保存", "文件系统"], ["CLI", "graphviz"], ["graphviz", "布局引擎"]]}),
    "formula": dict(title="",
        expr=r"\sum_{i=1}^{n} x_i \cdot w_i;;P(y \mid x) = \frac{P(x \mid y)\,P(y)}{P(x)}"),
}


def run_demo(outdir):
    """Render every chart type into outdir. Returns the list of files."""
    os.makedirs(outdir, exist_ok=True)
    made = []
    for i, (kind, spec) in enumerate(DEMOS.items(), 1):
        args = argparse.Namespace(
            title=spec.get("title", ""),
            out=os.path.join(outdir, "%02d-%s.png" % (i, kind)),
            width=None, height=None, dpi=None,
            json_file=None, data=None, expr=spec.get("expr"),
        )
        if kind == "formula":
            cmd_formula(args)
        else:
            CMDS[kind](args, spec["data"])
        made.append(args.out)
    print("%d charts -> %s" % (len(made), os.path.abspath(outdir)))
    return made


# ---------- 入口 ----------
CMDS = {"bar": cmd_bar, "line": cmd_line, "pie": cmd_pie, "scatter": cmd_scatter,
        "heatmap": cmd_heatmap, "flow": cmd_flow, "mind": cmd_mind,
        "gantt": cmd_gantt, "sankey": cmd_sankey, "treemap": cmd_treemap,
        "network": cmd_network}


def _require(dep, hint):
    try:
        __import__(dep)
    except ImportError:
        raise SystemExit("missing dependency: %s\n  pip install %s" % (dep, hint))


HELP_EXAMPLE = "example: viz bar --data {\"a\":1,\"b\":2} --title t --out a.png"


def main():
    ap = argparse.ArgumentParser(description="visual-explain - one command, one chart",
                                 epilog=HELP_EXAMPLE)
    ap.add_argument("kind", nargs="?", choices=list(CMDS) + ["formula"])
    ap.add_argument("--demo", metavar="DIR", help="render all 12 example charts into DIR")
    ap.add_argument("--data", help="inline JSON, or - to read stdin")
    ap.add_argument("--json-file", help="path to a JSON data file")
    ap.add_argument("--expr", help="LaTeX for formula; separate several with ;;")
    ap.add_argument("--title", default="")
    ap.add_argument("--out", help="output image path (required unless --demo)")
    ap.add_argument("--width", type=float)
    ap.add_argument("--height", type=float)
    ap.add_argument("--dpi", type=int)
    args = ap.parse_args()

    if args.demo:
        run_demo(args.demo)
        return
    if not args.kind:
        ap.error("give a chart kind, or --demo DIR")
    if args.kind != "formula" and not args.out:
        ap.error("--out is required")

    if args.kind in ("flow", "mind") and not HAS_GRAPHVIZ:
        raise SystemExit("flow and mind need graphviz: https://graphviz.org/download/")
    if args.kind == "heatmap":
        _require("seaborn", "seaborn")
    if args.kind == "treemap":
        _require("squarify", "squarify")
    if args.kind == "network":
        _require("networkx", "networkx")
    if args.kind == "formula":
        if not args.expr:
            ap.error("formula needs --expr")
        return cmd_formula(args)
    return CMDS[args.kind](args, load(args))


if __name__ == "__main__":
    main()

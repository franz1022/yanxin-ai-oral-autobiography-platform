from __future__ import annotations

from pathlib import Path

import matplotlib

# 终端运行时使用 Agg，避免弹出窗口
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch


# ============================================================
# 0. 输出路径
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "diagrams"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. 可集中修改的样式参数
# ============================================================

FIGURE_DPI = 170

FONT_FAMILY = "DejaVu Sans"
TITLE_FONT_SIZE = 22
SUBTITLE_FONT_SIZE = 11
BOX_TITLE_FONT_SIZE = 11.5
BOX_TEXT_FONT_SIZE = 9.2
LANE_TITLE_FONT_SIZE = 11.5
NOTE_FONT_SIZE = 8.8

BOX_EDGE_WIDTH = 1.5
ARROW_WIDTH = 1.5
ARROW_HEAD_SIZE = 14

COLORS = {
    "background": "#F7F9FC",
    "text": "#1F2937",
    "muted_text": "#5B6472",
    "line": "#6B778C",
    "ui": "#DCEEFF",
    "service": "#E8E2FF",
    "storage": "#DDF5E5",
    "analytics": "#FFF0CC",
    "review": "#FFE0E0",
    "disabled": "#ECEFF3",
    "success": "#DDF4E6",
    "warning": "#FFF3D6",
    "lane_a": "#F2F7FD",
    "lane_b": "#F8F5FF",
    "lane_c": "#F3FAF5",
    "lane_d": "#FFF8EF",
}


# ============================================================
# 2. 通用绘图函数
# ============================================================

def add_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str = "",
    facecolor: str = "#FFFFFF",
    edgecolor: str = "#4B5563",
    title_size: float = BOX_TITLE_FONT_SIZE,
    body_size: float = BOX_TEXT_FONT_SIZE,
    radius: float = 0.14,
) -> None:
    """添加圆角矩形框。"""
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=BOX_EDGE_WIDTH,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(patch)

    ax.text(
        x + w / 2,
        y + h * 0.66,
        title,
        ha="center",
        va="center",
        fontsize=title_size,
        fontweight="bold",
        color=COLORS["text"],
        family=FONT_FAMILY,
    )

    if body:
        ax.text(
            x + w / 2,
            y + h * 0.30,
            body,
            ha="center",
            va="center",
            fontsize=body_size,
            color=COLORS["muted_text"],
            family=FONT_FAMILY,
            linespacing=1.22,
        )


def add_arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = "#667085",
    label: str | None = None,
    label_offset: tuple[float, float] = (0.0, 0.16),
    dashed: bool = False,
) -> None:
    """添加直线箭头。"""
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=ARROW_HEAD_SIZE,
        linewidth=ARROW_WIDTH,
        color=color,
        linestyle="--" if dashed else "-",
        shrinkA=3,
        shrinkB=3,
    )
    ax.add_patch(arrow)

    if label:
        mid_x = (start[0] + end[0]) / 2 + label_offset[0]
        mid_y = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(
            mid_x,
            mid_y,
            label,
            ha="center",
            va="center",
            fontsize=NOTE_FONT_SIZE,
            color=COLORS["muted_text"],
            family=FONT_FAMILY,
            bbox={
                "boxstyle": "round,pad=0.14",
                "facecolor": COLORS["background"],
                "edgecolor": "none",
                "alpha": 0.96,
            },
        )


def add_poly_arrow(
    ax,
    points: list[tuple[float, float]],
    color: str = "#667085",
    label: str | None = None,
    label_xy: tuple[float, float] | None = None,
    dashed: bool = False,
) -> None:
    """添加横平竖直的折线箭头。"""
    if len(points) < 2:
        raise ValueError("At least two points are required.")

    vertices = [points[0]]
    codes = [MplPath.MOVETO]

    for point in points[1:]:
        vertices.append(point)
        codes.append(MplPath.LINETO)

    path = MplPath(vertices, codes)
    line = PathPatch(
        path,
        fill=False,
        linewidth=ARROW_WIDTH,
        edgecolor=color,
        linestyle="--" if dashed else "-",
        capstyle="round",
        joinstyle="round",
    )
    ax.add_patch(line)

    arrow = FancyArrowPatch(
        points[-2],
        points[-1],
        arrowstyle="-|>",
        mutation_scale=ARROW_HEAD_SIZE,
        linewidth=ARROW_WIDTH,
        color=color,
        linestyle="--" if dashed else "-",
        shrinkA=0,
        shrinkB=3,
    )
    ax.add_patch(arrow)

    if label and label_xy:
        ax.text(
            label_xy[0],
            label_xy[1],
            label,
            ha="center",
            va="center",
            fontsize=NOTE_FONT_SIZE,
            color=COLORS["muted_text"],
            family=FONT_FAMILY,
            bbox={
                "boxstyle": "round,pad=0.14",
                "facecolor": COLORS["background"],
                "edgecolor": "none",
                "alpha": 0.96,
            },
        )


def add_lane(
    ax,
    y: float,
    h: float,
    title: str,
    facecolor: str,
    x_left: float = 0.4,
    x_right: float = 19.6,
) -> None:
    """添加泳道背景。"""
    patch = FancyBboxPatch(
        (x_left, y),
        x_right - x_left,
        h,
        boxstyle="round,pad=0.01,rounding_size=0.07",
        linewidth=0.9,
        edgecolor="#D5DAE1",
        facecolor=facecolor,
    )
    ax.add_patch(patch)

    ax.text(
        x_left + 0.2,
        y + h - 0.22,
        title,
        ha="left",
        va="top",
        fontsize=LANE_TITLE_FONT_SIZE,
        fontweight="bold",
        color=COLORS["text"],
        family=FONT_FAMILY,
    )


def add_diamond(
    ax,
    cx: float,
    cy: float,
    w: float,
    h: float,
    text: str,
    facecolor: str = "#FFF3D6",
    edgecolor: str = "#A66B00",
) -> None:
    """添加判断菱形。"""
    points = [
        (cx, cy + h / 2),
        (cx + w / 2, cy),
        (cx, cy - h / 2),
        (cx - w / 2, cy),
    ]
    patch = Polygon(
        points,
        closed=True,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=BOX_EDGE_WIDTH,
    )
    ax.add_patch(patch)

    ax.text(
        cx,
        cy,
        text,
        ha="center",
        va="center",
        fontsize=BOX_TEXT_FONT_SIZE,
        fontweight="bold",
        color=COLORS["text"],
        family=FONT_FAMILY,
        linespacing=1.15,
    )


# ============================================================
# 3. 图一：系统架构图
# ============================================================

def draw_system_architecture() -> None:
    fig, ax = plt.subplots(figsize=(18, 10))
    fig.patch.set_facecolor(COLORS["background"])
    ax.set_facecolor(COLORS["background"])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 11)
    ax.axis("off")

    ax.text(
        0.55,
        10.45,
        "Yanxin V2 System Architecture",
        fontsize=TITLE_FONT_SIZE,
        fontweight="bold",
        color=COLORS["text"],
        family=FONT_FAMILY,
    )
    ax.text(
        0.55,
        10.03,
        "Local-first bilingual extraction, structured storage, evaluation analytics and human review",
        fontsize=SUBTITLE_FONT_SIZE,
        color=COLORS["muted_text"],
        family=FONT_FAMILY,
    )

    # 三层背景
    layer_specs = [
        (8.25, 1.25, "Presentation Layer", COLORS["lane_a"]),
        (5.15, 2.45, "Application Services", COLORS["lane_b"]),
        (1.65, 2.75, "Data, Engines and Evaluation Artefacts", COLORS["lane_c"]),
    ]

    for y, h, title, color in layer_specs:
        add_lane(ax, y, h, title, color, x_left=0.5, x_right=19.4)

    # 第一层
    add_box(
        ax,
        6.6,
        8.52,
        6.8,
        0.78,
        "Streamlit Dashboard",
        "Overview · Projects · Materials · Timeline · Content · Review · Evaluation Analytics",
        facecolor=COLORS["ui"],
        edgecolor="#3B82C4",
        title_size=13,
        body_size=9.5,
    )

    # 第二层：服务
    service_x = [0.95, 4.72, 8.49, 12.26, 16.03]
    service_titles = [
        ("Database Service", "SQLite CRUD\nProject summaries"),
        ("Media Manager", "Validate and store\nphoto/audio files"),
        ("Extraction Provider", "Provider abstraction\nprivacy controls"),
        ("Story Generator", "Biography · Scene\nStoryboard · Prompt"),
        ("Evaluation Analytics", "Development and\nfrozen holdout metrics"),
    ]

    for x, (title, body) in zip(service_x, service_titles):
        is_analytics = title == "Evaluation Analytics"
        add_box(
            ax,
            x,
            5.75,
            3.0,
            1.2,
            title,
            body,
            facecolor=COLORS["analytics"] if is_analytics else COLORS["service"],
            edgecolor="#B47B14" if is_analytics else "#7864B5",
        )

    # 第三层：数据与引擎
    lower_items = [
        (0.95, 2.55, "SQLite Database", "Profiles · Projects\nMaterials · Events · Reviews", COLORS["storage"], "#2F8F57"),
        (4.72, 2.55, "Local Upload Storage", "Project folders\nPhotos and audio", COLORS["storage"], "#2F8F57"),
        (8.49, 2.55, "Rule-Based Extractor", "Chinese–English fields\nConfidence and warnings", COLORS["storage"], "#2F8F57"),
        (12.26, 2.55, "Template Generator", "Editable narrative and\nvisual planning drafts", COLORS["storage"], "#2F8F57"),
        (16.03, 2.55, "Evaluation Snapshot", "Versioned JSON metrics\nFrozen commit and hash", COLORS["storage"], "#2F8F57"),
    ]

    for x, y, title, body, face, edge in lower_items:
        add_box(ax, x, y, 3.0, 1.2, title, body, facecolor=face, edgecolor=edge)

    # Optional provider 放在抽取器下方
    add_box(
        ax,
        8.49,
        1.02,
        3.0,
        0.9,
        "Optional LLM Provider",
        "Registered but disabled",
        facecolor=COLORS["disabled"],
        edgecolor="#8A94A3",
        title_size=10.5,
        body_size=8.7,
    )

    # Human review gate
    add_box(
        ax,
        5.2,
        0.15,
        9.6,
        0.62,
        "Mandatory Human Review Gate",
        "Extracted facts and generated content remain editable until the user confirms them.",
        facecolor=COLORS["review"],
        edgecolor="#C65D5D",
        title_size=11.5,
        body_size=8.8,
    )

    # 界面到服务：统一从主干分流
    add_arrow(ax, (10.0, 8.52), (10.0, 7.72))
    ax.plot([2.45, 17.55], [7.72, 7.72], color=COLORS["line"], linewidth=ARROW_WIDTH)

    for x in [2.45, 6.22, 9.99, 13.76, 17.53]:
        add_arrow(ax, (x, 7.72), (x, 6.95))

    # 服务到对应实现
    for x in [2.45, 6.22, 9.99, 13.76, 17.53]:
        add_arrow(ax, (x, 5.75), (x, 3.75))

    # Provider 到 Optional LLM
    add_arrow(
        ax,
        (9.99, 2.55),
        (9.99, 1.92),
        dashed=True,
        label="future option",
        label_offset=(0.75, 0.0),
    )

    # Review gate：从 Extractor / Generator 下来
    add_poly_arrow(
        ax,
        [(9.99, 2.55), (9.99, 2.15), (8.0, 2.15), (8.0, 0.77)],
        label="reviewable fields",
        label_xy=(8.75, 2.02),
    )
    add_poly_arrow(
        ax,
        [(13.76, 2.55), (13.76, 2.15), (12.0, 2.15), (12.0, 0.77)],
        label="generated drafts",
        label_xy=(12.9, 2.02),
    )

    # Review gate 反馈到数据库
    add_poly_arrow(
        ax,
        [(5.2, 0.46), (2.45, 0.46), (2.45, 2.55)],
        label="confirmed records",
        label_xy=(3.75, 0.62),
    )

    png_path = OUTPUT_DIR / "system_architecture_v2.png"
    svg_path = OUTPUT_DIR / "system_architecture_v2.svg"

    plt.tight_layout()
    fig.savefig(png_path, dpi=FIGURE_DPI, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Created: {png_path}")
    print(f"Created: {svg_path}")


# ============================================================
# 4. 图二：数据和审核工作流
# ============================================================

def draw_data_review_workflow() -> None:
    fig, ax = plt.subplots(figsize=(18, 11))
    fig.patch.set_facecolor(COLORS["background"])
    ax.set_facecolor(COLORS["background"])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 12.5)
    ax.axis("off")

    ax.text(
        0.45,
        11.95,
        "Yanxin V2 Data and Human-Review Workflow",
        fontsize=TITLE_FONT_SIZE,
        fontweight="bold",
        color=COLORS["text"],
        family=FONT_FAMILY,
    )
    ax.text(
        0.45,
        11.53,
        "From source materials to confirmed life events and reviewed autobiography content",
        fontsize=SUBTITLE_FONT_SIZE,
        color=COLORS["muted_text"],
        family=FONT_FAMILY,
    )

    add_lane(ax, 9.0, 2.1, "1. User and Source Materials", COLORS["lane_a"])
    add_lane(ax, 6.35, 2.1, "2. Local Processing and Structured Draft", COLORS["lane_b"])
    add_lane(ax, 3.45, 2.45, "3. Human Review and Confirmed Timeline", COLORS["lane_c"])
    add_lane(ax, 0.55, 2.35, "4. Content Generation and Approval", COLORS["lane_d"])

    # 第一泳道
    input_boxes = [
        (1.0, "Written Memory", "Chinese or English passage"),
        (5.0, "Photo or Audio", "Historical image or voice file"),
        (9.0, "Source Metadata", "Year · Location · People\nDescription"),
        (13.0, "Local Material Record", "SQLite metadata + local path"),
    ]

    for x, title, body in input_boxes:
        face = COLORS["storage"] if title == "Local Material Record" else COLORS["ui"]
        edge = "#2F8F57" if title == "Local Material Record" else "#3B82C4"
        add_box(ax, x, 9.42, 3.1, 1.12, title, body, facecolor=face, edgecolor=edge)

    add_arrow(ax, (4.1, 9.98), (9.0, 9.98))
    add_arrow(ax, (8.1, 9.72), (9.0, 9.72))
    add_arrow(ax, (12.1, 9.98), (13.0, 9.98))

    # 第二泳道
    add_box(
        ax,
        1.0,
        6.77,
        3.1,
        1.12,
        "Provider Selection",
        "Rule-based local mode\nLLM mode disabled",
        facecolor=COLORS["service"],
        edgecolor="#7864B5",
    )
    add_box(
        ax,
        5.0,
        6.77,
        3.1,
        1.12,
        "Bilingual Extraction",
        "Title · Years · Location\nPeople · Emotion",
        facecolor=COLORS["service"],
        edgecolor="#7864B5",
    )
    add_box(
        ax,
        9.0,
        6.77,
        3.1,
        1.12,
        "Reviewable Draft",
        "Confidence values\nWarnings · Source link",
        facecolor=COLORS["warning"],
        edgecolor="#B47B14",
    )

    add_arrow(ax, (4.1, 7.33), (5.0, 7.33))
    add_arrow(ax, (8.1, 7.33), (9.0, 7.33))

    # 第一泳道到第二泳道
    add_poly_arrow(
        ax,
        [(14.55, 9.42), (14.55, 8.65), (2.55, 8.65), (2.55, 7.89)],
        label="selected text memory",
        label_xy=(8.55, 8.78),
    )

    # 第三泳道
    add_box(
        ax,
        1.0,
        4.13,
        3.1,
        1.15,
        "Human Review and Edit",
        "Correct title, place, people,\nyears and emotional tone",
        facecolor=COLORS["review"],
        edgecolor="#C65D5D",
    )
    add_diamond(
        ax,
        6.3,
        4.70,
        2.45,
        1.35,
        "Confirm\nthis draft?",
        facecolor=COLORS["warning"],
    )
    add_box(
        ax,
        8.7,
        4.13,
        3.1,
        1.15,
        "Confirm and Save",
        "Only reviewed fields are written",
        facecolor=COLORS["success"],
        edgecolor="#2F8F57",
    )
    add_box(
        ax,
        12.5,
        4.13,
        3.1,
        1.15,
        "Life Event Record",
        "Confirmed structured event\nwith optional source material",
        facecolor=COLORS["storage"],
        edgecolor="#2F8F57",
    )
    add_box(
        ax,
        16.3,
        4.13,
        2.6,
        1.15,
        "Editable Timeline",
        "Ordered life events",
        facecolor=COLORS["storage"],
        edgecolor="#2F8F57",
    )
    add_box(
        ax,
        5.05,
        3.50,
        2.5,
        0.42,
        "Discard Draft",
        "",
        facecolor=COLORS["disabled"],
        edgecolor="#8A94A3",
        title_size=9.5,
    )

    # Draft 下到 Human Review
    add_poly_arrow(
        ax,
        [(10.55, 6.77), (10.55, 6.10), (2.55, 6.10), (2.55, 5.28)],
        label="nothing is saved yet",
        label_xy=(6.65, 6.22),
    )

    add_arrow(ax, (4.1, 4.70), (5.08, 4.70))
    add_arrow(ax, (7.52, 4.70), (8.7, 4.70), label="Yes")
    add_arrow(ax, (11.8, 4.70), (12.5, 4.70))
    add_arrow(ax, (15.6, 4.70), (16.3, 4.70))

    add_arrow(
        ax,
        (6.3, 4.02),
        (6.3, 3.92),
        label="No",
        label_offset=(0.38, -0.02),
    )

    # 第四泳道
    add_box(
        ax,
        1.0,
        1.15,
        3.1,
        1.12,
        "Generate Drafts",
        "Biography · Chapter · Scene\nStoryboard · Video prompt",
        facecolor=COLORS["service"],
        edgecolor="#7864B5",
    )
    add_box(
        ax,
        5.0,
        1.15,
        3.1,
        1.12,
        "Human Content Review",
        "Check wording, sources\nand unsupported details",
        facecolor=COLORS["review"],
        edgecolor="#C65D5D",
    )
    add_box(
        ax,
        9.0,
        1.15,
        3.1,
        1.12,
        "Review Status",
        "Draft · Reviewed\nApproved · Rejected",
        facecolor=COLORS["warning"],
        edgecolor="#B47B14",
    )
    add_box(
        ax,
        13.0,
        1.15,
        3.6,
        1.12,
        "Approved Portfolio Output",
        "Editable autobiography content\nwith visible AI notice",
        facecolor=COLORS["success"],
        edgecolor="#2F8F57",
    )

    add_poly_arrow(
        ax,
        [(17.6, 4.13), (17.6, 3.16), (2.55, 3.16), (2.55, 2.27)],
        label="selected life events",
        label_xy=(9.9, 3.28),
    )
    add_arrow(ax, (4.1, 1.71), (5.0, 1.71))
    add_arrow(ax, (8.1, 1.71), (9.0, 1.71))
    add_arrow(ax, (12.1, 1.71), (13.0, 1.71))

    ax.text(
        17.7,
        7.30,
        "Extraction remains a draft\nuntil explicit confirmation.",
        ha="center",
        va="center",
        fontsize=NOTE_FONT_SIZE,
        color="#A44949",
        family=FONT_FAMILY,
        fontweight="bold",
    )
    ax.text(
        17.85,
        1.71,
        "Generated content remains\neditable and reviewable.",
        ha="center",
        va="center",
        fontsize=NOTE_FONT_SIZE,
        color=COLORS["muted_text"],
        family=FONT_FAMILY,
    )

    png_path = OUTPUT_DIR / "data_review_workflow_v2.png"
    svg_path = OUTPUT_DIR / "data_review_workflow_v2.svg"

    plt.tight_layout()
    fig.savefig(png_path, dpi=FIGURE_DPI, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Created: {png_path}")
    print(f"Created: {svg_path}")


# ============================================================
# 5. 主程序
# ============================================================

def main() -> None:
    draw_system_architecture()
    draw_data_review_workflow()
    print("Yanxin V2 diagrams generated successfully.")


if __name__ == "__main__":
    main()

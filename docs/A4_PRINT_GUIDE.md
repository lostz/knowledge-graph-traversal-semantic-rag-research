# Plotly A4 打印指南

本指南介绍如何使用 Plotly 生成适合 A4 纸打印的可视化图表。

## 功能概述

我们提供了**两种方法**来生成 A4 打印优化的 HTML 文件：

### 方法 1: 静态图片版本（推荐 ⭐）

使用 Jinja2 模板 + Base64 编码的静态图片

- **`save_figure_for_a4_print_static()`** - 保存单个图表（静态）
- **`save_multiple_figures_for_a4_print_static()`** - 保存多个图表为多页文档（静态）

**优点：**
- ✅ 文件完全自包含（图片以 base64 嵌入）
- ✅ 不依赖外部 Plotly.js 库
- ✅ 打印效果最稳定
- ✅ 加载速度快
- ✅ 可离线查看

**需要安装：** `pip install jinja2 kaleido`

### 方法 2: 交互式版本

使用 Plotly.js 的动态交互图表

- **`save_figure_for_a4_print()`** - 保存单个图表（交互式）
- **`save_multiple_figures_for_a4_print()`** - 保存多个图表为多页文档（交互式）

**优点：**
- ✅ 浏览器中可交互（缩放、旋转、悬停）
- ✅ 图表动态渲染

## A4 纸张尺寸

- **纵向 (Portrait)**: 210mm × 297mm
  - 可用内容区域: 约 700px × 850px
  - 适合：柱状图、折线图、竖向布局的图表

- **横向 (Landscape)**: 297mm × 210mm
  - 可用内容区域: 约 1000px × 600px
  - 适合：3D 图表、宽度较大的图表、横向对比图

## 快速开始

### 方法 1: 静态图片版本（推荐）

#### 1.1 基本用法 - 单个图表

```python
from utils.plotly_visualizer import save_figure_for_a4_print_static
import plotly.graph_objects as go

# 创建你的 Plotly 图表
fig = go.Figure(data=[...])
fig.update_layout(title="My Chart")

# 保存为 A4 打印优化的静态版本
save_figure_for_a4_print_static(
    fig=fig,
    output_path="output/my_chart.html",
    orientation="portrait",  # 或 "landscape"
    title="图表标题",
    description="这里可以添加图表的说明文字",
    image_quality=2  # 1-4，数值越大质量越高
)
```

#### 1.2 多个图表 - 生成静态报告

```python
from utils.plotly_visualizer import save_multiple_figures_for_a4_print_static

# 准备多个图表
figures = [
    (fig1, "第一个图表标题", "第一个图表的说明"),
    (fig2, "第二个图表标题", "第二个图表的说明"),
    (fig3, "第三个图表标题", "第三个图表的说明"),
]

# 保存为多页静态文档
save_multiple_figures_for_a4_print_static(
    figures=figures,
    output_path="output/report.html",
    orientation="portrait",
    main_title="分析报告",
    image_quality=2
)
```

#### 1.3 与现有代码集成（静态版本）

```python
from utils.plotly_visualizer import (
    create_algorithm_visualization,
    save_figure_for_a4_print_static
)

# 1. 创建可视化
fig = create_algorithm_visualization(
    result=result,
    query=query,
    knowledge_graph=kg,
    method='pca'
)

# 2. 保存为静态打印优化版本
save_figure_for_a4_print_static(
    fig=fig,
    output_path='output/printable_visualization.html',
    orientation='landscape',  # 3D 图表建议使用横向
    title=f'{result.algorithm_name} 可视化',
    description=f'查询: {query}',
    image_quality=3  # 高质量
)
```

### 方法 2: 交互式版本

#### 2.1 基本用法 - 单个图表

```python
from utils.plotly_visualizer import save_figure_for_a4_print
import plotly.graph_objects as go

# 创建你的 Plotly 图表
fig = go.Figure(data=[...])
fig.update_layout(title="My Chart")

# 保存为 A4 打印优化版本（交互式）
save_figure_for_a4_print(
    fig=fig,
    output_path="output/my_chart_interactive.html",
    orientation="portrait",
    title="图表标题",
    description="这里可以添加图表的说明文字"
)
```

#### 2.2 多个图表 - 生成交互式报告

```python
from utils.plotly_visualizer import save_multiple_figures_for_a4_print

figures = [
    (fig1, "第一个图表标题", "第一个图表的说明"),
    (fig2, "第二个图表标题", "第二个图表的说明"),
    (fig3, "第三个图表标题", "第三个图表的说明"),
]

save_multiple_figures_for_a4_print(
    figures=figures,
    output_path="output/report_interactive.html",
    orientation="portrait",
    main_title="分析报告"
)
```

## 打印步骤

生成 HTML 文件后，按以下步骤打印或保存为 PDF：

### 方法 1: 浏览器打印为 PDF（推荐）

1. 在 Chrome/Edge/Firefox 中打开生成的 HTML 文件
2. 按 `Ctrl+P` (Windows/Linux) 或 `Cmd+P` (Mac)
3. 在打印对话框中：
   - **目标打印机**: 选择"保存为 PDF"
   - **纸张大小**: A4
   - **边距**: 默认
   - **选项**: 建议取消勾选"页眉和页脚"
4. 点击"保存"

### 方法 2: 直接打印

1. 打开 HTML 文件
2. 按 `Ctrl+P` 或点击页面右上角的"🖨️ 打印"按钮
3. 选择打印机
4. 确认纸张大小为 A4
5. 打印

## 参数说明

### `save_figure_for_a4_print()`

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `fig` | `go.Figure` | Plotly 图表对象 | 必填 |
| `output_path` | `str` | 输出文件路径 | 必填 |
| `orientation` | `str` | 页面方向: "portrait" 或 "landscape" | "portrait" |
| `title` | `str` | 页面标题 | "Knowledge Graph Visualization" |
| `description` | `str` | 图表说明文字 | "" |

### `save_multiple_figures_for_a4_print()`

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `figures` | `List[Tuple]` | 列表，每项为 (图表, 标题, 说明) | 必填 |
| `output_path` | `str` | 输出文件路径 | 必填 |
| `orientation` | `str` | 页面方向 | "portrait" |
| `main_title` | `str` | 文档总标题 | "Knowledge Graph Analysis Report" |

## 示例代码

完整的示例代码请查看：`examples/plotly_a4_print_example.py`

运行示例：

```bash
python examples/plotly_a4_print_example.py
```

这将生成三个示例文件在 `output/` 目录：
- `example_1_portrait.html` - 单图表纵向布局
- `example_2_landscape.html` - 单图表横向布局
- `example_3_multi_page.html` - 多图表多页文档

## 技术细节

### 图表尺寸优化

代码自动根据 A4 纸张大小和方向设置最佳图表尺寸：

```python
# 纵向
width = 700px   # 约 185mm
height = 850px  # 约 225mm

# 横向
width = 1000px  # 约 265mm
height = 600px  # 约 159mm
```

### CSS 打印优化

HTML 模板包含专门的打印样式：
- 使用 `@media print` 优化打印输出
- 使用 `@page` 设置 A4 纸张大小
- 自动分页，避免图表被切割
- 隐藏不必要的屏幕元素

### 交互性保留

- 生成的 HTML 在浏览器中仍然是交互式的
- 可以缩放、旋转 3D 图表
- 打印时自动转换为静态输出

## 常见问题

### Q: 打印出来的图表太小/太大？

A: 可以调整图表的 `margin` 参数，或者在打印对话框中调整缩放比例。

### Q: 可以修改默认的图表尺寸吗？

A: 可以。在 `plotly_visualizer.py` 中找到 `save_figure_for_a4_print()` 函数，修改 `width` 和 `height` 变量。

### Q: 如何添加页码或水印？

A: 修改 `plotly_a4_print_template.html` 中的 `.page-footer` 部分。

### Q: 能否导出为图片格式（PNG/PDF）？

A: 如果需要直接导出图片，使用 `kaleido`：

```bash
pip install kaleido
```

```python
fig.write_image("output.png", width=1920, height=1080, scale=2)
fig.write_image("output.pdf", width=800, height=600)
```

但建议使用本指南的 HTML → 浏览器打印 → PDF 方式，效果更好。

## 文件说明

- `utils/plotly_visualizer.py` - 主要功能代码
- `utils/plotly_a4_print_template.html` - HTML 模板文件
- `examples/plotly_a4_print_example.py` - 完整示例代码
- `docs/A4_PRINT_GUIDE.md` - 本指南

## 更新日志

- 2025-11: 初始版本，支持单图表和多图表 A4 打印优化

# Plotly A4 打印功能

## 快速链接

- 📖 [快速入门指南](A4_PRINT_QUICK_START.md) - 1 分钟上手
- 📚 [完整使用指南](A4_PRINT_GUIDE.md) - 详细文档
- ⚖️ [方法对比](A4_PRINT_COMPARISON.md) - 选择最适合你的方法

## 一句话说明

**将 Plotly 图表转换为适合 A4 纸打印的 HTML 文件，支持两种方式：**
1. **静态图片版本**（推荐）：Jinja2 + Base64，完全自包含
2. **交互式版本**：Plotly.js，可交互

## 30 秒快速开始

### 静态版本（推荐）

```python
from utils.plotly_visualizer import save_figure_for_a4_print_static

save_figure_for_a4_print_static(
    fig=your_plotly_figure,
    output_path="output/report.html",
    orientation="landscape",  # 或 "portrait"
    title="我的图表",
    image_quality=2  # 1-4
)
```

### 交互式版本

```python
from utils.plotly_visualizer import save_figure_for_a4_print

save_figure_for_a4_print(
    fig=your_plotly_figure,
    output_path="output/report.html",
    orientation="landscape",
    title="我的图表"
)
```

## 安装依赖

```bash
# 静态版本（推荐）
pip install plotly jinja2 kaleido

# 交互式版本
pip install plotly
```

## 运行示例

```bash
# 静态版本示例
python examples/plotly_a4_static_example.py

# 交互式版本示例
python examples/plotly_a4_print_example.py
```

## 主要功能

✅ **A4 纸张优化**
- 纵向: 210mm × 297mm (700×850px)
- 横向: 297mm × 210mm (1000×600px)

✅ **两种实现方式**
- 静态图片（Base64 PNG）
- 交互式图表（Plotly.js）

✅ **单图表和多图表**
- 单个图表保存
- 多图表自动分页

✅ **打印优化**
- 专门的 CSS 打印样式
- 自动分页避免切割
- 一键打印/保存 PDF

✅ **灵活配置**
- 自定义标题和描述
- 可调节图片质量
- 支持纵向/横向

## 文件结构

```
utils/
├── plotly_visualizer.py              # 主要功能代码
├── plotly_a4_print_template.html     # 交互式版本模板
└── plotly_a4_jinja2_template.html    # 静态版本模板

examples/
├── plotly_a4_static_example.py       # 静态版本示例
└── plotly_a4_print_example.py        # 交互式版本示例

docs/
├── PLOTLY_A4_PRINTING_README.md      # 本文件
├── A4_PRINT_QUICK_START.md           # 快速入门
├── A4_PRINT_GUIDE.md                 # 完整指南
└── A4_PRINT_COMPARISON.md            # 方法对比
```

## API 参考

### 静态图片版本

#### `save_figure_for_a4_print_static()`

单个图表保存为静态 HTML。

```python
save_figure_for_a4_print_static(
    fig: go.Figure,              # Plotly 图表对象
    output_path: str,            # 输出路径
    orientation: str = "portrait",  # "portrait" 或 "landscape"
    title: str = "...",          # 页面标题
    description: str = "",       # 图表说明
    image_quality: int = 2       # 1-4，数值越大质量越高
) -> str
```

#### `save_multiple_figures_for_a4_print_static()`

多个图表保存为多页静态 HTML。

```python
save_multiple_figures_for_a4_print_static(
    figures: List[Tuple[go.Figure, str, str]],  # [(图表, 标题, 描述), ...]
    output_path: str,            # 输出路径
    orientation: str = "portrait",
    main_title: str = "...",     # 总标题
    image_quality: int = 2
) -> str
```

### 交互式版本

#### `save_figure_for_a4_print()`

单个图表保存为交互式 HTML。

```python
save_figure_for_a4_print(
    fig: go.Figure,
    output_path: str,
    orientation: str = "portrait",
    title: str = "...",
    description: str = ""
) -> str
```

#### `save_multiple_figures_for_a4_print()`

多个图表保存为多页交互式 HTML。

```python
save_multiple_figures_for_a4_print(
    figures: List[Tuple[go.Figure, str, str]],
    output_path: str,
    orientation: str = "portrait",
    main_title: str = "..."
) -> str
```

### 辅助函数

#### `figure_to_base64()`

将 Plotly 图表转换为 base64 编码的图片。

```python
figure_to_base64(
    fig: go.Figure,
    width: int = 1200,
    height: int = 800,
    scale: int = 2,
    format: str = 'png'
) -> str
```

## 常见使用场景

### 场景 1: 生成技术报告

```python
from utils.plotly_visualizer import save_multiple_figures_for_a4_print_static

figures = [
    (performance_fig, "性能对比", "各算法的性能指标对比"),
    (accuracy_fig, "准确率分析", "不同参数下的准确率"),
    (time_fig, "时间开销", "算法运行时间对比")
]

save_multiple_figures_for_a4_print_static(
    figures=figures,
    output_path="output/tech_report.html",
    orientation="portrait",
    main_title="技术分析报告",
    image_quality=2
)
```

### 场景 2: 知识图谱可视化

```python
from utils.plotly_visualizer import (
    create_algorithm_visualization,
    save_figure_for_a4_print_static
)

# 创建知识图谱可视化
fig = create_algorithm_visualization(
    result=retrieval_result,
    query=query,
    knowledge_graph=kg,
    method='pca'
)

# 保存为 A4 打印版本
save_figure_for_a4_print_static(
    fig=fig,
    output_path='output/kg_visualization.html',
    orientation='landscape',  # 3D 图表用横向
    title=f'{retrieval_result.algorithm_name} 可视化',
    description=f'查询: {query}',
    image_quality=3
)
```

### 场景 3: 快速预览

```python
# 低质量快速生成预览
save_figure_for_a4_print_static(
    fig=fig,
    output_path="preview.html",
    image_quality=1  # 快速预览
)
```

### 场景 4: 高质量出版

```python
# 高质量用于出版
save_figure_for_a4_print_static(
    fig=fig,
    output_path="publication.html",
    image_quality=4  # 最高质量
)
```

## 打印到 PDF

生成 HTML 后：

1. 在 Chrome/Edge/Firefox 中打开
2. 按 `Ctrl+P` (Windows/Linux) 或 `Cmd+P` (Mac)
3. 选择"保存为 PDF"
4. 确认纸张为 A4
5. 保存

## 常见问题

**Q: 应该选择哪种方法？**
A: 如果需要打印或发送报告，选择静态版本。如果需要在线演示和交互，选择交互式版本。

**Q: kaleido 安装失败怎么办？**
A: 可以尝试 `pip install --upgrade kaleido` 或查看 [kaleido 文档](https://github.com/plotly/Kaleido)。

**Q: 如何调整图表大小？**
A: 图表大小已经针对 A4 纸优化。如需微调，可以修改 `plotly_visualizer.py` 中的 `width` 和 `height` 变量。

**Q: 可以自定义模板吗？**
A: 可以。修改 `utils/plotly_a4_jinja2_template.html` 或 `utils/plotly_a4_print_template.html`。

## 更多信息

- [完整使用指南](A4_PRINT_GUIDE.md)
- [方法对比](A4_PRINT_COMPARISON.md)
- [快速入门](A4_PRINT_QUICK_START.md)

## 版本历史

- **v1.0** (2025-11) - 初始版本
  - 支持静态图片版本（Jinja2 + Base64）
  - 支持交互式版本（Plotly.js）
  - 单图表和多图表支持
  - A4 纸张优化
  - 纵向和横向布局

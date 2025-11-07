# Plotly A4 打印快速入门

## 两种方法

### 方法 1: 静态图片版本（推荐 ⭐）

**使用 Jinja2 模板 + Base64 编码的静态图片**

优点：
- ✅ 文件完全自包含，不依赖外部 JS
- ✅ 打印效果最稳定
- ✅ 加载速度快
- ✅ 可离线查看

```python
from utils.plotly_visualizer import save_figure_for_a4_print_static

# 假设你已经有一个 Plotly figure 对象
fig = create_algorithm_visualization(result, query, kg)

# 保存为 A4 打印优化的静态 HTML
save_figure_for_a4_print_static(
    fig=fig,
    output_path="output/my_visualization.html",
    orientation="landscape",  # 横向，适合 3D 图
    title="知识图谱可视化",
    description="这是我的知识图谱遍历可视化结果",
    image_quality=2  # 1-4，数值越大质量越高
)
```

需要安装：`pip install jinja2 kaleido`

### 方法 2: 交互式版本

**使用 Plotly.js 的交互式图表**

优点：
- ✅ 浏览器中可交互（缩放、旋转）
- ✅ 图表动态渲染

```python
from utils.plotly_visualizer import save_figure_for_a4_print

fig = create_algorithm_visualization(result, query, kg)

save_figure_for_a4_print(
    fig=fig,
    output_path="output/my_visualization.html",
    orientation="landscape",
    title="知识图谱可视化",
    description="这是我的知识图谱遍历可视化结果"
)
```

### 3. 打印为 PDF

1. 在浏览器中打开 `output/my_visualization.html`
2. 按 `Ctrl+P` 打开打印对话框
3. 选择"保存为 PDF"
4. 点击保存

完成！

## 关键点

### 选择方向

- **纵向 (portrait)**: 适合柱状图、折线图
  ```python
  orientation="portrait"  # 700×850px
  ```

- **横向 (landscape)**: 适合 3D 图、宽图表
  ```python
  orientation="landscape"  # 1000×600px
  ```

### 多图表报告

```python
from utils.plotly_visualizer import save_multiple_figures_for_a4_print

figures = [
    (fig1, "算法性能对比", "不同算法的 Precision/Recall 对比"),
    (fig2, "3D 节点分布", "知识图谱节点的语义空间分布"),
    (fig3, "训练曲线", "模型训练过程"),
]

save_multiple_figures_for_a4_print(
    figures=figures,
    output_path="output/report.html",
    orientation="portrait",
    main_title="知识图谱分析报告"
)
```

## 完整示例

运行示例代码：

```bash
python examples/plotly_a4_print_example.py
```

查看详细文档：`docs/A4_PRINT_GUIDE.md`

## 效果预览

生成的 HTML 文件具有：
- ✅ A4 纸张适配的图表尺寸
- ✅ 专业的页眉和页脚
- ✅ 浏览器中仍可交互（缩放、旋转）
- ✅ 打印时自动优化布局
- ✅ 一键打印/导出为 PDF
- ✅ 多图表自动分页

就这么简单！

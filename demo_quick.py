#!/usr/bin/env python3
"""
最简单的 A4 打印 Demo - 快速版本
直接使用核心函数，避免复杂依赖
"""
import plotly.graph_objects as go
import os
from pathlib import Path

# 直接从文件导入，避免导入整个 utils 包
import sys
sys.path.insert(0, str(Path(__file__).parent))

# 检查依赖
try:
    from jinja2 import Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

try:
    import kaleido
    HAS_KALEIDO = True
except ImportError:
    HAS_KALEIDO = False

print("="*60)
print("📦 依赖检查:")
print(f"   Plotly: ✅")
print(f"   Jinja2: {'✅' if HAS_JINJA2 else '❌ (pip install jinja2)'}")
print(f"   Kaleido: {'✅' if HAS_KALEIDO else '❌ (pip install kaleido)'}")
print("="*60)

# 导入核心函数
if HAS_JINJA2 and HAS_KALEIDO:
    print("\n使用静态版本（推荐）")
    from utils.plotly_visualizer import save_figure_for_a4_print_static as save_func
    USE_STATIC = True
else:
    print("\n使用交互式版本")
    from utils.plotly_visualizer import save_figure_for_a4_print as save_func
    USE_STATIC = False

# 创建简单的柱状图
print("\n📊 创建示例图表...")
fig = go.Figure(data=[
    go.Bar(
        name='算法 A',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.85, 0.82, 0.83],
        marker_color='#FF6B6B'
    ),
    go.Bar(
        name='算法 B',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.78, 0.90, 0.84],
        marker_color='#4ECDC4'
    ),
    go.Bar(
        name='算法 C',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.92, 0.88, 0.90],
        marker_color='#45B7D1'
    )
])

fig.update_layout(
    title='算法性能对比',
    xaxis_title='指标',
    yaxis_title='得分',
    barmode='group',
    yaxis=dict(range=[0, 1])
)

# 保存
os.makedirs("output", exist_ok=True)

print("\n🎨 生成 A4 打印版本...")
if USE_STATIC:
    output_file = save_func(
        fig=fig,
        output_path="output/demo.html",
        orientation="portrait",
        title="算法性能对比分析",
        description="这是一个示例图表，展示了三种算法在 Precision、Recall 和 F1-Score 三个指标上的表现。算法 C 表现最佳。",
        image_quality=2
    )
else:
    output_file = save_func(
        fig=fig,
        output_path="output/demo.html",
        orientation="portrait",
        title="算法性能对比分析",
        description="这是一个示例图表，展示了三种算法在 Precision、Recall 和 F1-Score 三个指标上的表现。算法 C 表现最佳。"
    )

print("\n" + "="*60)
print("✅ Demo 完成！")
print("="*60)
print(f"\n📁 生成的文件: {output_file}")
print(f"   文件类型: {'静态图片版本' if USE_STATIC else '交互式版本'}")
print(f"\n🖥️  如何查看:")
print(f"   在浏览器中打开该文件")
print(f"\n🖨️  如何打印:")
print(f"   在浏览器中按 Ctrl+P (或 Cmd+P)")
print(f"   选择 '保存为 PDF' → 选择 A4 纸张 → 保存")
print("\n" + "="*60)

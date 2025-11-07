#!/usr/bin/env python3
"""
最简单的 A4 打印 Demo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import plotly.graph_objects as go

# 检查是否可以使用静态版本
try:
    import jinja2
    import kaleido
    USE_STATIC = True
    print("✅ 将使用静态版本（Jinja2 + Base64）")
except ImportError:
    USE_STATIC = False
    print("⚠️  将使用交互式版本（缺少 jinja2 或 kaleido）")

from utils.plotly_visualizer import (
    save_figure_for_a4_print,
    save_figure_for_a4_print_static
)

# 创建一个简单的柱状图
print("\n📊 创建示例图表...")
fig = go.Figure(data=[
    go.Bar(
        name='算法 A',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.85, 0.82, 0.83],
        marker_color='indianred'
    ),
    go.Bar(
        name='算法 B',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.78, 0.90, 0.84],
        marker_color='lightsalmon'
    ),
    go.Bar(
        name='算法 C',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.92, 0.88, 0.90],
        marker_color='lightseagreen'
    )
])

fig.update_layout(
    title='算法性能对比',
    xaxis_title='指标',
    yaxis_title='得分',
    barmode='group',
    yaxis=dict(range=[0, 1])
)

# 保存为 A4 打印版本
os.makedirs("output", exist_ok=True)

if USE_STATIC:
    print("\n🎨 生成静态版本...")
    output_file = save_figure_for_a4_print_static(
        fig=fig,
        output_path="output/demo_static.html",
        orientation="portrait",
        title="算法性能对比分析",
        description="这是一个简单的示例图表，展示三种算法在不同指标上的表现。",
        image_quality=2
    )
else:
    print("\n🎨 生成交互式版本...")
    output_file = save_figure_for_a4_print(
        fig=fig,
        output_path="output/demo_interactive.html",
        orientation="portrait",
        title="算法性能对比分析",
        description="这是一个简单的示例图表，展示三种算法在不同指标上的表现。"
    )

print("\n" + "="*60)
print("✅ Demo 完成！")
print("="*60)
print(f"\n📁 文件位置: {output_file}")
print("\n🖥️  查看方式:")
print("   1. 在文件浏览器中找到该文件")
print("   2. 双击用浏览器打开")
print("   3. 按 Ctrl+P 可以打印或保存为 PDF")
print("\n💡 提示:")
if USE_STATIC:
    print("   - 这是静态版本，图片已嵌入 HTML")
    print("   - 文件可以离线查看，无需网络")
else:
    print("   - 这是交互式版本，可以悬停查看数据")
    print("   - 安装 jinja2 和 kaleido 可使用静态版本:")
    print("     pip install jinja2 kaleido")
print()

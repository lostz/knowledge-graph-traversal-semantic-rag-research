#!/usr/bin/env python3
"""
示例：如何使用 Plotly 生成适合 A4 打印的可视化图表

这个示例展示了：
1. 如何为单个图表生成 A4 打印优化的 HTML
2. 如何为多个图表生成多页 A4 文档
3. 纵向和横向布局的使用
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils.plotly_visualizer import (
    save_figure_for_a4_print,
    save_multiple_figures_for_a4_print
)


def create_sample_3d_figure():
    """创建一个示例 3D 图表"""
    # 生成示例数据
    np.random.seed(42)
    n_points = 100

    x = np.random.randn(n_points)
    y = np.random.randn(n_points)
    z = np.random.randn(n_points)
    colors = np.random.choice(['red', 'blue', 'green'], n_points)

    fig = go.Figure(data=[
        go.Scatter3d(
            x=x[colors == 'red'],
            y=y[colors == 'red'],
            z=z[colors == 'red'],
            mode='markers',
            marker=dict(size=8, color='red'),
            name='Category A'
        ),
        go.Scatter3d(
            x=x[colors == 'blue'],
            y=y[colors == 'blue'],
            z=z[colors == 'blue'],
            mode='markers',
            marker=dict(size=8, color='blue'),
            name='Category B'
        ),
        go.Scatter3d(
            x=x[colors == 'green'],
            y=y[colors == 'green'],
            z=z[colors == 'green'],
            mode='markers',
            marker=dict(size=8, color='green'),
            name='Category C'
        )
    ])

    fig.update_layout(
        title="3D Scatter Plot - Knowledge Graph Nodes",
        scene=dict(
            xaxis_title='Dimension 1',
            yaxis_title='Dimension 2',
            zaxis_title='Dimension 3'
        ),
        legend=dict(x=0.02, y=0.98)
    )

    return fig


def create_sample_2d_figure():
    """创建一个示例 2D 图表"""
    # 生成示例数据
    categories = ['Algorithm 1', 'Algorithm 2', 'Algorithm 3', 'Algorithm 4']
    precision = [0.85, 0.78, 0.92, 0.88]
    recall = [0.82, 0.90, 0.87, 0.85]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Precision',
        x=categories,
        y=precision,
        marker_color='indianred'
    ))

    fig.add_trace(go.Bar(
        name='Recall',
        x=categories,
        y=recall,
        marker_color='lightsalmon'
    ))

    fig.update_layout(
        title='Algorithm Performance Comparison',
        xaxis_title='Algorithms',
        yaxis_title='Score',
        barmode='group',
        yaxis=dict(range=[0, 1])
    )

    return fig


def create_sample_line_chart():
    """创建一个示例折线图"""
    x = list(range(1, 11))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=[0.5, 0.6, 0.65, 0.7, 0.75, 0.78, 0.82, 0.85, 0.87, 0.90],
        mode='lines+markers',
        name='Training Score',
        line=dict(color='blue', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=[0.48, 0.55, 0.58, 0.62, 0.65, 0.67, 0.70, 0.72, 0.73, 0.75],
        mode='lines+markers',
        name='Validation Score',
        line=dict(color='red', width=3, dash='dash')
    ))

    fig.update_layout(
        title='Training Progress Over Time',
        xaxis_title='Epoch',
        yaxis_title='Score',
        legend=dict(x=0.02, y=0.98)
    )

    return fig


def example_1_single_figure_portrait():
    """示例 1: 保存单个图表为 A4 纵向页面"""
    print("=" * 60)
    print("示例 1: 单个图表 - A4 纵向布局")
    print("=" * 60)

    fig = create_sample_3d_figure()

    output_path = save_figure_for_a4_print(
        fig=fig,
        output_path="output/example_1_portrait.html",
        orientation="portrait",
        title="3D Knowledge Graph Visualization",
        description="这是一个 3D 散点图，展示了知识图谱中节点在降维后的分布情况。不同颜色代表不同的类别。"
    )

    print(f"\n✅ 文件已保存，请在浏览器中打开: {output_path}")
    print("   在浏览器中按 Ctrl+P 打开打印对话框")
    print("   选择 '保存为 PDF' 即可导出为 PDF 文件\n")


def example_2_single_figure_landscape():
    """示例 2: 保存单个图表为 A4 横向页面"""
    print("=" * 60)
    print("示例 2: 单个图表 - A4 横向布局")
    print("=" * 60)

    fig = create_sample_2d_figure()

    output_path = save_figure_for_a4_print(
        fig=fig,
        output_path="output/example_2_landscape.html",
        orientation="landscape",
        title="Algorithm Performance Comparison",
        description="横向布局更适合宽度较大的图表，如柱状图对比。"
    )

    print(f"\n✅ 文件已保存，请在浏览器中打开: {output_path}\n")


def example_3_multiple_figures():
    """示例 3: 保存多个图表为多页 A4 文档"""
    print("=" * 60)
    print("示例 3: 多个图表 - 多页 A4 文档")
    print("=" * 60)

    # 创建多个图表
    figures = [
        (
            create_sample_3d_figure(),
            "3D Node Distribution",
            "第一页：展示知识图谱节点的 3D 分布情况"
        ),
        (
            create_sample_2d_figure(),
            "Performance Metrics",
            "第二页：不同算法的性能对比"
        ),
        (
            create_sample_line_chart(),
            "Training Progress",
            "第三页：模型训练过程中的性能变化"
        )
    ]

    output_path = save_multiple_figures_for_a4_print(
        figures=figures,
        output_path="output/example_3_multi_page.html",
        orientation="portrait",
        main_title="Knowledge Graph Analysis Report"
    )

    print(f"\n✅ 多页文件已保存: {output_path}")
    print("   打印时每个图表会自动分页\n")


def example_4_use_with_existing_visualization():
    """示例 4: 结合现有的 knowledge graph visualization 使用"""
    print("=" * 60)
    print("示例 4: 与现有可视化代码集成")
    print("=" * 60)

    print("\n如果你已经有一个 RetrievalResult 对象，可以这样使用：\n")
    print("```python")
    print("from utils.plotly_visualizer import create_algorithm_visualization, save_figure_for_a4_print")
    print("")
    print("# 1. 创建普通可视化")
    print("fig = create_algorithm_visualization(")
    print("    result=result,")
    print("    query=query,")
    print("    knowledge_graph=kg,")
    print("    method='pca'")
    print(")")
    print("")
    print("# 2. 保存为 A4 打印优化版本")
    print("save_figure_for_a4_print(")
    print("    fig=fig,")
    print("    output_path='output/kg_visualization_printable.html',")
    print("    orientation='landscape',  # 3D 图表通常用横向更好")
    print("    title=f'{result.algorithm_name} Visualization',")
    print("    description=f'Query: {query}'")
    print(")")
    print("```\n")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Plotly A4 打印优化示例")
    print("=" * 60 + "\n")

    # 创建输出目录
    os.makedirs("output", exist_ok=True)

    # 运行各个示例
    example_1_single_figure_portrait()
    example_2_single_figure_landscape()
    example_3_multiple_figures()
    example_4_use_with_existing_visualization()

    print("=" * 60)
    print("所有示例已完成！")
    print("=" * 60)
    print("\n📋 使用提示：")
    print("1. 在浏览器中打开生成的 HTML 文件")
    print("2. 按 Ctrl+P (或 Cmd+P) 打开打印对话框")
    print("3. 选择 '保存为 PDF' 作为目标打印机")
    print("4. 确保纸张大小设置为 A4")
    print("5. 建议关闭 '页眉和页脚' 选项以获得更好效果")
    print("\n💡 尺寸说明：")
    print("   - 纵向 (portrait): 700x850px, 适合 A4 纵向")
    print("   - 横向 (landscape): 1000x600px, 适合 A4 横向")
    print("   - 这些尺寸已经考虑了打印边距和页面布局\n")


if __name__ == "__main__":
    main()

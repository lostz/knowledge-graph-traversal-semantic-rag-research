#!/usr/bin/env python3
"""
示例：使用 Jinja2 模板和 Base64 图片生成 A4 打印优化的静态 HTML

这个方法的优点：
1. 文件完全自包含（图片以 base64 嵌入）
2. 不依赖外部 Plotly.js 库
3. 打印效果更稳定
4. 加载速度更快
5. 可以离线查看

需要安装：
    pip install plotly jinja2 kaleido
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotly.graph_objects as go
import numpy as np
from utils.plotly_visualizer import (
    save_figure_for_a4_print_static,
    save_multiple_figures_for_a4_print_static,
    figure_to_base64
)


def create_sample_3d_scatter():
    """创建一个 3D 散点图示例"""
    np.random.seed(42)
    n = 80

    x = np.random.randn(n)
    y = np.random.randn(n)
    z = np.random.randn(n)

    fig = go.Figure(data=[
        go.Scatter3d(
            x=x[:30], y=y[:30], z=z[:30],
            mode='markers',
            marker=dict(size=8, color='red', opacity=0.8),
            name='类别 A'
        ),
        go.Scatter3d(
            x=x[30:60], y=y[30:60], z=z[30:60],
            mode='markers',
            marker=dict(size=8, color='blue', opacity=0.8),
            name='类别 B'
        ),
        go.Scatter3d(
            x=x[60:], y=y[60:], z=z[60:],
            mode='markers',
            marker=dict(size=8, color='green', opacity=0.8),
            name='类别 C'
        )
    ])

    fig.update_layout(
        title="知识图谱节点 3D 分布",
        scene=dict(
            xaxis_title='维度 1',
            yaxis_title='维度 2',
            zaxis_title='维度 3',
            bgcolor='rgba(240,240,240,0.9)'
        ),
        legend=dict(x=0.02, y=0.98)
    )

    return fig


def create_sample_bar_chart():
    """创建一个柱状图示例"""
    algorithms = ['基础检索', '查询遍历', '主题遍历', '混合遍历']
    precision = [0.82, 0.88, 0.85, 0.91]
    recall = [0.79, 0.85, 0.90, 0.87]
    f1_score = [0.805, 0.865, 0.875, 0.89]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Precision',
        x=algorithms,
        y=precision,
        marker_color='#FF6B6B'
    ))

    fig.add_trace(go.Bar(
        name='Recall',
        x=algorithms,
        y=recall,
        marker_color='#4ECDC4'
    ))

    fig.add_trace(go.Bar(
        name='F1 Score',
        x=algorithms,
        y=f1_score,
        marker_color='#45B7D1'
    ))

    fig.update_layout(
        title='算法性能对比',
        xaxis_title='算法',
        yaxis_title='得分',
        barmode='group',
        yaxis=dict(range=[0, 1]),
        legend=dict(x=0.02, y=0.98)
    )

    return fig


def create_sample_line_chart():
    """创建一个折线图示例"""
    epochs = list(range(1, 11))
    train_score = [0.50, 0.62, 0.68, 0.73, 0.77, 0.81, 0.84, 0.86, 0.88, 0.90]
    val_score = [0.48, 0.58, 0.63, 0.67, 0.70, 0.72, 0.74, 0.75, 0.76, 0.77]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=epochs,
        y=train_score,
        mode='lines+markers',
        name='训练集',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=10)
    ))

    fig.add_trace(go.Scatter(
        x=epochs,
        y=val_score,
        mode='lines+markers',
        name='验证集',
        line=dict(color='#4ECDC4', width=3, dash='dash'),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title='训练进度',
        xaxis_title='Epoch',
        yaxis_title='得分',
        yaxis=dict(range=[0.4, 1.0]),
        legend=dict(x=0.02, y=0.98),
        hovermode='x unified'
    )

    return fig


def create_sample_heatmap():
    """创建一个热力图示例"""
    algorithms = ['算法 A', '算法 B', '算法 C', '算法 D']
    metrics = ['Precision', 'Recall', 'F1', 'Speed', 'Memory']

    # 模拟性能数据
    np.random.seed(42)
    data = np.random.rand(len(metrics), len(algorithms)) * 100

    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=algorithms,
        y=metrics,
        colorscale='Viridis',
        text=np.round(data, 1),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="得分")
    ))

    fig.update_layout(
        title='算法性能热力图',
        xaxis_title='算法',
        yaxis_title='指标'
    )

    return fig


def example_1_single_static_portrait():
    """示例 1: 单图表静态版本 - 纵向"""
    print("=" * 60)
    print("示例 1: 单图表静态版本 - A4 纵向（Jinja2 + Base64）")
    print("=" * 60)

    fig = create_sample_bar_chart()

    output_path = save_figure_for_a4_print_static(
        fig=fig,
        output_path="output/static_portrait.html",
        orientation="portrait",
        title="算法性能对比分析",
        description="此图表对比了四种不同知识图谱遍历算法的性能指标，包括 Precision、Recall 和 F1 Score。",
        image_quality=2  # 1-4, 数值越大图片质量越高
    )

    print(f"\n✅ 静态 HTML 已保存: {output_path}")
    print("   文件是完全自包含的，图片以 base64 编码嵌入\n")


def example_2_single_static_landscape():
    """示例 2: 单图表静态版本 - 横向"""
    print("=" * 60)
    print("示例 2: 单图表静态版本 - A4 横向（Jinja2 + Base64）")
    print("=" * 60)

    fig = create_sample_3d_scatter()

    output_path = save_figure_for_a4_print_static(
        fig=fig,
        output_path="output/static_landscape.html",
        orientation="landscape",
        title="知识图谱 3D 可视化",
        description="3D 散点图展示了经过 PCA 降维后的知识图谱节点分布。不同颜色代表不同的语义类别。",
        image_quality=3  # 更高质量的图片
    )

    print(f"\n✅ 静态 HTML 已保存: {output_path}\n")


def example_3_multi_page_static():
    """示例 3: 多页静态报告"""
    print("=" * 60)
    print("示例 3: 多页静态报告（Jinja2 + Base64）")
    print("=" * 60)

    figures = [
        (
            create_sample_3d_scatter(),
            "3D 节点分布",
            "第一页：展示知识图谱节点在语义空间中的 3D 分布情况"
        ),
        (
            create_sample_bar_chart(),
            "算法性能对比",
            "第二页：不同遍历算法的性能指标对比"
        ),
        (
            create_sample_line_chart(),
            "训练进度曲线",
            "第三页：模型训练过程中性能的变化趋势"
        ),
        (
            create_sample_heatmap(),
            "性能热力图",
            "第四页：算法在各个指标上的综合表现"
        )
    ]

    output_path = save_multiple_figures_for_a4_print_static(
        figures=figures,
        output_path="output/static_multi_page_report.html",
        orientation="portrait",
        main_title="知识图谱遍历算法分析报告",
        image_quality=2
    )

    print(f"\n✅ 多页静态报告已保存: {output_path}\n")


def example_4_base64_conversion():
    """示例 4: 直接获取图表的 base64 编码"""
    print("=" * 60)
    print("示例 4: 直接转换图表为 base64 字符串")
    print("=" * 60)

    fig = create_sample_bar_chart()

    # 直接转换为 base64
    base64_str = figure_to_base64(
        fig,
        width=800,
        height=600,
        scale=2,
        format='png'
    )

    print(f"✅ Base64 字符串长度: {len(base64_str)} 字符")
    print(f"   图片大小: {len(base64_str) / 1024:.1f} KB")
    print(f"   前 100 个字符: {base64_str[:100]}...")
    print("\n   可以直接在 HTML 中使用:")
    print(f'   <img src="data:image/png;base64,{base64_str[:50]}..." />\n')


def example_5_integration_with_kg():
    """示例 5: 与现有知识图谱可视化集成"""
    print("=" * 60)
    print("示例 5: 与知识图谱可视化集成示例")
    print("=" * 60)

    print("\n如果你已经使用 create_algorithm_visualization() 创建了图表:\n")
    print("```python")
    print("from utils.plotly_visualizer import (")
    print("    create_algorithm_visualization,")
    print("    save_figure_for_a4_print_static")
    print(")")
    print("")
    print("# 1. 创建可视化")
    print("fig = create_algorithm_visualization(")
    print("    result=result,")
    print("    query=query,")
    print("    knowledge_graph=kg,")
    print("    method='pca'")
    print(")")
    print("")
    print("# 2. 保存为静态 A4 版本（推荐）")
    print("save_figure_for_a4_print_static(")
    print("    fig=fig,")
    print("    output_path='output/kg_static.html',")
    print("    orientation='landscape',")
    print("    title=f'{result.algorithm_name} 可视化',")
    print("    description=f'查询: {query}',")
    print("    image_quality=3  # 高质量图片")
    print(")")
    print("```\n")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Plotly A4 静态打印示例（Jinja2 + Base64）")
    print("=" * 60 + "\n")

    print("📦 依赖检查...")
    try:
        import plotly
        print("   ✅ plotly 已安装")
    except ImportError:
        print("   ❌ plotly 未安装: pip install plotly")
        return

    try:
        import jinja2
        print("   ✅ jinja2 已安装")
    except ImportError:
        print("   ❌ jinja2 未安装: pip install jinja2")
        return

    try:
        import kaleido
        print("   ✅ kaleido 已安装")
    except ImportError:
        print("   ⚠️  kaleido 未安装（将使用 plotly.io 作为后备）")
        print("       建议安装: pip install kaleido")

    print()

    # 创建输出目录
    os.makedirs("output", exist_ok=True)

    # 运行各个示例
    try:
        example_1_single_static_portrait()
        example_2_single_static_landscape()
        example_3_multi_page_static()
        example_4_base64_conversion()
        example_5_integration_with_kg()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请确保已安装所有依赖:")
        print("   pip install plotly jinja2 kaleido")
        return

    print("=" * 60)
    print("所有示例已完成！")
    print("=" * 60)
    print("\n📋 静态版本的优点：")
    print("   ✅ 文件完全自包含（图片以 base64 嵌入）")
    print("   ✅ 不依赖外部 Plotly.js 库")
    print("   ✅ 打印效果更稳定")
    print("   ✅ 加载速度更快")
    print("   ✅ 可以离线查看")
    print("\n📊 图片质量设置:")
    print("   image_quality=1  低质量，文件小")
    print("   image_quality=2  标准质量（推荐）")
    print("   image_quality=3  高质量")
    print("   image_quality=4  超高质量，文件大")
    print("\n🖨️  打印步骤：")
    print("   1. 在浏览器中打开生成的 HTML 文件")
    print("   2. 按 Ctrl+P（或点击打印按钮）")
    print("   3. 选择 '保存为 PDF'")
    print("   4. 确认纸张为 A4")
    print("   5. 保存\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
完全独立的 A4 打印 Demo
不需要其他依赖，只需要 plotly
"""
import plotly.graph_objects as go
import os

print("="*60)
print("🎨 Plotly A4 打印 Demo")
print("="*60)

# 创建一个简单漂亮的柱状图
print("\n📊 创建示例图表...")
fig = go.Figure(data=[
    go.Bar(
        name='算法 A',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.85, 0.82, 0.83],
        marker_color='#FF6B6B',
        text=[0.85, 0.82, 0.83],
        textposition='auto',
    ),
    go.Bar(
        name='算法 B',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.78, 0.90, 0.84],
        marker_color='#4ECDC4',
        text=[0.78, 0.90, 0.84],
        textposition='auto',
    ),
    go.Bar(
        name='算法 C',
        x=['Precision', 'Recall', 'F1-Score'],
        y=[0.92, 0.88, 0.90],
        marker_color='#45B7D1',
        text=[0.92, 0.88, 0.90],
        textposition='auto',
    )
])

# 设置适合 A4 纵向打印的尺寸
fig.update_layout(
    title={
        'text': '算法性能对比分析',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    xaxis_title='指标',
    yaxis_title='得分',
    barmode='group',
    yaxis=dict(range=[0, 1]),
    width=700,   # A4 纵向宽度
    height=850,  # A4 纵向高度
    margin=dict(l=50, r=50, t=100, b=50),
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(size=12),
    legend=dict(
        x=0.5,
        y=-0.15,
        xanchor='center',
        yanchor='top',
        orientation='h'
    )
)

# 创建 HTML 内容
print("\n🎨 生成 A4 打印版本（交互式）...")

html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>算法性能对比分析</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Arial", "Microsoft YaHei", sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }
        .page {
            background: white;
            margin: 0 auto 20px auto;
            padding: 20mm;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 210mm;
            min-height: 297mm;
            position: relative;
        }
        .page-header {
            text-align: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #333;
        }
        .page-header h1 {
            font-size: 24px;
            color: #333;
            margin-bottom: 5px;
        }
        .page-header .subtitle {
            font-size: 14px;
            color: #666;
        }
        .chart-description {
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-left: 4px solid #4CAF50;
            font-size: 14px;
            line-height: 1.6;
        }
        .chart-container {
            width: 100%;
            margin: 10px 0;
        }
        .page-footer {
            position: absolute;
            bottom: 15mm;
            left: 20mm;
            right: 20mm;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 5px;
        }
        .print-button {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        .print-button:hover {
            background-color: #45a049;
        }
        @media print {
            body {
                background: white;
                padding: 0;
                margin: 0;
            }
            .page {
                margin: 0;
                padding: 20mm;
                box-shadow: none;
                page-break-after: always;
                width: 210mm;
                height: 297mm;
            }
            .page:last-child {
                page-break-after: auto;
            }
            .chart-container {
                page-break-inside: avoid;
            }
            .print-button {
                display: none !important;
            }
        }
        @page {
            size: A4 portrait;
            margin: 0;
        }
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">🖨️ 打印 / 保存为PDF</button>

    <div class="page">
        <div class="page-header">
            <h1>算法性能对比分析</h1>
            <div class="subtitle">Demo - Plotly A4 打印示例</div>
        </div>

        <div class="chart-description">
            这是一个示例图表，展示了三种算法在 <strong>Precision</strong>、<strong>Recall</strong> 和 <strong>F1-Score</strong> 三个指标上的表现。
            从图表可以看出，<strong>算法 C</strong> 在综合表现上最佳，<strong>算法 B</strong> 在 Recall 指标上表现突出。
        </div>

        <div class="chart-container" id="chart"></div>

        <div class="page-footer">
            Page 1 | Generated with Plotly
        </div>
    </div>

    <script>
        var data = {plot_data};
        var layout = {plot_layout};
        Plotly.newPlot('chart', data, layout, {
            displayModeBar: false,
            responsive: true
        });
    </script>
</body>
</html>
"""

# 获取图表数据
plot_data = fig.to_dict()['data']
plot_layout = fig.to_dict()['layout']

# 替换占位符
import json
html_content = html_template.replace('{plot_data}', json.dumps(plot_data))
html_content = html_content.replace('{plot_layout}', json.dumps(plot_layout))

# 保存文件
os.makedirs("output", exist_ok=True)
output_file = "output/standalone_demo.html"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n" + "="*60)
print("✅ Demo 完成！")
print("="*60)
print(f"\n📁 生成的文件: {output_file}")
print(f"   文件大小: {os.path.getsize(output_file) / 1024:.1f} KB")
print(f"   文件类型: 交互式 HTML (带 Plotly.js)")
print(f"\n🖥️  如何查看:")
print(f"   方式1: 在文件浏览器中双击该文件")
print(f"   方式2: 在浏览器中打开: file://{os.path.abspath(output_file)}")
print(f"\n🖨️  如何打印为 PDF:")
print(f"   1. 在浏览器中打开该文件")
print(f"   2. 按 Ctrl+P (Windows/Linux) 或 Cmd+P (Mac)")
print(f"   3. 选择 '保存为 PDF'")
print(f"   4. 纸张大小选择 A4")
print(f"   5. 点击保存")
print(f"\n💡 特点:")
print(f"   ✅ A4 纸张尺寸优化 (210x297mm)")
print(f"   ✅ 可以悬停查看数据点")
print(f"   ✅ 点击图例可以显示/隐藏数据系列")
print(f"   ✅ 专业的打印样式")
print(f"   ✅ 右上角有打印按钮")
print("\n" + "="*60)

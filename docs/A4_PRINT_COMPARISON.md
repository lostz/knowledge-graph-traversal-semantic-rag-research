# Plotly A4 打印方法对比

## 两种方法对比

| 特性 | 静态图片版本 ⭐ | 交互式版本 |
|------|----------------|-----------|
| **技术** | Jinja2 + Base64 PNG | Plotly.js |
| **文件依赖** | 完全自包含 | 需要加载外部 JS |
| **打印稳定性** | ⭐⭐⭐⭐⭐ 最稳定 | ⭐⭐⭐ 较稳定 |
| **加载速度** | ⭐⭐⭐⭐⭐ 很快 | ⭐⭐⭐ 中等 |
| **文件大小** | 中等（图片 base64） | 小（需下载 JS） |
| **离线查看** | ✅ 完全支持 | ❌ 首次需联网 |
| **交互性** | ❌ 无交互 | ✅ 可缩放旋转 |
| **图片质量** | 可调节（1-4） | 自动 |
| **适用场景** | 打印、报告、归档 | 在线演示、探索 |

## 推荐使用场景

### 使用静态图片版本（推荐）

**适合以下情况：**
1. 📄 需要打印成纸质文档
2. 📧 通过邮件发送报告
3. 📁 长期归档保存
4. 🌐 可能在无网络环境下查看
5. 📱 在移动设备上查看
6. 🖨️ 需要最稳定的打印效果

**示例代码：**
```python
from utils.plotly_visualizer import save_figure_for_a4_print_static

save_figure_for_a4_print_static(
    fig=fig,
    output_path="output/report.html",
    orientation="landscape",
    title="分析报告",
    image_quality=2  # 标准质量
)
```

### 使用交互式版本

**适合以下情况：**
1. 💻 在线演示和展示
2. 🔍 需要用户探索数据
3. 📊 3D 图表需要旋转查看
4. 🎯 希望用户能悬停查看详情

**示例代码：**
```python
from utils.plotly_visualizer import save_figure_for_a4_print

save_figure_for_a4_print(
    fig=fig,
    output_path="output/interactive_report.html",
    orientation="landscape",
    title="交互式分析报告"
)
```

## 图片质量设置（仅静态版本）

| image_quality | 分辨率倍数 | 文件大小 | 适用场景 |
|---------------|-----------|---------|---------|
| 1 | 1x | 最小 | 快速预览 |
| 2 | 2x | 中等 | **标准打印（推荐）** |
| 3 | 3x | 较大 | 高质量打印 |
| 4 | 4x | 最大 | 出版级质量 |

## 依赖包安装

### 静态图片版本
```bash
pip install plotly jinja2 kaleido
```

### 交互式版本
```bash
pip install plotly
```

## 实际示例

### 示例 1: 生成会议报告（使用静态版本）

```python
from utils.plotly_visualizer import save_multiple_figures_for_a4_print_static

# 准备多个图表
figures = [
    (performance_chart, "性能对比", "各算法的性能指标对比"),
    (trend_chart, "趋势分析", "性能随时间的变化趋势"),
    (distribution_3d, "3D 分布", "数据在语义空间的分布")
]

# 生成静态报告
save_multiple_figures_for_a4_print_static(
    figures=figures,
    output_path="output/meeting_report_2025.html",
    orientation="portrait",
    main_title="2025 年第一季度分析报告",
    image_quality=2
)
```

**优点：**
- 文件可以直接发送给所有人
- 不担心网络问题
- 打印效果完全一致
- 可以永久保存

### 示例 2: 在线演示（使用交互式版本）

```python
from utils.plotly_visualizer import save_figure_for_a4_print

# 创建交互式 3D 图表
save_figure_for_a4_print(
    fig=interactive_3d_chart,
    output_path="output/demo.html",
    orientation="landscape",
    title="交互式 3D 演示"
)
```

**优点：**
- 观众可以旋转、缩放 3D 图表
- 悬停可以查看详细数据
- 更有吸引力

## 总结

- **打印/报告** → 使用静态图片版本 ⭐
- **在线演示** → 使用交互式版本
- **不确定？** → 使用静态图片版本，更稳定

## 快速决策流程

```
需要打印或发送报告？
    └─ 是 → 使用静态图片版本
    └─ 否 → 需要用户交互探索数据？
            └─ 是 → 使用交互式版本
            └─ 否 → 使用静态图片版本
```

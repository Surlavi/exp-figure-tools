快速将实验结果批量生成实验图的工具

基于Python 2和[matplotlib](https://matplotlib.org/)

---
## 环境要求
- Python 2
- matplotlib >= 2.0
- Latex环境
- Windows下建议使用wsl

## 使用说明

- 执行脚本run.py，脚本将读取list.json中的数据列表，根据配置绘制图像
- list.json格式
```
[
    {
        "file": "", // 数据文件名，数据格式要求见下
        "y_label": "", // 纵轴label
        // 以下为非必需项
        "output": "", // 输出文件名，默认为输入文件名后缀换为pdf
        "style": 1, // 预设的格式，可选1~4，默认为1，分别对应chart文件夹中rcParams_x.json，纸张大小分别为8x4, 6.3x4，12x9.6,type为4的时候是长宽比14:6
        "chart.type": "", // 输出图表类型，可选"line"(折线图)或"bar"(柱状图)，默认为折线图
        "xtick.lim": [0, 0.8], // x轴显示范围
        "xtick.interval": 0.2, // x轴刻度间隔
        "ytick.lim": [0, 0.8], // y轴，同上
        "ytick.interval": 0.2,
        "marker": false, // 是否显示数据点，默认为true
        "separator": "," // 数据分割字符，默认为空白字符（空格、制表符）
    }
]
```

- 输入数据格式
  - 参考a.dat及b.dat，要求为文本文件，后缀名任意
  - 输入数据为表格，以空白字符分割（空格、制表符）；或者其他任意字符分割，请在config中指明
  - 第一行为标题信息
  - 第一列为对应的x值，第一列第一个元素用于显示x label
  - 其余列为不同组下的y值，每列第一个元素用于显示图例
- 其他说明
  - 所有文本支持latex语法，如`$\alpha$`
  - 注意json语法，如{}和[]的最后一个元素后不能包含逗号
- 待完善功能
  - 错误提示

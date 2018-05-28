ExpFigureTool是快速将实验结果批量生成实验图（折线图，柱状图）的工具

基于Python和[matplotlib](https://matplotlib.org/)

## 环境要求
- Python 2 or 3 (python 3支持测试中)
- matplotlib >= 2.0
- future库 (`pip install future`)
- Latex环境
- Windows下建议使用wsl

## 使用教程

- 在有了实验数据文件之后，需要编写一个json文件，用来表示如何从实验数据生成实验图，参考`demo/list.json`，具体说明见下

- 执行`python run.py list.json`即可根据`list.json`绘图，

- list.json文件中包含一个json数组，这个数组有若干个FigItem组成，每一个FigItem表示由一个数据文件绘制一张实验图

  ```javascript
  [
      {
          // FigItem
      },
      {
          // Another FigItem
      }
      // ...
  ]
  ```

- 每一个FigItem包含以下信息

    ```javascript
    {
        "file": "", // 数据文件名
        // 以下信息非必须，有默认值
        "output": "", // 输出文件名，默认为输入文件名后缀换为pdf
        "style": 1, // 预设的格式，可选1~5，默认为1，分别对应style文件夹中
        "chart.type": "", // 输出图表类型，可选"line"(折线图)或"bar"(柱状图)，默认为折线图
        "separator": "," // 数据分割字符，默认为空白字符（空格、制表符）
    }
    ```

- FigItem根据数据文件的不同可以分为两类

    - 简单表格（参考demo/a.dat，demo/b.dat）
      - 第一行为标题信息

      - 第一列为对应的x值，第一列第一个元素用于显示x label

      - 其余列为不同组下的y值，每列第一个元素用于显示图例

      - FigItem中需包含

        ```javascript
        {
            "y_label": "", // 纵轴label
        }
        ```

    - 数据透视表（参考demo/pivot.dat）

      - 很多情况下实验结果文件以数据透视表（pivot table）的形式呈现，即每一行代表一个项目（实验结果），不同的列代表不同的域，如：

        | Name      | Gender | Age  | Cource  | Score |
        | --------- | ------ | ---- | ------- | ----- |
        | Zhang San | Male   | 18   | Math    | 100   |
        | Li Si     | Male   | 19   | Math    | 98    |
        | Xiao Hong | Female | 20   | English | 95    |

      - ExpFigureTool可以直接根据该格式类型的文件生成实验图

      - 对应的FigItem中需要包含以下项目

        ```javascript
        {
            "file": "", // 数据文件名，同简单表格
            "pivotTable": true, // 表示数据格式为数据透视表
            "pivotTable.category": "Gender", // 表示category的列
            "pivotTable.independentVariable": "Age", // 自变量（x轴）的列
            "pivotTable.value": "Score", // 因变量（y轴）的列
            
            "pivotTable.point": "mean", // 对于每一个点的取值方式，可选mean和median
            "pivotTable.errorBar": "std" // error bar类型，可选min-max,std,percentile
        }
        ```

    - FigItem中的其他常用设置项

      ```javascript
      {
          "xlabel": "Age", // 将覆盖默认显示的x label
          "ylabel": "Score", // 将覆盖默认显示的y label
          "xtick.lim": [0, 0.8], // x轴显示范围
          "xtick.nbins": 3, // x轴最多显示3个label
          "xtick.interval": 0.2, // x轴刻度间隔，不可与nbins同用
          "xticks": [3, 4, 5], // 指定x轴上显示哪些label，适用于数值类型的x轴，覆盖上面除lim外的所有设置，可与对数坐标轴同用
          "ytick.lim": [0, 0.8], // y轴，同上
          "ytick.interval": 0.2,
          "ytick.nbins": 5,
          "yticks": [1, 2, 3],
          "marker": false, // 折线图中是否显示数据点，默认为true
      }
      ```

      

## 其他功能

- 所有文本支持latex语法，如`$\alpha$`
- json文件中支持`//`开头作为注释
- `demo/complex.json`中包含了更多高级功能的使用方法，可作为参考

## 待完善功能

- 错误提示
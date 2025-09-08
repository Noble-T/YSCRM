#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/5/14 10:59 
@Author  : 
@File    : check_excel_data2024051401.py
@ProjectName: CRM


ChatGPT3.5
使用Python中的pandas库来核对两个CSV文件中的数据并标记差异。以下是一个简单的示例，演示如何加载两个CSV文件，比较它们的内容，并将差异数据高亮显示出来。

在这个示例中，我们首先使用 pd.read_csv() 函数加载两个CSV文件为pandas的DataFrame对象 df1 和 df2。然后，我们使用 df1.compare(df2, align_axis=0) 比较这两个DataFrame，并找出它们之间的差异。最后，我们定义了一个 highlight_diff 函数，该函数会将差异数据高亮显示为指定的颜色（这里是黄色），然后应用这个函数来渲染差异的部分。

请注意，这只是一个简单的示例。在实际应用中，您可能需要根据具体需求进一步调整代码，以确保适应您的数据结构和差异标记需求。
'''
import numpy as np
import pandas as pd

# 加载两个CSV文件
file1 = 'path_to_file1.csv'
file2 = 'path_to_file2.csv'

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# 比较两个数据框并找出差异
diff = df1.compare(df2, align_axis=0)

# 将差异数据高亮显示
def highlight_diff(data, color='yellow'):
    attr = 'background-color: {}'.format(color)
    other = data.xs('self', axis='columns', level=-1)
    return pd.DataFrame(np.where(data.ne(other, level=1), attr, ''), index=data.index, columns=data.columns)

diff.style.apply(highlight_diff, axis=None)

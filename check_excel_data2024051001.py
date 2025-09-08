#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2024/5/7 11:07 
@Author  : 
@File    : check_excel_data2024050702.py
@ProjectName: CRM 
'''

"""
天工AI（https://www.tiangong.cn/）-研究模式
"""
import pandas as pd

# 读取CSV文件
df1 = pd.read_csv('file1.csv')
df2 = pd.read_csv('file2.csv')

# 检查两个DataFrame是否完全相同
if df1.equals(df2):
    print('两个DataFrame完全相同')
else:
    print('两个DataFrame不相同')

# 如果你需要找出具体的不同之处，可以使用applymap方法
differences = pd.DataFrame({
    'Row': df1.index,
    'Column': df1.columns,
    'Value': df1.applymap(lambda x: x != df2.values[x]).astype(int)
})

# 打印出不同的数据
print(differences)


"""
天工AI-增强模式
1.使用csv模块进行比较
优点：简单直观，易于理解。
缺点：当CSV文件格式不一致时，可能会导致错误。
"""
import csv

def compare_csv(file1, file2):
    # 读取第一个CSV文件
    with open(file1, 'r') as f1:
        csv1 = csv.reader(f1)
        data1 = [row for row in csv1]
    # 读取第二个CSV文件
    with open(file2, 'r') as f2:
        csv2 = csv.reader(f2)
        data2 = [row for row in csv2]
    # 比较两个CSV文件的内容
    if data1 == data2:
        print("两个CSV文件内容相同")
    else:
        print("两个CSV文件内容不同")
        # 输出不同的数据
        for data in data1:
            if data not in data2:
                print(data)


"""
2.使用pandas进行比较
优点：功能强大，可以很容易地处理丢失数据等情况。
缺点：相比使用csv模块，可能需要更多的内存
"""
import pandas as pd

def compare_pandas(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    # 使用merge方法进行合并，indicator参数用于标识合并的状态
    merged = df1.merge(df2, on=None, how='outer', indicator=True)
    # 筛选出左边独有的数据
    unique_to_df1 = merged[merged['_merge'] == 'left_only']
    # 输出结果
    print(unique_to_df1)


"""
3.使用第三方库csv-diff
优点：简化了比较过程，可以直接在终端中运行。
缺点：需要安装额外的库
"""
import csv_diff

def compare_csv_diff(file1, file2):
    # 安装csv-diff库
    # !pip install csv-diff
    # 使用csv-diff进行比较
    result = csv_diff.compare(load_csv(file1), load_csv(file2))
    # 输出结果
    print(result)


"""
4.逐行比较法
优点：不需要额外依赖，适合处理格式复杂的CSV文件。
缺点：当文件非常大时，可能会有性能问题。
"""
def line_by_line_compare(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()
        # 逐行比较
        for line1, line2 in zip(f1_lines, f2_lines):
            if line1 != line2:
                print(f"Line {line1}")
                print(f"Line {line2}")


"""
综合推荐
综合考虑，如果处理的是相对较小的CSV文件，且对性能要求不高，那么使用csv模块进行比较可能是最简单直接的方法。如果需要处理更大的数据集，且对性能有较高要求，可以考虑使用pandas进行比较。如果想要在命令行中快速进行比较，可以使用csv-diff库。

在实际应用中，可以根据具体情况选择最适合的方法。在进行选择时，应当考虑到数据的大小、可用内存、以及是否需要额外的库等因素
"""



"""
天工AI-简洁模式
在Python中，要核对两张CSV文件并标记它们之间不同的数据，可以使用pandas库来读取和处理CSV文件。以下是一个简单的示例代码：

这个代码段首先读取两个CSV文件为pandas DataFrame对象，然后检查它们的列是否匹配。接着，它定义了一个比较函数compare_rows，该函数接受两行数据作为参数，并返回一个布尔值来指示它们是否完全相同。

最后，代码使用列表推导式创建了一个名为'different'的新列，该列包含了与第二个数据集（df2）进行比较后，标记出不同数据的值。这里的逻辑是，如果compare_rows函数返回True，即有不同的数据，则'different'列对应的值设为1，否则保持为0。

最后，如果需要的话，可以将带有标记的df1保存回一个新的CSV文件中。注意，这里的代码没有考虑到可能存在的重复行，也没有处理缺失值或空值的情况，这些都是实际应用中可能需要考虑的细节。根据具体需求，你可能需要对代码进行调整。
"""
import pandas as pd

# 假设这是你的两个CSV文件路径
file_path1 = 'path/to/your/first.csv'
file_path2 = 'path/to/your/second.csv'

# 读取CSV文件到pandas DataFrame
df1 = pd.read_csv(file_path1)
df2 = pd.read_csv(file_path2)

# 确保两个DataFrame具有相同的列
if set(df1.columns) != set(df2.columns):
    raise ValueError("两个CSV文件的列不匹配")

# 定义一个函数来比较两行数据，并返回一个布尔值表示它们是否相等
def compare_rows(row1, row2):
    for col in df1.columns:
        if row1[col] != row2[col]:
            return False
    return True

# 创建一个新的列来标记不同的数据
df1['different'] = [0 if compare_rows(row1, row2) else 1 for i, row2 in df2.iterrows()]

# 将结果保存到一个新的CSV文件中，如果需要的话
output_file = 'path/to/your/output.csv'
df1.to_csv(output_file, index=False)



"""
天工AI-简洁模式
在Python中，您可以使用pandas库来核对两张CSV文件中的不同数据，并处理可能存在的重复行、缺失值或空值。以下是一个简单的示例代码：

这段代码首先读取了两个CSV文件到pandas的DataFrame对象中。然后，它通过比较两个DataFrame的索引来找出共同的行，并分别标记出只存在于一个DataFrame中的行。最后，它将这两组数据合并，以找出那些在两个DataFrame中都存在但至少有一个字段不同的记录。

请注意，这段代码假设两个CSV文件的列名是完全相同的。如果列名不同，您需要先将它们对齐，或者修改代码来处理不同的列名。此外，如果您的CSV文件包含标题行，并且您不希望将它们作为数据处理，可以在调用read_csv时设置header=0。
"""
import pandas as pd

# 读取第一张CSV文件
df1 = pd.read_csv('file1.csv')

# 读取第二张CSV文件
df2 = pd.read_csv('file2.csv')

# 检查两个DataFrame是否有相同的索引（行名）
same_index = df1.index.intersection(df2.index)

# 标记出第一张CSV中存在而第二张CSV中不存在的数据
not_in_second = df1[~df1.index.isin(same_index)]

# 标记出第二张CSV中存在而第一张CSV中不存在的数据
not_in_first = df2[~df2.index.isin(same_index)]

# 合并结果，并标记出两个CSV中都存在但内容不同的数据
differences = not_in_first[not_in_first.apply(lambda x: any(x != y for y in not_in_second.values), axis=1)]
differences = differences.append(not_in_second[not_in_second.apply(lambda x: any(x != y for y in differences.values), axis=1)])
differences.reset_index(drop=True, inplace=True)

# 输出结果
print("存在于第一张CSV但不在第二张CSV中的数据:")
print(not_in_second)

print("\n存在于第二张CSV但不在第一张CSV中的数据:")
print(not_in_first)

print("\n存在于两张CSV中但内容不同的数据:")
print(differences)
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter

# # 读取Excel文件
# def read_excel_data(filename):
#     return pd.read_excel(filename)

# # 生成图表
# def generate_chart(df, filename):
#     plt.figure(figsize=(10, 5))
#     sns.countplot(x='任务类型', data=df)
#     plt.title('任务类型分布')
#     plt.savefig(filename, bbox_inches='tight')

# # 生成PDF报告
# def generate_pdf_report(pdf_filename, chart_filename, df):
#     c = canvas.Canvas(pdf_filename, pagesize=letter)
#     width, height = letter
    
#     c.setTitle('测试报告')
#     c.setFont("Helvetica-Bold", 18)
#     c.drawString(150, height - 50, '测试报告')
    
#     c.setFont("Helvetica", 12)
#     c.drawString(50, height - 100, '任务类型分布图：')
#     c.drawImage(chart_filename, 50, 150, width=450, height=300)
    
#     c.drawString(50, 50, '数据摘要：')
#     c.drawString(50, 30, str(df.describe()))
#     c.save()

# # 主函数
# def main():
#     excel_filename = '/Users/apple/PycharmProjects/py_locust/abc_crm_app_apiweb/ApiFast/read_execl_report/asks.xlsx'  # Excel文件名
#     chart_filename = 'task_type_distribution.png'
#     pdf_filename = 'test_report.pdf'
    
#     # 读取Excel数据
#     # df = read_excel_data(excel_filename)
#     # from pandas.io.excel._xlrd import open_workbook
#     # from pandas.io.excel._openpyxl import open_workbook
#     df=pd.read_excel(excel_filename,engine='openpyxl')
    
#     # 生成图表
#     generate_chart(df, chart_filename)
    
#     # 生成PDF报告
#     generate_pdf_report(pdf_filename, chart_filename, df)

# if __name__ == '__main__':
#     main()

# excel_filename = '/Users/apple/PycharmProjects/py_locust/abc_crm_app_apiweb/ApiFast/read_execl_report/tasks1.csv'  # Excel文件名

# import pandas as pd
# import matplotlib.pyplot as plt

# # 读取xlsx文件
# file_path = excel_filename  # 替换为你的文件路径
# df = pd.read_excel(file_path)

# # 假设我们想绘制'Sales'列随时间的变化图，其中'Date'列为日期
# # 确保'Date'列被正确解析为日期类型
# df['执行者'] = pd.to_datetime(df['执行者'])

# # 设置'Date'列为索引
# df.set_index('执行者', inplace=True)

# # 绘制'Sales'列的折线图
# plt.figure(figsize=(10, 5))  # 设置图表大小
# plt.plot(df['Sales'], label='Sales')
# plt.title('Sales Over Time')  # 设置图表标题
# plt.xlabel('Date')  # 设置x轴标签
# plt.ylabel('Sales')  # 设置y轴标签
# plt.legend()  # 显示图例
# plt.grid(True)  # 显示网格
# plt.show()  # 显示图表

# import chardet
# with open(excel_filename, 'rb') as f:
#     result = chardet.detect(f.read())
# print(result)
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
# excel_filename # Excel文件名
# excel_filename="/Users/apple/PycharmProjects/py_locust/abc_crm_app_apiweb/ApiFast/read_execl_report/task77.csv"
excel_filename=r'D:/亚商\00-测试报告\【CRM-开发组】任务信息表_20251113.csv'
version="1.0.0"
# 读取CSV文件
df = pd.read_csv(excel_filename,encoding='utf-8')  # 替换'your_file.csv'为你的CSV文件路径
def user_executor():
    task_counts = df['执行者'].value_counts()
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 使用黑体或Arial Unicode MS字体
    mpl.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负数的负号显示问题
    # 生成图表
    plt.figure(figsize=(10, 6))  # 设置图表大小
    task_counts.plot(kind='bar')  # 绘制柱状图
    plt.xlabel('任务类型')  # 设置x轴标签
    plt.ylabel('任务数量')  # 设置y轴标签
    plt.title(str(version)+'###(统计-人员任务)###')  # 设置图表标题
    plt.xticks(rotation=0)  # 旋转x轴标签，以便更好地显示
    # 在图表中标注统计结果
    for i in range(len(task_counts)):
       plt.text(i, task_counts.iloc[i], str(task_counts.iloc[i]), ha='center', va='bottom')
    plt.tight_layout()  # 调整布局，防止标签被截断
    # plt.show()  # 显示图表
    plt.savefig(str(version)+'task_user.png')
def task_type():
    task_counts = df['任务类型'].value_counts()
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 使用黑体或Arial Unicode MS字体
    mpl.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负数的负号显示问题
    # 生成图表
    plt.figure(figsize=(10, 6))  # 设置图表大小
    task_counts.plot(kind='bar')  # 绘制柱状图
    plt.xlabel('任务类型')  # 设置x轴标签
    plt.ylabel('任务数量')  # 设置y轴标签
    plt.title(str(version)+'###(统计-任务数量)###')  # 设置图表标题
    plt.xticks(rotation=0)  # 旋转x轴标签，以便更好地显示
    # 在图表中标注统计结果
    for i in range(len(task_counts)):
       plt.text(i, task_counts.iloc[i], str(task_counts.iloc[i]), ha='center', va='bottom')
    plt.tight_layout()  # 调整布局，防止标签被截断
    # plt.show()  # 显示图表
    plt.savefig(str(version)+'task_type.png')

def task_status():
    task_counts = df['任务状态'].value_counts()
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 使用黑体或Arial Unicode MS字体
    mpl.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负数的负号显示问题
    # 生成图表
    plt.figure(figsize=(10, 6))  # 设置图表大小
    task_counts.plot(kind='bar')  # 绘制柱状图
    plt.xlabel('任务类型')  # 设置x轴标签
    plt.ylabel('任务数量')  # 设置y轴标签
    plt.title(str(version)+'###(统计-任务执行)###')  # 设置图表标题
    plt.xticks(rotation=0)  # 旋转x轴标签，以便更好地显示
    # 在图表中标注统计结果
    for i in range(len(task_counts)):
       plt.text(i, task_counts.iloc[i], str(task_counts.iloc[i]), ha='center', va='bottom')
    plt.tight_layout()  # 调整布局，防止标签被截断
    # plt.show()  # 显示图表
    plt.savefig(str(version)+'task_status.png')

def task_status1():
    task_counts = df['执行者'].value_counts()
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 使用黑体或Arial Unicode MS字体
    mpl.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负数的负号显示问题
    # 生成图表
    plt.figure(figsize=(10, 6))  # 设置图表大小
    task_counts.plot(kind='bar')  # 绘制柱状图
    plt.xlabel('任务类型')  # 设置x轴标签
    plt.ylabel('缺陷分类')  # 设置y轴标签
    plt.title('###(统计-任务执行)###')  # 设置图表标题
    plt.xticks(rotation=0)  # 旋转x轴标签，以便更好地显示
    # 在图表中标注统计结果
    for i in range(len(task_counts)):
       plt.text(i, task_counts.iloc[i], str(task_counts.iloc[i]), ha='center', va='bottom')
    plt.tight_layout()  # 调整布局，防止标签被截断
    # plt.show()  # 显示图表
    plt.savefig(str(version)+'task_status1.png')

user_executor()
task_type()
task_status()

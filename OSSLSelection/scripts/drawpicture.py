from asyncio.windows_events import NULL
import pygal
import csv


file_github = r'E:\OSSLSelection\OSSLSelection\homepage\github_license_usage.csv'
file_libraries = r'E:\OSSLSelection\OSSLSelection\homepage\libraries.io_license_usage.csv'

# pie_chart_github = pygal.Pie()
# pie_chart_github._title = 'Github licenses usage'
# with open(file_github,'r',encoding='utf-8') as f:
#     next(f)
#     reader = csv.reader(f)
#     i = 1
#     for row in reader:
#         if row[0] == NULL:
#             break
#         pie_chart_github.add(row[0],int(row[1]))
#         i += 1
# pie_chart_github.render_to_file(r'E:\oss_license_selection_analyze\github.svg')

pie_chart_libraries = pygal.Pie()
pie_chart_libraries._title = 'Github licenses usage'
with open(file_libraries,'r',encoding='utf-8') as f:
    next(f)
    reader = csv.reader(f)
    for row in reader:
        pie_chart_libraries.add(row[0],int(row[4]))
pie_chart_libraries.render_to_file(r'E:\oss_license_selection_analyze\libraries.svg')



x_labels = []
y_label1 = {}
with open(file_github,'r',encoding='utf-8') as f:
    next(f)
    reader = csv.reader(f)
    i = 1
    for row in reader:
        if i >= 26:
            break
        x_labels.append(row[0])
        y_label1[row[0]] = int(row[1])
        i += 1


y_label2 = {}
with open(file_libraries,'r',encoding='utf-8') as f:
    next(f)
    reader = csv.reader(f)
    i = 1
    for row in reader:
        if i >= 26:
            break
        if row[0] not in x_labels:
            x_labels.append(row[0])
        y_label2[row[0]] = int(row[4])
        i += 1


print(x_labels)
y_11 = []
y_22 = []
for xx in x_labels:
    if xx in y_label1.keys():
        y_11.append(y_label1[xx])
    else:
        y_11.append(0)
    if xx in y_label2.keys():
        y_22.append(y_label2[xx])
    else:
        y_22.append(0)

print(y_11)
print(y_22)


m_config = pygal.Config()
m_config.x_label_rotation = -35
bar_chart = pygal.Bar(m_config)
bar_chart._title = 'The first 20 licenses on Github and Libraries.io'
bar_chart.x_labels = x_labels
bar_chart.add('Github',y_11)
bar_chart.add('Libraries.io',y_22)
bar_chart.render_to_file(r'E:\oss_license_selection_analyze\first25.svg')
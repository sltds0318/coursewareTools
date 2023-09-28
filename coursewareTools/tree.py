from tkinter import *
from tkinter import filedialog, ttk
from tkinter.ttk import Frame

from business.taskConfig import get_school_subject, get_special_education, get_theme_education, get_professional_education

value = {}

a = get_school_subject()
if a.get('error_code') == 0:
    value['学科教育'] = a['data']['stageFilter']
else:
    print("学科教育下的学科学段获取失败，原因：" + a.get('message'))

b = get_theme_education()
if b.get('status') == 200:
    value['专题教育'] = b['data'][0]['children']
else:
    print("特殊教育下的学科学段获取失败，原因：" + b.get('message'))

c = get_special_education()
if c.get('error_code') == 0:
    value['特殊教育'] = c['data']['typeFilters']
else:
    print("特殊教育下的学科学段获取失败，原因：" + c.get('message'))

d = get_professional_education()
if d.get('error_code') == 0:
    value['职业教育'] = d['data']
else:
    print("特殊教育下的学科学段获取失败，原因：" + d.get('message'))

def onSelect(e):
    print(tree.focus())
    itm = tree.set(tree.focus())
    print(itm)

main = Tk()
tree = ttk.Treeview(main, show="tree headings", columns=('id'), displaycolumns=())
for i in value:
    f = tree.insert("", END, text=i, values=i)
    if i == "学科教育":
        for item in value[i]:
            g = tree.insert(f, END, text=item['name'])
            for item1 in item['subjects']:
                h = tree.insert(g, END, text=item1['name'])
                for item2 in item1['bookVersions']:
                    j = tree.insert(h, END, text=item2['name'], values=item2['code'])
    elif i == "特殊教育":
        for item in value[i]:
            g = tree.insert(f, END, text=item['name'])
            for item1 in item['subjectFilters']:
                h = tree.insert(g, END, text=item1['name'])
                for item2 in item1['subjects']:
                    j = tree.insert(h, END, text=item2['name'])
                    for item3 in item2['bookVersions']:
                        k = tree.insert(j, END, text=item3['name'], values=item3['code'])
    elif i == "职业教育":
        for item in value[i]:
            g = tree.insert(f, END, text=item['name'])
            for item1 in item['stages']:
                h = tree.insert(g, END, text=item1['name'])
                for item2 in item1['subjects']:
                    j = tree.insert(h, END, text=item2['name'])
                    for item3 in item2['bookVersions']:
                        k = tree.insert(j, END, text=item3['name'], values=item3['code'])
tree.pack(expand=1, fill=BOTH)
tree.bind("<<TreeviewSelect>>", onSelect)
main.mainloop()
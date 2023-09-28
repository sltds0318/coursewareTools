import os
import threading
import time
import json
import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Frame, Treeview

from business.dbConfig import get_en_cw_test, get_courseware_version
from business.taskConfig import get_courseware_word, get_courseware_maxVersion, upload_courseware, is_thumbnail, \
  get_progress, get_thumbnail_finish, get_courseware_uid, courseware_approve, courseware_shelf, courseware_disapprove, \
  get_school_subject, get_theme_education, get_special_education, get_professional_education
from business.userConfig import get_user_token, get_resource, get_resource_user_token


class SwitchFrame(object):
    def __init__(self, root):
        self.root = root
        root.title('coursewareTools')
        root.geometry('500x500')
        root.resizable(width=False, height=False)  # 阻止Python GUI的大小调整

        Label(root, text='章节选择：').grid(row=0, column=0)
        self.bookvalue = Entry(root, width=40)
        self.bookvalue.grid(row=0, column=1)
        Button(root, text="选择章节", command=self.select).grid(row=0, column=2, padx=10)

    def get_textbook(self):
        textbook = {}

        a = get_school_subject()
        if a.get('error_code') == 0:
            textbook['学科教育'] = a['data']['stageFilter']
        else:
            print("学科教育下的学科学段获取失败，原因：" + a.get('message'))

        b = get_theme_education()
        if b.get('status') == 200:
            textbook['专题教育'] = b['data'][0]['children']
        else:
            print("特殊教育下的学科学段获取失败，原因：" + b.get('message'))

        c = get_special_education()
        if c.get('error_code') == 0:
            textbook['特殊教育'] = c['data']['typeFilters']
        else:
            print("特殊教育下的学科学段获取失败，原因：" + c.get('message'))

        d = get_professional_education()
        if d.get('error_code') == 0:
            textbook['职业教育'] = d['data']
        else:
            print("特殊教育下的学科学段获取失败，原因：" + d.get('message'))

        return textbook

    def select(self):
        textbook = self.get_textbook()

        winNew = Toplevel(root)
        winNew.geometry('320x240')
        winNew.title('选择章节')
        Label(winNew, text='教材范围：').grid(row=0, column=0)
        self.bookvalue = StringVar()
        Entry(winNew, textvariable=self.bookvalue).grid(row=0, column=1)
        # Label(winNew, text='教材范围：').pack()
        # Entry(winNew).pack()

        global tree
        tree = Treeview(winNew, show="tree headings", columns=('id'), displaycolumns=(), height=5)
        for i in textbook:
          f = tree.insert("", END, text=i, values=i)
          if i == "学科教育":
            for item in textbook[i]:
              g = tree.insert(f, END, text=item['name'])
              for item1 in item['subjects']:
                h = tree.insert(g, END, text=item1['name'])
                for item2 in item1['bookVersions']:
                  j = tree.insert(h, END, text=item2['name'], values=item2['code'])
          elif i == "特殊教育":
            for item in textbook[i]:
              g = tree.insert(f, END, text=item['name'])
              for item1 in item['subjectFilters']:
                h = tree.insert(g, END, text=item1['name'])
                for item2 in item1['subjects']:
                  j = tree.insert(h, END, text=item2['name'])
                  for item3 in item2['bookVersions']:
                    k = tree.insert(j, END, text=item3['name'], values=item3['code'])
          elif i == "职业教育":
            for item in textbook[i]:
              g = tree.insert(f, END, text=item['name'])
              for item1 in item['stages']:
                h = tree.insert(g, END, text=item1['name'])
                for item2 in item1['subjects']:
                  j = tree.insert(h, END, text=item2['name'])
                  for item3 in item2['bookVersions']:
                    k = tree.insert(j, END, text=item3['name'], values=item3['code'])
        # tree.pack(expand=1, fill=BOTH)
        tree.grid(row=1, column=0)
        tree.bind("<<TreeviewSelect>>", onSelect)

        Label(winNew, text="111").grid(row=2)

def onSelect(self):
  code = tree.set(tree.focus()).get('id')
  if code:
      if code == '专题教育':
          a.bookvalue.set(code)
      elif code[0].isalpha() and code[0].isascii():
          a.bookvalue.set(code)



root = Tk()
a = SwitchFrame(root)
root.mainloop()
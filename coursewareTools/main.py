import os
import threading
import time
import json
import tkinter
import webbrowser
import winreg
import pyautogui
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Frame, Combobox

from business.dbConfig import get_en_cw_test, get_courseware_version, get_seewo_school_teaching_plan
from business.taskConfig import get_courseware_word, get_courseware_maxVersion, upload_courseware, is_thumbnail, \
    get_progress, get_thumbnail_finish, get_courseware_uid, courseware_approve, courseware_shelf, courseware_disapprove, \
    perform_task, upload_plan, plan_pass, get_plan_uid, plan_approve, plan_shelf, plan_disapprove
from business.userConfig import get_user_token, get_resource, get_resource_user_token, getMd5


class SwitchFrame(object):
    def __init__(self, root):
        # 获取屏幕正中间位置
        geometry = get_geometry()

        self.root = root
        root.title('coursewareTools')
        root.geometry(geometry)
        root.resizable(width=False, height=False)  # 阻止Python GUI的大小调整

        Button(root, text='获取课件和教案', command=self.firstpage).grid(row=0, column=0)
        Button(root, text='上传课件', command=self.secondpage).grid(row=0, column=1)
        Button(root, text='上传教案', command=self.thirdpage).grid(row=0, column=2)
        # Button(root, text='生成资源包', command=self.fourthpage).grid(row=0, column=3)

        # 页面1
        frame1 = Frame(root, width=500, height=150)
        self.frame1 = frame1
        self.get_resources_phone_text = Label(frame1, text='手机号：', pady=5)
        self.get_resources_phone_text.grid(row=0, column=0, sticky='w')

        self.get_resources_phone = StringVar()
        self.get_resources_phone.set(jsondata['get_resources_phone'])
        Entry(self.frame1, width=40, textvariable=self.get_resources_phone).grid(row=0, column=1)

        self.get_resources_password_text = Label(frame1, text='密码：', pady=5)
        self.get_resources_password_text.grid(row=1, column=0, sticky='w')
        self.get_resources_password = StringVar()
        self.get_resources_password.set(jsondata['get_resources_password'])
        self.get_resources_password_entry = Entry(frame1, width=40, textvariable=self.get_resources_password, show='*')
        self.get_resources_password_entry.grid(row=1, column=1, columnspan=3)
        self.get_resources_password_switch_button = Button(frame1, text='显      示',
                                                        command=self.get_resources_courseware_switch_password)
        self.get_resources_password_switch_button.grid(row=1, column=4, padx=20)

        self.get_resources_num_text = Label(frame1, text='需要的份数：', pady=5)
        self.get_resources_num_text.grid(row=2, column=0, sticky='w')

        self.get_resources_num = StringVar()
        self.get_resources_num.set(jsondata['get_resources_num'])
        Entry(frame1, width=40, textvariable=self.get_resources_num).grid(row=2, column=1)

        Button(frame1, text='获取课件和教案', pady=5, command=lambda: self.thread_it(self.getresources)).grid(row=3, column=0, sticky="w", ipadx=100, columnspan=2)

        self.lb = Label(self.frame1, text='')
        self.lb.grid(row=4, column=0, sticky='w', pady=5, columnspan=2)

        # 页面2
        frame2 = Frame(root, width=500, height=150)
        self.frame2 = frame2
        self.select_path_text = Label(frame2, text='选择en5Main目录：', pady=5)
        self.select_path_text.grid(row=0, column=0, sticky='w')
        self.upload_courseware_en5Path = StringVar()
        self.upload_courseware_en5Path.set(jsondata['upload_courseware_en5Path'])
        Entry(self.frame2, width=40, textvariable=self.upload_courseware_en5Path).grid(row=0, column=1, columnspan=3)
        Button(frame2, text='选择目录', command=self.getPath).grid(row=0, column=4, padx=20)

        self.phone_text = Label(frame2, text='手机号：', pady=5)
        self.phone_text.grid(row=1, column=0, sticky='w')
        self.upload_courseware_phone = StringVar()
        self.upload_courseware_phone.set(jsondata['upload_courseware_phone'])
        Entry(self.frame2, width=40, textvariable=self.upload_courseware_phone).grid(row=1, column=1, columnspan=3)

        self.password_text = Label(frame2, text='密码：', pady=5)
        self.password_text.grid(row=2, column=0, sticky='w')
        self.upload_courseware_password = StringVar()
        self.upload_courseware_password.set(jsondata['upload_courseware_password'])
        self.courseware_password_entry = Entry(frame2, width=40, textvariable=self.upload_courseware_password, show='*')
        self.courseware_password_entry.grid(row=2, column=1, columnspan=3)
        self.courseware_password_switch_button = Button(frame2, text='显      示', command=self.courseware_switch_password)
        self.courseware_password_switch_button.grid(row=2, column=4, padx=20)

        Label(frame2, text='课件名称：', pady=5).grid(row=3, column=0, sticky='w')
        self.upload_courseware_name = StringVar()
        self.upload_courseware_name.set(jsondata['upload_courseware_name'])
        Entry(frame2, width=40, textvariable=self.upload_courseware_name).grid(row=3, column=1, columnspan=3)

        self.v = IntVar()
        self.v.set(jsondata['upload_courseware_type'])
        self.coursewareType = ["原创课件", "引用课件（预留）"]
        Label(frame2, text='课件类型：', pady=5).grid(row=4, column=0, sticky='w')
        for i, item in enumerate(self.coursewareType):
            Radiobutton(frame2, text=item, variable=self.v, value=i, command=self.selectCoursewareType).grid(row=4, column=i + 1, sticky='w')

        self.lb1 = Label(frame2, text='简介：' if jsondata['upload_courseware_type'] == 0 else '引用说明：', pady=5)
        self.lb1.grid(row=5, column=0, sticky='w')
        self.upload_courseware_description = StringVar()
        self.upload_courseware_description.set(jsondata['upload_courseware_description'])
        Entry(frame2, width=40, textvariable=self.upload_courseware_description).grid(row=5, column=1, columnspan=3)

        self.referUi1 = Label(frame2, text='引用课件：')
        self.referUi1.grid(row=6, column=0, sticky='w')
        self.upload_courseware_referencedList = StringVar()
        self.upload_courseware_referencedList.set(jsondata['upload_courseware_referencedList'])
        self.referUi2 = Entry(frame2, width=40, textvariable=self.upload_courseware_referencedList)
        self.referUi2.grid(row=6, column=1, columnspan=3)

        if jsondata['upload_courseware_type'] == 0:
            self.referUi1.grid_forget()
            self.referUi2.grid_forget()

        Label(frame2, text='标签(使用、分割)：', pady=5).grid(row=7, column=0, sticky='w')
        self.upload_courseware_tag = StringVar()

        # list转string
        tagString = ''
        if len(jsondata['upload_courseware_tag']) == 1:
            tagString = jsondata['upload_courseware_tag']
        else:
            for i in range(len(jsondata['upload_courseware_tag'])):
                if i == len(jsondata['upload_courseware_tag']) - 1:
                    tagString = tagString + jsondata['upload_courseware_tag'][i]
                else:
                    tagString = tagString + jsondata['upload_courseware_tag'][i] + '、'

        self.upload_courseware_tag.set(tagString)
        Entry(frame2, width=40, textvariable=self.upload_courseware_tag).grid(row=7, column=1, columnspan=3)

        self.indexIds_text = Label(frame2, text='教材类型：', pady=5)
        self.indexIds_text.grid(row=8, column=0, sticky='w')
        self.upload_courseware_indexIds = StringVar()
        self.upload_courseware_indexIds.set(jsondata['upload_courseware_indexIds'])
        Entry(frame2, width=40, textvariable=self.upload_courseware_indexIds).grid(row=8, column=1, columnspan=3)

        self.v1 = IntVar()
        self.v1.set(jsondata['upload_courseware_approve'])
        self.approveType = ["上架", "通过机器审核", "被拒绝"]
        Label(frame2, text='课件状态：', pady=5).grid(row=9, column=0, sticky='w')
        for i, item in enumerate(self.approveType):
            Radiobutton(frame2, text=item, variable=self.v1, value=i, command=self.selectApproveType).grid(row=9, column=i + 1, sticky='w')

        self.courseware_audit_text = Label(frame2, text='拒绝理由：')
        self.courseware_audit_text.grid(row=10, column=0, sticky='w')
        self.upload_courseware_audit_type = StringVar()
        self.courseware_audit_type_combobox = Combobox(frame2, textvariable=self.upload_courseware_audit_type, state="readonly")
        self.courseware_audit_type_combobox['value'] = ['先进性-互动元素少', '教育性-有效页数低', '美观度-图片', '美观度-颜色搭配', '美观度-排版混乱', '美观度-字体样式不合理',
                                                        '版权问题', '没有合适的章节挂靠', '内容不合适', '其他（勿选，预留按钮）', '有明显内容缺失', '乱写引用说明', '原创度过高',
                                                        '乱写引用说明', '上传类型错误']
        self.courseware_audit_type_combobox.grid(row=10, column=1, sticky='w', columnspan=3)
        self.upload_courseware_audit_type.set(self.courseware_audit_type_combobox['value'][jsondata['upload_courseware_audit_type']])

        if jsondata['upload_courseware_approve'] != 2:
            self.courseware_audit_text.grid_forget()
            self.courseware_audit_type_combobox.grid_forget()

        Button(frame2, text='上传一份课件到该账号', width=40, command=lambda: self.thread_it(self.upload_courseware)).grid(row=11, column=0, columnspan=3, sticky='w', pady=5)

        Label(frame2, text='提示：如长时间未上传成功，请再点一次上传按钮！！！', fg='red').grid(row=12, column=0, sticky='w', columnspan=10)
        Label(frame2, text='提示：使用前请查看此教程，en5配置工具添加对应配置', fg='red').grid(row=13, column=0, sticky='w',
                                                                                           columnspan=10)
        Button(frame2, text='上传文档', fg='red', command=lambda: self.thread_it(self.tokb)).grid(row=13, column=3, sticky='w', pady=5, columnspan=10)

        frame4 = Frame(frame2, width=300, height=150)
        self.frame4 = frame4
        frame4.grid(row=14, columnspan=4)
        Label(frame4, text='上传进度：').grid(row=0, column=0, sticky='w')
        self.progress1 = Label(frame4, text='获取课件')
        self.progress1.grid(row=0, column=1, sticky='w')
        Label(frame4, text='→→→').grid(row=0, column=2, sticky='w')
        self.progress2 = Label(frame4, text='上传课件')
        self.progress2.grid(row=0, column=3, sticky='w')
        Label(frame4, text='→→→').grid(row=0, column=4, sticky='w')
        self.progress3 = Label(frame4, text='课件截图')
        self.progress3.grid(row=0, column=5, sticky='w')
        Label(frame4, text='→→→').grid(row=0, column=6, sticky='w')
        self.progress4 = Label(frame4, text='审核课件')
        self.progress4.grid(row=0, column=7, sticky='w')

        # frame4.grid_forget()

        self.message = Label(frame2, text="")
        self.message.grid(row=15, column=0, sticky="w", columnspan=10)

        # 页面3
        frame3 = Frame(root, width=500, height=150)
        self.frame3 = frame3

        self.plan_phone_text = Label(frame3, text='手机号：', pady=5)
        self.plan_phone_text.grid(row=0, column=0, sticky='w')
        self.upload_plan_phone = StringVar()
        self.upload_plan_phone.set(jsondata['upload_plan_phone'])
        Entry(self.frame3, width=40, textvariable=self.upload_plan_phone).grid(row=0, column=1, columnspan=3)

        self.plan_password_text = Label(frame3, text='密码：', pady=5)
        self.plan_password_text.grid(row=1, column=0, sticky='w')
        self.upload_plan_password = StringVar()
        self.upload_plan_password.set(jsondata['upload_plan_password'])
        self.upload_plan_password_entry = Entry(frame3, width=40, textvariable=self.upload_plan_password, show='*')
        self.upload_plan_password_entry.grid(row=1, column=1, columnspan=3)
        self.upload_plan_password_switch_button = Button(frame3, text='显      示',
                                                        command=self.plan_switch_password)
        self.upload_plan_password_switch_button.grid(row=1, column=4, padx=20)

        Label(frame3, text='教案名称：', pady=5).grid(row=2, column=0, sticky='w')
        self.upload_plan_name = StringVar()
        self.upload_plan_name.set(jsondata['upload_plan_name'])
        Entry(frame3, width=40, textvariable=self.upload_plan_name).grid(row=2, column=1, columnspan=3)


        Label(frame3, text='教案类型：', pady=5).grid(row=3, column=0, sticky='w')
        self.upload_plan_type = StringVar()
        self.plan_type_combobox = Combobox(frame3, textvariable=self.upload_plan_type, state="readonly")
        self.plan_type_combobox['value'] = ['教学设计', '导学案', '学历案', '说课稿', '作业设计', '教学反思', '其他']
        self.plan_type_combobox.grid(row=3, column=1, sticky='w', columnspan=3)
        self.upload_plan_type.set(self.plan_type_combobox['value'][jsondata['upload_plan_type']])

        Label(frame3, text='简介：', pady=5).grid(row=4, column=0, sticky='w')
        self.upload_plan_description = StringVar()
        self.upload_plan_description.set(jsondata['upload_plan_description'])
        Entry(frame3, width=40, textvariable=self.upload_plan_description).grid(row=4, column=1, columnspan=3)

        Label(frame3, text='标签(使用、分割)：', pady=5).grid(row=5, column=0, sticky='w')
        self.upload_plan_tag = StringVar()

        # list转string
        plan_tagString = ''
        if len(jsondata['upload_plan_tag']) == 1:
            plan_tagString = jsondata['upload_plan_tag']
        else:
            for i in range(len(jsondata['upload_plan_tag'])):
                if i == len(jsondata['upload_plan_tag']) - 1:
                    plan_tagString = plan_tagString + jsondata['upload_plan_tag'][i]
                else:
                    plan_tagString = plan_tagString + jsondata['upload_plan_tag'][i] + '、'

        self.upload_plan_tag.set(plan_tagString)
        Entry(frame3, width=40, textvariable=self.upload_plan_tag).grid(row=5, column=1, columnspan=3)

        self.plan_indexIds_text = Label(frame3, text='教材类型：', pady=5)
        self.plan_indexIds_text.grid(row=6, column=0, sticky='w')
        self.upload_plan_indexIds = StringVar()
        self.upload_plan_indexIds.set(jsondata['upload_plan_indexIds'])
        Entry(frame3, width=40, textvariable=self.upload_plan_indexIds).grid(row=6, column=1, columnspan=3)

        self.upload_plan_approve = IntVar()
        self.upload_plan_approve.set(jsondata['upload_plan_approve'])
        self.approveType = ["上架", "通过机器审核", "被拒绝"]
        Label(frame3, text='教案状态：', pady=5).grid(row=7, column=0, sticky='w')
        for i, item in enumerate(self.approveType):
            Radiobutton(frame3, text=item, variable=self.upload_plan_approve, value=i, command=self.select_plan_approveType).grid(row=7, column=i + 1, sticky='w')

        # self.upload_plan_auditUi_text = Label(frame3, text='拒绝理由：')
        # self.upload_plan_auditUi_text.grid(row=8, column=0, sticky='w')
        # self.upload_plan_auditUids = StringVar()
        # # self.upload_plan_auditUids.set(jsondata['upload_plan_auditUids'])
        # self.upload_plan_auditUi_entry = Entry(frame3, width=40, textvariable=self.upload_plan_auditUids)
        # self.upload_plan_auditUi_entry.grid(row=8, column=1, columnspan=3)

        self.upload_plan_auditUi_text = Label(frame3, text='拒绝理由：')
        self.upload_plan_auditUi_text.grid(row=8, column=0, sticky='w')
        self.upload_plan_audit_type = StringVar()
        self.plan_audit_type_combobox = Combobox(frame3, textvariable=self.upload_plan_audit_type,
                                                       state="readonly")
        self.plan_audit_type_combobox['value'] = ['编辑度不足', '有相似教案', '先进性-内容丰富度低',
                                                        '先进性-有效内容过少', '先进性-图片过多', '先进性-缺少段落标题',
                                                        '颜色搭配', '排版混乱', '字体样式不合理',
                                                        '错别字过多', '空白过多', '版权问题',
                                                        '内容不合适', '有明显内容缺失', '教案查重不通过',
                                                        '上传类型错误', '其他（勿选，预留）']
        self.plan_audit_type_combobox.grid(row=8, column=1, sticky='w', columnspan=3)
        self.upload_plan_audit_type.set(self.plan_audit_type_combobox['value'][jsondata['upload_plan_audit_type']])

        if jsondata['upload_plan_approve'] != 2:
            self.upload_plan_auditUi_text.grid_forget()
            self.plan_audit_type_combobox.grid_forget()

        Button(frame3, text='上传一份教案到该账号', width=40, command=lambda: self.thread_it(self.upload_plan)).grid(row=9, column=0, columnspan=3, sticky='w', pady=5)

        Label(frame3, text='提示：如长时间未上传成功，请再点一次上传按钮！！！', fg='red').grid(row=10, column=0, sticky='w', columnspan=10)

        # 教案上传进度
        frame5 = Frame(frame3, width=300, height=150)
        self.frame5 = frame5
        frame5.grid(row=11, columnspan=3)
        Label(frame5, text='上传进度：').grid(row=0, column=0, sticky='w')
        self.plan_progress1 = Label(frame5, text='获取教案')
        self.plan_progress1.grid(row=0, column=1, sticky='w')
        Label(frame5, text='→→→').grid(row=0, column=2, sticky='w')
        self.plan_progress2 = Label(frame5, text='上传教案')
        self.plan_progress2.grid(row=0, column=3, sticky='w')
        Label(frame5, text='→→→').grid(row=0, column=6, sticky='w')
        self.plan_progress3 = Label(frame5, text='审核教案')
        self.plan_progress3.grid(row=0, column=7, sticky='w')

        self.plan_message = Label(frame3, text="")
        self.plan_message.grid(row=12, column=0, sticky="w", columnspan=10)

        # 页面4
        frame4 = Frame(root, width=500, height=150)
        self.frame4 = frame4

        Label(frame4, text='页面4444', pady=5).grid(row=0, column=1)

        self.currentpage = frame1
        self.currentpage.place(x=1, y=40)

        # 检测代理
        self.get_proxy()

    # 检测代理
    def get_proxy(self):
        is_open_proxy = is_open_proxy_form_Win()
        if is_open_proxy == True:
            tkinter.messagebox.askokcancel('检测代理', '检测到您的电脑开启了代理，请您关闭代理，才能正常使用该工具！\n代理设置路径：设置-网络和Internet-代理-使用代理服务器')
        else:
            return True

    def firstpage(self):
        if self.currentpage != self.frame1:
            self.currentpage.place_forget()
            self.currentpage = self.frame1
            self.currentpage.place(x=1, y=40)

    def secondpage(self):
        if self.currentpage != self.frame2:
            self.currentpage.place_forget()
            self.currentpage = self.frame2
            self.currentpage.place(x=1, y=40)

    def thirdpage(self):
        if self.currentpage != self.frame3:
            self.currentpage.place_forget()
            self.currentpage = self.frame3
            self.currentpage.place(x=1, y=40)

    def fourthpage(self):
        if self.currentpage != self.frame4:
            self.currentpage.place_forget()
            self.currentpage = self.frame4
            self.currentpage.place(x=1, y=40)

    def get_resources_courseware_switch_password(self):
        if self.get_resources_password_entry['show'] == '*':
            self.get_resources_password_entry.configure(show='')
            self.get_resources_password_switch_button.configure(text='隐      藏')
        else:
            self.get_resources_password_entry.configure(show='*')
            self.get_resources_password_switch_button.configure(text='显      示')

    def courseware_switch_password(self):
        if self.courseware_password_entry['show'] == '*':
            self.courseware_password_entry.configure(show='')
            self.courseware_password_switch_button.configure(text='隐      藏')
        else:
            self.courseware_password_entry.configure(show='*')
            self.courseware_password_switch_button.configure(text='显      示')

    def plan_switch_password(self):
        if self.upload_plan_password_entry['show'] == '*':
            self.upload_plan_password_entry.configure(show='')
            self.upload_plan_password_switch_button.configure(text='隐      藏')
        else:
            self.upload_plan_password_entry.configure(show='*')
            self.upload_plan_password_switch_button.configure(text='显      示')


    def thread_it(self, func, *args):
        self.myThread = threading.Thread(target=func, args=args)
        self.myThread.daemon = True
        self.myThread.start()

    def getPath(self):
        path = filedialog.askdirectory(title='请选择一个目录')
        self.upload_courseware_en5Path.set(path)

    def getresources(self):
        self.lb.configure(text="", fg="black")

        # 验证输入框必填内容
        key = [self.get_resources_phone_text, self.get_resources_password_text, self.get_resources_num_text]
        value = [self.get_resources_phone, self.get_resources_password, self.get_resources_num]
        index = []

        for i in range(len(value)):
            if value[i].get() == '':
                key[i].configure(fg="red")
                index.append(i)
            else:
                key[i].configure(fg="black")

        if len(index) != 0:
            self.lb.configure(text="请填写必填内容！！", fg="red")
            quit()

        jsondata['get_resources_phone'] = self.get_resources_phone.get()
        jsondata['get_resources_password'] = self.get_resources_password.get()
        jsondata['get_resources_num'] = self.get_resources_num.get()
        file = open(r'C:\coursewareTools\data.json', 'w')
        file.write(json.dumps(jsondata))

        # 将密码md5加密
        password = getMd5(self.get_resources_password.get())

        data = get_courseware_word(self.get_resources_phone.get(), password, int(self.get_resources_num.get()))
        self.lb.configure(text=data.get('message'))

    def selectCoursewareType(self):
        if self.v.get() == 0:
            self.lb1.configure(text='简介：', fg="black")
            self.referUi1.grid_forget()
            self.referUi2.grid_forget()
        else:
            self.lb1.configure(text='引用说明：')
            self.referUi1.grid(row=6, column=0, sticky='w')
            self.referUi2.grid(row=6, column=1, columnspan=3)

    def selectApproveType(self):
        if self.v1.get() != 2:
            self.courseware_audit_text.grid_forget()
            self.courseware_audit_type_combobox.grid_forget()
        else:
            self.courseware_audit_text.grid(row=10, column=0, sticky='w')
            self.courseware_audit_type_combobox.grid(row=10, column=1, columnspan=3, sticky='w')

    def select_plan_approveType(self):
        if self.upload_plan_approve.get() != 2:
            self.upload_plan_auditUi_text.grid_forget()
            self.plan_audit_type_combobox.grid_forget()
        else:
            self.upload_plan_auditUi_text.grid(row=8, column=0, sticky='w')
            self.plan_audit_type_combobox.grid(row=8, column=1, columnspan=3, sticky='w')

    def tokb(self):
        url = "https://kb.cvte.com/pages/viewpage.action?pageId=346317698"
        webbrowser.open(url)

    def upload_courseware(self):

        self.progress1.configure(background="#f0f0f0")
        self.progress2.configure(background="#f0f0f0")
        self.progress3.configure(background="#f0f0f0")
        self.progress4.configure(background="#f0f0f0")
        self.message.configure(text="", fg="black")

        # 验证输入框必填内容，需要补充引用说明，
        key = [self.select_path_text, self.phone_text, self.password_text, self.indexIds_text]
        value = [self.upload_courseware_en5Path, self.upload_courseware_phone, self.upload_courseware_password, self.upload_courseware_indexIds]
        index = []

        if self.v.get() == 1:
            key.append(self.lb1)
            value.append(self.upload_courseware_description)

        for i in range(len(value)):
            if value[i].get() == '':
                key[i].configure(fg="red")
                index.append(i)
            else:
                key[i].configure(fg="black")

        if len(index) != 0:
            self.message.configure(text="请填写必填内容！！", fg="red")
            quit()

        tagNames = self.upload_courseware_tag.get().split("、")

        jsondata['upload_courseware_en5Path'] = self.upload_courseware_en5Path.get()
        jsondata['upload_courseware_phone'] = self.upload_courseware_phone.get()
        jsondata['upload_courseware_password'] = self.upload_courseware_password.get()
        jsondata['upload_courseware_name'] = self.upload_courseware_name.get()
        jsondata['upload_courseware_type'] = self.v.get()
        jsondata['upload_courseware_description'] = self.upload_courseware_description.get()
        jsondata['upload_courseware_tag'] = tagNames
        jsondata['upload_courseware_indexIds'] = self.upload_courseware_indexIds.get()
        jsondata['upload_courseware_approve'] = self.v1.get()
        jsondata['upload_courseware_referencedList'] = self.upload_courseware_referencedList.get()
        jsondata['upload_courseware_audit_type'] = self.courseware_audit_type_combobox.current()
        file = open(r'C:\coursewareTools\data.json', 'w')
        file.write(json.dumps(jsondata))
        file.close()

        referencedList = ['836c3aa52eb939a3a7313e3b212948e4', 'aad27fed42cf3ce99b96e8b9554468e4',
                          '70c19278a86d3953b25f578e1c060238']
        # 拒绝理由
        auditUids = ['4dc1d46bea3049c788043a3c87cd5e63', '4dc1d46bea3049c788043a3c87cd5e64', '4dc1d46bea3049c788043a3c87cd5e65', '4dc1d46bea3049c788043a3c87cd5e66',
                     '4dc1d46bea3049c788043a3c87cd5e67', '4dc1d46bea3049c788043a3c87cd5e68', '4dc1d46bea3049c788043a3c87cd5e69', '4dc1d46bea3049c788043a3c87cd5e70',
                     '4dc1d46bea3049c788043a3c87cd5e71', '4dc1d46bea3049c788043a3c87cd5e73', '2160dbe0b1534d25b9141d1a74cdde11', '609ed3edb42c44118f3d3a9fb6fe5432',
                     '3afa44e41d5d4368a180c4d79535b1bd', '7a6585bd98c5466988482f8f0c6b5522', '398de7ac9ef34c6680f29fca9ef14156']
        # 将密码md5加密
        password = getMd5(self.upload_courseware_password.get())

        # 连接mysql
        conn = get_en_cw_test('en_cw_test')
        conn1 = get_courseware_version('courseware_version')

        # 获取token
        values = get_user_token(self.upload_courseware_phone.get(), password)
        if values.get('error_code') == 0:
            token = values.get('token')
            print('token获取成功', values.get('token'))
        else:
            print(values.get('message'))
            self.message.configure(text='获取token失败，原因：' + values.get('message'))
            self.progress1.configure(background="red")
            quit()

        cIds = []

        # 获取课件并获取课件id
        for index in range(1):
            values1 = get_resource(token)
            if values1.get('code') == 0:
                cIds.append(values1.get('cid'))
                print('课件获取成功：', values1.get('cid'))
            else:
                self.message.configure(text='课件获取失败，原因：' + values1.get('message'))
                self.progress1.configure(background="red")
                print('课件获取失败，原因：', values1.get('message'))
                quit()

        cid = cIds[0]

        # 获取课件版本最大数
        maxVersion = get_courseware_maxVersion(cid)[0]

        cursor = conn.cursor()
        cursor1 = conn1.cursor()

        # 课件版本大于5，就不用更改课件版本，反之则更改课件版本为5
        if maxVersion >= 5:
            sql = "UPDATE t_courseware SET c_size = 2200000 WHERE c_id = " + '\'' + cid + '\''
            sql1 = "UPDATE t_courseware_version " \
                   "SET c_size = 2200000,c_server_time=DATE_SUB(NOW(),INTERVAL 1 DAY) " \
                   "WHERE t_courseware_c_id =" + '\'' + cid + '\'' \
                                                              "and c_version = (select max(c_version) from t_courseware_version " \
                                                              "where t_courseware_c_id =" + '\'' + cid + '\' )'
        else:
            maxVersion = 5
            sql = "UPDATE t_courseware SET c_size = 2200000,c_version = 5 WHERE c_id = " + '\'' + cid + '\''
            sql1 = "UPDATE t_courseware_version " \
                   "SET c_size = 2200000,c_version = 5,c_server_time=DATE_SUB(NOW(),INTERVAL 1 DAY) " \
                   "WHERE t_courseware_c_id =" + '\'' + cid + '\'' \
                                                              "and c_version = (select max(c_version) from t_courseware_version " \
                                                              "where t_courseware_c_id =" + '\'' + cid + '\' )'

        # 执行sql语句
        cursor.execute(sql)
        cursor1.execute(sql1)

        # 提交sql
        conn.commit()
        conn1.commit()
        print('成功修改t_courseware表中', cursor.rowcount, '条数据')
        print('成功修改t_courseware_version表中', cursor1.rowcount, '条数据')

        conn.close()
        conn1.close()

        self.progress1.configure(background="green")

        print('正在上传课件')

        # 上传课件
        values2 = upload_courseware(cid, maxVersion, token, self.upload_courseware_indexIds.get(), self.upload_courseware_name.get(),
                                    tagNames, self.upload_courseware_description.get(), self.v.get(), referencedList)
        if values2.get('error_code') == 0:
            print('课件上传成功')
            self.progress2.configure(background="green")
        else:
            self.progress2.configure(background="red")
            self.message.configure(text='课件上传失败，原因：' + values2.get('message'))
            print('课件上传失败，原因：', values2.get('message'))
            quit()

        # 运行定时任务
        print("定时任务-上架课件：", perform_task(1913))
        print("定时任务-课件库上传课件任务：", perform_task(1527))

        # 调用cmd进行截图
        cmd1 = 'c:'
        cmd2 = self.upload_courseware_en5Path.get()[0:2]
        cmd3 = 'cd ' + self.upload_courseware_en5Path.get()
        cmd4 = '.\easinote.exe --ExtensionCommand TakeSlideOfCourseware --CoursewareId ' + cid + ' --CoursewareVersion 5'
        cmd = cmd1 + '&&' + cmd2 + '&&' + cmd3 + '&&' + cmd4
        os.popen(cmd)
        print('截图命令：' + cmd4)

        # 等待20秒，等截图完成
        time.sleep(20)

        print("定时任务-上架课件：", perform_task(1913))

        # 课件截图上传完成就通过机器审核
        print(get_thumbnail_finish(cid))

        self.progress3.configure(background="green")

        if self.v1.get() == 1:
            self.progress4.configure(background="green")
            self.message.configure(text='课件已通过机器审核')
            quit()

        time.sleep(5)

        # 获取uid
        uid = get_courseware_uid(cid, maxVersion)[0][1]

        # 获取有希沃资源管理后台权限用户的token
        resource = get_resource_user_token()
        if resource.get('error_code') == 0:
            resource_token = resource.get('token')
        else:
            print('获取希沃资源管理后台权限用户的token失败，原因：', resource.get('message'))
            self.progress4.configure(background="red")
            self.message.configure(text='获取希沃资源管理后台权限用户的token失败，原因：' + resource.get('message'))
            quit()

        # type为0则通过人工审核并上架课件，type为2则拒绝人工审核
        if self.v1.get() == 0:
            values3 = courseware_approve(uid, resource_token)
            if values3.get('code') == 0:
                print('课件已通过人工审核')
                values4 = courseware_shelf(uid, resource_token)
                if values4.get('code') == 0:
                    print('课件已上架')
                    self.progress4.configure(background="green")
                    self.message.configure(text='课件已上架')
                else:
                    print('课件上架出现异常，原因：', values4.get('errorMsg'))
                    self.progress4.configure(background="red")
                    self.message.configure(text='课件上架出现异常，原因：' + values4.get('errorMsg'))
                    quit()
            else:
                self.progress4.configure(background="red")
                self.message.configure(text='课件通过人工审核出现异常，原因：' + values3.get('errorMsg'))
                print('课件通过人工审核出现异常，原因：', values3.get('errorMsg'))
                quit()
        elif self.v1.get() == 2:
            values3 = courseware_disapprove(uid, resource_token, auditUids[self.courseware_audit_type_combobox.current()])
            if values3.get('code') == 0:
                print('课件未通过人工审核')
                self.progress4.configure(background="green")
                self.message.configure(text='因为您选中了"被拒绝"，所以课件未通过人工审核')
            else:
                print('课件拒绝人工审核出现异常，原因：', values3.get('errorMsg'))
                self.progress4.configure(background="red")
                self.message.configure(text='课件拒绝人工审核出现异常，原因：' + values3.get('errorMsg'))
                quit()

    def upload_plan(self):
        self.plan_progress1.configure(background="#f0f0f0")
        self.plan_progress2.configure(background="#f0f0f0")
        self.plan_progress3.configure(background="#f0f0f0")
        self.plan_message.configure(text="", fg="black")

        # 验证输入框必填内容
        key = [self.plan_phone_text, self.plan_password_text, self.plan_indexIds_text]
        value = [self.upload_plan_phone, self.upload_plan_password, self.upload_plan_indexIds]
        index = []

        for i in range(len(value)):
            if value[i].get() == '':
                key[i].configure(fg="red")
                index.append(i)
            else:
                key[i].configure(fg="black")

        if len(index) != 0:
            self.plan_message.configure(text="请填写必填内容！！", fg="red")
            quit()

        tagNames = self.upload_plan_tag.get().split("、")

        jsondata['upload_plan_phone'] = self.upload_plan_phone.get()
        jsondata['upload_plan_password'] = self.upload_plan_password.get()
        jsondata['upload_plan_name'] = self.upload_plan_name.get()
        jsondata['upload_plan_type'] = self.plan_type_combobox.current()
        jsondata['upload_plan_description'] = self.upload_plan_description.get()
        jsondata['upload_plan_tag'] = tagNames
        jsondata['upload_plan_indexIds'] = self.upload_plan_indexIds.get()
        jsondata['upload_plan_approve'] = self.upload_plan_approve.get()
        jsondata['upload_plan_audit_type'] = self.plan_audit_type_combobox.current()
        file = open(r'C:\coursewareTools\data.json', 'w')
        file.write(json.dumps(jsondata))
        file.close()


        # 拒绝理由
        auditUids = ['4dad5d1b410c4f239f5c12db923486de', 'f902633a241943a1be0e62c32b9fadc8', '74d7aad37ad647fea7a40cbab1681cbc',
                     'a82b037dd8fb4fa4b83d07e3574c638d', '833f37377b8b456da2a0a1acb9568b4d', '80c19c3f905b4124b6bd62d79de1f11e',
                     '80d76203ca5249458dd0752db84e122c', 'c3980d6e989d448e9f1de87c9ecb6802', 'e136c3a622ea4e0eaeec785cf6d26f13',
                     'e03d1e4a4dfc4d2bbe5681ee3a7779f5', '3f9960eea3b9456db566a92ee3dd6f56', 'be7ba86fb2cb4d3296df543ac1030198',
                     '2ac3fb3cac6241749f8bd719805f9061', 'b38d58e9bde04ea3af87241827e68511', 'a6ed3431039442b19f45e7f4ae71e2e3',
                     '4c7251ee81e944dbbaf7be2b3be19a8d', 'dd621d18dd984ef692e7abadce10ff43']

        # 教案类型
        plan_types = ["486292f0e829453cb179446d7685fa28", "e29c9b4ee6c64417afeff75ca3b67d14", "0fc641b1eca340a794dd362b7fa7b12f",
                      "1e0c2c5368f44ee4b8e89ff2b6c1a3fb", "44ae2ea876054f3dad317110f035c913", "efd0f0b63d8f44aba5c2be43028b068e",
                      "111edc6d7dbe436bb128cc396b55661c"]

        # print(self.plan_audit_type_combobox.current())
        # print(auditUids[self.plan_audit_type_combobox.current()])
        # quit()

        # 将密码md5加密
        password = getMd5(self.upload_plan_password.get())

        # 连接mysql
        conn = get_seewo_school_teaching_plan('seewo_school_teaching_plan')

        # 获取token
        values = get_user_token(self.upload_plan_phone.get(), password)
        if values.get('error_code') == 0:
            token = values.get('token')
            print('token获取成功', values.get('token'))
        else:
            print('获取token失败，原因：', values.get('message'))
            quit()

        uid = ''

        # 获取教案、课件并获取教案、课件id
        values1 = get_resource(token)
        if values1.get('code') == 0:
            print('教案获取成功：', values1.get('uid'))
            uid = values1.get('uid')
        else:
            self.plan_message.configure(text='教案获取失败，原因：' + values1.get('message'))
            self.plan_progress1.configure(background="red")
            print('教案获取失败，原因：', values1.get('message'))
            quit()

        sql = "UPDATE t_teacher_teaching_plan_content_version SET c_version = 5 WHERE c_teaching_plan_id = (SELECT c_id FROM `t_teacher_teaching_plan_info` WHERE c_uid = " + '\'' + uid + '\' )'

        cursor = conn.cursor()
        # 执行sql语句
        cursor.execute(sql)
        # 提交sql
        conn.commit()

        print('成功修改t_teacher_teaching_plan_content_version表中', cursor.rowcount, '条数据')
        conn.close()

        self.plan_progress1.configure(background="green")

        print('正在上传教案')

        # 上传教案
        values2 = upload_plan(uid, 5, token, self.upload_plan_indexIds.get(), self.upload_plan_name.get(), tagNames, self.upload_plan_description.get(),
                              plan_types[self.plan_type_combobox.current()])
        if values2.get('error_code') == 0:
            print('教案上传成功')
            self.plan_progress2.configure(background="green")
        else:
            self.plan_progress2.configure(background="red")
            self.plan_message.configure(text='教案上传失败，原因：' + values2.get('message'))
            print('教案上传失败，原因：', values2.get('message'))
            quit()

        # 教案跑到希沃资源管理后台就通过机器审核
        print(plan_pass(uid))

        if self.upload_plan_approve.get() == 1:
            self.plan_progress3.configure(background="green")
            self.plan_message.configure(text='教案已通过机器审核')
            quit()

        # 获取资源uid
        resource_uid = get_plan_uid(uid)[0][1]

        # 获取有希沃资源管理后台权限用户的token
        resource = get_resource_user_token()
        if resource.get('error_code') == 0:
            resource_token = resource.get('token')
        else:
            print('获取希沃资源管理后台权限用户的token失败，原因：', resource.get('message'))
            self.progress4.configure(background="red")
            self.message.configure(text='获取希沃资源管理后台权限用户的token失败，原因：' + resource.get('message'))
            quit()

        # type为0则通过人工审核并上架教案，type为2则拒绝人工审核
        if self.upload_plan_approve.get() == 0:
            values3 = plan_approve(resource_uid, resource_token)
            if values3.get('code') == 0:
                print('教案已通过人工审核')
                values4 = plan_shelf(resource_uid, resource_token)
                if values4.get('code') == 0:
                    print('教案已上架')
                    self.plan_progress3.configure(background="green")
                    self.plan_message.configure(text='教案已上架')
                else:
                    print('教案上架出现异常，原因：', values4.get('errorMsg'))
                    self.plan_progress3.configure(background="red")
                    self.plan_message.configure(text='教案上架出现异常，原因：' + values4.get('errorMsg'))
                    quit()
            else:
                self.plan_progress3.configure(background="red")
                self.plan_message.configure(text='教案通过人工审核出现异常，原因：' + values3.get('errorMsg'))
                print('教案通过人工审核出现异常，原因：', values3.get('errorMsg'))
                quit()
        elif self.upload_plan_approve.get() == 2:
            auditUid = auditUids[self.plan_audit_type_combobox.current()]
            values3 = plan_disapprove(resource_uid, resource_token, auditUid)
            if values3.get('code') == 0:
                print('教案未通过人工审核')
                self.plan_progress3.configure(background="green")
                self.plan_message.configure(text='因为您选中了"被拒绝"，所以教案未通过人工审核')
            else:
                print('教案拒绝人工审核出现异常，原因：', values3.get('errorMsg'))
                self.plan_progress3.configure(background="red")
                self.plan_message.configure(text='教案拒绝人工审核出现异常，原因：' + values3.get('errorMsg'))
                quit()


def add_directory():
    path = r'C:\coursewareTools'
    if not os.path.exists(path):
        os.mkdir(path)

    if not os.path.exists(r'C:\coursewareTools\data.json'):
        json1 = {'get_resources_phone': '', 'get_resources_password': '', 'get_resources_num': '',
                 'upload_courseware_en5Path': '', 'upload_courseware_phone': '', 'upload_courseware_password': '', 'upload_courseware_name': '',
                 'upload_courseware_type': 0, 'upload_courseware_description': '', 'upload_courseware_tag': '', 'upload_courseware_indexIds': '',
                 'upload_courseware_approve': 0, 'upload_courseware_referencedList': '', 'upload_courseware_audit_type': 0,
                 'upload_plan_phone': '', 'upload_plan_password': '', 'upload_plan_name': '', 'upload_plan_type': 0, 'upload_plan_description': '',
                 'upload_plan_tag': '', 'upload_plan_indexIds': '', 'upload_plan_approve': 0, 'upload_plan_audit_type': 0}
        file = open(r'C:\coursewareTools\data.json', 'w')
        file.write(json.dumps(json1))
        file.close()

    if os.path.exists(r'C:\coursewareTools\data.json'):
        file = open(r'C:\coursewareTools\data.json')
        global jsondata
        jsondata = json.loads(file.read())

# 判断电脑是否开启了代理
def is_open_proxy_form_Win():
    path = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
    INTERNET_SETTINGS = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,
                                                path, 0, winreg.KEY_ALL_ACCESS)
    try:
        if winreg.QueryValueEx(INTERNET_SETTINGS, "ProxyEnable")[0] == 1:
            return True
    except FileNotFoundError as err:
        print("没有找到代理信息：" + str(err))
    except Exception as err:
        print("有其他报错：" + str(err))
    return False

# 获取屏幕正中间位置
def get_geometry():
    toolWidth = 500
    toolHeight = 500
    # 获取屏幕分辨率
    screenWidth, screenHeight = pyautogui.size()

    width = int((screenWidth - toolWidth) / 2)
    height = int((screenHeight - toolHeight) / 2)

    geometry = str(toolWidth) + 'x' + str(toolHeight) + '+' + str(width) + '+' + str(height)

    return geometry


add_directory()
root = Tk()
SwitchFrame(root)
root.mainloop()

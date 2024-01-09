#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tkinter as tk
from my_tool_kit import DraggableLabel
from module_niftiViewer import NiftiViewer
from module_transfer_file import TransferFile
from module_dcm2nii import Dcm2Nii
class MainMenu(tk.Frame):
    def __init__(self, master=None, callback=None):
        super().__init__(master)
        self.config(bg='#181818')
        self.pack()
        self.callback = callback
        tk.Frame(self, bg='#181818').pack(pady=70)
        main_Frame = tk.Frame(self,bg='#181818')
        main_Frame.pack()
        btn_style = {'width': 15, 'height': 4, 'font': ("Helvetica", 15, "bold"), 'bg': '#abe338', 'fg': 'black'}
        tk.Button(main_Frame, text="Dcm2nii", command=lambda: self.open_module("Dcm2Nii"), **btn_style).pack(side='left', padx=20)
        tk.Button(main_Frame, text="Nifti viewer", command=lambda: self.open_module("Nifti viewer"), **btn_style).pack(side='left', padx=20)
        tk.Button(main_Frame, text="TransferFile", command=lambda: self.open_module("TransferFile"), **btn_style).pack(side='left', padx=20)
        tk.Frame(self,bg='#181818').pack(pady=70)
        tk.Label(self,text='Version 1.0.20230620; Contact author by <vanshaw@126.com>;\nThank you for using.',
                 font=("Helvetica", 8, "bold"), bg='#181818',fg='#87939a').pack()
    def open_module(self,which_module):
        if self.callback:
            self.callback(which_module)
class MyMenu(tk.Frame):
    def __init__(self, master, module_dict, **kwargs):
        super().__init__(master, **kwargs)
        self.module_dict = module_dict
        self.module_selected = None     # 初始的 self.module_selected
        # 设置主框架的高度为50像素，宽度充满父级框架
        self.pack(fill='x', pady=0)
        self.config(height=80,bg='red')
        # 创建一个放置菜单按钮的框架
        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(side='left', padx=0, pady=0,fill='x', expand=True)
        # 创建一个下拉菜单
        self.menu = tk.Menu(self.menu_frame, tearoff=0)
        self.menu.add_command(label='Dcm2Nii', command=lambda: self.select_module('Dcm2Nii'))
        self.menu.add_command(label='Nifti viewer', command=lambda: self.select_module('Nifti viewer'))
        self.menu.add_command(label='TransferFile', command=lambda: self.select_module('TransferFile'))
        # 创建一个按钮来展示下拉菜单
        self.menu_button = tk.Button(self.menu_frame, text='MODULE', command=self.show_menu,bg='black',fg='white',font=("Helvetica", 10, "bold"),relief=tk.GROOVE)
        self.menu_button.pack(side='left',fill=tk.Y)
        # 创建一个label来展示选择的模块
        # 用来拖拽窗口并展示选择的模块
        self.which_module = tk.StringVar()
        self.which_module.set('Nifti file label recorder')
        draggable_button_options = {'bg': '#181818','fg':'#abe338', 'font': ("Helvetica", 20, "bold"),'anchor': 'w', 'justify': 'left'}
        self.parent = master
        self.draggable_button = DraggableLabel(self.parent, self.menu_frame, textvariable=self.which_module, **draggable_button_options)
        self.draggable_button.pack(side='left', fill='both', expand=True, anchor='w')
        # # 用来关闭窗口
        # tk.Button(self.menu_frame, text="Exit", font=("Helvetica", 8, "bold"),
        #           bg='#af0101', fg='#ffffff', height=1, width=4,
        #           command=self.quit).pack(side='left',fill=tk.Y)
        # 用来关闭窗口
        tk.Button(self.menu_frame, text="HOME", font=("Helvetica", 10, "bold"),
                  bg='#af0101', fg='#ffffff', height=1, width=10,
                  command=lambda: self.select_module('home')).pack(side='left',fill=tk.Y)
        # 记录菜单的状态
        self.menu_shown = False
        # 显示初始的界面
        self.module_selected = MainMenu(root, callback=self.select_module)
        self.module_selected.place(relx=0.5, rely=0.52, anchor=tk.CENTER)
        # self.module_selected = MainMenu(root, callback=self.select_module)
    def show_menu(self):
        # 获取菜单相对于屏幕的位置
        x = self.menu_button.winfo_rootx()
        y = self.menu_button.winfo_rooty()
        # 如果菜单已经显示，则隐藏菜单
        if self.menu_shown:
            self.menu.unpost()
            self.menu_shown = False
            return
        # 否则，显示菜单并将菜单状态设置为显示
        self.menu_shown = True
        self.menu.post(x, y + 30)
        self.menu_button.focus_set()
        # 当焦点离开菜单按钮时隐藏菜单
        self.menu_button.bind('<FocusOut>', lambda _: self.hide_menu())
    def hide_menu(self):
        if self.menu_shown:
            self.menu.unpost()
            self.menu_shown = False
    def select_module(self, module_name):
        # 处理选择的模块
        # next_step = tk.messagebox.askyesno(title='你保存了吗？', message='你保存了吗？\n你保存了吗？\n你保存了吗？')
        # if next_step:
        # 首先设置显示的名字
        self.which_module.set(module_name)
        # 销毁之前的模块
        self.module_selected.destroy()
        # 显示模块
        if module_name == 'home':
            self.module_selected = MainMenu(root, callback=self.select_module)
            self.module_selected.place(relx=0.5, rely=0.52, anchor=tk.CENTER)
        else:
            self.module_selected = module_dict[module_name](root)
            self.module_selected.pack(fill='x',expand=True)
        # 隐藏菜单并将菜单状态设置为隐藏
        self.menu.unpost()
        self.menu_shown = False
if __name__ == "__main__":
    root = tk.Tk()
    # # -------------窗口居中---------------
    # 设置窗口大小
    winWidth = 1020
    winHeight = 600
    # 获取屏幕分辨率
    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()
    # 中间位置坐标
    x = int((screenWidth - winWidth) / 2)
    y = int((screenHeight - winHeight) / 2)
    # 设置窗口初始位置在屏幕居中
    root.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
    # root.overrideredirect(True)  # 关闭边框
    # root.attributes("-topmost", True)  # 窗口置顶
    # -------------其他定义------------
    root.title("File Browser")
    root.config(background="#181818")
    # root.configure(highlightthickness=10, highlightbackground='#abe338', highlightcolor='#181818')  # 设置边框
    # menubar = tk.Menu(root)
    #
    # filemenu = tk.Menu(menubar, tearoff=0)
    # menubar.add_cascade(label='File', menu=filemenu)
    # filemenu.add_command(label='Save')
    # filemenu.add_command(label='Exit', command=root.quit)
    #
    # editmenu = tk.Menu(menubar, tearoff=0)
    # menubar.add_cascade(label='Help', menu=editmenu)
    #
    # root.config(menu=menubar)
    module_dict = {'Nifti viewer':NiftiViewer,'home':MainMenu,'TransferFile':TransferFile,'Dcm2Nii':Dcm2Nii}
    # tk.Frame(root,bg='#181818').pack(pady=3)  # 间隔用的
    MyMenu(root,module_dict).pack(fill="both",pady=0)
    # tk.Frame(root,bg='#181818').pack(pady=3)  # 间隔用的
    # NiftiViewer(root).pack()
root.mainloop()

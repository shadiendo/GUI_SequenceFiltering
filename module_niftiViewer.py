#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from my_tool_kit import NiftiViewerFrame
from my_tool_kit import Tooltip
from my_tool_kit import ShowTopLevel
from my_tool_kit import DraggableButton
from my_tool_kit import ClickableLabel
class NiftiViewer(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # 给打开按钮
        btn_sty_open = {'height':1,'width': '10', 'bg': '#3b3abe', 'fg': '#ffffff', 'font': ("Helvetica", 10, "bold"),
                        'borderwidth':5,'relief':'raised','highlightbackground':'#abe338','highlightcolor':'#abe338',
                        }
        # 给SAVE按钮
        btn_sty_save = {'height':1,'width': '10', 'bg': '#af0101', 'fg': '#ffffff', 'font': ("Helvetica", 10, "bold"),
                        'borderwidth':5,'relief':'raised','highlightbackground':'#abe338','highlightcolor':'#abe338',
                        }
        # 给CHECK按钮
        btn_sty_check = {'height':1,'width': '10', 'bg': '#3b3abe', 'fg': '#ffffff', 'font': ("Helvetica", 10, "bold"),
                        'borderwidth':5,'relief':'raised','highlightbackground':'#abe338','highlightcolor':'#abe338',
                        }
        # 给那6个按钮
        btn_sty1 = {'width': '10', 'bg': '#3b3abe', 'fg': '#ffffff', 'font': ("Helvetica",10,"bold")}
        self.binding_dict = {}
        self.json_save_path = tk.StringVar()
        self.file_path = tk.StringVar()
        self.root_folder = tk.StringVar()
        self.json_save_path.set(os.path.join(os.getcwd(),'defualt.json'))
        # 大frame
        main_frame = tk.Frame(self, bg='#181818')
        main_frame.pack(fill="both")
        # 右侧frame   treeview/限制 + 操作面板 + 图像显示
        mian_frame_TOP = tk.Frame(main_frame, bg='#181818')
        mian_frame_TOP.pack(padx=0, pady=0, anchor=tk.NW)
        # treeview页面
        main_frame_L = tk.Frame(mian_frame_TOP, bg='#181818')
        main_frame_L.pack(side='left', padx=0, pady=0, anchor=tk.NW,fill="both")
        # 操作面板
        main_frame_M = tk.Frame(mian_frame_TOP, bg='#181818')
        main_frame_M.pack(side='left', padx=5, pady=5, anchor=tk.NW)
        # 图像页面
        main_frame_R = tk.Frame(mian_frame_TOP, bg='#181818')
        main_frame_R.pack(side='left', padx=0, pady=0, anchor=tk.NW, fill=tk.BOTH, expand=True)
        # 底部frame json
        mian_frame_RRR_bottom = tk.Frame(main_frame, bg='#181818')
        mian_frame_RRR_bottom.pack(padx=0, pady=0, anchor=tk.NW, fill=tk.BOTH, expand=True)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 创建中部，用来放树结构
        frame_L_body = tk.Frame(main_frame_L, bg='#181818')
        frame_L_body.pack(expand=True, anchor=tk.NW)
        style = ttk.Style(parent)
        style.theme_use("clam")  # set ttk theme to "clam" which support the fieldbackground option
        style.configure("Treeview", background="black", fieldbackground="black", foreground="white"
                        # ,font=['Helvetica',8]
                        )
        style.configure("Treeview.Heading", background="black",fieldbackground="black", foreground="white")
        # 创建并配置树状结构的列和列标题
        self.treeview = ttk.Treeview(frame_L_body, height=24)
        self.treeview["columns"] = ("size")
        self.treeview.column("#0", width=330, minwidth=100, stretch=True)
        self.treeview.column("size", width=80, minwidth=80, stretch=True)
        self.treeview.heading("#0", text="FileName", anchor=tk.W)
        self.treeview.heading("size", text="Size", anchor=tk.W)
        # 将树状结构放到界面上并配置展示参数
        self.treeview.pack(padx=0, pady=0, expand=True, anchor=tk.NW)
        self.treeview.bind("<<TreeviewSelect>>", self.on_treeview_select)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 创建顶部 frame，用于输入限制条件和根目录位置
        frame_L_top = tk.Frame(frame_L_body, bg='#181818', width=380, height=20)
        frame_L_top.pack(anchor=tk.W, fill=tk.X, expand=True)
        frame_L_top.pack_propagate(0)
        ClickableLabel(frame_L_top,lambda:self.open_current_file_folder(self.file_path.get()), text='Open Current Nifti Path', width=0, bg='#181818', fg='#abe338',
                 font=("Helvetica", 8, "bold"), relief='groove').pack(side="left", padx=0, pady=0)
        tk.Entry(frame_L_top, textvariable=self.root_folder,
                 font=("Helvetica", 8, "bold"), bg='#242424', fg='#b0b1b3').pack(side='left', expand=True, fill=tk.X,anchor=tk.W)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 创建浏览按钮和根目录输入框
        frame_M_body1 = tk.Frame(main_frame_M, bg='#181818')
        frame_M_body1.pack(anchor='center', padx=0, pady=0,fill=tk.BOTH,expand=True)
        # Open_tips = tk.Label(frame_M_body1, text='Open', font=("Helvetica", 8, "bold"),
        #                      width=0, bg='#181818', fg='#ffffff')
        # Open_tips.grid(row=0, column=0, sticky='e')
        browse_button = tk.Button(frame_M_body1, text='Open Root', **btn_sty_open,
                                  command=self.on_browse_button_click)
        browse_button.pack(anchor='center',fill=tk.X)
        # self.create_tooltip(
        #     browse_button, 'Tips:'
        #                '\n  1.Click the "Root" button and select the root directory where the NIFTI file folder is stored.'
        #                '\n  2.You can click the buttons below to flip through pages, or use the up and down arrow keys on your keyboard.'
        #                '\n  3.Classify the sequence displayed on the right into one of the six categories shown bellow.')
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 分隔符
        frame_M_body4_s = tk.Frame(main_frame_M, bg='#181818')
        frame_M_body4_s.pack(fill=tk.BOTH, padx=0, pady=4)
        ttk.Separator(frame_M_body4_s, orient=tk.HORIZONTAL).pack(side="left", padx=0, pady=5, fill='x', expand=True)
        tk.Label(frame_M_body4_s, text='Json related', width=0, bg='#181818', fg='#abe338',
                 font=("Helvetica", 8, "bold")).pack(side="left", padx=0, pady=0)  # 填空
        ttk.Separator(frame_M_body4_s, orient=tk.HORIZONTAL).pack(side="left", padx=0, pady=5, fill='x', expand=True)
        tk.Button(main_frame_M, text='Load',**btn_sty_check,
                                command=self.load_json_file).pack()
        # 用来保存分类后的字典文件→JSON
        frame_M_body4 = tk.Frame(main_frame_M, bg='#181818')
        frame_M_body4.pack(fill=tk.BOTH, padx=0, pady=0)
        tk.Button(frame_M_body4, text='Save', **btn_sty_save, command=self.save_json_file).pack()
        tk.Button(frame_M_body4, text='Check',**btn_sty_check,
                  command=lambda: self.show_top_level(json.dumps(self.binding_dict, indent=4))).pack()
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 分隔符
        frame_M_body3_s = tk.Frame(main_frame_M, bg='#181818')
        frame_M_body3_s.pack(fill=tk.BOTH, padx=0, pady=4)
        ttk.Separator(frame_M_body3_s, orient=tk.HORIZONTAL).pack(side="left", padx=0, pady=5, fill='x', expand=True)
        tk.Label(frame_M_body3_s, text='classify', width=0, bg='#181818', fg='#abe338',
                 font=("Helvetica", 8, "bold")).pack(side="left", padx=0, pady=0)  # 填空
        ttk.Separator(frame_M_body3_s, orient=tk.HORIZONTAL).pack(side="left", padx=0, pady=5, fill='x', expand=True)
        # 用来放6个分类按钮
        frame_M_body3 = tk.Frame(main_frame_M, bg='#181818')
        frame_M_body3.pack(fill=tk.BOTH, padx=0, pady=0)
        self.btn_T1 = tk.Button(frame_M_body3, text='T1', **btn_sty1,height=1,
                                command=lambda: self.button_classify_clicked('T1'))
        self.btn_T1.pack()
        self.btn_T1CE = tk.Button(frame_M_body3, text='T1CE', **btn_sty1,height=1,
                                  command=lambda: self.button_classify_clicked('T1CE'))
        self.btn_T1CE.pack()
        self.btn_T2 = tk.Button(frame_M_body3, text='T2', **btn_sty1,height=1,
                                command=lambda: self.button_classify_clicked('T2'))
        self.btn_T2.pack()
        self.btn_T2Flair = tk.Button(frame_M_body3, text='T2Flair', **btn_sty1,height=1,
                                     command=lambda: self.button_classify_clicked('T2Flair'))
        self.btn_T2Flair.pack()
        self.btn_DWI = tk.Button(frame_M_body3, text='DWI', **btn_sty1,height=1,
                                 command=lambda: self.button_classify_clicked('DWI'))
        self.btn_DWI.pack()
        self.btn_ADC = tk.Button(frame_M_body3, text='ADC', **btn_sty1,height=1,
                                 command=lambda: self.button_classify_clicked('ADC'))
        self.btn_ADC.pack()
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 分隔符
        frame_M_body5_s = tk.Frame(main_frame_M, bg='#181818')
        frame_M_body5_s.pack(fill=tk.BOTH, padx=0, pady=4)
        ttk.Separator(frame_M_body5_s, orient=tk.HORIZONTAL).pack(side="left", padx=0, pady=5, fill='x', expand=True)
        tk.Label(frame_M_body5_s, text='drag panel', width=0, bg='#181818', fg='#abe338',
                 font=("Helvetica", 8, "bold")).pack(side="left", padx=0, pady=0)  # 填空
        ttk.Separator(frame_M_body5_s, orient=tk.HORIZONTAL).pack(side="left", padx=0, pady=5, fill='x', expand=True)
        # 用来拖动整个窗口
        frame_M_body5 = tk.Frame(main_frame_M, bg='#181818')
        frame_M_body5.pack(fill=tk.BOTH, padx=0, pady=0)
        # 界面拖动按钮的参数为三个 1.父级框架(整个窗口) 2.这个控件的位置 3.按钮参数
        btn_text = '''
,-.       _,---._ __  / \\
 /  )    .-'       `./ /   \\
(  (   ,'            `/    /|
 \\  `-"             \\'\\   / |
  `.              ,  \\ \\ /  |
   /`.          ,'-`----Y   |
  (            ;        |   '
  |  ,-.    ,-'         |  /
  \\  | (   |           | /
  `'`   `'`_____|/
        van
        '''
        button_options = {"text": btn_text, 'bg': '#b0b1b3', 'width': '15', 'height': '16',
                          'font': ("Helvetica", 5, "bold")}
        self.parent = parent
        self.draggable_button = DraggableButton(parent, frame_M_body5, **button_options)
        self.draggable_button.pack(fill="both", expand=True, anchor='center')
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 创建右侧frame，用于展示图像
        self.frame_bottommmmm = tk.Frame(main_frame_R, bg='#181818')
        self.frame_bottommmmm.pack()
        viewer_frame = NiftiViewerFrame(self.frame_bottommmmm, "feifei.nii.gz")
        viewer_frame.pack(fill="both", expand=True)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        frame_M_body0 = tk.Frame(mian_frame_RRR_bottom, bg='#181818')
        frame_M_body0.pack(fill=tk.BOTH, padx=0, pady=0, expand=True,anchor=tk.W)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ClickableLabel(frame_M_body0,lambda:self.open_current_file_folder(self.json_save_path.get()), text='Open JSON Saving Path', width=0, bg='#181818', fg='#abe338',
                 font=("Helvetica", 8, "bold"), relief='groove').pack(side="left", padx=0, pady=0)
        tk.Entry(frame_M_body0, textvariable=self.json_save_path,width=20,
                 font=("Helvetica", 8, "bold"), bg='#242424', fg='#b0b1b3').pack(side='left', expand=True,fill=tk.X,anchor=tk.W)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 创建顶部 frame，用于输入限制条件和根目录位置
        frame_restrict = tk.Frame(frame_M_body0, bg='#181818', width=570, height=20)
        frame_restrict.pack(side='left',anchor=tk.W, fill=tk.X, expand=True)
        # frame_restrict.pack_propagate(0)
        Label_top3 = tk.Label(frame_restrict, text='Min Size', font=("Helvetica", 8), width=7, bg='#181818', fg='#ffffff')
        Label_top3.pack(side='left')
        self.restrict_size = tk.StringVar()
        self.restrict_size.set('200')
        entry_top1 = tk.Entry(frame_restrict, textvariable=self.restrict_size, font=("Helvetica", 8, "bold"), width=4,
                              bg='#242424', fg='#b0b1b3')
        entry_top1.pack(side='left')
        self.create_tooltip(entry_top1, 'If the file size exceeds the threshold, the file will not appear.')
        Label_top1 = tk.Label(frame_restrict, text='Include', font=("Helvetica", 8), width=6, bg='#181818', fg='#ffffff')
        Label_top1.pack(side='left')
        self.restrict_mustHave = tk.StringVar()
        self.restrict_mustHave.set('.nii.gz')
        entry_top2 = tk.Entry(frame_restrict, textvariable=self.restrict_mustHave, font=("Helvetica", 8, "bold"), width=8,
                              bg='#242424', fg='#b0b1b3')
        entry_top2.pack(side='left')
        self.create_tooltip(entry_top2, 'If neither of the two is included, the file will not appear.\n'
                                        'But, in this version only .nii.gz files will be recognized by default.')
        Label_top2 = tk.Label(frame_restrict, text='Exclude', font=("Helvetica", 8), width=7, bg='#181818', fg='#ffffff')
        Label_top2.pack(side='left')
        self.restrict_mustNotHave = tk.StringVar()
        self.restrict_mustNotHave.set('localizer|PosDisp|Screen_Save|SWI|Pl_Loc|Pha_Images|vibe|DKI|DTI|mIP_Images|Mag_Images')
        entry_top3 = tk.Entry(frame_restrict, textvariable=self.restrict_mustNotHave, font=("Helvetica", 8, "bold"),
                              bg='#242424', fg='#b0b1b3')
        entry_top3.pack(side='left', fill=tk.BOTH, expand=True)
        self.create_tooltip(entry_top3, 'If either one is included, the file will not appear.\n\n'+self.restrict_mustNotHave.get())
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def open_current_file_folder(self,file_path):
        """
        打开指定路径的文件夹
        """
        try:
            folder = os.path.dirname(file_path)
            os.startfile(folder)
        except:
            pass
    def show_top_level(self, info):
        ShowTopLevel(self, info)
    def load_json_file(self):
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), defaultextension='.json',
                                               filetypes=[('JSON Files', '*.json')])
        if file_path:
            with open(file_path, 'r') as f:
                self.binding_dict.update(json.load(f))
            # 清空现有的 Treeview 项目
            for item in self.treeview.get_children():
                self.treeview.delete(item)
            # 使用更新后的 self.binding_dict 重新填充 Treeview
            root_folder = self.root_folder.get()
            self.fill_treeview(root_folder, '')
            # self.fill_treeview(root_path, root_parent, highlight_paths)
            self.highlight_parent_directories(self.treeview)
            # 设置成保存文件的路径
            self.json_save_path.set(file_path)
    def save_json_file(self):
        # 打开资源管理器对话框，让用户选择要保存文件的位置
        file_path = self.json_save_path.get()
        # 将字典转换为 JSON 格式字符串，并将其写入文件中
        json_str = json.dumps(self.binding_dict, indent=4)
        with open(file_path, 'w') as f:
            f.write(json_str)
        self.show_top_level('已经保存！')
    # 专门用来改变颜色
    def button_change_color(self):
        buttons = [self.btn_T1, self.btn_T1CE, self.btn_T2, self.btn_T2Flair, self.btn_DWI, self.btn_ADC]
        def set_button_colors(active_btn, toggle):
            for btn in buttons:
                if btn == active_btn:
                    if toggle:
                        btn.config(bg='#3b3abe')
                    else:
                        btn.config(bg='red')
                else:
                    btn.config(bg='#3b3abe')
        current_image_path = self.file_path.get()
        if current_image_path in self.binding_dict:
            label_name = self.binding_dict[current_image_path]
            button_dict = {
                'T1': self.btn_T1,
                'T1CE': self.btn_T1CE,
                'T2': self.btn_T2,
                'T2Flair': self.btn_T2Flair,
                'DWI': self.btn_DWI,
                'ADC': self.btn_ADC
            }
            if label_name in button_dict:
                active_btn = button_dict[label_name]
                toggle = active_btn.cget('bg') == 'red'  # 判断按钮是否为红色，若是，则切换颜色
                set_button_colors(active_btn, toggle)
                # 设置目录的颜色
                self.highlight_selected_directory(color='red', toggle=toggle)
                if toggle:  # 如果在切换颜色时，需要将按钮颜色恢复为原始颜色，也要从字典中删除该键值对
                    del self.binding_dict[current_image_path]
            else:
                for btn in buttons:
                    btn.config(bg='#3b3abe')
        else:
            # 如果当前路径没有被打上标签，那么按钮颜色清空成本来的状态
            for btn in buttons:
                btn.config(bg='#3b3abe')
    # 用来给序列打标签的
    def button_classify_clicked(self, sequence_name):
        # 获取当前文件路径
        current_image_path = self.file_path.get()
        # 更新字典中对应文件路径的标签信息，使用传递的 button_name 参数
        self.binding_dict[current_image_path] = sequence_name
        # 将更新后的字典保存到 JSON 文件中
        # with open('binding_dict.json', 'w') as f:
        #     json.dump(self.binding_dict, f)
        self.button_change_color()
    def create_tooltip(self, widget, text):
        tooltip = Tooltip(widget, text)
        widget.bind('<Enter>', lambda _: tooltip.show_tip())
        widget.bind('<Leave>', lambda _: tooltip.hide_tip())
    def include_exclude(self):
        restrict_size = self.restrict_size.get()
        restrict_mustHave = self.restrict_mustHave.get()
        restrict_mustNotHave = self.restrict_mustNotHave.get()
        try:
            restrict_mustHave_list = []
            for i in restrict_mustHave.split('|'):
                restrict_mustHave_list.append(i.strip())
            restrict_mustNotHave_list = []
            for i in restrict_mustNotHave.split('|'):
                restrict_mustNotHave_list.append(i.strip())
            restrict_size_int = int(restrict_size.strip())* 1024
            retdict = {'restrict_size': restrict_size_int,
                       'restrict_mustHave': restrict_mustHave_list,
                       'restrict_mustNotHave': restrict_mustNotHave_list}
            return retdict
        except:
            tk.messagebox.showinfo(title='重新修改', message='三个限制条件不符合规范')
            return 'error'
    # 将父级也变成红色
    def highlight_parent_directories(self, treeview):
        for item in treeview.get_children(''):
            self._highlight_parent_directories_recursive(treeview, item)
    # 辅助函数
    def _highlight_parent_directories_recursive(self, treeview, item):
        # 获取当前项的所有子项
        children = treeview.get_children(item)
        # 遍历子项
        for child in children:
            # 检查子项是否是红色字体
            if 'highlight' in treeview.item(child)['tags']:
                # 获取选中行及其父行
                items_to_highlight = []
                parent_item = treeview.parent(child)
                while parent_item:
                    items_to_highlight.append(parent_item)
                    parent_item = treeview.parent(parent_item)
                # 根据 toggle 参数添加或移除标签
                for item_to_highlight in items_to_highlight:
                    self.treeview.item(item_to_highlight, tags=('highlight',))
                # 配置标签颜色
                self.treeview.tag_configure('highlight', foreground='red')
            # 继续递归地检查子项的子项
            self._highlight_parent_directories_recursive(treeview, child)
        treeview.update_idletasks()
    # 给文件目录及其父级设置颜色高亮
    def highlight_selected_directory(self, color, toggle):
        selected_item = self.treeview.selection()
        if selected_item:
            item = selected_item[0]
            # 获取选中行及其父行
            items_to_highlight = [item]
            parent_item = self.treeview.parent(item)
            while parent_item:
                items_to_highlight.append(parent_item)
                parent_item = self.treeview.parent(parent_item)
            # 根据 toggle 参数添加或移除标签
            tags = () if toggle else ('highlight',)
            for item_to_highlight in items_to_highlight:
                self.treeview.item(item_to_highlight, tags=tags)
            # 配置标签颜色
            self.treeview.tag_configure('highlight', foreground=color)
        self.treeview.update_idletasks()
    # 加载树状结构
    def fill_treeview(self, path, parent):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            if os.path.isdir(abspath):
                oid = self.treeview.insert(parent, 'end', text=p, open=False)
                self.fill_treeview(abspath, oid)
            else:
                # 获取文件大小
                size = os.path.getsize(abspath)
                # any() returns True if at least one element in an iterable (such as a list, tuple, or set) evaluates to True, and False otherwise.
                # all() returns True if all elements in an iterable (such as a list, tuple, or set) evaluate to True, and False otherwise.
                # 检查文件名是不是设定的其中之一
                flag1 = any(i in p for i in self.include_exclude()['restrict_mustHave'])
                # 先检查文件名中是否有关键词，有的话直接毙掉
                flag2 = all(i not in p for i in self.include_exclude()['restrict_mustNotHave'])
                # 检查文件大小是否合法
                flag3 = size > self.include_exclude()['restrict_size']
                if flag1 and flag2 and flag3:
                    # print(f'当前文件为{p},纳入')
                    oid = self.treeview.insert(parent, 'end', text=p, open=False)
                    # 如果文件路径在 binding_dict 中，将其在 Treeview 中显示为红色
                    if abspath in self.binding_dict:
                        self.treeview.item(oid, tags=('highlight',))
                        self.treeview.tag_configure('highlight', foreground='red')
                    if size < 1024:
                        size = '1KB'
                    elif size / 1024 < 1024:
                        size = str(round((size / 1024), 1)) + ' KB'
                    else:
                        size = str(round((size / 1024 / 1024), 1)) + ' MB'
                    # 把文件载入树状结构中
                    self.treeview.set(oid, 'size', ' '+size)
                else:
                    # print(f'当前文件为{p},否纳入')
                    pass
    # 打开主文件夹按钮
    def on_browse_button_click(self):
        # 首先确保限制条件格式正确
        # print(self.include_exclude())
        if self.include_exclude() != 'error':
            folder_selected = filedialog.askdirectory()
            if folder_selected:
                self.root_folder.set(folder_selected)
                self.treeview.delete(*self.treeview.get_children())
                self.fill_treeview(folder_selected, '')
    def on_treeview_select(self, event):
        selected_item = self.treeview.selection()
        if selected_item:
            file_path = self.treeview.item(selected_item[0], 'text')
            parent_item = self.treeview.parent(selected_item[0])
            while parent_item:
                file_path = os.path.join(self.treeview.item(parent_item, 'text'), file_path)
                parent_item = self.treeview.parent(parent_item)
            full_path = os.path.join(self.root_folder.get(), file_path)
            self.file_path.set(full_path)
            # 改变颜色  但是这里有个bug
            self.button_change_color()
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 输出图像
            if self.file_path.get()[-7:] == '.nii.gz':
                for widget in self.frame_bottommmmm.winfo_children():
                    widget.destroy()
                viewer_frame = NiftiViewerFrame(self.frame_bottommmmm, self.file_path.get())
                viewer_frame.pack(fill="both", expand=True)

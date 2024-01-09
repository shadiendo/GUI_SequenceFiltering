import threading
import os
import shutil
import tkinter as tk
from tkinter import scrolledtext, END, messagebox
from my_tool_kit import ShowTopLevel
from tkinter import filedialog
import json
class TransferFile(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg="#181818")
        self.parent = parent
        self.binding_dict = {}
        self.json_file_path = tk.Variable()
        self.check_btn_name = tk.Variable()
        self.check_btn_name.set('Check Mappings')
        self.root_path = tk.Variable()
        self.save_path = tk.Variable()
        label_style = {'bg': '#181818', 'fg': 'white'}
        # 放顶部的所有按钮
        frame_Top = tk.Frame(self,bg="#181818")
        frame_Top.pack(pady=0)
        # 打开按钮和check按钮
        self.frame_Top_1 = tk.Frame(frame_Top,bg="#181818")
        self.frame_Top_1.pack(side='left')
        tk.Label(frame_Top, text=' next → ',**label_style).pack(side='left')
        # 设置路径转移
        self.frame_Top_2 = tk.Frame(frame_Top,bg="#181818")
        self.frame_Top_2.pack(side='left')
        self.frame_Top_2.config(highlightbackground="#dd001b", highlightthickness=7)
        tk.Label(frame_Top, text=' next → ',**label_style).pack(side='left')
        # 启动和停止按钮
        self.frame_Top_3 = tk.Frame(frame_Top,bg="#181818")
        self.frame_Top_3.pack(side='left')
        self.frame_Top_3.config(highlightbackground="#dd001b", highlightthickness=7)
        # 填空
        tk.Frame(self,bg="#181818").pack(pady=15)
        # 放日志
        frame_Bottom = tk.Frame(self,bg="#181818")
        frame_Bottom.pack(pady=0,anchor=tk.CENTER)
        # #######################################
        # 设置启动
        self.btn_load_json = tk.Button(self.frame_Top_1, text='Load Json File',width=20, height=1,bg='#abe338',fg='black',command=self.load_json_file)
        self.btn_load_json.grid(row=0, column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        tk.Button(self.frame_Top_1, textvariable=self.check_btn_name,width=20, height=1,bg='#2b2b2b',fg='white',
                  command=lambda: ShowTopLevel(self,json.dumps(self.binding_dict, indent=4))).grid(row=1, column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        # 设置路径
        self.set_dst = tk.Button(self.frame_Top_2, text='Set Root Path\n(src copy to dst)',width=20, height=2,bg='black',fg='white',
                                 command=self.set_transfer_path, state='disabled')
        self.set_dst.grid(row=0, column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        # 创建转移按钮和终止按钮
        self.transfer_button = tk.Button(self.frame_Top_3, text='Copy\nStart',width=7, height=2, command=self.start_transfer,bg='black',fg='white', state='disabled')
        self.transfer_button.grid(row=0, column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.stop_button = tk.Button(self.frame_Top_3, text='Pause',width=7, height=2, command=self.stop_transfer,bg='black',fg='white', state='disabled')
        self.stop_button.grid(row=0, column=1,sticky=tk.N+tk.S+tk.E+tk.W)
        # #######################################
        self.stop_requested = False  # 记录是否请求停止文件转移
        # #######################################
        # 创建日志窗口
        self.log_info = scrolledtext.ScrolledText(self)
        self.log_info.configure(bg='lightgray')
        self.log_info.insert("insert", "python")
        self.log_info.delete(1.0, END)  # 使用 delete
        self.log_info.pack(anchor=tk.CENTER)
    def start_transfer(self):
        # 禁用转移按钮，并启用终止按钮
        self.transfer_button.config(state='disabled')
        self.stop_button.config(state='normal')
        # 创建一个线程来执行文件转移操作
        transfer_thread = threading.Thread(target=self.transfer_files)
        transfer_thread.start()
    def transfer_files(self):
        json_data = self.binding_dict
        next_step = tk.messagebox.askyesno(title='确定要转移', message='确定无误后再转移！')
        if next_step:
            dict_folder = self.rearrangingTheDict(json_data)
            for folder_path, subdict in dict_folder.items():
                # 如果停止按钮被请求，退出循环
                if self.stop_requested:
                    break
                new_subdict = self.rearranging_the_subdictName(subdict)
                for old_name, label in new_subdict.items():
                    old_path = os.path.join(folder_path, old_name)
                    old_path_change_name = os.path.join(folder_path, label + '.nii.gz')
                    trans_path = old_path_change_name.replace(self.root_path.get(), self.save_path.get())
                    # 检查停止按钮是否被请求
                    if self.stop_requested:
                        break
                    self.log_info.insert(END, f"\n复制一份到新路径\n    {old_path}\n    {trans_path}\n")
                    self.log_info.see(tk.END)  # 自动滚动到最底部
                    if not os.path.exists(trans_path):
                        file_folder = '\\'.join(trans_path.split('\\')[:-1])
                        if not os.path.exists(file_folder):
                            os.makedirs(file_folder)
                        shutil.copy(old_path, trans_path)
        # 启用转移按钮，并禁用终止按钮
        self.transfer_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.stop_requested = False
    def stop_transfer(self):
        # 请求停止文件转移
        self.stop_requested = True
        self.log_info.insert(END, f"\n{'#' * 50}\n已经终止转移！！！")
    '''
    {'demo1.nii.gz': 'T1CE', 'demo2.nii.gz': 'T1CE', 'demo3.nii.gz': 'DWI'}
    整理成↓↓↓
    {'demo1.nii.gz': 'T1CE', 'demo2.nii.gz': 'T1CE_1', 'demo3.nii.gz': 'DWI'}
    '''
    def rearranging_the_subdictName(self,sub_dict):
        # 定义一个字典，用于保存每个属性对应的出现次数
        dict_count = {}
        # 定义一个新的字典，用于保存更新后的键值对
        dict_file_new = {}
        for key, value in sub_dict.items():
            # 如果当前属性已经在dict_count中，则将计数器加1，并将属性名修改为属性名+计数器
            if value in dict_count:
                dict_count[value] += 1
                new_value = f"{value}_{dict_count[value]}"
            else:
                # 否则，将计数器设置为0，并将属性名保持不变
                dict_count[value] = 0
                new_value = value
            # 将更新后的键值对保存到新的字典中
            dict_file_new[key] = new_value
        return dict_file_new
    '''
    {'J:/20230602/X0871181\demo1.nii.gz': 'T1CE',
    'J:/20230602/X0871181\demo2.nii.gz': 'T1CE',
    'J:/20230602/X0941181\demo3.nii.gz': 'T1'}
    整理成↓↓↓
    {'J:/20230602/X0871181': {'demo1.nii.gz': 'T1CE', 'demo2.nii.gz': 'T1CE'},
     'J:/20230602/X0941181': {'demo3.nii.gz': 'T1'}}
    '''
    def rearrangingTheDict(self,dict_orig):
        # 定义一个字典，用于保存每个文件夹内的文件属性和文件名
        dict_folder = {}
        for key, value in dict_orig.items():
            # 获取文件所在的文件夹路径和文件名
            folder_path, filename = os.path.split(key)
            # 如果当前文件夹路径已经在dict_folder中，则将当前文件属性和文件名添加到该文件夹对应的字典中
            if folder_path in dict_folder:
                dict_folder[folder_path][filename] = value
            else:
                # 否则，创建一个新的字典，并将当前文件属性和文件名添加到字典中
                dict_folder[folder_path] = {filename: value}
        return dict_folder
    def set_transfer_path(self):
        # 打开资源管理器对话框并选择路径
        save_path = filedialog.askdirectory()
        self.log_info.insert(END, f"{'#' * 50}\n设置转移路径：{save_path}\n")
        self.save_path.set(save_path.replace("/", "\\"))
        if len(save_path)>3:
            # 下一步的按钮激活，边框颜色激活
            self.transfer_button.config(state='normal',bg='#2b2b2b')
            self.frame_Top_3.config(highlightbackground="#abe338", highlightthickness=7)
            self.frame_Top_3.update()
        else:
            self.log_info.insert(END, f"{'#' * 50}\n设置转移路径：{save_path}，建议重设，别在根目录\n")
    '''
    {'J:/20230602/X0871181\demo1.nii.gz': 'T1CE',
    'J:/20230602/X0871181\demo2.nii.gz': 'T1CE',
    'J:/20230602/X0941181\demo3.nii.gz': 'T1'}
    修正成↓↓↓
    {'J:\\20230602\\X0871181\\demo1.nii.gz': 'T1CE',
    'J:\\20230602\\X0871181\\demo2.nii.gz': 'T1CE',
    'J:\\20230602\\X0941181\\demo3.nii.gz': 'T1'}
    '''
    def fix_dict_paths(self,dict_file):
        dict_file_new = {}
        for key, value in dict_file.items():
            # 将反斜杠替换为正斜杠，并使用os.path.normpath()函数将字符串转换为标准路径
            new_key = os.path.normpath(key.replace('\\', '/'))
            dict_file_new[new_key] = value
        return dict_file_new
    def load_json_file(self):
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), defaultextension='.json',
                                               filetypes=[('JSON Files', '*.json')])
        self.json_file_path.set(file_path)
        try:
            if file_path:
                with open(file_path, 'r') as f:
                    self.binding_dict.update(json.load(f))
            self.log_info.insert(END, f"{'#'*50}\n成功读取json文件:\n{file_path}\n\n")
            # 先修复一下文件路径的问题
            self.binding_dict = self.fix_dict_paths(self.binding_dict)
            json_data = self.binding_dict
            self.check_btn_name.set(f'Mappings(n={len(json_data)})')
            # 展示前三个
            self.log_info.insert(END, f"{'#' * 50}\n共{len(json_data)}个文件，随机查看两个映射:\n")
            for i in list(json_data.items())[:2]:
                self.log_info.insert(END, f"{i[1]} : {i[0]}\n")
            # 检查所有文件是否都真实存在
            all_file_exist = True
            for file_path in json_data.keys():
                if not os.path.exists(file_path):
                    self.log_info.insert(END, f"  文件路径不存在: {file_path}\n")
                    all_file_exist = False
            if all_file_exist:
                self.log_info.insert(END, f"\n读取{len(json_data)}个文件，所有文件都真实存在\n")
            else:
                self.log_info.insert(END, f"\n\n{'#' * 50}\n{'#' * 50}\n你应该先检查这些不存在的文件路径再进行下一步!{'#' * 50}\n{'#' * 50}\n\n")
            # 获取共同根目录
            keys = list(json_data.keys())  # 获取所有的路径
            common_prefix = os.path.commonprefix(keys)  # os.path.commonprefix()方法来找到公共前缀
            orig_root = os.path.normpath("\\".join(common_prefix.split('\\')[:-1]))
            self.log_info.insert(END, f"\n原始路径：{orig_root}\n\n")
            self.root_path.set(orig_root)
            # 将下一步的边框按钮变成绿色，下一步的按钮启动
            self.frame_Top_2.config(highlightbackground="#abe338", highlightthickness=7)
            self.frame_Top_2.update()
            self.set_dst.config(state='normal',bg='#2b2b2b')
            # 将自己变成普通状态
            self.btn_load_json.config(bg='#2b2b2b',fg='white')
            self.btn_load_json.update()
        except:
            self.log_info.insert(END, f"{'?'*35}\njson文件内容读不出？:\n {file_path}\n")
if __name__ == "__main__":
    window = tk.Tk()
    window.geometry("1000x600+400+200")
    window.config(bg="#181818")
    main_menu = TransferFile(window)
    main_menu.place(relx=0.5, rely=0.50, anchor=tk.CENTER)
    window.mainloop()

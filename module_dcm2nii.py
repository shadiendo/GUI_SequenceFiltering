import os
import threading
import time
import tkinter as tk
from tkinter import ttk
import random
from tkinter import scrolledtext, END, filedialog
from my_tool_kit import MaxDepthFinder, FolderStructure, Tooltip, DirectoryReader
import subprocess
class Dcm2Nii(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg="#181818")
        self.root_src_path = ''  # 打开的根目录
        self.root_dst_path = ''
        self.path_exe = os.path.join(os.getcwd(), 'Tools', 'dcm2niix.exe')
        self.aim_depth = ''
        self.folder_find = []   # 所有需要转换的文件夹
        self.stop_requested = False  # 记录是否请求停止文件转移
        label_style = {'bg': '#181818', 'fg': 'white'}
        frame_body = tk.Frame(self,bg="#181818")
        frame_body.pack()
        # 放顶部
        frame_TOP = tk.Frame(frame_body,bg="#181818")
        frame_TOP.pack(pady=0)
        frame_TOP_1 = tk.Frame(frame_TOP,bg="#181818")
        frame_TOP_1.pack(side='left',pady=0,padx=5)
        tk.Label(frame_TOP, text=' next → ',**label_style).pack(side='left')
        frame_TOP_2 = tk.Frame(frame_TOP,bg="#181818")
        frame_TOP_2.pack(side='left',pady=0,padx=5)
        tk.Label(frame_TOP, text=' next → ',**label_style).pack(side='left')
        frame_TOP_3 = tk.Frame(frame_TOP,bg="#181818")
        frame_TOP_3.pack(side='left',pady=0,padx=5)
        tk.Label(frame_TOP, text=' next → ',**label_style).pack(side='left')
        frame_TOP_4 = tk.Frame(frame_TOP,bg="#181818")
        frame_TOP_4.pack(side='left',pady=0,padx=5)
        # 放底部
        frame_BOTTOM = tk.Frame(frame_body,bg="#181818")
        frame_BOTTOM.pack(pady=0, fill='x',expand=True)
        BarStyle_npnf = ttk.Style()
        BarStyle_npnf.theme_use('classic')
        # win10环境下主题：('winnative','clam','alt','default','classic','vista','xpnative')
        # 进度条漕的宽度改变测试成功的是：'winnative','alt','default','classic'
        BarStyle_npnf.configure("my0.Horizontal.TProgressbar", troughcolor='white', background='#499c54',
                                thickness=30)  # troughcolor 水槽色
        self.progress = ttk.Progressbar(frame_BOTTOM, orient='horizontal', style="my0.Horizontal.TProgressbar", length=300, mode='determinate')
        self.progress.pack(padx=0, pady=0, fill='x',expand=True)
        # 放两个日志
        frame_BOTTOM_log = tk.Frame(frame_body,bg="#181818")
        frame_BOTTOM_log.pack(pady=0)
        # #################################################
        # 设置根目录路径
        self.set_src = tk.Button(frame_TOP_1, text='Set Root Path', command=self.set_root_path,bg='#abe338',fg='black')
        self.set_src.grid(row=0, column=1, sticky=tk.W + tk.E)
        # #################################################
        # 设置要处理的文件夹层级
        help_1 = tk.Label(frame_TOP_2,text='❓',bg='#181818',fg='white')
        help_1.grid(row=0,column=0)
        self.create_tooltip(help_1,f"★本程序调用MRIcroGL的dcm2nii.exe\n"
                           f"  ·可以进入dicom所在目录直接操作，识别一个dicom文件，就转换整个文件夹，但如此会增加扫描深度;\n"
                           f"  ·可以对dicom所在的父目录【即你的最深目录】进行操作，但如此也不方便，理由同前;\n"
                           f"  ·最佳策略应进入所有序列文件夹目录的上一层，不管它是被试文件夹还是别的什么。\n"
                                   f"注1：如果二级目录不好，大概率是你数据库建设的不好。\n"
                                   f"注2：如果你想要的深度超过3，大概率是你数据库建设的不好"
                           f"注3: 如果你所有的dicom文件都混在了一起，没有被文件夹分开来那么可以用最大目录深度")
        style_combobox = ttk.Style()
        style_combobox.configure('Custom.TCombobox', background='#2b2b2b',foreground='white',fieldbackground='#2b2b2b', disabledbackground='black', disabledforeground='black')
        self.operate_depth = tk.StringVar()
        self.cb = ttk.Combobox(frame_TOP_2, textvariable=self.operate_depth, width=14,style='Custom.TCombobox',state = 'disabled',foreground='white',
                          values=("选择操作深度", "一级目录", "二级目录(推荐)", "三级目录", "dcm所在目录(未实现)"))
        self.cb.current(0)  # 设置默认显示值为列表中的第一个可选项
        self.operate_depth.set("选择操作深度")
        self.cb.grid(row=0,column=1, sticky=tk.W + tk.E)
        self.cb.bind("<<ComboboxSelected>>", self.on_combobox_selected)
        # 设置转移根目录路径
        help_2 = tk.Label(frame_TOP_2,text='❓',bg='#181818',fg='white')
        help_2.grid(row=1,column=0)
        self.create_tooltip(help_2,f"设置转移路径，别跟原始路径一样最好")
        self.set_dst = tk.Button(frame_TOP_2, text='Set convert Path', command=self.set_root_dst, state='disabled',bg='black',fg='white')
        self.set_dst.grid(row=1,column=1, sticky=tk.W + tk.E)
        # #######################################
        # 设置nifti文件名和其他参数
        help_3 = tk.Label(frame_TOP_3,text='❓',bg='#181818',fg='white')
        help_3.grid(row=0,column=0)
        self.create_tooltip(help_3,f"★本程序调用MRIcroGL的dcm2nii.exe，设置nifti文件名和其他参数，这个参数比较好，没事别瞎鸡儿改\n"
                                   f"    -o :output directory\n"
                                   f"    -f :filename\n"
                                   f"    -p :Philips precise float\n"
                                   f"    -z :gz compress images\n"
                                   f"    -b :BIDS sidecar 不输出json\n"
                                   f"  command = <path_exe> -o <path_nifti_save> -f <parm_file_name>[%s--%d--%p--%z] -p y -z y -b n <dicom_path>\n"
                                   f"想要知道更多指令，自行在cmd中查看 dcm2nii.exe")
        self.dcm2nii_parm = tk.Variable()
        self.dcm2nii_parm.set("-f %s--%d--%p--%z -p y -z y -b n")
        self.set_parm = tk.Entry(frame_TOP_3, textvariable=self.dcm2nii_parm, state='disabled',bg='black',fg='white', disabledbackground='black')
        self.set_parm.grid(row=0, column=1, sticky=tk.W + tk.E)
        # 检查并展示层级转换,并计时，看看这一个要转多少时间
        help_4 = tk.Label(frame_TOP_3,text='❓',bg='#181818',fg='white')
        help_4.grid(row=1,column=0)
        self.create_tooltip(help_4,f"检查并展示层级转换,并计时，看看这一个要转多少时间")
        self.convertOneDemo = tk.Button(frame_TOP_3, text='Convert a demo',command=self.check_Dcm2Nii, state='disabled',bg='black',fg='white')
        self.convertOneDemo.grid(row=1,column=1, sticky=tk.W + tk.E)
        # 创建转移按钮和终止按钮
        self.convert_button = tk.Button(frame_TOP_4, text='Convert\nStart',width=7, height=2, command=self.start_convert,bg='black',fg='white', state='disabled')
        self.convert_button.pack(side='left')
        self.stop_button = tk.Button(frame_TOP_4, text='Pause',width=7, height=2, command=self.stop_convert,bg='black',fg='white', state='disabled')
        self.stop_button.pack(side='left')
        # #######################################
        # 创建日志窗口
        self.log_info = scrolledtext.ScrolledText(frame_BOTTOM_log,width=70,height=30)
        self.log_info.configure(bg='lightgray')
        self.log_info.insert("insert", "python")
        self.log_info.delete(1.0, END)  # 使用 delete
        self.log_info.pack(side='left')
        # 创建结果
        self.log_ret = scrolledtext.ScrolledText(frame_BOTTOM_log,width=55,height=30)
        self.log_ret.configure(bg='lightgray')
        self.log_ret.insert("insert", "python")
        self.log_ret.delete(1.0, END)  # 使用 delete
        self.log_ret.pack(side='left')
        # FolderStructure 实例
        self.folder_structure = FolderStructure(folder_path='')
    def on_combobox_selected(self, event):
        # 确认下深度
        if (self.operate_depth.get() == '选择操作深度') or (self.operate_depth.get() == 'dcm所在目录(未实现)'):
            self.log_ret.insert(END, f"\n当前深度无效\n")
            self.log_ret.see(END)
            self.set_dst.config(state='disabled')
            self.set_parm.config(state='disabled')
            self.convertOneDemo.config(state='disabled')
            self.convert_button.config(state='disabled')
            self.stop_button.config(state='disabled')
        else:
            if self.operate_depth.get() == "一级目录":
                self.aim_depth = 1
            if self.operate_depth.get() == "二级目录(推荐)":
                self.aim_depth = 2
            if self.operate_depth.get() == "三级目录":
                self.aim_depth = 3
            self.log_ret.insert(END, f"\n设定的深度为 {self.aim_depth}")
            self.log_ret.see(END)
            self.set_dst.config(state='normal')
            self.set_parm.config(state='disabled')
            self.convertOneDemo.config(state='disabled')
            self.convert_button.config(state='disabled')
            self.stop_button.config(state='disabled')
    def start_convert(self):
        # 禁用转移按钮，并启用终止按钮
        self.convert_button.config(state='disabled')
        self.stop_button.config(state='normal')
        # 创建一个线程来执行文件转移操作
        convert_thread = threading.Thread(target=self.shell_dcm2niix, args=(
            self.root_src_path, self.root_dst_path, self.folder_find, self.progress))
        convert_thread.start()
    def stop_convert(self):
        # 请求停止文件转移
        self.stop_requested = True
        self.log_ret.insert(END, f"\n{'#' * 50}\n正在申请终止转换！！！")
    def shell_dcm2niix(self,root_path, root_save_path, all_origDicom_path, progress):
        start_time = time.time()  # 记录开始时间
        error_list = []
        total_count = len(all_origDicom_path)
        progress['maximum'] = total_count
        progress['value'] = 0
        for path_dicom in all_origDicom_path:
            # 如果停止按钮被请求，退出循环
            if self.stop_requested:
                break
            path_nifti_save = path_dicom.replace('/', '\\').replace(
                root_path.replace('/', '\\'),
                root_save_path.replace('/', '\\'))
            # 保存位置
            if not os.path.exists(path_nifti_save):
                os.makedirs(path_nifti_save)
            # 参数
            command_dcm2niix = '"%s" -o %s %s %s' % (self.path_exe, path_nifti_save, self.dcm2nii_parm.get(), path_dicom)
            # if len(all_origDicom_path) == 1:
            #     self.log_ret.insert(END, f"\n转换命令(shell):\n{command_dcm2niix} \n")
            self.log_ret.insert(END, f"\n{'#' * 40}\n正在转换,请耐心等待→→→\n{path_dicom}\n{path_nifti_save}\n")
            self.log_ret.see(END)
            # status = os.system(command_dcm2niix)  # 会阻塞线程，直到完成执行。这意味着在这个执行期间，self.stop_requested的值无法立即生效
            process = subprocess.Popen(command_dcm2niix, shell=True)  # 使用 Popen 启动子进程
            while process.poll() is None:  # 检查子进程是否仍在运行
                if self.stop_requested:
                    process.terminate()  # 如果请求停止，终止子进程
                    break
                time.sleep(2)  # 等待一段时间再次检查
            if process.returncode == 0:
                # print(f'转换成功')
                self.log_ret.insert(END,f'  ---Successfully converted---\n')
                self.log_ret.see(END)
                if len(all_origDicom_path) == 1:
                    end_time = time.time()
                    time_taken = end_time - start_time
                    time_taken = float("{:.2f}".format(time_taken))
                    total_s = len(self.folder_find)*time_taken
                    self.log_ret.insert(END, f"\n代码执行时间为：{time_taken}秒,全部运行完大概要{len(self.folder_find)}×{time_taken}={total_s}秒，约{total_s//60}分钟")
                    folder = os.path.dirname(path_nifti_save)
                    os.startfile(folder)
            else:
                error_list.append(path_dicom)
            progress['value'] += 1
            progress.update()
        # print(f'下列dicom无法成功转换:\n{error_list}')
        self.log_ret.insert(END, f'\n\n下列dicom无法成功转换:\n{error_list}')
        self.log_ret.see(END)
        
        # 启用转移按钮，并禁用终止按钮
        self.convert_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.stop_requested = False
    def create_tooltip(self, widget, text):
        tooltip = Tooltip(widget, text)
        widget.bind('<Enter>', lambda _: tooltip.show_tip())
        widget.bind('<Leave>', lambda _: tooltip.hide_tip())
    def check_Dcm2Nii(self):
        # 确认dcm2niix能否调取成功
        self.log_info.insert(END, f"{'#' * 40}\n{self.path_exe}\n")
        state_exe = os.system('"%s"' % (self.path_exe))
        if state_exe != 0:
            self.log_info.insert(END, '调用失败!!!\n\n')
        else:
            self.log_info.insert(END, '调用成功 ^_^ \n\n')
            self.log_ret.insert(END, f"\n选一个文件夹开始转换\n{self.folder_find[0]}\n")
            # 创建一个线程来执行文件转移操作
            convert_thread = threading.Thread(target=self.shell_dcm2niix, args=(
                self.root_src_path, self.root_dst_path, [self.folder_find[0]], self.progress))
            convert_thread.start()
            self.cb.config(state='disabled')
            self.set_dst.config(state='disabled')
            self.set_parm.config(state='disabled')
            self.convertOneDemo.config(state='disabled')
            self.convert_button.config(state='normal')
            self.stop_button.config(state='normal')
    def set_root_dst(self):
        # 打开资源管理器对话框并选择路径
        root_set_dst = filedialog.askdirectory()
        self.root_dst_path = root_set_dst
        if self.root_src_path == self.root_dst_path:
            self.log_ret.insert(END, f'我奉劝你一句最好根目录根转移目录别设在一起!搞个空的转移路径不好么?')
        else:
            self.log_ret.insert(END, f'\n\n根目录:\n  {self.root_src_path}\n转移目录:\n  {root_set_dst}\n')
            self.folder_find = DirectoryReader(self.root_src_path, self.aim_depth).get_aim_directories()
            self.log_info.insert(END, f"{'#' * 40}\n")
            for i in self.folder_find:
                self.log_info.insert(END, f"  {i}\n")
            self.log_info.insert(END, f"\n在给定深度下共找到【{len(self.folder_find)}】个文件夹，都是待转换的文件夹\n\n")
            self.log_info.see(END)
            self.cb.config(state='disabled')
            self.set_dst.config(state='disabled')
            self.set_parm.config(state='normal')
            self.convertOneDemo.config(state='normal')
            self.convert_button.config(state='disabled')
            self.stop_button.config(state='disabled')
    def output_to_log_info(self, text):
        self.log_info.insert(END, text + "\n")
        # self.log_info.see(END)
        self.log_info.update_idletasks()
    def set_root_path(self):
        # 打开资源管理器对话框并选择路径
        root_path = filedialog.askdirectory()
        self.root_src_path = root_path
        # 一级目录
        folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
        # 根目录下的所有文件夹
        root_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
        # 如果没有找到文件夹，那么无法进行下一步
        if len(folders)==0:
            self.output_to_log_info(f"你好好检查！！")
        else:
            # 找到最大文件夹深度
            max_depth = MaxDepthFinder(os.path.join(root_path, root_folders[0])).find_max_depth()
            self.log_ret.insert(END,f"{'#' * 40}\n找到一级目录【{len(folders)}】个\n是否代表你有【{len(folders)}】个被试文件夹？如果是，就进行下一步\n")
            self.log_info.insert(END,f"{'#' * 40}\n0级目录：即根目录：{root_path}\n"
                                    f"1级目录：应为每个被试的文件夹\n"
                                    f"......\n"
                                    f"{max_depth}级目录：各存放dicom序列的文件夹\n")
            self.log_ret.insert(END, f"\n最大目录深度【{max_depth}】级\n推荐操作深度【{max_depth-1}】级，理由看多选框旁的问号\n\n{'#' * 40}\n")
            # 设置 FolderStructure 实例的 folder_path 属性并打印文件夹结构,但是呢我们不要打印全部的，我们只打印第一个文件夹，不然的话等着死机吧
            self.output_to_log_info(f"\n随机展示最多5个一级目录的文件夹，选一个铺开其结构：\n")
            # 如果只有一个文件夹，那就打印呗
            if len(folders) ==1:
                self.folder_structure.folder_path = os.path.join(root_path,root_folders[0])
                self.folder_structure.print_folder_structure(output=self.output_to_log_info)
            # 如果文件夹个数超过1了，打印某一个结构的文件夹，同时顺便取最多5个
            else:
                if 1 < len(folders) <5:
                    sample = len(folders)
                else:
                    sample = 5
                random_folders = random.sample(folders, sample)  # 在一级目录中随机取最多5个
                for i in range(len(random_folders)):
                    if i != len(random_folders)-1:
                        self.output_to_log_info(f"{random_folders[i]}")
                    else:
                        self.folder_structure.folder_path = os.path.join(root_path, root_folders[0])
                        self.folder_structure.print_folder_structure(output=self.output_to_log_info)
            self.cb.config(state='normal')
            self.set_dst.config(state='disabled',bg='black',fg='white')
            self.set_parm.config(state='disabled',bg='black',fg='white')
            self.convertOneDemo.config(state='disabled',bg='black',fg='white')
            self.convert_button.config(state='disabled',bg='black',fg='white')
            self.stop_button.config(state='disabled',bg='black',fg='white')
if __name__ == "__main__":
    window = tk.Tk()
    window.geometry("1000x600+400+200")
    window.config(bg="#181818")
    main_menu = Dcm2Nii(window)
    main_menu.place(relx=0.5, rely=0.50, anchor=tk.CENTER)
    window.mainloop()

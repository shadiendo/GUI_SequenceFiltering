#!/usr/bin/env python
# -*- coding: utf-8 -*-
import SimpleITK as sitk
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import scrolledtext
import time
import os
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox('insert')
        x = x + self.widget.winfo_rootx() -20
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        tw.attributes("-topmost", True)  # 置顶
        tw.lift()  # 窗口置顶等级再提升
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                              background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                              font=("宋体", "10", "normal"))
        label.pack(ipadx=1)
    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
class ShowTopLevel:
    def __init__(self, master,info):
        self.top_level = tk.Toplevel(master)
        self.top_level.title("lologlogg")
        self.top_level.config(background="black")
        self.top_level.attributes("-topmost", True) # 置顶
        self.top_level.lift()  # 窗口置顶等级再提升
        self.info = info
        st = tk.scrolledtext.ScrolledText(self.top_level,width=100, height=20, wrap=tk.WORD)
        st.insert("insert", self.info)
        st.pack()
        button_close = tk.Button(self.top_level, text='关闭',bg='#af0101',fg='#ffffff',
                                 height= 1, command=self.top_level.destroy)
        button_close.pack(fill=tk.BOTH, expand=True)
        # 获取鼠标点击时的坐标
        x = master.winfo_pointerx()
        y = master.winfo_pointery()
        # 设置新的Toplevel窗口的位置
        self.top_level.geometry(f"+{x + 50}+{y - 30}")
class NiftiViewerFrame(tk.Frame):
    def __init__(self, master, file_path):
        super().__init__(master)
        self.file_path = file_path
        self.array = self.load_nifti_file()[0]
        self.current_slice = 0
        self.photo = None
        self.current_scale = 1.0
        self.right_click_start_x = 0
        self.right_click_start_y = 0
        self.middle_click_start_x = 0
        self.middle_click_start_y = 0
        self.pan_offset_x = None
        self.pan_offset_y = None
        self.last_update_time = 0
        self.update_interval = 1 / 90  # Update at most 30 times per second
        self.win_width = 500
        self.win_height = 510
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 主背景建立在一个frame上
        self.frame = tk.Frame(self,bg='#181818',width=self.win_width,height=self.win_height)
        self.frame.pack(fill="both", expand=True)
        self.frame.pack_propagate(0)
        # Canvas建立在主背景上
        self.canvas = tk.Canvas(self.frame, bg='black')
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_click_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_click_release)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<B2-Motion>", self.on_middle_click_drag)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_click_release)
        self.update_image(self.current_slice)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        self.bottom_frame = tk.Frame(self,bg='#181818',width=self.win_width,height=self.win_height)
        self.bottom_frame.pack(fill="both", expand=True)
        # # 创建文件路径输入框
        # entry = tk.Entry(self.bottom_frame,
        #                  font=("Helvetica", 8),bg='black',fg='#ffffff')
        # entry.insert(0, file_path)
        # entry.pack(side='left',fill="both", expand=True,anchor=tk.NW)
        # 添加复位按钮
        button_options = {'bg': '#2b2b2b', 'fg': '#abe338', 'relief': 'groove', 'font': ("Helvetica", 8, "bold"),
                          'width':7, 'height': 1, 'text': "refresh", 'anchor': 'center'}
        self.reset_button = ClickableLabel(self.bottom_frame, self.reset_canvas, **button_options)
        self.reset_button.pack(anchor="center", side='right')
        # 基本信息
        dim = self.load_nifti_file()[1]
        spacing = self.load_nifti_file()[2]
        title_label = tk.Label(self.bottom_frame, text='dim:'+str(dim)+'  |  voxel:'+str(spacing),
                               bg='#181818',fg="white", font=("Helvetica", 8),anchor= 'center', justify='left')
        title_label.pack(anchor="center",side='right')
    def create_tooltip(self,widget, text):
        tooltip = Tooltip(widget, text)
        widget.bind('<Enter>', lambda _: tooltip.show_tip())
        widget.bind('<Leave>', lambda _: tooltip.hide_tip())
    def load_nifti_file(self):
        # 加载4Dnifti格式，第一位是多个B值的维度
        image = sitk.ReadImage(self.file_path)
        # 数据
        array = sitk.GetArrayFromImage(image)
        # 维度
        dim = image.GetSize()
        # 体素
        spacing = image.GetSpacing()
        spacing = tuple(round(x, 3) for x in spacing)
        # print(f'图像维度总数（一般3D，DWI是4D，如果有问题，再说）：\n{len(dim)}')
        # print('dim:'+str(dim)+'  |  voxel:'+str(spacing))
        if len(dim) == 3 and len(array.shape) == 3:
            # print('普通3维度的nifti')
            return [array, dim, spacing]
        elif len(dim) == 4 and len(array.shape) == 4:
            # print('普通4维度的nifti')
            dim4_num = dim[3]   # 四维的维度，指有几个b指
            if dim4_num>=3:
                dim4_num=3
            array_0 = array[0,:,:,:]
            for i in range(1, dim4_num):
                # vstack垂直方向顺序堆叠arrays, 此外还有 dstack  hstack
                array_0 = np.vstack((array_0, array[i,:,:,:]))
            array = array_0
            return [array, dim, spacing]
        # 特殊情况，具有RGB通道的彩色nifti
        elif len(dim) == 3 and len(array.shape) == 4:
            array = array[:, :, :, 2]
            return [array, dim, spacing]
        else:
            print('这个序列不知道是什么东西噢')
            return [array,dim,spacing]
    def reset_canvas(self):
        # 将Canvas的大小和位置还原到初始值
        self.canvas.delete("image")
        self.pan_offset_x = None
        self.pan_offset_y = None
        self.update_image(self.current_slice)
    # def array_to_photoimage(self, array):
    #     array_normalized = (array - array.min()) / (array.max() - array.min())
    #     img = Image.fromarray((array_normalized * 255).astype('uint8'), mode='L')
    #     img_resized = img.resize((int(img.width * self.current_scale), int(img.height * self.current_scale)), Image.NEAREST)
    #     return ImageTk.PhotoImage(img_resized)
    '''
    这里使用 img.thumbnail(max_size, Image.ANTIALIAS) 方法来降低图像质量。
    max_size 变量设置为 (100, 100)，表示我们希望保持图像的原始纵横比，并将较长的边缩小到 100。
    Image.ANTIALIAS 参数表示我们将使用抗锯齿采样来获得较好的缩略图质量。这将在保持图像质量的同时提高处理速度。
    '''
    def array_to_photoimage(self, array):
        array_normalized = (array - array.min()) / (array.max() - array.min())
        img = Image.fromarray((array_normalized * 255).astype('uint8'), mode='L')
        # 检查数组的维度是否超过 500
        if img.width > 500 or img.height > 500:
            max_size = (500, 500)
            img.thumbnail(max_size, Image.ANTIALIAS)
        img_resized = img.resize((int(img.width * self.current_scale), int(img.height * self.current_scale)),
                                 Image.NEAREST)
        return ImageTk.PhotoImage(img_resized)
    def update_image(self, slice_index):
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            self.photo = self.array_to_photoimage(np.flipud(self.array[slice_index, :, :]))
            # 设定图像的初始位置
            if self.pan_offset_x is None:
                self.pan_offset_x = self.win_width //2
                # print(f'现在的位置：{500}-{self.photo.width()} // 2')
            if self.pan_offset_y is None:
                self.pan_offset_y = self.win_height //2
                # print(f'现在的位置：{500}-{self.photo.height()} // 2')
            self.canvas.delete("image")  # 删除之前的图像
            self.canvas.create_image(self.pan_offset_x, self.pan_offset_y, image=self.photo, anchor="c", tags="image")
            self.last_update_time = current_time
    def on_scroll(self, event):
        if event.delta > 0:
            self.current_slice = max(0, self.current_slice - 1)
        else:
            self.current_slice = min(self.array.shape[0] - 1, self.current_slice + 1)
        self.update_image(self.current_slice)
    def on_right_click(self, event):
        self.right_click_start_x = event.x
        self.right_click_start_y = event.y
    def on_right_click_drag(self, event):
        delta_y = event.y - self.right_click_start_y
        self.current_scale += delta_y * 0.01
        self.current_scale = max(0.1, self.current_scale)
        self.right_click_start_y = event.y
        self.update_image(self.current_slice)
    def on_right_click_release(self, event):
        pass
    def on_middle_click(self, event):
        self.middle_click_start_x = event.x
        self.middle_click_start_y = event.y
    def on_middle_click_drag(self, event):
        delta_x = event.x - self.middle_click_start_x
        delta_y = event.y - self.middle_click_start_y
        self.pan_offset_x += delta_x
        self.pan_offset_y += delta_y
        self.middle_click_start_x = event.x
        self.middle_click_start_y = event.y
        self.update_image(self.current_slice)
    def on_middle_click_release(self, event):
        pass
class DraggableLabel(tk.Label):
    def __init__(self, parent, frame, **kwargs):
        super().__init__(frame, **kwargs)
        self.parent = parent
        # 绑定鼠标事件
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    def stop_move(self, event):
        self.x = None
        self.y = None
    def do_move(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        self.parent.geometry(f"+{self.parent.winfo_x() + dx}+{self.parent.winfo_y() + dy}")
        self.parent.update_idletasks()
class DraggableButton(tk.Button):
    def __init__(self, parent, frame, **kwargs):
        super().__init__(frame, **kwargs)
        self.parent = parent
        # 绑定鼠标事件
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    def stop_move(self, event):
        self.x = None
        self.y = None
    def do_move(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        self.parent.geometry(f"+{self.parent.winfo_x() + dx}+{self.parent.winfo_y() + dy}")
        self.parent.update_idletasks()
'''
描述：一个可以触发点击效果的按钮
parent:父级构建，可以是frame等
your_function：自己定义的点击触发函数
**kwargs：输入按钮相关的参数，可以设置为这种
        label_options = {"text": 'btn_text', 'bg': '#b0b1b3','relief': 'raised'}
用法：ClickableLabel(root,your_function, **button_options).pack()
'''
class ClickableLabel(tk.Label):
    def __init__(self, frame, your_function, **kwargs):
        super().__init__(frame,**kwargs)
        self.your_function = your_function
        # 绑定鼠标事件
        self.bind("<Button-1>", self.toggle_active)
        self.bind("<ButtonRelease-1>", self.toggle_active)
    def toggle_active(self, event):
        if event.type == tk.EventType.ButtonPress:
            self["fg"] = 'red'
            self.your_function()
        elif event.type == tk.EventType.ButtonRelease:
            self["fg"] = self["fg"] if self["fg"] != 'red' else "#abe338"
# 用来寻找最大文件夹深度
class MaxDepthFinder:
    def __init__(self, root_path):
        self.root_path = root_path
    def _traverse_directory(self, path, depth):
        max_depth = depth
        try:
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                if os.path.isdir(entry_path):
                    max_depth = max(max_depth, self._traverse_directory(entry_path, depth + 1))
        except FileNotFoundError as e:
            print(f"Error: {e}")
        return max_depth
    def find_max_depth(self):
        return self._traverse_directory(self.root_path, 1)
# 用来打印目录结构
class FolderStructure:
    def __init__(self, folder_path):
        self.folder_path = folder_path
    def count_items(self, folder_path):
        num_files = 0
        num_dirs = 0
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                num_dirs += 1
            else:
                num_files += 1
        return num_files, num_dirs
    def print_folder_structure(self, folder_path=None, indent='  ', output=None, is_root=True):
        if folder_path is None:
            folder_path = self.folder_path
        if is_root:
            num_files, num_dirs = self.count_items(folder_path)
            folder_summary = []
            if num_dirs > 0:
                folder_summary.append(f"{num_dirs} folders")
            if num_files > 0:
                folder_summary.append(f"{num_files} files")
            summary_str = "，".join(folder_summary)
            root_folder_name = os.path.basename(folder_path)  # 获取根目录的文件名
            output_text = f"{root_folder_name}/【{summary_str}】"
            if output:
                output(output_text)
            else:
                print(output_text)
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                num_files, num_dirs = self.count_items(item_path)
                folder_summary = []
                if num_dirs > 0:
                    folder_summary.append(f"{num_dirs} folders")
                if num_files > 0:
                    folder_summary.append(f"{num_files} files")
                summary_str = "，".join(folder_summary)
                output_text = f"{indent}└── {item}/【{summary_str}】"
                if output:
                    output(output_text)
                else:
                    print(output_text)
                self.print_folder_structure(item_path, indent + '   ', output, is_root=False)
'''
输入根目录和最大深度后，可以选择返回路径的模式
root_path = r"J:\\20230602\\dicom\\REMBRANDT"
max_depth = int(input("请输入最大文件夹层级深度："))
directory_reader = DirectoryReader(root_path, max_depth)
folder_path = directory_reader.get_aim_directories()
print("找到的文件夹：")
for folder_name in folder_path:
    print(folder_name)
'''
class DirectoryReader:
    def __init__(self, root_path, max_depth):
        self.root_path = root_path
        self.max_depth = max_depth
        self.folder_path = []
    def _traverse_directory(self, path, depth):
        if depth > self.max_depth:
            return
        try:
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                if os.path.isdir(entry_path):
                    self.folder_path.append(entry_path)
                    self._traverse_directory(entry_path, depth + 1)
        except FileNotFoundError as e:
            print(f"Error: {e}")
    # 返回指定深度的所有文件夹，包括之前的
    def get_directories(self):
        self._traverse_directory(self.root_path, 1)
        return self.folder_path
    # 返回指定深度的文件夹
    def get_aim_directories(self):
        self._traverse_directory(self.root_path, 1)
        cleared_path = []
        for i in self.folder_path:
            split_list = i.replace(self.root_path, '').split('\\')
            split_list_noneSpace = list(filter(None, split_list))
            if len(split_list_noneSpace) == self.max_depth:
                i = i.replace('/','\\')
                cleared_path.append(i)
        return cleared_path

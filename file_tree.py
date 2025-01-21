import tkinter as tk
import os

class FileTreeWidget:
    @staticmethod
    def get_file_structure(old_path, new_path):
        """建立檔案結構字典"""
        def get_sorted_items(base_path):
            items = []
            if os.path.exists(base_path):
                # 獲取頂層目錄的內容
                dirs = []
                files = []
                for item in os.scandir(base_path):
                    if item.is_dir():
                        dirs.append((item.name, True))
                    else:
                        files.append((item.name, False))
                # 分別排序目錄和檔案
                return sorted(dirs) + sorted(files)
            return items

        # 合併兩個路徑的項目
        all_items_old = get_sorted_items(old_path)
        all_items_new = get_sorted_items(new_path)
        
        # 合併並去重
        seen = set()
        all_items = []
        for name, is_dir in all_items_old + all_items_new:
            if name not in seen:
                seen.add(name)
                all_items.append((name, is_dir))
        
        # 重新排序（確保目錄在前）
        directories = sorted(item for item in all_items if item[1])
        files = sorted(item for item in all_items if not item[1])
        all_items = directories + files

        # 建立結構
        structure = {}
        for name, is_dir in all_items:
            if is_dir:
                # 遞迴處理子目錄
                subpath_old = os.path.join(old_path, name) if os.path.exists(os.path.join(old_path, name)) else None
                subpath_new = os.path.join(new_path, name) if os.path.exists(os.path.join(new_path, name)) else None
                structure[name] = FileTreeWidget.get_file_structure(
                    subpath_old if subpath_old else "",
                    subpath_new if subpath_new else ""
                )
            else:
                structure[name] = None
        
        return structure

    def __init__(self, parent, on_file_click):
        self.parent = parent
        self.on_file_click = on_file_click
        self.file_vars = {}
        self.folder_states = {}
        self.folder_frames = {}
        self.selected_files = {}
        self.last_selected = None
        
        # 建立捲動框
        self.scrollbar = tk.Scrollbar(parent)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 建立 Canvas 和內部 Frame
        self.canvas = tk.Canvas(parent)
        self.inner_frame = tk.Frame(self.canvas)
        
        # 配置捲動
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 將內部 Frame 放入 Canvas
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        self.inner_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

    def create_tree_items(self, parent, structure, path='', level=0):
        """遞迴創建樹狀結構的 GUI 元件"""
        # 分離目錄和檔案
        directories = [(name, struct) for name, struct in structure.items() if struct is not None]
        files = [(name, struct) for name, struct in structure.items() if struct is None]
        
        # 先處理目錄
        for name, substructure in sorted(directories):
            full_path = os.path.join(path, name) if path else name
            
            # 創建資料夾主容器
            folder_container = tk.Frame(parent)
            folder_container.pack(fill=tk.X, expand=True)
            
            # 創建資料夾標題框架
            folder_header = tk.Frame(folder_container)
            folder_header.pack(fill=tk.X, side=tk.TOP)
            
            # 建立縮排
            indent = '    ' * level
            
            # 創建 checkbutton 變數
            self.file_vars[full_path] = tk.BooleanVar(value=True)
            
            # 初始化資料夾狀態（預設摺疊）
            self.folder_states[full_path] = tk.BooleanVar(value=False)
            
            # 創建展開/摺疊按鈕
            toggle_btn = tk.Label(folder_header, text="▶️", cursor="hand2")
            toggle_btn.pack(side=tk.LEFT, padx=(indent.count(' ') * 2, 0))
            
            # 綁定點擊事件
            toggle_btn.bind('<Button-1>', lambda e, path=full_path, btn=toggle_btn: 
                        self.toggle_folder(path, btn))
            
            # 資料夾圖示和名稱
            text = f"📁 {name}"
            
            def make_check_handler(current_path):
                def handler():
                    checked = self.file_vars[current_path].get()
                    self.toggle_children(current_path, checked)
                return handler
            
            # 創建 checkbutton
            chk = tk.Checkbutton(folder_header, text=text, 
                                variable=self.file_vars[full_path],
                                command=make_check_handler(full_path))
            chk.pack(side=tk.LEFT, anchor='w')
            
            # 創建子項目的容器
            sub_frame = tk.Frame(folder_container)
            self.folder_frames[full_path] = sub_frame
            
            # 創建子項目
            if substructure:
                self.create_tree_items(sub_frame, substructure, full_path, level + 1)
            
            # 根據預設狀態顯示或隱藏子框架
            if self.folder_states[full_path].get():
                sub_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 0))
            else:
                sub_frame.pack_forget()
        
        # 再處理檔案
        for name, _ in sorted(files):
            full_path = os.path.join(path, name) if path else name
            
            # 創建檔案容器框架
            item_frame = tk.Frame(parent)
            item_frame.pack(fill=tk.X, side=tk.TOP)
            
            # 創建 checkbutton 變數
            self.file_vars[full_path] = tk.BooleanVar(value=True)
            
            # 創建可點擊的標籤
            text = f"📄 {name}"
            label = tk.Label(item_frame, text=text, cursor="hand2")
            label.pack(side=tk.LEFT, padx=((level + 1) * 20, 5), anchor='w')
            
            # 綁定點擊事件
            label.bind('<Button-1>', lambda e, path=full_path: self.on_file_click(path))
            
            # 創建 checkbutton (不顯示文字)
            chk = tk.Checkbutton(item_frame, variable=self.file_vars[full_path])
            chk.pack(side=tk.LEFT, anchor='w')
            
            # 儲存標籤引用
            self.selected_files[full_path] = {'label': label, 'frame': item_frame}

    def toggle_folder(self, folder_path, toggle_btn):
        """切換資料夾的展開/摺疊狀態"""
        current_state = self.folder_states[folder_path].get()
        new_state = not current_state
        self.folder_states[folder_path].set(new_state)
        
        # 更新按鈕圖示
        toggle_btn.config(text="🔽" if new_state else "▶️")
        
        # 顯示或隱藏子項目
        if folder_path in self.folder_frames:
            if new_state:
                self.folder_frames[folder_path].pack(fill=tk.X)
                self.folder_frames[folder_path].update()
            else:
                self.folder_frames[folder_path].pack_forget()

    def toggle_children(self, folder_path, checked):
        """切換資料夾內所有子項目的選中狀態"""
        for path, var in self.file_vars.items():
            if path.startswith(folder_path + os.sep):
                var.set(checked)

    def highlight_selected_file(self, file_path):
        """高亮顯示選中的檔案"""
        if self.last_selected and self.last_selected in self.selected_files:
            self.selected_files[self.last_selected]['label'].config(
                background='SystemButtonFace',  # 使用系統預設背景色
                foreground='black'  # 使用系統預設文字顏色
            )
        
        if file_path in self.selected_files:
            self.selected_files[file_path]['label'].config(
                background='#2a4d69',
                foreground='white'
            )
            self.last_selected = file_path

    def get_file_vars(self):
        """獲取檔案選擇狀態"""
        return self.file_vars

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from datetime import datetime
import stat
from file_tree import FileTreeWidget
from file_compare import FileCompareWidget

class FileUpdateTool:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("檔案更新工具")
        self.window.minsize(800, 600)
        # 定義路徑變數
        self.old_folder_path = tk.StringVar()
        self.new_folder_path = tk.StringVar()
        
        self.create_gui()
    
    def create_gui(self):
        # 頂部的資料夾選擇區域
        folder_frame = tk.Frame(self.window)
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 舊資料夾選擇
        old_frame = tk.Frame(folder_frame)
        old_frame.pack(fill=tk.X, pady=2)
        old_button = tk.Button(old_frame, text="選擇舊資料夾", command=self.select_old_folder)
        old_button.pack(side=tk.LEFT, padx=5)
        old_label = tk.Label(old_frame, textvariable=self.old_folder_path)
        old_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 新資料夾選擇
        new_frame = tk.Frame(folder_frame)
        new_frame.pack(fill=tk.X, pady=2)
        new_button = tk.Button(new_frame, text="選擇新資料夾", command=self.select_new_folder)
        new_button.pack(side=tk.LEFT, padx=5)
        new_label = tk.Label(new_frame, textvariable=self.new_folder_path)
        new_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 使用PanedWindow分割左右兩側
        self.paned = tk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左側檔案列表區域
        left_frame = tk.Frame(self.paned)
        self.file_tree = FileTreeWidget(left_frame, self.on_file_click)
        self.paned.add(left_frame)
        
        # 右側比較視圖
        right_frame = tk.Frame(self.paned)
        self.file_compare = FileCompareWidget(right_frame)
        self.paned.add(right_frame)
        
        # 底部更新按鈕
        update_button = tk.Button(self.window, text="開始更新", command=self.start_update)
        update_button.pack(pady=5)
        
    def on_file_click(self, file_path):
        """處理檔案點擊事件"""
        self.file_tree.highlight_selected_file(file_path)
        
        # 更新比較視圖
        old_path = os.path.join(self.old_folder_path.get(), file_path)
        new_path = os.path.join(self.new_folder_path.get(), file_path)
        self.file_compare.show_diff(old_path, new_path)

    def make_writable(self, path):
        """修改檔案或資料夾的權限使其可寫入"""
        try:
            if os.path.isfile(path):
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            else:
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    for f in files:
                        os.chmod(os.path.join(root, f), stat.S_IWRITE | stat.S_IREAD)
        except Exception as e:
            print(f"修改權限失敗: {e}")

    def copy_with_permissions(self, src, dst):
        """複製檔案或資料夾，並處理權限問題"""
        try:
            # 如果目標已存在，先嘗試修改其權限
            if os.path.exists(dst):
                self.make_writable(dst)
                
            if os.path.isdir(src):
                # 如果是資料夾，需要遞迴複製
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                self.make_writable(dst)
            else:
                # 如果是檔案，直接複製
                shutil.copy2(src, dst)
                self.make_writable(dst)
            return True
        except Exception as e:
            print(f"複製失敗: {e}")
            return False

    def select_old_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.old_folder_path.set(folder_selected)
            print(f"Old folder selected: {folder_selected}")
            self.update_file_list()
    
    def select_new_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.new_folder_path.set(folder_selected)
            print(f"New folder selected: {folder_selected}")
            self.update_file_list()
    
    def update_file_list(self):
        old_path = self.old_folder_path.get()
        new_path = self.new_folder_path.get()
        
        if old_path and new_path:
            # 建立檔案結構
            file_structure = FileTreeWidget.get_file_structure(old_path, new_path)
            # 創建檔案樹狀結構
            self.file_tree.create_tree_items(self.file_tree.inner_frame, file_structure)

    def backup_old_folder(self):
        old_path = self.old_folder_path.get()
        if old_path and os.path.exists(old_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(old_path)}_backup_{timestamp}"
            backup_path = os.path.join(os.path.dirname(old_path), backup_name)
            try:
                shutil.copytree(old_path, backup_path)
                print(f"Old folder backed up to: {backup_path}")
                return True
            except Exception as e:
                print(f"Error backing up folder: {e}")
                return False
        return False
    
    def start_update(self):
        print("開始更新...")
        
        # 檢查是否有選擇資料夾
        old_path = self.old_folder_path.get()
        new_path = self.new_folder_path.get()
        
        if not (old_path and new_path):
            messagebox.showerror("錯誤", "請先選擇舊資料夾和新資料夾")
            return
            
        # 執行備份
        if not self.backup_old_folder():
            messagebox.showerror("錯誤", "備份失敗，更新已取消")
            return
        
        success_count = 0
        fail_count = 0
        
        # 更新檔案
        file_vars = self.file_tree.get_file_vars()
        for filename, var in file_vars.items():
            if var.get():
                old_file = os.path.join(old_path, filename)
                new_file = os.path.join(new_path, filename)
                
                if os.path.exists(new_file):
                    if self.copy_with_permissions(new_file, old_file):
                        print(f"已更新: {filename}")
                        success_count += 1
                    else:
                        print(f"更新失敗: {filename}")
                        fail_count += 1
        
        # 顯示更新結果
        message = f"更新完成\n成功: {success_count} 個檔案\n失敗: {fail_count} 個檔案"
        messagebox.showinfo("更新結果", message)
        print("更新完成.")
    
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = FileUpdateTool()
    app.run()

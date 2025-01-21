import tkinter as tk
import difflib
import os

class FileCompareWidget:
    def __init__(self, parent):
        self.parent = parent
        
        # 建立文字區域和捲動條
        self.text_widget = tk.Text(parent, wrap=tk.NONE)
        scrolly = tk.Scrollbar(parent, command=self.text_widget.yview)
        scrollx = tk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        
        # 設置捲動
        self.text_widget.config(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        
        # 設置標籤樣式
        self.text_widget.tag_configure('add', background='#e6ffe6')
        self.text_widget.tag_configure('delete', background='#ffe6e6')
        self.text_widget.tag_configure('header', background='#f0f0f0')
        
        # 放置元件
        self.text_widget.grid(row=0, column=0, sticky='nsew')
        scrolly.grid(row=0, column=1, sticky='ns')
        scrollx.grid(row=1, column=0, sticky='ew')
        
        # 設置grid權重
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # 設置唯讀
        self.text_widget.config(state='disabled')

    def show_diff(self, old_path, new_path):
        """顯示兩個檔案的差異"""
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', tk.END)
        
        try:
            # 讀取檔案內容
            old_content = ''
            new_content = ''
            
            if os.path.exists(old_path):
                with open(old_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
            
            if os.path.exists(new_path):
                with open(new_path, 'r', encoding='utf-8') as f:
                    new_content = f.read()
            
            # 使用difflib比較差異
            diff = difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile='舊檔案',
                tofile='新檔案',
                lineterm=''
            )
            
            # 顯示差異
            for line in diff:
                if line.startswith('---') or line.startswith('+++'):
                    self.text_widget.insert(tk.END, line + '\n', 'header')
                elif line.startswith('+'):
                    self.text_widget.insert(tk.END, line + '\n', 'add')
                elif line.startswith('-'):
                    self.text_widget.insert(tk.END, line + '\n', 'delete')
                else:
                    self.text_widget.insert(tk.END, line + '\n')
                
        except Exception as e:
            self.text_widget.insert(tk.END, f"無法比較檔案: {str(e)}")
        
        self.text_widget.config(state='disabled')

import tkinter as tk
import difflib
import os

class FileCompareWidget:
    def __init__(self, parent):
        self.parent = parent
        
        # Create text area and scrollbars
        self.text_widget = tk.Text(parent, wrap=tk.NONE)
        scrolly = tk.Scrollbar(parent, command=self.text_widget.yview)
        scrollx = tk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        
        # Configure scrolling
        self.text_widget.config(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        
        # Set tag styles
        self.text_widget.tag_configure('add', background='#e6ffe6')
        self.text_widget.tag_configure('delete', background='#ffe6e6')
        self.text_widget.tag_configure('header', background='#f0f0f0')
        
        # Place components
        self.text_widget.grid(row=0, column=0, sticky='nsew')
        scrolly.grid(row=0, column=1, sticky='ns')
        scrollx.grid(row=1, column=0, sticky='ew')
        
        # Set grid weights
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Set to readonly
        self.text_widget.config(state='disabled')

    def show_diff(self, old_path, new_path):
        """Show the difference between two files"""
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', tk.END)
        
        try:
            # Read file contents
            old_content = ''
            new_content = ''
            
            if os.path.exists(old_path):
                with open(old_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
            
            if os.path.exists(new_path):
                with open(new_path, 'r', encoding='utf-8') as f:
                    new_content = f.read()
            
            # Use difflib to compare differences
            diff = difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile='Old file',
                tofile='New file',
                lineterm=''
            )
            
            # Display differences
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
            self.text_widget.insert(tk.END, f"Can't compare files: {str(e)}")
        
        self.text_widget.config(state='disabled')

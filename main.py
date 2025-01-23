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
        self.window.title("File Replacer")
        self.window.minsize(800, 600)
        # Define path
        self.old_folder_path = tk.StringVar()
        self.new_folder_path = tk.StringVar()        
        self.create_gui()

    def create_gui(self):
        # Top section for folder selection
        folder_frame = tk.Frame(self.window)
        folder_frame.pack(fill=tk.X, padx=5, pady=5)

        # Old folder selection
        old_frame = tk.Frame(folder_frame)
        old_frame.pack(fill=tk.X, pady=2)
        old_button = tk.Button(old_frame, text="Select Old Folder", command=self.select_old_folder)
        old_button.pack(side=tk.LEFT, padx=5)
        old_label = tk.Label(old_frame, textvariable=self.old_folder_path)
        old_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # New folder selection
        new_frame = tk.Frame(folder_frame)
        new_frame.pack(fill=tk.X, pady=2)
        new_button = tk.Button(new_frame, text="Select New Folder", command=self.select_new_folder)
        new_button.pack(side=tk.LEFT, padx=5)
        new_label = tk.Label(new_frame, textvariable=self.new_folder_path)
        new_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Use PanedWindow to split the left and right sections
        self.paned = tk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left section for file list
        left_frame = tk.Frame(self.paned)
        self.file_tree = FileTreeWidget(left_frame, self.on_file_click)
        self.paned.add(left_frame)

        # Right section for comparison view
        right_frame = tk.Frame(self.paned)
        self.file_compare = FileCompareWidget(right_frame)
        self.paned.add(right_frame)

        # Bottom update button
        update_button = tk.Button(self.window, text="Update", command=self.start_update)
        update_button.pack(pady=5)

    def on_file_click(self, file_path):
        """Handle file click event"""
        self.file_tree.highlight_selected_file(file_path)

        # Update compare UI
        old_path = os.path.join(self.old_folder_path.get(), file_path)
        new_path = os.path.join(self.new_folder_path.get(), file_path)
        self.file_compare.show_diff(old_path, new_path)

    def make_writable(self, path):
        """Modify file or folder permissions to make it writable"""
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
            print(f"Modify permissions fail: {e}")

    def copy_with_permissions(self, src, dst):
        """Copy file or folder and handle permissions issues"""
        try:
            # Modify permissions
            if os.path.exists(dst):
                self.make_writable(dst)

            if os.path.isdir(src):
                # Copy folder
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                self.make_writable(dst)
            else:
                # Copy file
                shutil.copy2(src, dst)
                self.make_writable(dst)
            return True
        except Exception as e:
            print(f"Copy fail : {e}")
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
            # create file structure
            file_structure = FileTreeWidget.get_file_structure(old_path, new_path)
            # create folder tree
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
        print("Updating...")

        # folder check
        old_path = self.old_folder_path.get()
        new_path = self.new_folder_path.get()

        if not (old_path and new_path):
            messagebox.showerror("Error", "Please select old and new folder.")
            return

        # execute backup
        if not self.backup_old_folder():
            messagebox.showerror("Error", "backup failed, stop update process.")
            return

        success_count = 0
        fail_count = 0

        # update files
        file_vars = self.file_tree.get_file_vars()
        for filename, var in file_vars.items():
            if var.get():
                old_file = os.path.join(old_path, filename)
                new_file = os.path.join(new_path, filename)

                if os.path.exists(new_file):
                    if self.copy_with_permissions(new_file, old_file):
                        print(f"Update success : {filename}")
                        success_count += 1
                    else:
                        print(f"Update fail: {filename}")
                        fail_count += 1

        # Show update result
        message = f"Update completed\nSuccess : {success_count} files\nFail : {fail_count} files"
        messagebox.showinfo("Update result", message)
        print("Update completed.")


    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = FileUpdateTool()
    app.run()

# ======== standard Libraries ========
import os
import shutil
import stat
import re
import difflib
import configparser
from datetime import datetime

# ======== Tkinter GUI ========
import tkinter as tk
from tkinter import filedialog, messagebox

# ======== Project Internal Modules ========
from file_tree import FileTreeWidget
from file_compare import FileCompareWidget
from pdf_report import PDFReportGenerator  # Import a separate PDF generation module


class FileUpdateTool:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("File Replacer")
        self.window.minsize(800, 600)
        # Define path
        self.old_folder_path = tk.StringVar()
        self.new_folder_path = tk.StringVar()
        
        # Store the latest backup folder path
        self.latest_backup_folder = None
        
        # Store button references
        self.update_button = None
        self.update_new_only_button = None

        self.create_gui()
        self.update_file_list()  # Load file list immediately for testing

    def create_gui(self):
        # Create the top container, split into left and right frames
        top_frame = tk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left section: Contains buttons and OP input field, arranged in three rows
        left_top_frame = tk.Frame(top_frame)
        left_top_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Row 1: [Select Old Folder] [Select New Folder]
        row1 = tk.Frame(left_top_frame)
        row1.pack(fill=tk.X, pady=2)
        select_old_button = tk.Button(row1, text="Select Old Folder", command=self.select_old_folder)
        select_old_button.pack(side=tk.LEFT, padx=5)
        select_new_button = tk.Button(row1, text="Select New Folder", command=self.select_new_folder)
        select_new_button.pack(side=tk.LEFT, padx=5)
        
        # Row 2: OP label and OP input field
        row2 = tk.Frame(left_top_frame)
        row2.pack(fill=tk.X, pady=2)
        op_label = tk.Label(row2, text="OP:")
        op_label.pack(side=tk.LEFT, padx=5)
        self.op_entry = tk.Entry(row2, width=15)
        self.op_entry.pack(side=tk.LEFT, padx=5)
        
        # Set default placeholder text
        default_text = "Enter your OP ID"
        self.op_entry.insert(0, default_text)
        self.op_entry.config(fg="grey")  # Set default text color

        # Clear placeholder text when user clicks the input field
        def on_entry_click(event):
            if self.op_entry.get() == default_text:
                self.op_entry.delete(0, tk.END)  # Clear content
                self.op_entry.config(fg="black")  # Change text color
            self.update_button_states()  # Update button states

        # Restore placeholder text if the input field loses focus and is empty
        def on_focus_out(event):
            if self.op_entry.get() == "":
                self.op_entry.insert(0, default_text)
                self.op_entry.config(fg="grey")  # Change text color            
            self.update_button_states()  # Update button state

        # Monitor input field content changes
        def on_entry_change(*args):
            self.update_button_states()

        # Bind events
        self.op_entry.bind("<FocusIn>", on_entry_click)
        self.op_entry.bind("<FocusOut>", on_focus_out)
        self.op_entry.bind("<KeyRelease>", lambda e: on_entry_change())

        # Row 3: [Select All Files] [Select By Config]
        row3 = tk.Frame(left_top_frame)
        row3.pack(fill=tk.X, pady=2)
        select_all_button = tk.Button(row3, text="Select All Files", command=self.select_all_files)
        select_all_button.pack(side=tk.LEFT, padx=5)
        select_by_config_button = tk.Button(row3, text="Select By Config", command=self.select_by_config)
        select_by_config_button.pack(side=tk.LEFT, padx=5)    
        
        # Right section: Displays the paths of old_folder and new_folder (left-aligned)
        right_top_frame = tk.Frame(top_frame)
        right_top_frame.pack(side=tk.RIGHT, anchor='ne', padx=5, pady=5, fill=tk.X)  # Set fill=tk.X to allow stretching

        # Use grid layout for Old Path and New Path
        right_top_inner_frame = tk.Frame(right_top_frame)
        right_top_inner_frame.pack(side=tk.TOP, anchor='w', padx=5, pady=5, fill=tk.X)  # Internal frame to ensure left alignment

        # Old Path Label and corresponding Label
        old_path_label = tk.Label(right_top_inner_frame, text="Old Path:")
        old_path_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        old_label = tk.Label(
            right_top_inner_frame, 
            textvariable=self.old_folder_path, 
            anchor="w", 
            wraplength=400,  # Set maximum line wrapping length
            width=60  # Set sufficient width
        )
        old_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # New Path Label and corresponding Label
        new_path_label = tk.Label(right_top_inner_frame, text="New Path:")
        new_path_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)

        new_label = tk.Label(
            right_top_inner_frame, 
            textvariable=self.new_folder_path, 
            anchor="w", 
            wraplength=400,  # Set maximum line wrapping length
            width=60  # Set sufficient width
        )
        new_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Use PanedWindow to split the left file tree and the right comparison view
        self.paned = tk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left section: File tree
        left_frame = tk.Frame(self.paned)
        self.file_tree = FileTreeWidget(left_frame, self.on_file_click)
        self.paned.add(left_frame)
        
        # Right section: Comparison view
        right_frame = tk.Frame(self.paned)
        self.file_compare = FileCompareWidget(right_frame)
        self.paned.add(right_frame)
        
        # Bottom button area (e.g., Update, Add New Lines Only, Export PDF)
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=5)        

        self.update_button = tk.Button(button_frame, text="Update", command=self.start_update, state=tk.DISABLED)
        self.update_button.grid(row=0, column=0, padx=5)

        self.update_new_only_button = tk.Button(button_frame, text="Update New Lines Only", command=self.update_with_new_lines_only, state=tk.DISABLED)
        self.update_new_only_button.grid(row=0, column=1, padx=5)


    def update_button_states(self):
        """Update button enable/disable states"""
        current_text = self.op_entry.get()
        if current_text and current_text != "Enter your OP ID":
            self.update_button.config(state=tk.NORMAL)
            self.update_new_only_button.config(state=tk.NORMAL)
        else:
            self.update_button.config(state=tk.DISABLED)
            self.update_new_only_button.config(state=tk.DISABLED)
    
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
                self.latest_backup_folder = backup_path # Store the latest backup folder path
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
        
        # Automatically Generate a PDF Report
        self.auto_generate_pdf()
        
        print("Update completed.")

    def update_with_new_lines_only(self):
        """
        Only add completely new lines from the new file to the old file, ignoring modified lines.
        """
        # Get the paths of the old and new folders
        old_folder = self.old_folder_path.get()
        new_folder = self.new_folder_path.get()
        if not (old_folder and new_folder):
            messagebox.showerror("Error", "Please select old and new folder.")
            return

        # Backup the old folder first (stop the update process if the backup fails)
        if not self.backup_old_folder():
            messagebox.showerror("Error", "Backup failed, stopping update process.")
            return

        file_vars = self.file_tree.get_file_vars()  # Get the selection status of all files
        success_count = 0
        fail_count = 0

        # Update each selected file
        for filename, var in file_vars.items():
            if var.get():
                old_file = os.path.join(old_folder, filename)
                new_file = os.path.join(new_folder, filename)
                if os.path.exists(new_file):
                    try:
                        # Read the content of the old and new files (line by line)
                        with open(old_file, 'r', encoding='utf-8') as f:
                            old_lines = f.readlines()
                        with open(new_file, 'r', encoding='utf-8') as f:
                            new_lines = f.readlines()

                        # Use difflib.ndiff() to get line differences
                        diff = list(difflib.ndiff(old_lines, new_lines))
                        added_lines = []
                        insert_positions = []
                        previous_line_deleted = False  # Track if the previous line was a `-` (deleted)
                        old_index = 0  # Index for the old file
                        new_index = 0  # Index for the new file

                        for line in diff:
                            if line.startswith('? '):  # Ignore marker lines to avoid affecting index calculations
                                continue
                            if line.startswith('- '):
                                previous_line_deleted = True  # Mark it when encountering a deleted line
                                old_index += 1
                            elif line.startswith('+ '):
                                if not previous_line_deleted:
                                    added_lines.append(line[2:])  # Ensure the newline character is correct
                                    insert_positions.append(new_index)  # Use the new file's line index for insertion
                                previous_line_deleted = False  # Reset the marker
                                new_index += 1
                            else:
                                previous_line_deleted = False  # Reset the marker when encountering identical content
                                old_index += 1
                                new_index += 1
                        
                        # Insert lines sequentially from top to bottom to ensure the correct order
                        for index, new_line in zip(insert_positions, added_lines):
                            old_lines.insert(index, new_line)

                        # Update the old file only if there are new lines
                        if added_lines:
                            with open(old_file, 'w', encoding='utf-8') as f:
                                f.writelines(old_lines)

                        print(f"Update success: {filename}")
                        success_count += 1
                    except Exception as e:
                        print(f"Update fail: {filename}, Fail: {e}")
                        fail_count += 1

        # Display update results
        message = f"Update completed\nSuccess: {success_count} files\nFail: {fail_count} files"
        messagebox.showinfo("Update result", message)

        # Automatically generate a PDF report
        self.auto_generate_pdf()

        print("Update completed.")

    def get_pdf_filename(self):
        """Generate a PDF filename based on the current timestamp and OP ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        op_id = self.op_entry.get().strip()
        return f"{timestamp}_{op_id}.pdf"
    
    
    def auto_generate_pdf(self):
        """Automatically generate a PDF report"""
        if not self.latest_backup_folder:
            messagebox.showerror("Error", "Backup folder not found")
            return

        # Get the directory of the executing script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Create the pdf directory if it doesn't exist
        pdf_dir = os.path.join(current_dir, "pdf")
        os.makedirs(pdf_dir, exist_ok=True)

        # Generate the PDF filename and set the full path
        pdf_filename = self.get_pdf_filename()
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        # Generate PDF content
        updated_files = []
        file_vars = self.file_tree.get_file_vars()

        for filename, var in file_vars.items():
            if var.get():
                backup_file = os.path.join(self.latest_backup_folder, filename)
                new_file = os.path.join(self.new_folder_path.get(), filename)

                if os.path.exists(backup_file) and os.path.exists(new_file):
                    try:
                        with open(backup_file, 'r', encoding='utf-8') as f:
                            backup_lines = f.readlines()
                        with open(new_file, 'r', encoding='utf-8') as f:
                            new_lines = f.readlines()
                    except Exception:
                        updated_files.append((filename, None))
                        continue

                    diff_lines = list(difflib.unified_diff(
                        backup_lines, new_lines, fromfile='Old file', tofile='New file', lineterm=''
                    ))

                    if any(re.search(r'[\u4e00-\u9fff\uFFFD]', line) for line in diff_lines):
                        updated_files.append((filename, None))
                    elif diff_lines:
                        updated_files.append((filename, diff_lines))

        if updated_files:
            op_text = self.op_entry.get().strip()
            PDFReportGenerator.generate(pdf_path, op_text, updated_files)
            messagebox.showinfo("PDF Export", f"PDF report has been saved to：{pdf_path}")
        else:
            messagebox.showinfo("PDF Export", "No files were updated")


    def select_all_files(self):
        """Select All Files (Set the selection status of all files to True)"""
        file_vars = self.file_tree.get_file_vars()
        for path, var in file_vars.items():
            var.set(True)
        
    def select_by_config(self):
        """
        Select files based on the config.ini file in the same directory.
        The config.ini file should contain a [Files] section, where each key represents a file name,
        and the corresponding value is either True (selected) or False (not selected).
        """

        # Get the directory where main.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.ini")

        if not os.path.exists(config_path):
            messagebox.showerror("Error", "Config file not found in new folder.")
            return

        # Read config.ini file
        config = configparser.ConfigParser()
        try:
            config.read(config_path, encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading config file: {e}")
            return

        if "Files" not in config:
            messagebox.showerror("Error", "Invalid config file format. Missing [Files] section.")
            return

        # Retrieve file selection settings from the config file
        config_files = {key: value.lower() == "true" for key, value in config["Files"].items()}

        # Get all file variables
        file_vars = self.file_tree.get_file_vars()
        
        for path, var in file_vars.items():
            basename = os.path.basename(path)
            if basename in config_files:
                var.set(config_files[basename])
            else:
                var.set(False)  # Default to not selected

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = FileUpdateTool()
    app.run()

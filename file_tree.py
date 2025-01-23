import tkinter as tk
import os

class FileTreeWidget:
    @staticmethod
    def get_file_structure(old_path, new_path):
        """Build file structure dictionary"""
        def get_sorted_items(base_path):
            items = []
            if os.path.exists(base_path):
                # Get the contents of the top level directory
                dirs = []
                files = []
                for item in os.scandir(base_path):
                    if item.is_dir():
                        dirs.append((item.name, True))
                    else:
                        files.append((item.name, False))
                # Sort directories and files separately
                return sorted(dirs) + sorted(files)
            return items

        # Merge items from two paths
        all_items_old = get_sorted_items(old_path)
        all_items_new = get_sorted_items(new_path)
        
        # Merge and deduplicate
        seen = set()
        all_items = []
        for name, is_dir in all_items_old + all_items_new:
            if name not in seen:
                seen.add(name)
                all_items.append((name, is_dir))
        
        # Re-sort (ensure directories come first)
        directories = sorted(item for item in all_items if item[1])
        files = sorted(item for item in all_items if not item[1])
        all_items = directories + files

        # Build structure
        structure = {}
        for name, is_dir in all_items:
            if is_dir:
                # Recursively process subdirectories
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
        
        # Create scrollbar
        self.scrollbar = tk.Scrollbar(parent)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create Canvas and inner Frame
        self.canvas = tk.Canvas(parent)
        self.inner_frame = tk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Put inner Frame in Canvas
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        self.inner_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

    def create_tree_items(self, parent, structure, path='', level=0):
        """Recursively create tree structure GUI elements"""
        # Separate directories and files
        directories = [(name, struct) for name, struct in structure.items() if struct is not None]
        files = [(name, struct) for name, struct in structure.items() if struct is None]
        
        # Process directories first
        for name, substructure in sorted(directories):
            full_path = os.path.join(path, name) if path else name
            
            # Create folder main container
            folder_container = tk.Frame(parent)
            folder_container.pack(fill=tk.X, expand=True)
            
            # Create folder header frame
            folder_header = tk.Frame(folder_container)
            folder_header.pack(fill=tk.X, side=tk.TOP)
            
            # Establish indentation
            indent = '    ' * level
            
            # Create checkbutton variable
            self.file_vars[full_path] = tk.BooleanVar(value=True)
            
            # Initialize folder state (default collapsed)
            self.folder_states[full_path] = tk.BooleanVar(value=False)
            
            # Create expand/collapse button
            toggle_btn = tk.Label(folder_header, text="▶️", cursor="hand2")
            toggle_btn.pack(side=tk.LEFT, padx=(indent.count(' ') * 2, 0))
            
            # Bind click event
            toggle_btn.bind('<Button-1>', lambda e, path=full_path, btn=toggle_btn: 
                        self.toggle_folder(path, btn))
            
            # Folder icon and name
            text = f"📁 {name}"
            
            def make_check_handler(current_path):
                def handler():
                    checked = self.file_vars[current_path].get()
                    self.toggle_children(current_path, checked)
                return handler
            
            # Create checkbutton
            chk = tk.Checkbutton(folder_header, text=text, 
                                variable=self.file_vars[full_path],
                                command=make_check_handler(full_path))
            chk.pack(side=tk.LEFT, anchor='w')
            
            # Create container for sub-items
            sub_frame = tk.Frame(folder_container)
            self.folder_frames[full_path] = sub_frame
            
            # Create sub-items
            if substructure:
                self.create_tree_items(sub_frame, substructure, full_path, level + 1)
            
            # Show/hide subframes based on default state
            if self.folder_states[full_path].get():
                sub_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 0))
            else:
                sub_frame.pack_forget()
        
        # Process files next
        for name, _ in sorted(files):
            full_path = os.path.join(path, name) if path else name
            
            # Create file container frame
            item_frame = tk.Frame(parent)
            item_frame.pack(fill=tk.X, side=tk.TOP)
            
            # Create checkbutton variable
            self.file_vars[full_path] = tk.BooleanVar(value=True)
            
            # Create clickable label
            text = f"📄 {name}"
            label = tk.Label(item_frame, text=text, cursor="hand2")
            label.pack(side=tk.LEFT, padx=((level + 1) * 20, 5), anchor='w')
            
            # Bind click event
            label.bind('<Button-1>', lambda e, path=full_path: self.on_file_click(path))
            
            # Create checkbutton (no text displayed)
            chk = tk.Checkbutton(item_frame, variable=self.file_vars[full_path])
            chk.pack(side=tk.LEFT, anchor='w')
            
            # Save label reference
            self.selected_files[full_path] = {'label': label, 'frame': item_frame}

    def toggle_folder(self, folder_path, toggle_btn):
        """Toggle folder expand/collapse state"""
        current_state = self.folder_states[folder_path].get()
        new_state = not current_state
        self.folder_states[folder_path].set(new_state)
        
        # Update button icon
        toggle_btn.config(text="🔽" if new_state else "▶️")
        
        # Show/hide sub-items
        if folder_path in self.folder_frames:
            if new_state:
                self.folder_frames[folder_path].pack(fill=tk.X)
                self.folder_frames[folder_path].update()
            else:
                self.folder_frames[folder_path].pack_forget()

    def toggle_children(self, folder_path, checked):
        """Toggle checked state of all children in folder"""
        for path, var in self.file_vars.items():
            if path.startswith(folder_path + os.sep):
                var.set(checked)

    def highlight_selected_file(self, file_path):
        """Highlight selected file"""
        if self.last_selected and self.last_selected in self.selected_files:
            self.selected_files[self.last_selected]['label'].config(
                background='SystemButtonFace',  # Use system default background color
                foreground='black'  # Use system default text color
            )
        
        if file_path in self.selected_files:
            self.selected_files[file_path]['label'].config(
                background='#2a4d69',
                foreground='white'
            )
            self.last_selected = file_path

    def get_file_vars(self):
        """Get file selection status"""
        return self.file_vars

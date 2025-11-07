# Replacer

This application helps manage and replace files in a folder containing both old and new versions. It provides a clear view of the files and highlights the differences between versions, making updates and comparisons simple and efficient.

git link: https://github.com/KaiJuY/Replacer

[中文版](README_ZHTW.md)

## Features

- 📁 **Dual Folder Comparison** - Compare old and new folder structures side-by-side
- 🔍 **File Diff Viewer** - Visual comparison with color-coded additions (green) and deletions (red)
- ✅ **Selective Updates** - Choose which files to update using checkboxes
- 🔄 **Two Update Modes:**
  - **Full Update** - Complete file replacement
  - **New Lines Only** - Add only new lines without modifying existing content
- 💾 **Automatic Backup** - Creates timestamped backup before any update
- 📄 **PDF Report Generation** - Automatically generates update reports with diffs
- 👤 **Operator Tracking** - OP ID field for accountability and report tracking
- ⚙️ **Configuration Support** - Pre-configure file selections via `config.ini`

## Requirements

- Python 3.8 or higher
- Dependencies (install via requirements.txt):
  - tkinter (usually included with Python)
  - reportlab

## Installation

1. Clone the repository:
```bash
git clone https://github.com/KaiJuY/Replacer.git
cd Replacer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Run

```bash
python main.py
```

## GUI Operation Guide

![alt text](Aserts/image.png)

### Top Section Buttons

- **Select Old Folder**

    Select the folder containing the files you want to replace (target folder).

- **Select New Folder**

    Select the folder containing the updated files (source folder).

- **OP Field**

    Enter your Operator ID. This field is required before you can perform any updates. The OP ID will be included in the PDF report for tracking purposes.

- **Select All Files**

    Quickly check all files in the file tree for updating.

- **Select By Config**

    Load file selections from `config.ini`. This allows you to pre-configure which files should be selected by default.

### File Browser Section (Left Panel)

The left pane displays a hierarchical tree view of all files in the selected folders:
- 📁 Folders can be expanded/collapsed by clicking the arrow (▶️/🔽)
- 📄 Files are listed with checkboxes
- Click on any file to view its differences in the comparison section
- Checking a folder will automatically check/uncheck all files within it

### File Comparison Section (Right Panel)

When a file is selected in the File Browser, this section displays the differences between old and new versions:
- Lines with **red background (-)** indicate content removed in the new version
- Lines with **green background (+)** indicate content added in the new version
- Unchanged lines are displayed normally for context

### Update Buttons (Bottom)

- **Update**

    Performs a full file replacement. Selected files in the old folder will be completely replaced with their corresponding versions from the new folder.
    - Automatically creates a backup before updating
    - Generates a PDF report after completion

- **Update New Lines Only**

    Performs a partial update. Only adds completely new lines from the new file to the old file, while preserving existing content (even if modified).
    - Useful when you want to merge new content without overwriting changes
    - Automatically creates a backup before updating
    - Generates a PDF report after completion

### File Check Boxes

- **Checked** - File will be updated
- **Unchecked** - File will be preserved (no changes)

## Configuration File (config.ini)

Create a `config.ini` file in the same directory as `main.py` to pre-configure file selections:

```ini
[Files]
file1.txt = True
file2.py = False
folder/file3.js = True
```

## Backup & Reports

- **Backups**: Automatically created in the parent directory of the old folder with naming format: `{folder_name}_backup_{YYYYMMDD_HHMMSS}`
- **PDF Reports**: Saved in the `pdf/` folder with naming format: `{YYYYMMDD_HHMMSS}_{OP_ID}.pdf`
  - Contains operator ID, timestamp, and detailed diffs for all updated files
- **Report Sample** : 
![alt text](Aserts/report.png)

## Troubleshooting

- **Buttons are disabled**: Make sure to enter an OP ID in the OP field
- **Permission errors**: The application automatically handles read-only files by modifying permissions before copying
- **Unicode in diffs**: Files with Chinese characters or special symbols will show "Diff omitted" in PDF reports to avoid encoding issues

## Completed Features

- ✅ Partial update functionality (New Lines Only)
- ✅ PDF report generation with update details
- ✅ Default file selection based on differences
- ✅ Configuration-based file selection
- ✅ Automatic backup system
- ✅ Operator ID tracking
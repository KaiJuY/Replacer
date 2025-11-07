from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import red, green, black
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class PDFReportGenerator:
    """ Responsible for generating a PDF update report """
    
    @staticmethod
    def generate(pdf_path, op_text, updated_files):
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        y = height - 50

        # Title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Update Report")
        y -= 30

        # OP and Timestamp
        now_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"OP: {op_text}")
        y -= 20
        c.drawString(50, y, f"Time: {now_time}")
        y -= 30

        # List of updated files
        for filename, diff_lines in updated_files:
            if y < 50:
                c.showPage()
                y = height - 50
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Filename: {filename}")
            y -= 20
            c.setFont("Helvetica", 10)
            if diff_lines is None:
                c.drawString(60, y, "Diff omitted.")
                y -= 15
            else:
                for line in diff_lines:
                    if y < 50:
                        c.showPage()
                        y = height - 50
                    if line.startswith('-'):
                        c.setFillColor(red)
                    elif line.startswith('+'):
                        c.setFillColor(green)
                    else:
                        c.setFillColor(black)
                    c.drawString(60, y, line.strip())
                    y -= 15
            y -= 20

        c.save()
        return pdf_path  # Return the PDF file path

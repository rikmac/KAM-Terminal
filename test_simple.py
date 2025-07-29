#!/usr/bin/env python3
"""
Test semplificato KAM Terminal
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time

class KAMTerminalSimple:
    def __init__(self):
        print("Creando finestra...")
        self.root = tk.Tk()
        self.root.title("KAM Terminal - Test")
        self.root.geometry("600x400")
        
        print("Creando interfaccia...")
        self.create_interface()
        print("Interfaccia creata!")
        
    def create_interface(self):
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra di stato
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(status_frame, text="Test KAM Terminal")
        self.status_label.pack(side=tk.LEFT)
        
        # Display
        self.rx_display = scrolledtext.ScrolledText(
            main_frame, 
            height=10, 
            bg="black", 
            fg="lime", 
            font=("Courier", 10)
        )
        self.rx_display.pack(fill=tk.BOTH, expand=True)
        self.rx_display.insert(tk.END, "=== KAM Terminal Test ===\n")
        
    def run(self):
        print("Avviando mainloop...")
        self.root.mainloop()
        print("Mainloop terminato")

if __name__ == "__main__":
    print("Avvio test...")
    app = KAMTerminalSimple()
    app.run()
    print("Test completato")

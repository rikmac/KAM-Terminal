#!/usr/bin/env python3
"""
KAM Terminal - Versione semplificata che funziona
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import threading
import time

# --- CONFIGURAZIONE ---
SERIAL_PORT = "COM5"
BAUD_RATE = 1200

class KAMTerminal:
    def __init__(self):
        print("Inizializzo KAM Terminal...")
        
        self.root = tk.Tk()
        self.root.title("KAM Terminal - Kantronics All Mode")
        self.root.geometry("800x600")
        
        # Variabili
        self.serial_connection = None
        self.running = True
        
        print("Creo interfaccia...")
        self.create_interface()
        
        print("Provo connessione seriale...")
        self.try_serial_connection()
        
        print("Inizializzazione completata!")
        
    def create_interface(self):
        """Crea l'interfaccia utente."""
        
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra di stato
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text=f"Porta: {SERIAL_PORT} @ {BAUD_RATE} baud - Inizializzazione...")
        self.status_label.pack(side=tk.LEFT)
        
        # Pulsanti
        ttk.Button(status_frame, text="Connetti", command=self.connect_kam).pack(side=tk.RIGHT, padx=(5,0))
        ttk.Button(status_frame, text="TX", command=self.tx_mode).pack(side=tk.RIGHT, padx=(5,0))
        ttk.Button(status_frame, text="RX", command=self.rx_mode).pack(side=tk.RIGHT, padx=(5,0))
        
        # Display principale
        self.display = scrolledtext.ScrolledText(
            main_frame, 
            height=20, 
            bg="black", 
            fg="lime", 
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Comando:").pack(side=tk.LEFT)
        self.input_entry = ttk.Entry(input_frame, font=("Courier", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.input_entry.bind("<Return>", self.send_command)
        
        ttk.Button(input_frame, text="Invia", command=self.send_command).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Macro semplici
        macro_frame = ttk.Frame(main_frame)
        macro_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(macro_frame, text="F1-CQ", command=lambda: self.send_macro("CQ CQ CQ")).pack(side=tk.LEFT, padx=2)
        ttk.Button(macro_frame, text="F2-73", command=lambda: self.send_macro("73")).pack(side=tk.LEFT, padx=2)
        ttk.Button(macro_frame, text="CWMODE", command=lambda: self.send_macro("CWMODE")).pack(side=tk.LEFT, padx=2)
        ttk.Button(macro_frame, text="RTTYMODE", command=lambda: self.send_macro("RTTYMODE")).pack(side=tk.LEFT, padx=2)
        
        self.log("=== KAM Terminal Avviato ===")
        
    def log(self, text):
        """Aggiunge testo al display."""
        self.display.config(state=tk.NORMAL)
        self.display.insert(tk.END, text + "\n")
        self.display.see(tk.END)
        self.display.config(state=tk.DISABLED)
    
    def try_serial_connection(self):
        """Prova la connessione seriale senza bloccare."""
        try:
            self.serial_connection = serial.Serial(
                SERIAL_PORT, 
                BAUD_RATE, 
                timeout=0.1
            )
            
            # Thread per lettura
            self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.read_thread.start()
            
            self.status_label.config(text=f"Porta: {SERIAL_PORT} @ {BAUD_RATE} baud - Connesso")
            self.log("=== Connesso al KAM ===")
            
        except Exception as e:
            self.status_label.config(text=f"Porta: {SERIAL_PORT} @ {BAUD_RATE} baud - Errore")
            self.log(f"=== Errore connessione: {e} ===")
            self.log("=== Modalità offline ===")
    
    def connect_kam(self):
        """Riconnette al KAM."""
        self.log("=== Tentativo riconnessione ===")
        self.try_serial_connection()
    
    def read_serial(self):
        """Legge dalla porta seriale."""
        buffer = ""
        while self.running and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    text = data.decode('ascii', errors='ignore')
                    
                    buffer += text
                    while '\r' in buffer or '\n' in buffer:
                        if '\r\n' in buffer:
                            line, buffer = buffer.split('\r\n', 1)
                        elif '\r' in buffer:
                            line, buffer = buffer.split('\r', 1)
                        elif '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                        
                        if line.strip():
                            self.root.after(0, lambda: self.log(f"RX: {line}"))
                
                time.sleep(0.05)
                
            except Exception as e:
                if self.running:
                    self.root.after(0, lambda: self.log(f"Errore lettura: {e}"))
                break
    
    def send_command(self, event=None):
        """Invia comando."""
        command = self.input_entry.get().strip()
        if command:
            self.send_to_kam(command)
            self.input_entry.delete(0, tk.END)
    
    def send_macro(self, command):
        """Invia macro."""
        self.send_to_kam(command)
    
    def send_to_kam(self, command):
        """Invia comando al KAM."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write((command + '\r').encode('ascii'))
                self.log(f"TX: {command}")
            except Exception as e:
                self.log(f"Errore TX: {e}")
        else:
            self.log(f"OFFLINE: {command}")
    
    def tx_mode(self):
        """Modalità trasmissione."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # CTRL-C + T
                self.serial_connection.write(b'\x03')  # CTRL-C
                time.sleep(0.1)
                self.serial_connection.write(b'T')
                self.log("=== MODALITÀ TX ===")
                self.status_label.config(text=f"Porta: {SERIAL_PORT} @ {BAUD_RATE} baud - TX")
            except Exception as e:
                self.log(f"Errore TX: {e}")
        else:
            messagebox.showwarning("Avviso", "KAM non connesso!")
    
    def rx_mode(self):
        """Modalità ricezione."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # CTRL-C + R
                self.serial_connection.write(b'\x03')  # CTRL-C
                time.sleep(0.1)
                self.serial_connection.write(b'R')
                self.log("=== MODALITÀ RX ===")
                self.status_label.config(text=f"Porta: {SERIAL_PORT} @ {BAUD_RATE} baud - RX")
            except Exception as e:
                self.log(f"Errore RX: {e}")
        else:
            messagebox.showwarning("Avviso", "KAM non connesso!")
    
    def run(self):
        """Avvia l'applicazione."""
        print("Avvio mainloop...")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        print("Programma terminato")
    
    def on_closing(self):
        """Chiusura."""
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.root.destroy()

if __name__ == "__main__":
    print("=== Avvio KAM Terminal ===")
    app = KAMTerminal()
    app.run()
    print("=== Fine ===")

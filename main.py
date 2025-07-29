#!/usr/bin/env python3
"""
KAM Terminal - Versione semplice che funziona come PuTTY
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import serial
import threading
import time

# --- CONFIGURAZIONE ---
SERIAL_PORT = "COM1"
BAUD_RATE = 1200

class KAMTerminal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KAM Terminal - Kantronics All Mode")
        self.root.geometry("800x600")
        
        # Variabili
        self.serial_connection = None
        self.running = True
        
        self.create_interface()
        self.try_serial_connection()
        
    def create_interface(self):
        """Crea l'interfaccia utente con terminale diviso."""
        
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra di stato
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text=f"Porta: {SERIAL_PORT} @ {BAUD_RATE} baud")
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Button(status_frame, text="Configura", command=self.configure_serial).pack(side=tk.RIGHT, padx=(5,0))
        ttk.Button(status_frame, text="Connetti", command=self.try_serial_connection).pack(side=tk.RIGHT, padx=(5,0))
        
        # PARTE ALTA - Display di ricezione (solo lettura)
        ttk.Label(main_frame, text="Ricezione dal KAM:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.display = scrolledtext.ScrolledText(
            main_frame, 
            height=15, 
            bg="black", 
            fg="lime", 
            font=("Courier", 10),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.display.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # SEPARATORE VISUALE
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)
        
        # PARTE BASSA - Terminale di invio
        ttk.Label(main_frame, text="Terminale per invio comandi al KAM:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.terminal_input = tk.Text(
            main_frame,
            height=8,
            bg="black",
            fg="white",
            font=("Courier", 10),
            insertbackground="white",
            wrap=tk.NONE
        )
        self.terminal_input.pack(fill=tk.X, pady=(0, 10))
        self.terminal_input.focus()
        
        # Bind per invio con RETURN
        self.terminal_input.bind("<Return>", self.send_terminal_command)
        
        # Bind per combinazioni di tasti speciali
        self.terminal_input.bind("<Control-c>", self.send_ctrl_c)
        self.terminal_input.bind("<Control-C>", self.send_ctrl_c)
        
        # Configurazione script F1-F8
        self.scripts = {
            "F1": "CQ CQ CQ DE IW5DGQ IW5DGQ K",
            "F2": "TNX QSO 73",
            "F3": "TU",
            "F4": "",
            "F5": "",
            "F6": "",
            "F7": "",
            "F8": ""
        }
        
        # Bind per tasti funzione F1-F8
        self.terminal_input.bind("<F1>", lambda e: self.send_script("F1"))
        self.terminal_input.bind("<F2>", lambda e: self.send_script("F2"))
        self.terminal_input.bind("<F3>", lambda e: self.send_script("F3"))
        self.terminal_input.bind("<F4>", lambda e: self.send_script("F4"))
        self.terminal_input.bind("<F5>", lambda e: self.send_script("F5"))
        self.terminal_input.bind("<F6>", lambda e: self.send_script("F6"))
        self.terminal_input.bind("<F7>", lambda e: self.send_script("F7"))
        self.terminal_input.bind("<F8>", lambda e: self.send_script("F8"))
        
        # Pulsanti F1-F8 configurabili in una sola riga
        macro_frame = ttk.Frame(main_frame)
        macro_frame.pack(fill=tk.X)
        
        # Tutti i pulsanti F1-F8 in una riga orizzontale
        for i in range(1, 9):
            key = f"F{i}"
            btn = ttk.Button(macro_frame, text=key, width=6, 
                           command=lambda k=key: self.send_script(k))
            btn.pack(side=tk.LEFT, padx=2)
            # Tasto destro per configurare
            btn.bind("<Button-3>", lambda e, k=key: self.configure_script(k))
        
        # Pulsanti di controllo alla fine della riga
        tx_btn = ttk.Button(macro_frame, text="TX", command=self.tx_mode)
        tx_btn.pack(side=tk.LEFT, padx=2)
        
        rx_btn = ttk.Button(macro_frame, text="RX", command=self.rx_mode)
        rx_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(macro_frame, text="CMD", command=self.command_mode).pack(side=tk.LEFT, padx=2)
        
        # Configurazione colori per i pulsanti TX e RX
        style = ttk.Style()
        style.configure("TX.TButton", foreground="black", background="red")
        style.configure("RX.TButton", foreground="black", background="green")
        
        # Applica gli stili
        tx_btn.configure(style="TX.TButton")
        rx_btn.configure(style="RX.TButton")
        
        self.log("=== KAM Terminal Avviato ===")
        self.log("Parte alta: ricezione dal KAM")
        self.log("Parte bassa: scrivi e premi RETURN per inviare")
        self.log("FLUSSO: 1) TX per trasmettere, 2) F1-F8 o scrivi, 3) RX per ricevere")
        self.log("Tasti F1-F8: script configurabili (tasto destro per configurare)")
        self.log("CTRL-C: comandi speciali KAM")
        
    def log(self, text):
        """Aggiunge testo al display."""
        self.display.config(state=tk.NORMAL)
        self.display.insert(tk.END, text + "\n")
        self.display.see(tk.END)
        self.display.config(state=tk.DISABLED)
    
    def configure_serial(self):
        """Configura porta COM e velocità baud."""
        global SERIAL_PORT, BAUD_RATE
        
        # Finestra di configurazione seriale
        dialog = tk.Toplevel(self.root)
        dialog.title("Configurazione Porta Seriale")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centra la finestra
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Frame per porta COM
        com_frame = tk.Frame(dialog)
        com_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(com_frame, text="Porta COM:", font=("Arial", 10)).pack(anchor=tk.W)
        com_var = tk.StringVar(value=SERIAL_PORT)
        com_combo = ttk.Combobox(com_frame, textvariable=com_var, width=10)
        com_combo['values'] = ('COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10')
        com_combo.pack(pady=5, anchor=tk.W)
        
        # Frame per velocità baud
        baud_frame = tk.Frame(dialog)
        baud_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(baud_frame, text="Velocità (baud):", font=("Arial", 10)).pack(anchor=tk.W)
        baud_var = tk.StringVar(value=str(BAUD_RATE))
        baud_combo = ttk.Combobox(baud_frame, textvariable=baud_var, width=10)
        baud_combo['values'] = ('300', '600', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200')
        baud_combo.pack(pady=5, anchor=tk.W)
        
        result = [None, None]  # Lista per catturare il risultato
        
        def on_ok():
            try:
                new_port = com_var.get().upper()
                new_baud = int(baud_var.get())
                result[0] = new_port
                result[1] = new_baud
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Errore", "Velocità baud non valida!")
            
        def on_cancel():
            result[0] = None
            result[1] = None
            dialog.destroy()
            
        # Pulsanti
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Annulla", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
        
        # Aspetta che la finestra si chiuda
        dialog.wait_window()
        
        if result[0] is not None and result[1] is not None:
            # Aggiorna le variabili globali
            SERIAL_PORT = result[0]
            BAUD_RATE = result[1]
            
            # Chiudi connessione esistente se aperta
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                
            # Aggiorna la label di stato
            self.status_label.config(text=f"Porta: {SERIAL_PORT} @ {BAUD_RATE} baud")
            self.log(f"Configurazione aggiornata: {SERIAL_PORT} @ {BAUD_RATE} baud")
            self.log("Clicca 'Connetti' per applicare le nuove impostazioni")
    
    def try_serial_connection(self):
        """Prova la connessione seriale."""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                
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
            self.status_label.config(text=f"Porta: {SERIAL_PORT} @ {BAUD_RATE} baud - Errore: {e}")
            self.log(f"=== Errore connessione: {e} ===")
    
    def read_serial(self):
        """Legge dalla porta seriale - come un terminale normale."""
        while self.running and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    text = data.decode('ascii', errors='ignore')
                    # Mostra tutto quello che arriva, senza filtrare
                    if text:
                        self.root.after(0, lambda t=text: self.display_raw(t))
                
                time.sleep(0.01)
                
            except Exception as e:
                if self.running:
                    self.root.after(0, lambda: self.log(f"Errore lettura: {e}"))
                break
    
    def display_raw(self, text):
        """Mostra il testo grezzo come un terminale normale."""
        self.display.config(state=tk.NORMAL)
        self.display.insert(tk.END, text)
        self.display.see(tk.END)
        self.display.config(state=tk.DISABLED)
    
    def send_command(self, event=None):
        """Funzione obsoleta - ora si usa send_terminal_command."""
        pass
    
    def send_ctrl_c(self, event=None):
        """Invia CTRL-C al KAM."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03')  # CTRL-C
                self.log("CTRL-C inviato - ora premi X per command mode, T per TX, R per RX")
            except Exception as e:
                self.log(f"Errore CTRL-C: {e}")
        return "break"  # Evita che CTRL-C faccia altre cose
    
    def send_terminal_command(self, event=None):
        """Invia comando dal terminale inferiore."""
        # Ottieni la riga corrente dove si trova il cursore
        current_line = self.terminal_input.index(tk.INSERT).split('.')[0]
        line_start = f"{current_line}.0"
        line_end = f"{current_line}.end"
        
        # Leggi il testo della riga corrente
        command = self.terminal_input.get(line_start, line_end).strip()
        
        if command and self.serial_connection and self.serial_connection.is_open:
            try:
                # Invia il comando al KAM
                self.serial_connection.write(command.encode('ascii') + b'\r')
                
                # Mostra il comando inviato nella parte alta per feedback
                self.log(f"> {command}")
                
            except Exception as e:
                self.log(f"Errore invio: {e}")
        
        # Posiziona il cursore alla fine della riga corrente
        self.terminal_input.mark_set(tk.INSERT, line_end)
        # Inserisci un newline per andare a capo
        self.terminal_input.insert(tk.INSERT, "\n")
        # Assicurati che il cursore sia visibile
        self.terminal_input.see(tk.INSERT)
        
        # Evita che venga inserito un newline automatico aggiuntivo
        return "break"
    
    def send_script(self, key):
        """Invia lo script associato al tasto funzione."""
        script = self.scripts.get(key, "")
        if script:
            self.send_macro(script)
        else:
            self.log(f"{key}: Script non configurato - doppio click per configurare")
    
    def configure_script(self, key):
        """Configura lo script per un tasto funzione."""
        from tkinter import simpledialog
        
        current_script = self.scripts.get(key, "")
        
        # Finestra personalizzata per input più largo
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Configura {key}")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centra la finestra
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Label
        tk.Label(dialog, text=f"Inserisci il testo per {key}:\n(lascia vuoto per cancellare)", 
                font=("Arial", 10)).pack(pady=10)
        
        # Entry largo per 30+ caratteri
        entry = tk.Entry(dialog, width=50, font=("Courier", 10))
        entry.pack(pady=10, padx=20, fill=tk.X)
        entry.insert(0, current_script)
        entry.focus()
        entry.select_range(0, tk.END)
        
        result = [None]  # Lista per catturare il risultato
        
        def on_ok():
            result[0] = entry.get()
            dialog.destroy()
            
        def on_cancel():
            result[0] = None
            dialog.destroy()
            
        def on_enter(event):
            on_ok()
            
        # Pulsanti
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Annulla", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Bind ENTER per OK
        entry.bind("<Return>", on_enter)
        
        # Aspetta che la finestra si chiuda
        dialog.wait_window()
        
        new_script = result[0]
        if new_script is not None:  # None se annullato, "" se vuoto
            self.scripts[key] = new_script
            if new_script:
                self.log(f"{key} configurato: {new_script}")
            else:
                self.log(f"{key} cancellato")
    
    def send_direct(self, command):
        """Invia comando diretto per configurazione."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(command.encode('ascii') + b'\r')
            except Exception as e:
                self.log(f"Errore invio: {e}")
    
    def send_macro(self, text):
        """Invia il testo della macro con CR finale per eseguire il comando."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.log(f"Invio comando: {text}")
                
                # Invia il testo CON CR finale per eseguire il comando
                self.serial_connection.write(text.encode('ascii') + b'\r')
                
                self.log("Comando eseguito")
                
            except Exception as e:
                self.log(f"Errore invio: {e}")
        else:
            self.log(f"OFFLINE: {text}")
    
    def command_mode(self):
        """Torna al command mode del KAM (CTRL-C X)."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03X\r')
                self.log("Comando inviato: CTRL-C X (Command Mode)")
            except Exception as e:
                self.log(f"Errore CMD: {e}")
    
    def tx_mode(self):
        """Mette il KAM in trasmissione (CTRL-C T)."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03T\r')
                self.log("Comando inviato: CTRL-C T (TX Mode)")
            except Exception as e:
                self.log(f"Errore TX: {e}")
    
    def rx_mode(self):
        """Mette il KAM in ricezione (CTRL-C R)."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03R\r')
                self.log("Comando inviato: CTRL-C R (RX Mode)")
            except Exception as e:
                self.log(f"Errore RX: {e}")
    
    def run(self):
        """Avvia l'applicazione."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Chiusura."""
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.root.destroy()

if __name__ == "__main__":
    app = KAMTerminal()
    app.run()

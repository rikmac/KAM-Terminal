#!/usr/bin/env python3
"""
KAM Terminal - Versione Qt (PyQt5)
"""

import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QLineEdit, QComboBox, QDialog, QDialogButtonBox,
    QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import serial
import time

SERIAL_PORT = "COM1"
BAUD_RATE = 1200
CONFIG_FILE = "kam_config.json"

class SerialThread(QThread):
    received = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, serial_connection):
        super().__init__()
        self.serial_connection = serial_connection
        self.running = True

    def run(self):
        while self.running and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    text = data.decode('ascii', errors='ignore')
                    if text:
                        self.received.emit(text)
                time.sleep(0.01)
            except Exception as e:
                self.error.emit(str(e))
                break

    def stop(self):
        self.running = False
        self.wait()

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurazione Porta Seriale")
        self.setFixedSize(300, 180)
        layout = QVBoxLayout(self)

        self.com_label = QLabel("Porta COM:")
        self.com_combo = QComboBox()
        self.com_combo.addItems([f"COM{i}" for i in range(1, 11)])
        layout.addWidget(self.com_label)
        layout.addWidget(self.com_combo)

        self.baud_label = QLabel("Velocità (baud):")
        self.baud_combo = QComboBox()
        self.baud_combo.addItems([str(b) for b in [300,600,1200,2400,4800,9600,19200,38400,57600,115200]])
        layout.addWidget(self.baud_label)
        layout.addWidget(self.baud_combo)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_values(self):
        return self.com_combo.currentText(), int(self.baud_combo.currentText())

class KAMTerminalQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KAM Terminal - Qt")  # Titolo più breve
        self.resize(800, 800)  # Stessa larghezza ma 200px più alta

        self.serial_connection = None
        self.serial_thread = None
        self.script_buttons = {}  # Dizionario per tenere traccia dei pulsanti degli script
        
        # Default values (saranno sovrascritti se esiste un file di configurazione)
        self.callsign = "xx1xyz"  # Nominativo di default
        self.scripts = {
            "F1": "CQ CQ CQ DE <CALL> <CALL> K",
            "F2": "TNX QSO 73",
            "F3": "TU",
            "F4": "",
            "F5": "",
            "F6": "",
            "F7": "",
            "F8": ""
        }

        self.init_ui()
        self.try_serial_connection()

    def init_ui(self):
        central = QWidget()
        vbox = QVBoxLayout(central)
        self.setCentralWidget(central)

        # Crea menu bar
        menubar = self.menuBar()
        self.edit_menu = menubar.addMenu('Edit')
        
        # Azioni del menu
        config_action = self.edit_menu.addAction('Configura')
        config_action.triggered.connect(self.configure_serial)
        
        connect_action = self.edit_menu.addAction('Connetti KAM')
        connect_action.triggered.connect(self.try_serial_connection)
        
        callsign_action = self.edit_menu.addAction('Conf. Nominativo')
        callsign_action.triggered.connect(self.configure_callsign)
        
        # Aggiunge i pulsanti di controllo principali sotto la barra dei menu
        control_bar = QHBoxLayout()
        
        # Aggiunge uno stretch all'inizio per spingere i pulsanti a destra
        control_bar.addStretch()
        
        tx_btn = QPushButton("TX")
        tx_btn.setStyleSheet("background:red;color:black;")
        tx_btn.clicked.connect(self.tx_mode)
        tx_btn.setFixedWidth(50)
        control_bar.addWidget(tx_btn)
        
        rx_btn = QPushButton("RX")
        rx_btn.setStyleSheet("background:green;color:black;")
        rx_btn.clicked.connect(self.rx_mode)
        rx_btn.setFixedWidth(50)
        control_bar.addWidget(rx_btn)
        
        rx_buffer_btn = QPushButton("RX-E")
        rx_buffer_btn.setStyleSheet("background:orange;color:black;")
        rx_buffer_btn.clicked.connect(self.rx_after_buffer_empty)
        rx_buffer_btn.setToolTip("CTRL-C E: Torna in RX dopo svuotamento buffer TX")
        rx_buffer_btn.setFixedWidth(50)
        control_bar.addWidget(rx_buffer_btn)
        
        vbox.addLayout(control_bar)

        # RX display
        rx_container = QVBoxLayout()
        self.display = QTextEdit()
        self.display.setReadOnly(True)
        self.display.setStyleSheet("background:black;color:lime;font-family:Courier;font-size:10pt;")
        rx_container.addWidget(self.display)
        rx_widget = QWidget()
        rx_widget.setLayout(rx_container)
        vbox.addWidget(rx_widget, stretch=2)  # Rapporto 2:1 (2/3 in alto, 1/3 in basso)

        # Macro buttons spostati nella zona centrale
        hmacro = QHBoxLayout()
        for i in range(1, 9):
            key = f"F{i}"
            script_text = self.scripts.get(key, "")
            button_text = f"{key}: {script_text[:10]}{'...' if len(script_text) > 10 else ''}"
            btn = QPushButton(button_text)
            btn.setFixedWidth(110)  # Bottoni leggermente più stretti
            btn.clicked.connect(lambda _, k=key: self.send_script(k))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda _, k=key: self.configure_script(k))
            # Tooltip che mostra il testo completo
            if script_text:
                btn.setToolTip(script_text)
            else:
                btn.setToolTip("Tasto destro per configurare")
            hmacro.addWidget(btn)
            self.script_buttons[key] = btn  # Memorizza il riferimento al pulsante
        
        # Control buttons
        cmd_btn = QPushButton("CMD")
        cmd_btn.clicked.connect(self.command_mode)
        cmd_btn.setFixedWidth(50)  # Larghezza fissa per uniformità
        hmacro.addWidget(cmd_btn)
        
        clr_btn = QPushButton("CLR")
        clr_btn.clicked.connect(self.clear_rx_display)
        clr_btn.setFixedWidth(50)  # Larghezza fissa per uniformità
        hmacro.addWidget(clr_btn)
        hmacro.addStretch()
        vbox.addLayout(hmacro)

        # TX terminal
        tx_container = QVBoxLayout()
        self.terminal_input = QTextEdit()
        self.terminal_input.setStyleSheet("background:black;color:white;font-family:Courier;font-size:10pt;")
        tx_container.addWidget(self.terminal_input)
        self.terminal_input.installEventFilter(self)
        tx_widget = QWidget()
        tx_widget.setLayout(tx_container)
        vbox.addWidget(tx_widget, stretch=1)  # Mantiene lo stretch a 1 per l'area di invio

        self.log("> KAM Terminal Qt Avviato")
        
        # Carica la configurazione dopo aver creato l'interfaccia utente
        self.load_config()
        
        # Aggiungiamo una opzione per salvare la configurazione nel menu
        save_action = self.edit_menu.addAction('Salva Configurazione')
        save_action.triggered.connect(self.save_config)

    def eventFilter(self, obj, event):
        if obj == self.terminal_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.send_terminal_command()
                return True
            if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_C:
                self.send_ctrl_c()
                return True
            for i in range(1, 9):
                if event.key() == getattr(Qt, f"Key_F{i}"):
                    self.send_script(f"F{i}")
                    return True
        return super().eventFilter(obj, event)

    def log(self, text):
        self.display.append(text)
        self.display.moveCursor(self.display.textCursor().End)

    def configure_serial(self):
        global SERIAL_PORT, BAUD_RATE
        dlg = ConfigDialog(self)
        if dlg.exec_():
            SERIAL_PORT, BAUD_RATE = dlg.get_values()
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            self.log(f"> Configurato: {SERIAL_PORT} @ {BAUD_RATE}")
    
    def configure_callsign(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Configurazione Nominativo")
        dlg.setFixedSize(300, 120)
        vbox = QVBoxLayout(dlg)
        vbox.addWidget(QLabel("Inserisci il tuo nominativo:"))
        entry = QLineEdit()
        entry.setText(self.callsign)
        vbox.addWidget(entry)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if dlg.exec_():
            new_callsign = entry.text().strip().upper()
            if new_callsign:
                self.callsign = new_callsign
                # Aggiorna F1 con il nuovo nominativo
                if "F1" in self.scripts and "CQ CQ CQ DE" in self.scripts["F1"]:
                    self.scripts["F1"] = "CQ CQ CQ DE <CALL> <CALL> K"
                    if "F1" in self.script_buttons:
                        button = self.script_buttons["F1"]
                        # Mostra l'anteprima con il nominativo già sostituito
                        preview = self.scripts["F1"].replace("<CALL>", self.callsign)
                        button_text = f"F1: {preview[:10]}{'...' if len(preview) > 10 else ''}"
                        button.setText(button_text)
                        button.setToolTip(preview)
                
                # Aggiorna tutti i pulsanti degli script per mostrare il nuovo nominativo
                for key, script in self.scripts.items():
                    if "<CALL>" in script and key in self.script_buttons:
                        button = self.script_buttons[key]
                        preview = script.replace("<CALL>", self.callsign)
                        button_text = f"{key}: {preview[:10]}{'...' if len(preview) > 10 else ''}"
                        button.setText(button_text)
                        button.setToolTip(preview)
                
                self.log(f"> Nominativo configurato: {self.callsign}")
                
                # Salva la configurazione
                self.save_config()

    def try_serial_connection(self):
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            self.serial_connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            if self.serial_thread:
                self.serial_thread.stop()
            self.serial_thread = SerialThread(self.serial_connection)
            self.serial_thread.received.connect(self.display_raw)
            self.serial_thread.error.connect(lambda e: self.log(f"Errore: {e}"))
            self.serial_thread.start()
            self.log(f"> Connesso a {SERIAL_PORT} @ {BAUD_RATE}")
        except Exception as e:
            self.log(f"> Errore: {e}")

    def display_raw(self, text):
        self.display.setReadOnly(False)
        self.display.insertPlainText(text)
        self.display.moveCursor(self.display.textCursor().End)
        self.display.setReadOnly(True)

    def send_ctrl_c(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03')
                self.log("> CTRL-C")
            except Exception as e:
                self.log(f"Errore: {e}")

    def send_terminal_command(self):
        command = self.terminal_input.toPlainText().strip()
        if command and self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(command.encode('ascii') + b'\r')
                self.log(f"> {command}")
            except Exception as e:
                self.log(f"Errore: {e}")
        self.terminal_input.clear()

    def send_script(self, key):
        script = self.scripts.get(key, "")
        if script:
            # Sostituisci <CALL> con il nominativo attuale prima di inviare
            script_to_send = script.replace("<CALL>", self.callsign)
            self.send_macro(script_to_send)
        else:
            self.log(f"> {key}: Non configurato")

    def configure_script(self, key):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Configura {key}")
        dlg.setFixedSize(400, 150)
        vbox = QVBoxLayout(dlg)
        vbox.addWidget(QLabel(f"Inserisci il testo per {key}:\n(lascia vuoto per cancellare)\nUsa <CALL> per inserire il tuo nominativo"))
        entry = QLineEdit()
        entry.setText(self.scripts.get(key, ""))
        vbox.addWidget(entry)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if dlg.exec_():
            new_script = entry.text()
            # Salva lo script mantenendo il tag <CALL>
            self.scripts[key] = new_script
            
            # Aggiorna il testo del pulsante usando il riferimento memorizzato
            if key in self.script_buttons:
                button = self.script_buttons[key]
                if new_script:
                    # Per mostrare l'anteprima con il nominativo sostituito
                    preview_script = new_script.replace("<CALL>", self.callsign)
                    button_text = f"{key}: {preview_script[:10]}{'...' if len(preview_script) > 10 else ''}"
                    button.setText(button_text)
                    button.setToolTip(preview_script)
                    self.log(f"> {key}: {new_script}")
                else:
                    button_text = f"{key}: "
                    button.setText(button_text)
                    button.setToolTip("Tasto destro per configurare")
                    self.log(f"> {key}: Cancellato")
            
            # Salva la configurazione dopo aver modificato uno script
            self.save_config()

    def send_macro(self, text):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # Log solo del testo dello script, senza altri dettagli
                self.log(f"> {text}")
                # Invia TX mode prima del comando
                self.serial_connection.write(b'\x03T\r')
                time.sleep(0.1)  # Breve pausa per assicurarsi che il KAM sia in TX
                # Invia il comando dello script
                self.serial_connection.write(text.encode('ascii') + b'\r')
                time.sleep(0.1)  # Breve pausa per dare tempo al KAM di processare
                # Usa CTRL-C E per tornare in RX dopo lo svuotamento del buffer
                self.serial_connection.write(b'\x03E\r')
                # Nessun messaggio di completamento per mantenere lo schermo pulito
            except Exception as e:
                self.log(f"Errore: {e}")
        else:
            self.log(f"OFFLINE: {text}")

    def command_mode(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03X\r')
                self.log("> CMD")
            except Exception as e:
                self.log(f"Errore: {e}")

    def clear_rx_display(self):
        self.display.setReadOnly(False)
        self.display.clear()
        self.display.setReadOnly(True)

    def tx_mode(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03T\r')
                self.log("> TX")
            except Exception as e:
                self.log(f"Errore: {e}")

    def rx_mode(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03R\r')
                self.log("> RX")
            except Exception as e:
                self.log(f"Errore: {e}")
                
    def rx_after_buffer_empty(self):
        """Torna in ricezione dopo lo svuotamento del buffer TX"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'\x03E\r')
                self.log("> RX-Buffer")
            except Exception as e:
                self.log(f"Errore: {e}")

    def save_config(self):
        """Salva la configurazione attuale in un file JSON"""
        config = {
            "user_config": {
                "callsign": self.callsign
            },
            "scripts": self.scripts,
            "serial": {
                "port": SERIAL_PORT,
                "baud": BAUD_RATE
            }
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            self.log(f"> Configurazione salvata in {CONFIG_FILE}")
        except Exception as e:
            self.log(f"> Errore nel salvare la configurazione: {e}")

    def load_config(self):
        """Carica la configurazione da un file JSON"""
        if not os.path.exists(CONFIG_FILE):
            self.log(f"> File di configurazione {CONFIG_FILE} non trovato, uso default")
            return False
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            # Carica la configurazione utente
            if "user_config" in config and "callsign" in config["user_config"]:
                self.callsign = config["user_config"]["callsign"]
            
            # Carica gli script
            if "scripts" in config:
                self.scripts = config["scripts"]
                # Aggiorna i pulsanti degli script
                for key, script in self.scripts.items():
                    if key in self.script_buttons:
                        button = self.script_buttons[key]
                        preview_script = script.replace("<CALL>", self.callsign)
                        button_text = f"{key}: {preview_script[:10]}{'...' if len(preview_script) > 10 else ''}"
                        button.setText(button_text)
                        button.setToolTip(preview_script)
            
            # Carica configurazioni seriali
            global SERIAL_PORT, BAUD_RATE
            if "serial" in config:
                if "port" in config["serial"]:
                    SERIAL_PORT = config["serial"]["port"]
                if "baud" in config["serial"]:
                    BAUD_RATE = config["serial"]["baud"]
            
            self.log(f"> Configurazione caricata da {CONFIG_FILE}")
            return True
        except Exception as e:
            self.log(f"> Errore nel caricare la configurazione: {e}")
            return False

    def closeEvent(self, event):
        # Salva la configurazione prima di chiudere
        self.save_config()
        
        if self.serial_thread:
            self.serial_thread.stop()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = KAMTerminalQt()
    win.show()
    sys.exit(app.exec_())

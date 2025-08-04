#!/usr/bin/env python3
"""
KAM Terminal - Versione Qt (PyQt5)
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QLineEdit, QComboBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import serial
import time

SERIAL_PORT = "COM1"
BAUD_RATE = 1200

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
        self.setWindowTitle("KAM Terminal - Kantronics All Mode (Qt)")
        self.resize(800, 600)

        self.serial_connection = None
        self.serial_thread = None
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

        self.init_ui()
        self.try_serial_connection()

    def init_ui(self):
        central = QWidget()
        vbox = QVBoxLayout(central)
        self.setCentralWidget(central)

        # Status bar senza label di stato
        hstatus = QHBoxLayout()
        btn_config = QPushButton("Configura")
        btn_config.clicked.connect(self.configure_serial)
        hstatus.addWidget(btn_config)
        btn_connect = QPushButton("Connetti")
        btn_connect.clicked.connect(self.try_serial_connection)
        hstatus.addWidget(btn_connect)
        hstatus.addStretch()
        vbox.addLayout(hstatus)

        # RX display (2/3 spazio)
        vbox.addWidget(QLabel("Ricezione dal KAM:"))
        rx_container = QVBoxLayout()
        self.display = QTextEdit()
        self.display.setReadOnly(True)
        self.display.setStyleSheet("background:black;color:lime;font-family:Courier;font-size:10pt;")
        rx_container.addWidget(self.display)
        rx_widget = QWidget()
        rx_widget.setLayout(rx_container)
        vbox.addWidget(rx_widget, stretch=2)

        # TX terminal (1/3 spazio)
        vbox.addWidget(QLabel("Terminale per invio comandi al KAM:"))
        tx_container = QVBoxLayout()
        self.terminal_input = QTextEdit()
        self.terminal_input.setStyleSheet("background:black;color:white;font-family:Courier;font-size:10pt;")
        tx_container.addWidget(self.terminal_input)
        self.terminal_input.installEventFilter(self)
        tx_widget = QWidget()
        tx_widget.setLayout(tx_container)
        vbox.addWidget(tx_widget, stretch=1)

        # Macro buttons
        hmacro = QHBoxLayout()
        for i in range(1, 9):
            key = f"F{i}"
            btn = QPushButton(key)
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda _, k=key: self.send_script(k))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda _, k=key: self.configure_script(k))
            hmacro.addWidget(btn)
        # Control buttons
        tx_btn = QPushButton("TX")
        tx_btn.setStyleSheet("background:red;color:black;")
        tx_btn.clicked.connect(self.tx_mode)
        hmacro.addWidget(tx_btn)
        rx_btn = QPushButton("RX")
        rx_btn.setStyleSheet("background:green;color:black;")
        rx_btn.clicked.connect(self.rx_mode)
        hmacro.addWidget(rx_btn)
        rx_buffer_btn = QPushButton("RX Buffer")
        rx_buffer_btn.setStyleSheet("background:orange;color:black;")
        rx_buffer_btn.clicked.connect(self.rx_after_buffer_empty)
        rx_buffer_btn.setToolTip("CTRL-C E: Torna in RX dopo svuotamento buffer TX")
        hmacro.addWidget(rx_buffer_btn)
        cmd_btn = QPushButton("CMD")
        cmd_btn.clicked.connect(self.command_mode)
        hmacro.addWidget(cmd_btn)
        clr_btn = QPushButton("CLR")
        clr_btn.clicked.connect(self.clear_rx_display)
        hmacro.addWidget(clr_btn)
        hmacro.addStretch()
        vbox.addLayout(hmacro)

        self.log("> KAM Terminal Qt Avviato")

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
            self.send_macro(script)
        else:
            self.log(f"> {key}: Non configurato")

    def configure_script(self, key):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Configura {key}")
        dlg.setFixedSize(400, 150)
        vbox = QVBoxLayout(dlg)
        vbox.addWidget(QLabel(f"Inserisci il testo per {key}:\n(lascia vuoto per cancellare)"))
        entry = QLineEdit()
        entry.setText(self.scripts.get(key, ""))
        vbox.addWidget(entry)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        if dlg.exec_():
            new_script = entry.text()
            self.scripts[key] = new_script
            if new_script:
                self.log(f"> {key}: {new_script}")
            else:
                self.log(f"> {key}: Cancellato")

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

    def closeEvent(self, event):
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

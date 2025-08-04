# Changelog

Tutte le modifiche rilevanti a questo progetto verranno documentate in questo file.

## [1.0.0] - 2025-07-29

### Aggiunto
- Interfaccia grafica PyQt5 con terminale diviso
- Parte superiore per ricezione dal KAM (display verde)
- Parte inferiore per invio comandi (terminale nero)
- Pulsanti F1-F8 configurabili per script rapidi
- Configurazione script tramite tasto destro
- Pulsanti TX (rosso), RX (verde) e RX-E (arancio) per controllo manuale
- Pulsante CMD per command mode
- Configurazione porta seriale e baud rate
- Gestione del nominativo personalizzabile
- Connessione seriale automatica con thread dedicato
- Gestione comandi CTRL-C per controllo KAM
- Script predefiniti per operazioni comuni
- Salvataggio/caricamento della configurazione in JSON

### Funzionalità Tecniche
- Comunicazione seriale asincrona con pyserial
- Gestione errori di connessione
- Thread separato per lettura seriale
- Interfaccia Qt con finestre dialog personalizzate
- Stili colore per pulsanti TX/RX
- Font monospace per terminale
- Encoding ASCII per compatibilità KAM
- Sostituzione tag <CALL> nei messaggi

### Script Predefiniti
- F1: "CQ CQ CQ DE <CALL> <CALL> K"
- F2: "TNX QSO 73"
- F3: "TU"
- F4-F8: Configurabili dall'utente

### Configurazioni di Default
- Porta seriale: COM1
- Baud rate: 1200
- Timeout: 0.1 secondi
- Supporto porte COM1-COM10
- Velocità baud: 300-115200

### Compatibilità
- Windows 10/11
- Python 3.x
- Radio KAM (Kantronics All Mode)
- Modi digitali: CW, PSK31, RTTY, Packet

---

**Sviluppato con ❤️ per la comunità radioamatoriale**
**73** 📻

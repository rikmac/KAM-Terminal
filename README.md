# KAM Terminal de IW5DGQ

Un terminale moderno e intuitivo per radio Kantronics All Mode (KAM) sviluppato in Python con interfaccia grafica PyQt5.

## 🎯 Scopo del Progetto

Questo programma fornisce un'interfaccia terminale semplice e moderna per comunicare con radio KAM (Kantronics All Mode), permettendo di operare in modo digitale sui modi CW, RTTY e altri modi digitali supportati dal KAM.

## ✨ Caratteristiche Principali

- **Interfaccia Divisa**: Parte superiore per ricezione, parte inferiore per invio comandi
- **Script Configurabili F1-F8**: Messaggi preimpostati per operazioni rapide
- **Controllo TX/RX Manuale**: Pulsanti colorati per gestire trasmissione/ricezione
- **Configurazione Seriale**: Porta COM e velocità baud configurabili
- **Terminale Real-time**: Comunicazione bidirezionale in tempo reale
- **Interfaccia Intuitiva**: Design pulito e facile da usare

## 🖥️ Interfaccia Utente

### Finestra Principale
- **Parte Alta (sfondo nero, testo verde)**: Display di ricezione dal KAM (solo lettura)
- **Parte Bassa (sfondo nero, testo bianco)**: Terminale per digitare e inviare comandi
- **Menu in alto**: Contiene le opzioni per configurazione e connessione

### Pulsanti di Controllo
- **F1-F8**: Script configurabili (tasto destro per configurare)
- **TX (rosso)**: Mette il KAM in trasmissione
- **RX (verde)**: Mette il KAM in ricezione immediata
- **RX Buffer (arancio)**: Mette il KAM in ricezione dopo lo svuotamento del buffer TX
- **CMD**: Torna al command mode del KAM

## 🚀 Come Usare

### Flusso di Lavoro Tipico
1. **Connetti** il KAM alla porta seriale
2. **Configura** la porta COM se necessario
3. **Clicca Connetti** per stabilire la comunicazione
4. **TX** → Vai in trasmissione nella modalità in uso **scrivi manualmente**
5. **RX** → Torna in ricezione nella modalità in uso
6. **F1-F8** per script rapidi 

### Configurazione Script
- **Tasto destro** su qualsiasi pulsante F1-F8 per configurare
- Inserisci il testo desiderato (max 50 caratteri visibili)
- Gli script vengono eseguiti in sequenza automatica:
  1. Passa in modalità TX
  2. Invia il testo dello script
  3. Torna in RX dopo lo svuotamento del buffer


## ⚙️ Configurazione

### Requisiti di Sistema
- Windows (testato su Windows 10/11)
- Python 3.x
- Porta seriale disponibile
- Radio KAM collegata

### Configurazione Seriale
- **Porta COM**: COM1-COM10 (configurabile)
- **Velocità Baud**: 300-9600 (default 1200)
- **Configurazione**: 8-N-1 (standard per KAM)

## 📋 Installazione

### Prerequisiti
```bash
pip install pyserial PyQt5
```

### Esecuzione
```bash
python main.py
```

## 🎛️ Configurazioni Predefinite

### Script di Default
- **F1**: `CQ CQ CQ DE <CALL> <CALL> K`
- **F2**: `TNX QSO 73`
- **F3**: `TU`
- **F4-F8**: Vuoti (configurabili)

### Comunicazione Seriale
- **Porta**: COM1
- **Baud Rate**: 1200
- **Timeout**: 0.1 secondi
- **Encoding**: ASCII

## 🔧 Funzionalità Tecniche

### Gestione Seriale
- Comunicazione asincrona con thread dedicato
- Gestione automatica degli errori di connessione
- Riconnessione manuale disponibile

### Interfaccia
- Tkinter con stili personalizzati
- Colori distintivi per TX (rosso) e RX (verde)
- Font monospace per terminale
- Finestre dialog personalizzate

### Controllo KAM
- Invio comandi CTRL-C per controllo mode
- Gestione TX/RX indipendente
- Supporto per tutti i comandi KAM standard

## 📝 Note per Radioamatori

### Modi Supportati
- **CW**: Telegrafia
- **RTTY**: Radio Teletype
- **Packet**: Packet Radio
- Altri modi digitali supportati dal KAM

### Utilizzo Tipico
Perfetto per:
- Contest digitali
- QSO routine
- Sperimentazione modi digitali
- Configurazione KAM
- Monitoraggio traffico digitale

## 🐛 Risoluzione Problemi

### Problemi Comuni
1. **Errore connessione**: Verificare porta COM e cavi
2. **Caratteri strani**: Controllare baud rate
3. **Script non funzionano**: Verificare configurazione
4. **KAM non risponde**: Provare CMD per command mode

### Log e Debug
Il programma mostra tutti i messaggi di stato nella parte superiore per facilitare il debug.

## 👥 Contributi

Progetto sviluppato con l'assistenza di GitHub Copilot per un radioamatore italiano.

## 📄 Licenza

Progetto open source per la comunità radioamatoriale.

---

**73** 📻

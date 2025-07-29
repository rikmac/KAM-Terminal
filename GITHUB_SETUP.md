# Come Pubblicare su GitHub

Questa guida ti aiuterà a pubblicare il progetto KAM Terminal su GitHub.

## Prerequisiti

1. **Account GitHub**: Crea un account su [github.com](https://github.com) se non lo hai già
2. **Git installato**: Scarica da [git-scm.com](https://git-scm.com/)
3. **Configurazione Git** (solo la prima volta):
   ```bash
   git config --global user.name "Il Tuo Nome"
   git config --global user.email "tua-email@example.com"
   ```

## Passi per Pubblicare

### 1. Crea Repository su GitHub
1. Vai su [github.com](https://github.com)
2. Clicca il pulsante verde "New" o "+"
3. Nome repository: `kam-terminal`
4. Descrizione: "Modern terminal interface for Kantronics All Mode (KAM) radio"
5. Seleziona "Public" per renderlo visibile a tutti
6. NON aggiungere README, .gitignore o LICENSE (li abbiamo già)
7. Clicca "Create repository"

### 2. Inizializza Git nella Cartella del Progetto
Apri PowerShell nella cartella `C:\Users\ykzri\Desktop\Programmazione\Kantronics` e esegui:

```bash
# Inizializza repository locale
git init

# Aggiungi tutti i file
git add .

# Primo commit
git commit -m "Initial commit - KAM Terminal v1.0.0"

# Aggiungi il repository remoto (sostituisci rikmac con il tuo username GitHub)
git remote add origin https://github.com/rikmac/kam-terminal.git

# Rinomina branch principale
git branch -M main

# Pubblica su GitHub
git push -u origin main
```

### 3. File Inclusi nel Repository
✅ `main.py` - Programma principale
✅ `README.md` - Documentazione completa
✅ `requirements.txt` - Dipendenze Python
✅ `.gitignore` - File da escludere
✅ `LICENSE` - Licenza MIT
✅ `CHANGELOG.md` - Cronologia modifiche
✅ `GITHUB_SETUP.md` - Questa guida

### 4. Comandi Git Utili per il Futuro

```bash
# Vedere lo stato
git status

# Aggiungere modifiche
git add .
git commit -m "Descrizione delle modifiche"
git push

# Scaricare modifiche dal repository
git pull

# Vedere la cronologia
git log --oneline

# Creare una nuova versione (tag)
git tag v1.0.0
git push origin v1.0.0
```

### 5. Struttura Repository Finale
```
kam-terminal/
├── main.py
├── README.md
├── requirements.txt
├── LICENSE
├── CHANGELOG.md
├── .gitignore
└── GITHUB_SETUP.md
```

### 6. Aggiornamenti Futuri
Quando modifichi il programma:
1. Testa le modifiche
2. Aggiorna `CHANGELOG.md` con le novità
3. Aggiorna il numero versione se necessario
4. Commit e push:
   ```bash
   git add .
   git commit -m "Descrizione modifiche"
   git push
   ```

### 7. Badge per README (Opzionale)
Puoi aggiungere questi badge all'inizio del README:

```markdown
![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![HAM Radio](https://img.shields.io/badge/HAM-Radio-red.svg)
```

## Supporto
Se hai problemi con Git o GitHub, cerca tutorials online o chiedi aiuto nella comunità radioamatoriale!

**73 de IW5DGQ** 📻

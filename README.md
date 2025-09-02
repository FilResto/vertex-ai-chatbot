# 🤖 Vertex AI Chatbot con MySQL

Un chatbot intelligente che usa **Vertex AI** per rispondere alle FAQ aziendali e salva tutte le conversazioni in **Cloud SQL MySQL**.

## 🚀 Cosa fa questo progetto

✅ **Step 1 COMPLETATO**: Agent Vertex AI con Gemini 2.5 Flash Lite  
✅ **Step 2 COMPLETATO**: Salvataggio conversazioni in Cloud SQL MySQL  
✅ **Step 3 COMPLETATO**: CI/CD Pipeline con Cloud Build  
🔄 **Step 4**: Deploy su Cloud Run (prossimo)  

## 📋 Prerequisiti

- ✅ Google Cloud Project configurato
- ✅ Cloud SQL MySQL attivo (IP: 35.195.153.11:3306)
- ✅ Vertex AI abilitato
- ✅ Python 3.8+

## 🛠️ Installazione

### 1. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 2. Configura le credenziali
Modifica `config.py` con le tue credenziali MySQL:
```python
DB_CONFIG = {
    'host': '35.195.153.11',
    'port': 3306,
    'user': 'root',  # Il tuo username MySQL
    'password': 'password123',  # La tua password MySQL
    'database': 'chatbot_db',  # Il nome del tuo database
    'charset': 'utf8mb4'
}
```

### 3. Crea il database MySQL
Vai su **Cloud SQL Studio** e esegui:
```sql
CREATE DATABASE chatbot_db;
```

### 4. Testa la connessione
```bash
python test_db.py
```

## 🚀 Avvia il chatbot

```bash
python app.py
```

Il server sarà disponibile su: `http://localhost:5000`

## 📡 API Endpoints

### POST `/chat`
Invia una domanda al chatbot:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Che prodotto sviluppate?"}'
```

### GET `/conversations`
Visualizza le ultime 10 conversazioni:
```bash
curl http://localhost:5000/conversations
```

## 🗄️ Struttura Database

Tabella `conversations`:
- `id`: ID auto-increment
- `user_message`: Messaggio dell'utente
- `ai_response`: Risposta dell'AI
- `timestamp`: Data/ora conversazione

## 🔧 Troubleshooting

### Errore connessione database:
1. Verifica che MySQL sia attivo
2. Controlla username/password in `config.py`
3. Verifica che il database esista
4. Controlla che l'IP pubblico sia accessibile

### Errore Vertex AI:
1. Verifica che Vertex AI sia abilitato
2. Controlla le credenziali Google Cloud
3. Verifica la quota API

## 📚 Prossimi Step

1. **CI/CD Pipeline** con Cloud Build
2. **Deploy su Cloud Run**
3. **Secure Communication** con A2A
4. **Estensione con MCP**

## 🎯 FAQ Supportate

- "Che prodotto sviluppate?"
- "Dove avete la sede?"
- "Come funziona il vostro prodotto?"
- "Chi può usare il prodotto?"
- "Quanto costa?"

---

**Creato per il progetto Tech-Onboarding** 🚀



# 🚀 Guida Completa - Vertex AI Chatbot Project

## 📋 **Panoramica del Progetto**

Questo progetto implementa un chatbot intelligente che usa **Vertex AI** per rispondere alle FAQ aziendali e salva tutte le conversazioni in **Cloud SQL MySQL**. Il sistema è completamente containerizzato e deployato su **Cloud Run** con un pipeline CI/CD automatizzato.

---

## ✅ **Step 1 - Create an Agent with Vertex AI** - COMPLETATO

### 🎯 **A cosa serve:**
Creare un chatbot intelligente che risponde alle FAQ aziendali usando l'AI di Google (Gemini 2.5 Flash).

### 🛠️ **Comandi utilizzati:**
```bash
# Abilitare Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Installare dipendenze Python
pip install -r requirements.txt

# Testare l'applicazione localmente
python app.py
```

### 📁 **File creati/modificati:**
- `app.py` - Applicazione Flask principale con Vertex AI
- `config.py` - Configurazioni per Google Cloud
- `requirements.txt` - Dipendenze Python

### 🔧 **Configurazione:**
- **Modello AI**: Gemini 2.5 Flash
- **Prompt System**: FAQ aziendali predefinite
- **Endpoint**: `/chat` per ricevere messaggi
- **Risposte**: 5 FAQ specifiche + gestione domande non supportate

### ⚠️ **Problemi risolti:**
- Configurazione corretta delle credenziali Google Cloud
- Gestione degli errori per domande non supportate

---

## ✅ **Step 2 - Save Conversations in Cloud SQL** - COMPLETATO

### 🎯 **A cosa serve:**
Salvare tutte le conversazioni tra utenti e AI in un database MySQL per analisi e cronologia.

### 🛠️ **Comandi utilizzati:**
```bash
# Abilitare Cloud SQL API
gcloud services enable sqladmin.googleapis.com

# Creare istanza Cloud SQL MySQL (via Console)
# - Vai su Google Cloud Console > Cloud SQL
# - Clicca "Create Instance"
# - Seleziona MySQL
# - Configura: Regione, versione, storage
```

### 📁 **File creati/modificati:**
- `database.py` - Gestione database MySQL
- `app.py` - Aggiunto salvataggio conversazioni
- `.env` - Configurazioni database (nascosto)

### 🗄️ **Struttura Database:**
```sql
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_ip VARCHAR(45)
);
```

### ⚠️ **Problemi risolti:**
- ❌ **Errore SQL**: `You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '-onboarding'`
- ✅ **Soluzione**: Aggiunto backtick attorno al nome database: `CREATE DATABASE IF NOT EXISTS \`{Config.DB_NAME}\``

### 🔐 **Configurazione Sicurezza:**
- **IP Autorizzati**: `0.0.0.0/0` (tutti gli IP per Cloud Run)
- **Utente Database**: Configurato nel file `.env`
- **Password**: Sicura e configurata nel file `.env`

---

## ✅ **Step 3 - CI/CD Pipeline with Cloud Build** - COMPLETATO

### 🎯 **A cosa serve:**
Automatizzare il build e deploy dell'applicazione ogni volta che viene fatto un push su GitHub.

### 🛠️ **Comandi utilizzati:**
```bash
# Abilitare API necessarie
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Creare repository Artifact Registry
gcloud artifacts repositories create vertex-ai-chatbot \
    --repository-format=docker \
    --location=europe-west1 \
    --description="Docker repository for Vertex AI Chatbot"

# Inizializzare repository Git
git init
git add .
git commit -m "Initial commit: Vertex AI Chatbot with CI/CD pipeline"
git branch -M main
git remote add origin https://github.com/FilResto/vertex-ai-chatbot.git
git push -u origin main
```

### 📁 **File creati/modificati:**
- `Dockerfile` - Configurazione container Docker
- `cloudbuild.yaml` - Pipeline CI/CD
- `.dockerignore` - File da escludere dal build
- `.gitignore` - File da escludere da Git

### 🔄 **Pipeline CI/CD:**
1. **Trigger**: Push su branch `main` di GitHub
2. **Build**: Crea immagine Docker
3. **Push**: Carica immagine su Artifact Registry
4. **Tag**: Marca con commit SHA e "latest"

### ⚠️ **Problemi risolti:**
- ❌ **Errore GCR**: `denied: gcr.io repo does not exist. Creating on push requires the artifactregistry.repositories.createOnPush permission`
- ✅ **Soluzione**: 
  1. Abilitato Artifact Registry API
  2. Creato repository Artifact Registry
  3. Modificato `cloudbuild.yaml` per usare Artifact Registry invece di GCR

### 🎛️ **Configurazione Trigger:**
- **Nome**: `vertex-ai-chatbot-trigger`
- **Evento**: Push su branch `main`
- **Repository**: `FilResto/vertex-ai-chatbot`
- **Configurazione**: `cloudbuild.yaml`

---

## ✅ **Step 4 - Deploy to Cloud Run** - COMPLETATO

### 🎯 **A cosa serve:**
Deployare l'applicazione come servizio serverless su Cloud Run per renderla accessibile pubblicamente.

### 🛠️ **Comandi utilizzati:**
```bash
# Abilitare Cloud Run API
gcloud services enable run.googleapis.com

# Aggiungere permessi Cloud Run a Cloud Build
gcloud projects add-iam-policy-binding tech-onboarding-470810 \
    --member="serviceAccount:483650106826-compute@developer.gserviceaccount.com" \
    --role="roles/run.admin"

# Testare deploy locale (opzionale)
docker build -t vertex-ai-chatbot .
docker run -p 8080:8080 vertex-ai-chatbot
```

### 📁 **File creati/modificati:**
- `cloudbuild.yaml` - Aggiunto step deploy su Cloud Run
- `app.py` - Configurazione porta dinamica per Cloud Run
- `Dockerfile` - Ottimizzato per Cloud Run

### 🌐 **Configurazione Cloud Run:**
- **Porta**: 8080 (configurata dinamicamente via variabile `PORT`)
- **Host**: `0.0.0.0` (per accettare connessioni esterne)
- **Regione**: `europe-west1`
- **Accesso**: Pubblico (`--allow-unauthenticated`)

### ⚠️ **Problemi risolti:**
- ❌ **Errore Porta**: `The user-provided container failed to start and listen on the port defined provided by the PORT=5000 environment variable`
- ✅ **Soluzione**: 
  1. Modificato app.py per usare variabile `PORT` di Cloud Run
  2. Cambiato porta default da 5000 a 8080
  3. Aggiunto `host='0.0.0.0'` per connessioni esterne

- ❌ **Errore Permessi**: `Permission 'run.services.get' denied`
- ✅ **Soluzione**: Aggiunto ruolo `roles/run.admin` al service account di Cloud Build

- ❌ **Errore Database**: Connessione fallita per IP non autorizzato
- ✅ **Soluzione**: Aggiunto `0.0.0.0/0` alle reti autorizzate di Cloud SQL

### 🔧 **Variabili d'Ambiente Cloud Run:**
```
PROJECT_ID=$PROJECT_ID
LOCATION=europe-west1
DB_HOST=$_DB_HOST
DB_USER=$_DB_USER
DB_PASSWORD=$_DB_PASSWORD
DB_NAME=$_DB_NAME
```

---

## 📊 **Riepilogo Progresso**

| Step | Status | Completamento | Descrizione |
|------|--------|---------------|-------------|
| 1. Vertex AI Agent | ✅ COMPLETATO | 100% | Chatbot con Gemini 2.5 Flash |
| 2. Cloud SQL MySQL | ✅ COMPLETATO | 100% | Salvataggio conversazioni |
| 3. CI/CD Pipeline | ✅ COMPLETATO | 100% | Build e deploy automatizzati |
| 4. Cloud Run Deploy | ✅ COMPLETATO | 100% | Servizio serverless pubblico |

**Progresso Totale: 100%** 🚀

---

## 🛠️ **Comandi di Manutenzione**

### Git:
```bash
# Aggiungere modifiche
git add .

# Committare modifiche
git commit -m "Descrizione delle modifiche"

# Pushare su GitHub
git push origin main

# Vedere status
git status
git log --oneline
```

### Google Cloud - Servizi:
```bash
# Abilitare API
gcloud services enable aiplatform.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com

# Verificare API abilitate
gcloud services list --enabled
```

### Google Cloud - Database:
```bash
# Connettere a Cloud SQL
gcloud sql connect [INSTANCE_NAME] --user=[USERNAME]

# Creare repository Artifact Registry
gcloud artifacts repositories create vertex-ai-chatbot \
    --repository-format=docker \
    --location=europe-west1
```

### Google Cloud - Permessi:
```bash
# Aggiungere permessi Cloud Run a Cloud Build
gcloud projects add-iam-policy-binding [PROJECT_ID] \
    --member="serviceAccount:[SERVICE_ACCOUNT]" \
    --role="roles/run.admin"

# Verificare permessi
gcloud projects get-iam-policy [PROJECT_ID]
```

### Test Locale:
```bash
# Installare dipendenze
pip install -r requirements.txt

# Avviare applicazione
python app.py
# Vai su http://localhost:8080

# Testare endpoint
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Che prodotto sviluppate?"}'

# Vedere cronologia
curl http://localhost:8080/history
```

### Docker (opzionale):
```bash
# Build immagine locale
docker build -t vertex-ai-chatbot .

# Eseguire container
docker run -p 8080:8080 vertex-ai-chatbot

# Vedere log
docker logs [CONTAINER_ID]
```

---

## 🔗 **Link Utili**

### Repository e Console:
- **GitHub Repository**: https://github.com/FilResto/vertex-ai-chatbot
- **Google Cloud Console**: https://console.cloud.google.com/
- **Cloud Build**: https://console.cloud.google.com/cloud-build
- **Artifact Registry**: https://console.cloud.google.com/artifacts
- **Cloud SQL**: https://console.cloud.google.com/sql
- **Cloud Run**: https://console.cloud.google.com/run

### Documentazione:
- **Vertex AI**: https://cloud.google.com/vertex-ai/docs
- **Cloud SQL**: https://cloud.google.com/sql/docs
- **Cloud Build**: https://cloud.google.com/build/docs
- **Cloud Run**: https://cloud.google.com/run/docs

---

## 🎯 **Endpoint API**

### POST `/chat`
Invia una domanda al chatbot:
```bash
curl -X POST https://[CLOUD_RUN_URL]/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Che prodotto sviluppate?"}'
```

### GET `/history`
Visualizza le ultime 20 conversazioni:
```bash
curl https://[CLOUD_RUN_URL]/history
```

### GET `/`
Interfaccia web del chatbot:
```
https://[CLOUD_RUN_URL]/
```

---

## 🚨 **Troubleshooting**

### Errore connessione database:
1. Verifica che MySQL sia attivo
2. Controlla username/password in `.env`
3. Verifica che il database esista
4. Controlla che l'IP pubblico sia accessibile (`0.0.0.0/0`)

### Errore Vertex AI:
1. Verifica che Vertex AI sia abilitato
2. Controlla le credenziali Google Cloud
3. Verifica la quota API

### Errore Cloud Build:
1. Verifica che le API siano abilitate
2. Controlla i permessi del service account
3. Verifica la configurazione del trigger

### Errore Cloud Run:
1. Verifica che la porta sia configurata correttamente
2. Controlla i log per errori specifici
3. Verifica le variabili d'ambiente

---

**Ultimo aggiornamento**: 2 Settembre 2025  
**Progetto**: Tech-Onboarding - Vertex AI Chatbot  
**Status**: ✅ COMPLETATO - Tutti e 4 gli step implementati con successo!

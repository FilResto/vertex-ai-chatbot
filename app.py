import os
import vertexai                           # Libreria per Google Vertex AI
from vertexai.generative_models import GenerativeModel  # Modello AI Gemini
from flask import Flask, request, jsonify # Flask per web server
from flask_cors import CORS               # Per permettere richieste da browser
from database import init_database, save_conversation, get_recent_conversations  # Funzioni database
from config import Config                 # Configurazioni (database, project ID, etc.)
from mcp_web_scraper import get_website_context  # MCP per consultare il sito web


# Inizializza Vertex AI
vertexai.init(project=Config.PROJECT_ID, location=Config.LOCATION) # Connessione a Google Cloud
model = GenerativeModel("gemini-2.5-flash") # Carica il modello AI Gemini

SYSTEM_PROMPT = """
1. Rispondi SOLO alle seguenti FAQ della startup tech o domande generali che si riferiscono a startup e che possono essere risposte con una frase delle seguenti:
   - "Che prodotto sviluppate?" → "Sviluppiamo soluzioni AI"
   - "Dove avete la sede?" → "Siamo una startup di Milano con team remoto"
   - "Come funziona il vostro prodotto?" → "Utilizziamo Vertex AI di Google"
   - "Chi può usare il prodotto?" → "Aziende che gestiscono grandi volumi di documenti"
   - "Quanto costa?" → "Offriamo piani personalizzati in base al numero delle richieste/volume dell'azienda"

2. Se l'utente chiede qualcosa NON nelle FAQ sopra, consulta il sito web Alomana per trovare informazioni aggiuntive.

3. Non inventare informazioni non presenti nelle FAQ o nel sito web.
"""
# Le istruzioni per l'AI:
    # - Risponde solo alle FAQ specifiche
    # - Se chiedi altro, dice "Mi dispiace, posso rispondere solo alle FAQ"
    # - Non inventa informazioni

app = Flask(__name__) # Crea l'applicazione Flask
CORS(app) # Permette richieste da browser (per l'interfaccia web)

@app.route('/chat', methods=['POST']) # Route per ricevere messaggi
def chat():
    try:
        user_message = request.json['message'] # Prende il messaggio dall'utente
        user_ip = request.remote_addr # Prende l'IP dell'utente
        
        print(f"Ricevuto messaggio: {user_message}")
        
        # Controlla se la domanda è nelle FAQ base
        faq_keywords = ['prodotto', 'sede', 'funziona', 'chi può', 'costo', 'quanto costa']
        is_faq = any(keyword in user_message.lower() for keyword in faq_keywords)
        
        # Se non è una FAQ base, consulta il sito web con MCP
        website_context = ""
        if not is_faq:
            print("Domanda non nelle FAQ base, consultando il sito web...")
            website_context = get_website_context(user_message)
            print(f"Contesto dal sito web: {website_context[:200]}...")
        
        # Chiama Vertex AI con il contesto del sito web
        full_prompt = f"{SYSTEM_PROMPT}\n\n"
        if website_context:
            full_prompt += f"Informazioni dal sito web Alomana:\n{website_context}\n\n"
        full_prompt += f"Utente: {user_message}\nAssistente:"
        
        print(f"Chiamando Vertex AI...")
        response = model.generate_content(full_prompt) # Genera la risposta dell'AI
        ai_response = response.text # Prende la risposta
        print(f"Risposta AI: {ai_response}")
        
        # 🔥 SALVA NEL DATABASE
        save_conversation(user_message, ai_response, user_ip) # Salva tutto nel database
        
        return jsonify({'response': ai_response}) # Restituisce la risposta in JSON
    
    except Exception as e:
        print(f"Errore nel chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Errore interno: {str(e)}'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    conversations = get_recent_conversations(20) # Prende le ultime 20 conversazioni
    return jsonify({'conversations': conversations}) # Le restituisce in JSON



@app.route('/', methods=['GET'])
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot FAQ Startup </title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background-color: #e3f2fd; text-align: right; }
            .ai { background-color: #f5f5f5; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; background-color: #2196f3; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #1976d2; }
        </style>
    </head>
    <body>
        <h1>🤖 Chatbot FAQ</h1>
        <div class="chat-container" id="chat">
            <div class="ai message">Ciao! Sono il chatbot della startup. Fammi una domanda sulle nostre FAQ!</div>
        </div>
        <form id="chatForm">
            <input type="text" id="messageInput" placeholder="Scrivi la tua domanda..." required>
            <button type="submit">Invia</button>
        </form>
        
        <script>
            const chatForm = document.getElementById('chatForm');
            const messageInput = document.getElementById('messageInput');
            const chat = document.getElementById('chat');
            
            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const message = messageInput.value;
                if (!message) return;
                
                // Aggiungi messaggio utente
                chat.innerHTML += `<div class="user message">${message}</div>`;
                messageInput.value = '';
                chat.scrollTop = chat.scrollHeight;
                
                // Invia a AI
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    const data = await response.json();
                    
                    // Aggiungi risposta AI
                    chat.innerHTML += `<div class="ai message">${data.response}</div>`;
                    chat.scrollTop = chat.scrollHeight;
                } catch (error) {
                    chat.innerHTML += `<div class="ai message">Errore: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    try:
        # Inizializza database all'avvio
        print("Inizializzazione database...")
        init_database() # Inizializza il database
        print("Database inizializzato!")
        
        # Usa la porta da variabile d'ambiente (Cloud Run) o default 8080 (locale)
        port = int(os.environ.get('PORT', 8080))
        print(f"Backend Flask avviato su porta {port}")
        app.run(debug=False, host='0.0.0.0', port=port) # Avvia il server Flask
    except Exception as e:
        print(f"Errore durante l'avvio: {e}")
        import traceback
        traceback.print_exc()
        raise
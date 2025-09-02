import os
import logging
import vertexai
from vertexai.generative_models import GenerativeModel
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_database, save_conversation, get_recent_conversations
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Inizializza Vertex AI
try:
    vertexai.init(project=Config.PROJECT_ID, location=Config.LOCATION)
    model = GenerativeModel("gemini-2.0-flash-exp")
    logger.info("Vertex AI inizializzato correttamente")
except Exception as e:
    logger.error(f"Errore inizializzazione Vertex AI: {e}")
    raise

SYSTEM_PROMPT = """
1. Rispondi SOLO alle seguenti FAQ della startup tech:
   - "Che prodotto sviluppate?" → "Sviluppiamo soluzioni AI"
   - "Dove avete la sede?" → "Siamo una startup di Milano con team remoto"
   - "Come funziona il vostro prodotto?" → "Utilizziamo Vertex AI di Google"
   - "Chi può usare il prodotto?" → "Aziende che gestiscono grandi volumi di documenti"
   - "Quanto costa?" → "Offriamo piani personalizzati in base al numero delle richieste/volume dell'azienda"

2. Se l'utente chiede qualcosa NON nelle FAQ sopra, rispondi:
   "Mi dispiace, posso rispondere solo alle FAQ aziendali."

3. Non inventare informazioni non presenti nelle FAQ sopra.
"""

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json['message']
        user_ip = request.remote_addr
        
        # Chiama Vertex AI
        full_prompt = f"{SYSTEM_PROMPT}\n\nUtente: {user_message}\nAssistente:"
        response = model.generate_content(full_prompt)
        ai_response = response.text
        
        # Salva nel database
        save_conversation(user_message, ai_response, user_ip)
        
        return jsonify({'response': ai_response})
    
    except Exception as e:
        logger.error(f"Errore in /chat: {e}")
        return jsonify({'error': 'Errore interno del server'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        conversations = get_recent_conversations(20)
        return jsonify({'conversations': conversations})
    except Exception as e:
        logger.error(f"Errore in /history: {e}")
        return jsonify({'error': 'Errore nel recupero cronologia'}), 500

@app.route('/', methods=['GET'])
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot FAQ Startup</title>
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
                
                chat.innerHTML += `<div class="user message">${message}</div>`;
                messageInput.value = '';
                chat.scrollTop = chat.scrollHeight;
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    const data = await response.json();
                    
                    if (data.error) {
                        chat.innerHTML += `<div class="ai message">Errore: ${data.error}</div>`;
                    } else {
                        chat.innerHTML += `<div class="ai message">${data.response}</div>`;
                    }
                    chat.scrollTop = chat.scrollHeight;
                } catch (error) {
                    chat.innerHTML += `<div class="ai message">Errore di connessione: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    try:
        # Inizializza database
        init_database()
        logger.info("Database inizializzato!")
        
        # Porta da environment o default
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Avvio server su porta {port}")
        
        # IMPORTANTE: debug=False in produzione!
        app.run(debug=False, host='0.0.0.0', port=port)
        
    except Exception as e:
        logger.error(f"Errore fatale all'avvio: {e}")
        raise
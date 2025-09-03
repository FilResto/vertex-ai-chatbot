import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional

class MCPWebScraper:
    """
    Model Context Protocol - Web Scraper per estrarre informazioni dal sito web
    """
    
    def __init__(self, website_url: str = "https://skillcurb.com/ai_app_locator/alomana/"):
        self.website_url = website_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_website_content(self) -> Optional[str]:
        """
        Scarica il contenuto del sito web
        """
        try:
            print(f"Scaricando contenuto da: {self.website_url}")
            response = self.session.get(self.website_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Rimuovi script e style
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Estrai testo
            text = soup.get_text()
            
            # Pulisci il testo
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            print(f"Contenuto scaricato: {len(text)} caratteri")
            return text
            
        except Exception as e:
            print(f"Errore nel scaricare il sito web: {e}")
            return None
    
    def extract_key_information(self, content: str) -> Dict[str, str]:
        """
        Estrae informazioni chiave dal contenuto del sito
        """
        info = {}
        
        # Cerca informazioni sulla startup
        startup_patterns = {
            'company_name': r'(?i)(alomana|startup|azienda|company)',
            'services': r'(?i)(servizi|services|soluzioni|solutions)',
            'ai_services': r'(?i)(ai|artificial intelligence|intelligenza artificiale)',
            'location': r'(?i)(milano|italy|sede|headquarters)',
            'contact': r'(?i)(contatti|contact|email|telefono)'
        }
        
        for key, pattern in startup_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                info[key] = ', '.join(set(matches))
        
        # Estrai paragrafi rilevanti
        sentences = content.split('.')
        relevant_sentences = []
        
        keywords = ['alomana', 'startup', 'ai', 'servizi', 'soluzioni', 'milano', 'tecnologia']
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                if len(sentence.strip()) > 20:  # Filtra frasi troppo corte
                    relevant_sentences.append(sentence.strip())
        
        info['relevant_content'] = '. '.join(relevant_sentences[:5])  # Prime 5 frasi rilevanti
        
        return info
    
    def get_fallback_info(self, query: str) -> str:
        """
        Informazioni di fallback quando il sito web non è accessibile
        """
        query_lower = query.lower()
        
        # Informazioni generali su Alomana basate su quello che sappiamo
        fallback_info = {
            'servizi': 'Alomana è una startup che sviluppa soluzioni AI innovative per aziende',
            'tecnologia': 'Utilizziamo tecnologie all\'avanguardia come Vertex AI di Google',
            'ubicazione': 'Siamo una startup con sede a Milano e team distribuito',
            'target': 'Rivolgiamo i nostri servizi ad aziende che gestiscono grandi volumi di dati',
            'ai': 'Specializzati in intelligenza artificiale e machine learning',
            'startup': 'Alomana è una startup tech innovativa nel settore AI'
        }
        
        # Cerca corrispondenze con la query
        relevant_info = []
        for key, value in fallback_info.items():
            if any(word in query_lower for word in key.split()) or any(word in query_lower for word in value.lower().split()):
                relevant_info.append(value)
        
        if relevant_info:
            return f"Informazioni su Alomana: {' '.join(relevant_info)}"
        else:
            return "Alomana è una startup tech che sviluppa soluzioni AI innovative per aziende, con sede a Milano."

    def search_website_for_query(self, query: str) -> str:
        """
        Cerca informazioni specifiche nel sito web basandosi sulla query
        """
        content = self.get_website_content()
        if not content:
            print("Sito web non accessibile, usando informazioni di fallback...")
            return self.get_fallback_info(query)
        
        # Estrai informazioni chiave
        info = self.extract_key_information(content)
        
        # Cerca corrispondenze con la query
        query_lower = query.lower()
        relevant_info = []
        
        for key, value in info.items():
            if any(word in value.lower() for word in query_lower.split()):
                relevant_info.append(f"{key}: {value}")
        
        if relevant_info:
            return f"Informazioni dal sito web Alomana:\n" + "\n".join(relevant_info)
        else:
            # Ritorna informazioni generali se non trova corrispondenze specifiche
            general_info = []
            if info.get('relevant_content'):
                general_info.append(f"Contenuto rilevante: {info['relevant_content']}")
            if info.get('services'):
                general_info.append(f"Servizi: {info['services']}")
            
            if general_info:
                return f"Informazioni generali dal sito web Alomana:\n" + "\n".join(general_info)
            else:
                return self.get_fallback_info(query)

def get_website_context(query: str) -> str:
    """
    Funzione principale per ottenere contesto dal sito web
    """
    scraper = MCPWebScraper()
    return scraper.search_website_for_query(query)

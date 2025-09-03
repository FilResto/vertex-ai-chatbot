import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional

class MCPWebScraper:
    """
    Model Context Protocol - Web Scraper per estrarre informazioni dal sito web
    """
    
    def __init__(self, base_url: str = "https://alomana.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Configurazione route specifiche di Alomana
        self.routes_config = {
            'home': {
                'url': '/',
                'keywords': ['generale', 'home', 'informazioni', 'descrizione', 'chi siete']
            },
            'pricing': {
                'url': '/pricing',
                'keywords': ['prezzo', 'costo', 'quanto costa', 'pricing', 'piano', 'abbonamento', 'tariffe', 'prezzi']
            },
            'company': {
                'url': '/company', 
                'keywords': ['azienda', 'chi siete', 'storia', 'team', 'fondatori', 'company', 'about', 'mission']
            },
            'blog': {
                'url': '/blog',
                'keywords': ['blog', 'articoli', 'news', 'notizie', 'aggiornamenti', 'post', 'contenuti']
            },
            'careers': {
                'url': '/careers',
                'keywords': ['lavoro', 'carriere', 'assunzioni', 'posizioni', 'jobs', 'careers', 'opportunità', 'hiring']
            },
            'contact': {
                'url': '/contact',
                'keywords': ['contatti', 'email', 'telefono', 'indirizzo', 'contact', 'sede', 'ufficio']
            }
        }
        
        # Cache per evitare richieste duplicate
        self.content_cache = {}
    
    def detect_relevant_routes(self, query: str) -> List[str]:
        """
        Determina quali route consultare basandosi sulla query
        """
        query_lower = query.lower()
        relevant_routes = []
        
        for route, config in self.routes_config.items():
            if any(keyword in query_lower for keyword in config['keywords']):
                relevant_routes.append(route)
        
        # Se non trova match specifici, usa home come default
        if not relevant_routes:
            relevant_routes.append('home')
        
        return relevant_routes
    
    def get_route_content(self, route: str) -> Optional[str]:
        """
        Scarica il contenuto di una route specifica
        """
        if route not in self.routes_config:
            print(f"Route '{route}' non configurata")
            return None
        
        # Controlla cache
        if route in self.content_cache:
            print(f"Usando contenuto cached per route: {route}")
            return self.content_cache[route]
        
        route_url = f"{self.base_url}{self.routes_config[route]['url']}"
        
        try:
            print(f"Scaricando contenuto da: {route_url}")
            response = self.session.get(route_url, timeout=10)
            
            if response.status_code == 403:
                print(f"403 Forbidden per {route_url}")
                return None
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Rimuovi script e style
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Estrai testo
            text = soup.get_text()
            
            # Pulisci il testo
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Cache il risultato
            self.content_cache[route] = clean_text
            print(f"Contenuto scaricato da {route}: {len(clean_text)} caratteri")
            return clean_text
            
        except Exception as e:
            print(f"Errore nel scaricare {route_url}: {e}")
            return None
    
    def extract_key_information(self, content: str, route: str) -> Dict[str, str]:
        """
        Estrae informazioni chiave dal contenuto basandosi sulla route
        """
        info = {}
        
        # Pattern specifici per route
        if route == 'pricing':
            pricing_patterns = {
                'plans': r'(?i)(piano|plan|package|tier)\s+([a-zA-Z0-9\s]+)',
                'prices': r'(?i)[\€\$]?\s*\d+[\.,]?\d*\s*(?:euro|€|\$|al mese|month|anno|year)',
                'features': r'(?i)(incluso|include|feature|caratteristica)[:]\s*([^\.]+)'
            }
            for key, pattern in pricing_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    info[key] = [match[1] if isinstance(match, tuple) else match for match in matches[:5]]
        
        elif route == 'company':
            company_patterns = {
                'team_info': r'(?i)(fondatore|founder|ceo|team|staff)[:]\s*([^\.]+)',
                'mission': r'(?i)(mission|missione|obiettivo|goal)[:]\s*([^\.]+)',
                'history': r'(?i)(storia|fondat|nasce|history|started)([^\.]+)'
            }
            for key, pattern in company_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    info[key] = [match[1] if isinstance(match, tuple) else match for match in matches[:3]]
        
        elif route == 'careers':
            career_patterns = {
                'positions': r'(?i)(posizione|position|job|lavoro)[:]\s*([^\.]+)',
                'requirements': r'(?i)(richiesto|required|requisiti)[:]\s*([^\.]+)',
                'benefits': r'(?i)(benefit|vantaggi|offriamo)[:]\s*([^\.]+)'
            }
            for key, pattern in career_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    info[key] = [match[1] if isinstance(match, tuple) else match for match in matches[:3]]
        
        elif route == 'contact':
            contact_patterns = {
                'email': r'(?i)([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                'phone': r'(?i)(\+?\d{1,3}[\s\-]?\d{2,3}[\s\-]?\d{3,4}[\s\-]?\d{3,4})',
                'address': r'(?i)(via|address|indirizzo)[:]\s*([^\.]+)'
            }
            for key, pattern in contact_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    info[key] = list(set(matches[:3]))  # Rimuovi duplicati
        
        elif route == 'blog':
            # Per il blog, estrai titoli e date recenti
            blog_patterns = {
                'recent_posts': r'(?i)(articolo|post|blog)[:]\s*([^\.]+)',
                'topics': r'(?i)(ai|artificial intelligence|machine learning|startup|tech)([^\.]*)'
            }
            for key, pattern in blog_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    info[key] = [match[1] if isinstance(match, tuple) else match for match in matches[:5]]
        
        # Pattern generici per tutte le route
        general_patterns = {
            'alomana_mentions': r'(?i)(alomana)([^\.]*)',
            'ai_services': r'(?i)(ai|artificial intelligence|intelligenza artificiale)([^\.]*)',
            'solutions': r'(?i)(soluzione|solution|servizio|service)([^\.]*)'
        }
        
        for key, pattern in general_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                info[key] = [match[1] if isinstance(match, tuple) else match for match in matches[:3]]
        
        return info
    
    def get_fallback_info(self, query: str, route: str = 'general') -> str:
        """
        Informazioni di fallback specifiche per route quando il sito web non è accessibile
        """
        query_lower = query.lower()
        
        route_fallbacks = {
            'pricing': {
                'default': 'Offriamo piani personalizzati in base al numero delle richieste/volume dell\'azienda. Contattaci per un preventivo su misura.',
                'keywords': ['prezzo', 'costo', 'piano', 'pricing']
            },
            'company': {
                'default': 'Alomana è una startup tech innovativa di Milano specializzata in soluzioni AI. Il nostro team sviluppa tecnologie all\'avanguardia per aziende.',
                'keywords': ['azienda', 'team', 'storia', 'mission']
            },
            'careers': {
                'default': 'Alomana è sempre alla ricerca di talenti nel settore AI e tech. Siamo una startup in crescita con sede a Milano.',
                'keywords': ['lavoro', 'carriere', 'posizioni']
            },
            'contact': {
                'default': 'Alomana ha sede a Milano con team distribuito. Contattaci tramite il nostro sito web per informazioni specifiche.',
                'keywords': ['contatti', 'sede', 'email']
            },
            'blog': {
                'default': 'Il nostro blog copre argomenti su AI, startup, tecnologia e innovazione nel settore tech.',
                'keywords': ['blog', 'articoli', 'news']
            },
            'general': {
                'default': 'Alomana è una startup tech che sviluppa soluzioni AI innovative per aziende che gestiscono grandi volumi di documenti, con sede a Milano.',
                'keywords': []
            }
        }
        
        # Cerca fallback più specifico basato sulla route rilevata
        for route_name, fallback_config in route_fallbacks.items():
            if route_name != 'general' and any(keyword in query_lower for keyword in fallback_config['keywords']):
                return f"[FALLBACK - {route_name.upper()}] {fallback_config['default']}"
        
        # Fallback generale
        return f"[FALLBACK] {route_fallbacks['general']['default']}"
    
    def search_website_for_query(self, query: str) -> str:
        """
        Cerca informazioni specifiche consultando le route rilevanti
        """
        # Determina quali route consultare
        relevant_routes = self.detect_relevant_routes(query)
        print(f"Query: '{query}' → Routes da consultare: {relevant_routes}")
        
        all_extracted_info = {}
        successful_routes = []
        
        # Consulta ogni route rilevante
        for route in relevant_routes:
            content = self.get_route_content(route)
            if content:
                extracted_info = self.extract_key_information(content, route)
                if extracted_info:
                    all_extracted_info[route] = extracted_info
                    successful_routes.append(route)
        
        # Se nessuna route è accessibile, usa fallback
        if not successful_routes:
            print("Nessuna route accessibile, usando informazioni di fallback...")
            primary_route = relevant_routes[0] if relevant_routes else 'general'
            return self.get_fallback_info(query, primary_route)
        
        # Formatta risposta dalle route consultate
        return self.format_multi_route_response(query, all_extracted_info, successful_routes)
    
    def format_multi_route_response(self, query: str, data: Dict, routes: List[str]) -> str:
        """
        Formatta la risposta basandosi sui dati estratti dalle multiple route
        """
        response_parts = []
        
        for route in routes:
            route_data = data.get(route, {})
            
            if route == 'pricing' and route_data:
                pricing_info = []
                if 'plans' in route_data:
                    pricing_info.append(f"Piani: {', '.join(route_data['plans'][:3])}")
                if 'prices' in route_data:
                    pricing_info.append(f"Prezzi: {', '.join(route_data['prices'][:3])}")
                if pricing_info:
                    response_parts.append(f"PRICING: {' | '.join(pricing_info)}")
            
            elif route == 'company' and route_data:
                company_info = []
                if 'team_info' in route_data:
                    company_info.append(f"Team: {', '.join(route_data['team_info'][:2])}")
                if 'mission' in route_data:
                    company_info.append(f"Mission: {', '.join(route_data['mission'][:1])}")
                if company_info:
                    response_parts.append(f"COMPANY: {' | '.join(company_info)}")
            
            elif route == 'careers' and route_data:
                career_info = []
                if 'positions' in route_data:
                    career_info.append(f"Posizioni: {', '.join(route_data['positions'][:2])}")
                if 'benefits' in route_data:
                    career_info.append(f"Benefici: {', '.join(route_data['benefits'][:2])}")
                if career_info:
                    response_parts.append(f"CAREERS: {' | '.join(career_info)}")
            
            elif route == 'contact' and route_data:
                contact_info = []
                if 'email' in route_data:
                    contact_info.append(f"Email: {route_data['email'][0]}")
                if 'phone' in route_data:
                    contact_info.append(f"Tel: {route_data['phone'][0]}")
                if 'address' in route_data:
                    contact_info.append(f"Indirizzo: {route_data['address'][0]}")
                if contact_info:
                    response_parts.append(f"CONTACT: {' | '.join(contact_info)}")
            
            elif route == 'blog' and route_data:
                blog_info = []
                if 'recent_posts' in route_data:
                    blog_info.append(f"Post recenti: {', '.join(route_data['recent_posts'][:2])}")
                if 'topics' in route_data:
                    blog_info.append(f"Argomenti: {', '.join(route_data['topics'][:3])}")
                if blog_info:
                    response_parts.append(f"BLOG: {' | '.join(blog_info)}")
            
            # Aggiungi sempre informazioni generali su Alomana se trovate
            if 'alomana_mentions' in route_data:
                response_parts.append(f"Info Alomana: {route_data['alomana_mentions'][0][:150]}...")
        
        if response_parts:
            return f"[WEBSITE] " + " || ".join(response_parts)
        else:
            # Se non riesce a estrarre info significative, usa fallback
            primary_route = routes[0] if routes else 'general'
            return self.get_fallback_info(query, primary_route)
    
    def get_website_content(self) -> Optional[str]:
        """
        Metodo legacy - ora usa get_route_content('home')
        """
        return self.get_route_content('home')
    
    def extract_key_information(self, content: str, route: str = 'home') -> Dict[str, List[str]]:
        """
        Versione aggiornata che usa il nuovo sistema di estrazione
        """
        return self.extract_key_information(content, route)

def get_website_context(query: str) -> str:
    """
    Funzione principale per ottenere contesto dal sito web - ora con multiple route
    """
    scraper = MCPWebScraper()
    return scraper.search_website_for_query(query)
"""
Secure Configuration Management for A2A Communication
Gestisce le credenziali in modo sicuro usando Google Cloud IAM
"""

import os
from google.cloud import secretmanager
from google.auth import default
from typing import Optional

class SecureConfig:
    """
    Classe per gestire le configurazioni in modo sicuro
    Usa Google Cloud Secret Manager e autenticazione automatica
    """
    
    def __init__(self):
        self.project_id = os.environ.get('PROJECT_ID', 'tech-onboarding-470810')
        self.location = os.environ.get('LOCATION', 'europe-west1')
        self._secrets_client = None
    
    def get_secret_client(self):
        """Inizializza il client per Secret Manager"""
        if not self._secrets_client:
            try:
                self._secrets_client = secretmanager.SecretManagerServiceClient()
            except Exception as e:
                print(f"Errore nell'inizializzazione Secret Manager: {e}")
                print("Usando variabili d'ambiente come fallback...")
        return self._secrets_client
    
    def get_secret(self, secret_name: str, fallback_env_var: str) -> str:
        """
        Recupera un segreto da Secret Manager o usa variabile d'ambiente come fallback
        
        Args:
            secret_name: Nome del segreto in Secret Manager
            fallback_env_var: Nome della variabile d'ambiente di fallback
            
        Returns:
            Valore del segreto o della variabile d'ambiente
        """
        try:
            client = self.get_secret_client()
            if client:
                secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                response = client.access_secret_version(request={"name": secret_path})
                return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Errore nel recupero del segreto {secret_name}: {e}")
            print(f"Usando variabile d'ambiente {fallback_env_var} come fallback...")
        
        # Fallback alle variabili d'ambiente
        return os.environ.get(fallback_env_var, "")
    
    @property
    def db_host(self) -> str:
        """Host del database Cloud SQL"""
        return self.get_secret("db-host", "DB_HOST")
    
    @property
    def db_user(self) -> str:
        """Username del database"""
        return self.get_secret("db-user", "DB_USER")
    
    @property
    def db_password(self) -> str:
        """Password del database"""
        return self.get_secret("db-password", "DB_PASSWORD")
    
    @property
    def db_name(self) -> str:
        """Nome del database"""
        return self.get_secret("db-name", "DB_NAME")
    
    def get_database_config(self) -> dict:
        """Restituisce la configurazione del database"""
        return {
            'host': self.db_host,
            'user': self.db_user,
            'password': self.db_password,
            'database': self.db_name
        }
    
    def verify_authentication(self) -> bool:
        """
        Verifica che l'autenticazione A2A funzioni correttamente
        
        Returns:
            True se l'autenticazione è valida, False altrimenti
        """
        try:
            # Prova a ottenere le credenziali di default
            credentials, project = default()
            print(f"✅ Autenticazione A2A verificata per progetto: {project}")
            return True
        except Exception as e:
            print(f"❌ Errore nell'autenticazione A2A: {e}")
            return False

# Istanza globale per l'uso nell'applicazione
secure_config = SecureConfig()

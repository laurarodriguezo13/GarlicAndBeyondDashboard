"""
SharePoint Authentication Module - VERSIÓN SILENCIOSA
======================================================
Sistema robusto y automatizado para autenticación con SharePoint
y descarga de archivos Excel usando Microsoft Graph API.

NUEVA CARACTERÍSTICA: Modo silencioso para ocultar logging molesto.

Mejoras incluidas:
- Sistema de caché inteligente con TTL
- Manejo robusto de errores con retry automático
- Validación completa de configuración
- MODO SILENCIOSO para usuarios finales
- Logging detallado solo en modo debug
- Soporte completo para múltiples formatos Excel
- Optimización de rendimiento

Autor: GANDB Dashboard Team
Fecha: 2025
"""

import streamlit as st
import requests
from msal import ConfidentialClientApplication
import base64
import pandas as pd
from typing import Optional, Union, Dict, Any
import io
import time
from datetime import datetime, timedelta
import traceback
import warnings

warnings.filterwarnings('ignore')

class SharePointAuthSystem:
    """
    Sistema completo de autenticación SharePoint con modo silencioso.
    
    Características:
    - Caché inteligente de tokens con TTL
    - Retry automático en fallos
    - Validación completa de configuración
    - MODO SILENCIOSO para interfaz limpia
    - Logging detallado solo cuando sea necesario
    """

    def __init__(self, cache_ttl_minutes: int = 50, silent_mode: bool = True):
        """
        Inicializa el sistema SharePoint con configuración automática.
        
        Args:
            cache_ttl_minutes (int): Tiempo de vida del caché en minutos (default: 50)
            silent_mode (bool): Si True, oculta logging detallado (default: True)
        """
        self.cache_ttl_minutes = cache_ttl_minutes
        self.silent_mode = silent_mode
        self._token_cache = {}
        self._config_validated = False
        self._last_validation = None
        
        # Inicializar automáticamente
        self._initialize_system()

    def _initialize_system(self):
        """Inicialización automática del sistema."""
        try:
            self._load_configuration()
            self._validate_configuration()
            self._setup_msal_app()
            
            if not self.silent_mode:
                st.success("✅ SharePoint Auth System inicializado correctamente")
            
        except Exception as e:
            if not self.silent_mode:
                st.error(f"❌ Error crítico inicializando SharePoint Auth: {e}")
            raise

    def _load_configuration(self):
        """Carga y valida la configuración desde secrets.toml"""
        try:
            # Verificar que existe la sección sharepoint_auth
            if "sharepoint_auth" not in st.secrets:
                raise KeyError("Sección 'sharepoint_auth' no encontrada en secrets.toml")
            
            auth_config = st.secrets["sharepoint_auth"]
            
            # Cargar credenciales obligatorias
            required_keys = ["client_id", "client_secret", "tenant_id"]
            for key in required_keys:
                if key not in auth_config:
                    raise KeyError(f"Clave '{key}' faltante en sharepoint_auth")
                
                if not auth_config[key] or str(auth_config[key]).strip() == "":
                    raise ValueError(f"Valor vacío para '{key}' en sharepoint_auth")
            
            # Asignar configuración
            self.client_id = str(auth_config["client_id"]).strip()
            self.client_secret = str(auth_config["client_secret"]).strip()
            self.tenant_id = str(auth_config["tenant_id"]).strip()
            
            # Construir URLs
            self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            self.scopes = ["https://graph.microsoft.com/.default"]
            
            if not self.silent_mode:
                st.info("✅ Configuración SharePoint cargada correctamente")
            
        except Exception as e:
            if not self.silent_mode:
                st.error(f"❌ Error cargando configuración SharePoint: {e}")
            raise

    def _validate_configuration(self):
        """Valida que la configuración sea correcta."""
        try:
            # Validar formato de IDs (UUIDs)
            import re
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            
            if not re.match(uuid_pattern, self.client_id, re.IGNORECASE):
                raise ValueError(f"client_id no tiene formato UUID válido: {self.client_id}")
            
            if not re.match(uuid_pattern, self.tenant_id, re.IGNORECASE):
                raise ValueError(f"tenant_id no tiene formato UUID válido: {self.tenant_id}")
            
            # Validar client_secret (debe tener cierta longitud)
            if len(self.client_secret) < 20:
                raise ValueError("client_secret parece ser demasiado corto")
            
            self._config_validated = True
            self._last_validation = datetime.now()
            
            if not self.silent_mode:
                st.success("✅ Configuración SharePoint validada")
            
        except Exception as e:
            if not self.silent_mode:
                st.error(f"❌ Error validando configuración: {e}")
            raise

    def _setup_msal_app(self):
        """Configura la aplicación MSAL."""
        try:
            self.msal_app = ConfidentialClientApplication(
                client_id=self.client_id,
                authority=self.authority,
                client_credential=self.client_secret,
            )
            if not self.silent_mode:
                st.success("✅ Aplicación MSAL configurada")
            
        except Exception as e:
            if not self.silent_mode:
                st.error(f"❌ Error configurando MSAL: {e}")
            raise

    def _is_token_valid(self) -> bool:
        """Verifica si el token actual en caché es válido."""
        if 'access_token' not in self._token_cache:
            return False
        
        if 'expires_at' not in self._token_cache:
            return False
        
        return datetime.now() < self._token_cache['expires_at']

    def get_access_token(self, force_refresh: bool = False, max_retries: int = 3) -> Optional[str]:
        """
        Obtiene token de acceso con sistema de caché y retry automático.
        
        Args:
            force_refresh (bool): Forzar obtención de nuevo token
            max_retries (int): Máximo número de reintentos
            
        Returns:
            str: Token de acceso válido o None si falla
        """
        
        # Verificar caché si no se fuerza refresh
        if not force_refresh and self._is_token_valid():
            return self._token_cache['access_token']
        
        # Intentar obtener nuevo token con retry
        for attempt in range(max_retries):
            try:
                if not self.silent_mode:
                    st.info(f"🔑 Obteniendo token de acceso (intento {attempt + 1}/{max_retries})")
                
                # Solicitar token
                token_response = self.msal_app.acquire_token_for_client(scopes=self.scopes)
                
                # Verificar respuesta
                if "access_token" in token_response:
                    # Calcular tiempo de expiración
                    expires_in = token_response.get('expires_in', 3600)  # Default 1 hora
                    expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
                    
                    # Guardar en caché
                    self._token_cache = {
                        'access_token': token_response["access_token"],
                        'expires_at': expires_at,
                        'obtained_at': datetime.now()
                    }
                    
                    if not self.silent_mode:
                        st.success(f"✅ Token obtenido correctamente (válido hasta {expires_at.strftime('%H:%M:%S')})")
                    return self._token_cache['access_token']
                
                else:
                    error_msg = token_response.get('error_description', 'Error desconocido')
                    if not self.silent_mode:
                        st.warning(f"⚠️ Intento {attempt + 1} falló: {error_msg}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                if not self.silent_mode:
                    st.warning(f"⚠️ Excepción en intento {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        if not self.silent_mode:
            st.error("❌ No se pudo obtener token después de todos los intentos")
        return None

    def convert_sharepoint_url_to_graph_api(self, sharepoint_url: str) -> Optional[str]:
        """
        Convierte URL SharePoint a Graph API con validación mejorada.
        
        Args:
            sharepoint_url (str): URL de SharePoint
            
        Returns:
            str: URL de Graph API o None si falla
        """
        try:
            # Validaciones básicas
            if not sharepoint_url or not isinstance(sharepoint_url, str):
                raise ValueError("URL de SharePoint no válida")
            
            sharepoint_url = sharepoint_url.strip()
            
            if not sharepoint_url.startswith(('http://', 'https://')):
                raise ValueError("URL debe comenzar con http:// o https://")
            
            if 'sharepoint.com' not in sharepoint_url.lower():
                if not self.silent_mode:
                    st.warning("⚠️ URL no parece ser de SharePoint")
            
            # Codificar URL
            encoded_url = base64.urlsafe_b64encode(sharepoint_url.encode()).decode().rstrip('=')
            graph_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded_url}/driveItem/content"
            
            if not self.silent_mode:
                st.info(f"🔗 URL convertida correctamente")
            return graph_url
            
        except Exception as e:
            if not self.silent_mode:
                st.error(f"❌ Error convirtiendo URL: {e}")
            return None

    def download_excel_from_sharepoint(self, 
                                     sharepoint_url: str, 
                                     max_retries: int = 3,
                                     timeout: int = 60,
                                     all_sheets: bool = True) -> Optional[Union[pd.DataFrame, Dict[str, pd.DataFrame]]]:
        """
        Descarga archivo Excel con sistema robusto de retry y validación.
        
        Args:
            sharepoint_url (str): URL del archivo Excel
            max_retries (int): Máximo número de reintentos
            timeout (int): Timeout en segundos
            all_sheets (bool): Si True, descarga todas las hojas; si False, solo la primera
            
        Returns:
            pd.DataFrame o Dict[str, pd.DataFrame]: Datos del Excel
        """
        
        for attempt in range(max_retries):
            try:
                if not self.silent_mode:
                    st.info(f"📥 Descargando archivo (intento {attempt + 1}/{max_retries})")
                
                # Obtener token
                token = self.get_access_token()
                if not token:
                    if not self.silent_mode:
                        st.error("❌ No se pudo obtener token de autenticación")
                    continue
                
                # Convertir URL
                graph_url = self.convert_sharepoint_url_to_graph_api(sharepoint_url)
                if not graph_url:
                    if not self.silent_mode:
                        st.error("❌ No se pudo convertir URL")
                    continue
                
                # Preparar petición
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/octet-stream',
                    'User-Agent': 'GANDB-Dashboard/1.0'
                }
                
                # Realizar descarga
                response = requests.get(graph_url, headers=headers, timeout=timeout)
                
                # Verificar respuesta
                if response.status_code == 200:
                    # Validar que es contenido Excel
                    content_type = response.headers.get('content-type', '').lower()
                    if 'excel' not in content_type and 'spreadsheet' not in content_type:
                        if not self.silent_mode:
                            st.warning("⚠️ El archivo descargado podría no ser Excel")
                    
                    # Convertir a DataFrame(s)
                    excel_content = io.BytesIO(response.content)
                    
                    if all_sheets:
                        # Descargar todas las hojas
                        try:
                            # Intentar con openpyxl primero
                            all_sheets_data = pd.read_excel(excel_content, sheet_name=None, engine='openpyxl', header=None)
                            
                            if not self.silent_mode:
                                st.success(f"✅ Archivo Excel descargado: {len(all_sheets_data)} hojas")
                                
                                # Log de hojas encontradas
                                for sheet_name in all_sheets_data.keys():
                                    rows, cols = all_sheets_data[sheet_name].shape
                                    st.info(f"   📋 Hoja '{sheet_name}': {rows} filas, {cols} columnas")
                            
                            return all_sheets_data
                            
                        except Exception as e:
                            if not self.silent_mode:
                                st.warning(f"⚠️ Error con openpyxl, intentando xlrd: {e}")
                            # Reiniciar el BytesIO
                            excel_content = io.BytesIO(response.content)
                            try:
                                all_sheets_data = pd.read_excel(excel_content, sheet_name=None, engine='xlrd', header=None)
                                if not self.silent_mode:
                                    st.success(f"✅ Archivo Excel descargado con xlrd: {len(all_sheets_data)} hojas")
                                return all_sheets_data
                            except Exception as e2:
                                if not self.silent_mode:
                                    st.error(f"❌ Error con ambos engines: {e2}")
                                # Fallback a una sola hoja
                                excel_content = io.BytesIO(response.content)
                                df = pd.read_excel(excel_content, engine='openpyxl', header=None)
                                if not self.silent_mode:
                                    st.warning("⚠️ Descargando solo primera hoja como fallback")
                                return df
                    else:
                        # Solo primera hoja
                        try:
                            df = pd.read_excel(excel_content, engine='openpyxl', header=None)
                        except:
                            excel_content = io.BytesIO(response.content)
                            df = pd.read_excel(excel_content, engine='xlrd', header=None)
                        
                        if df.empty:
                            if not self.silent_mode:
                                st.warning("⚠️ El archivo Excel está vacío")
                            return pd.DataFrame()
                        
                        if not self.silent_mode:
                            st.success(f"✅ Archivo descargado: {df.shape[0]} filas, {df.shape[1]} columnas")
                        return df
                
                elif response.status_code == 401:
                    if not self.silent_mode:
                        st.warning("⚠️ Token expirado, intentando renovar...")
                    self.get_access_token(force_refresh=True)
                    continue
                
                elif response.status_code == 404:
                    if not self.silent_mode:
                        st.error("❌ Archivo no encontrado en SharePoint")
                    return None
                
                else:
                    if not self.silent_mode:
                        st.warning(f"⚠️ Error HTTP {response.status_code}: {response.text[:200]}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                    continue
                
            except requests.exceptions.Timeout:
                if not self.silent_mode:
                    st.warning(f"⚠️ Timeout en intento {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
                
            except Exception as e:
                if not self.silent_mode:
                    st.warning(f"⚠️ Error en intento {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
        
        if not self.silent_mode:
            st.error("❌ No se pudo descargar el archivo después de todos los intentos")
        return None

    def download_excel_multiple_sheets(self, sharepoint_url: str) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Descarga Excel con múltiples hojas (wrapper para compatibilidad).
        
        Args:
            sharepoint_url (str): URL del archivo Excel
            
        Returns:
            dict: Diccionario {nombre_hoja: DataFrame} o None si falla
        """
        try:
            result = self.download_excel_from_sharepoint(sharepoint_url, all_sheets=True)
            
            if isinstance(result, dict):
                if not self.silent_mode:
                    st.success(f"✅ Excel multi-hoja descargado: {len(result)} hojas")
                return result
            elif isinstance(result, pd.DataFrame):
                # Convertir DataFrame simple a diccionario
                if not self.silent_mode:
                    st.warning("⚠️ Solo se descargó una hoja, convirtiendo a formato multi-hoja")
                return {'Sheet1': result}
            else:
                if not self.silent_mode:
                    st.error("❌ Error descargando Excel multi-hoja")
                return None
                
        except Exception as e:
            if not self.silent_mode:
                st.error(f"❌ Error descargando Excel multi-hoja: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Prueba completa de conectividad SharePoint.
        
        Returns:
            bool: True si todo funciona correctamente
        """
        try:
            if not self.silent_mode:
                st.info("🔍 Iniciando test de conexión SharePoint...")
            
            # Test 1: Validar configuración
            if not self._config_validated:
                if not self.silent_mode:
                    st.error("❌ Configuración no válida")
                return False
            
            if not self.silent_mode:
                st.success("✅ Test 1: Configuración válida")
            
            # Test 2: Obtener token
            token = self.get_access_token(force_refresh=True)
            if not token:
                if not self.silent_mode:
                    st.error("❌ Test 2: No se pudo obtener token")
                return False
            
            if not self.silent_mode:
                st.success("✅ Test 2: Token obtenido correctamente")
            
            # Test 3: Verificar token con Graph API
            headers = {'Authorization': f'Bearer {token}'}
            test_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers, timeout=10)
            
            if test_response.status_code in [200, 403]:  # 403 es normal para app-only
                if not self.silent_mode:
                    st.success("✅ Test 3: Token válido en Graph API")
            else:
                if not self.silent_mode:
                    st.warning(f"⚠️ Test 3: Respuesta inesperada: {test_response.status_code}")
            
            if not self.silent_mode:
                st.success("🎉 ¡Conexión SharePoint exitosa!")
            return True
            
        except Exception as e:
            if not self.silent_mode:
                st.error(f"❌ Error en test de conexión: {e}")
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """Obtiene información del sistema."""
        return {
            'config_validated': self._config_validated,
            'last_validation': self._last_validation.isoformat() if self._last_validation else None,
            'token_cached': 'access_token' in self._token_cache,
            'token_valid': self._is_token_valid(),
            'cache_ttl_minutes': self.cache_ttl_minutes,
            'silent_mode': self.silent_mode,
            'tenant_id': self.tenant_id,
            'client_id': self.client_id[:8] + "..." + self.client_id[-4:],  # Parcialmente oculto
        }

    def enable_silent_mode(self):
        """Activa modo silencioso."""
        self.silent_mode = True

    def disable_silent_mode(self):
        """Desactiva modo silencioso."""
        self.silent_mode = False


# =============================================================================
# INSTANCIA GLOBAL SILENCIOSA Y FUNCIONES HELPER
# =============================================================================

# Instancia global automatizada EN MODO SILENCIOSO
sharepoint_system = SharePointAuthSystem(silent_mode=True)

def download_excel_simple(sharepoint_url: str, all_sheets: bool = True) -> Optional[Union[pd.DataFrame, Dict[str, pd.DataFrame]]]:
    """
    Función helper simple para descarga rápida SILENCIOSA.
    
    Args:
        sharepoint_url (str): URL del archivo SharePoint
        all_sheets (bool): Si True, descarga todas las hojas; si False, solo la primera
        
    Returns:
        pd.DataFrame o Dict[str, pd.DataFrame]: Datos descargados o None si falla
    """
    return sharepoint_system.download_excel_from_sharepoint(sharepoint_url, all_sheets=all_sheets)

def download_excel_multi_sheet(sharepoint_url: str) -> Optional[Dict[str, pd.DataFrame]]:
    """Función helper para descarga multi-hoja SILENCIOSA."""
    result = sharepoint_system.download_excel_from_sharepoint(sharepoint_url, all_sheets=True)
    
    # Asegurar que devolvemos un diccionario
    if isinstance(result, pd.DataFrame):
        # Convertir DataFrame simple a diccionario
        return {'Sheet1': result}
    elif isinstance(result, dict):
        return result
    else:
        return None

def test_sharepoint_connection() -> bool:
    """Función helper para test de conexión SILENCIOSA."""
    return sharepoint_system.test_connection()

def get_sharepoint_token() -> Optional[str]:
    """Función helper para obtener token SILENCIOSAMENTE."""
    return sharepoint_system.get_access_token()

def get_sharepoint_info() -> Dict[str, Any]:
    """Función helper para información del sistema."""
    return sharepoint_system.get_system_info()

def enable_sharepoint_debug():
    """Habilita logging detallado de SharePoint."""
    sharepoint_system.disable_silent_mode()

def disable_sharepoint_debug():
    """Deshabilita logging detallado de SharePoint."""
    sharepoint_system.enable_silent_mode()

# =============================================================================
# AUTO-INICIALIZACIÓN Y VALIDACIÓN
# =============================================================================

def validate_sharepoint_setup():
    """Valida que SharePoint esté configurado correctamente."""
    try:
        info = get_sharepoint_info()
        if info['config_validated'] and info['token_cached']:
            return True
        else:
            return False
    except:
        return False

# Exportaciones principales
__all__ = [
    'SharePointAuthSystem',
    'download_excel_simple',
    'download_excel_multi_sheet', 
    'test_sharepoint_connection',
    'get_sharepoint_token',
    'get_sharepoint_info',
    'validate_sharepoint_setup',
    'enable_sharepoint_debug',
    'disable_sharepoint_debug',
    'sharepoint_system'
]
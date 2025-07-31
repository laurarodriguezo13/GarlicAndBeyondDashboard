"""
Excel Loader System - VERSIÓN SILENCIOSA
=========================================
Sistema automatizado para carga de datos Excel desde SharePoint
SIN logging molesto para usuarios finales.

Características principales:
- Carga silenciosa desde SharePoint
- Logging solo en modo debug
- Funcionamiento independiente
- Manejo robusto de errores

Autor: GANDB Dashboard Team  
Fecha: 2025
Versión: 2.2 (Silenciosa)
"""

import streamlit as st
import pandas as pd
import os
import sys
import importlib.util
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
import warnings
import traceback

warnings.filterwarnings('ignore')

# =============================================================================
# SISTEMA DE IMPORTACIÓN SHAREPOINT SILENCIOSO
# =============================================================================

class SharePointImporter:
    """Gestor silencioso para importar SharePoint Auth."""
    
    def __init__(self, debug_mode: bool = False):
        self.sharepoint_functions = None
        self.debug_mode = debug_mode
        self._setup_sharepoint()
    
    def _setup_sharepoint(self):
        """Configura SharePoint Auth silenciosamente."""
        try:
            # Detectar estructura de directorios
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)  # utils/
            project_root = os.path.dirname(current_dir)  # raíz del proyecto
            
            # Añadir rutas al path
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Importación directa
            try:
                from auth.sharepoint_auth import (
                    download_excel_simple, 
                    test_sharepoint_connection
                )
                
                self.sharepoint_functions = {
                    'download_excel_simple': download_excel_simple,
                    'test_sharepoint_connection': test_sharepoint_connection
                }
                
                if self.debug_mode:
                    st.success("✅ SharePoint Auth cargado correctamente")
                return
                
            except ImportError:
                pass
            
            # Importación por path como fallback
            auth_file = os.path.join(project_root, 'auth', 'sharepoint_auth.py')
            if os.path.exists(auth_file):
                spec = importlib.util.spec_from_file_location("sharepoint_auth", auth_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.sharepoint_functions = {
                    'download_excel_simple': module.download_excel_simple,
                    'test_sharepoint_connection': module.test_sharepoint_connection
                }
                
                if self.debug_mode:
                    st.success("✅ SharePoint Auth cargado por path")
                return
            
            if self.debug_mode:
                st.error("❌ No se pudo cargar SharePoint Auth")
            
        except Exception as e:
            if self.debug_mode:
                st.error(f"❌ Error configurando SharePoint: {e}")
    
    def is_available(self) -> bool:
        """Verifica si SharePoint está disponible."""
        return self.sharepoint_functions is not None
    
    def download_excel(self, url: str) -> Optional[Union[pd.DataFrame, Dict[str, pd.DataFrame]]]:
        """Descarga Excel desde SharePoint silenciosamente."""
        if not self.is_available():
            if self.debug_mode:
                st.error("❌ SharePoint no disponible")
            return None
        
        try:
            # Descargar silenciosamente
            return self.sharepoint_functions['download_excel_simple'](url, all_sheets=True)
        except Exception as e:
            if self.debug_mode:
                st.error(f"❌ Error descargando desde SharePoint: {e}")
            return None

# =============================================================================
# SISTEMA PRINCIPAL SILENCIOSO
# =============================================================================

class ExcelLoaderSilent:
    """Sistema de carga Excel silencioso para usuarios finales."""
    
    def __init__(self, debug_mode: bool = False):
        """Inicialización silenciosa."""
        self.parsers_cache = {}
        self.debug_mode = debug_mode
        self.sharepoint_importer = SharePointImporter(debug_mode)
        
    def get_sharepoint_url(self, module_id: str) -> Optional[str]:
        """Obtiene URL de SharePoint para un módulo."""
        try:
            # Verificar configuración
            if 'page_mapping' not in st.secrets:
                if self.debug_mode:
                    st.error("❌ 'page_mapping' no encontrado en secrets.toml")
                return None
            
            page_mapping = dict(st.secrets['page_mapping'])
            
            if module_id not in page_mapping:
                if self.debug_mode:
                    st.error(f"❌ '{module_id}' no encontrado en page_mapping")
                return None
            
            # Navegar por el path de configuración
            mapping_path = page_mapping[module_id]
            path_parts = mapping_path.split('.')
            current = st.secrets
            
            for part in path_parts:
                if part in current:
                    current = current[part]
                else:
                    if self.debug_mode:
                        st.error(f"❌ Path '{mapping_path}' no válido")
                    return None
            
            if isinstance(current, str) and current.startswith('http'):
                return current
            else:
                if self.debug_mode:
                    st.error(f"❌ URL no válida para {module_id}")
                return None
                
        except Exception as e:
            if self.debug_mode:
                st.error(f"❌ Error obteniendo URL: {e}")
            return None
    
    def load_parser(self, module_id: str):
        """Carga parser para un módulo específico."""
        try:
            # Verificar caché
            if module_id in self.parsers_cache:
                return self.parsers_cache[module_id]
            
            # Buscar archivo parser
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parser_file = f"parser_{module_id}.py"
            parser_path = os.path.join(current_dir, parser_file)
            
            if not os.path.exists(parser_path):
                if self.debug_mode:
                    st.error(f"❌ Parser no encontrado: {parser_file}")
                return None
            
            # Cargar parser
            spec = importlib.util.spec_from_file_location(f"parser_{module_id}", parser_path)
            parser_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(parser_module)
            
            # Verificar función parse_excel
            if not hasattr(parser_module, 'parse_excel'):
                if self.debug_mode:
                    st.error(f"❌ Parser {module_id} no tiene función 'parse_excel'")
                return None
            
            # Guardar en caché
            self.parsers_cache[module_id] = parser_module
            return parser_module
            
        except Exception as e:
            if self.debug_mode:
                st.error(f"❌ Error cargando parser {module_id}: {e}")
            return None
    
    def load_module_data(self, module_id: str) -> Optional[Any]:
        """Carga datos para un módulo específico de forma silenciosa."""
        try:
            # Solo mostrar info básica
            progress_placeholder = st.empty()
            
            # 1. Verificar SharePoint
            if not self.sharepoint_importer.is_available():
                if self.debug_mode:
                    st.error("❌ SharePoint no disponible")
                return None
            
            # 2. Obtener URL
            sharepoint_url = self.get_sharepoint_url(module_id)
            if not sharepoint_url:
                return None
            
            # 3. Descargar datos
            progress_placeholder.info("📥 Descargando datos desde SharePoint...")
            raw_data = self.sharepoint_importer.download_excel(sharepoint_url)
            
            if raw_data is None:
                if self.debug_mode:
                    st.error("❌ Error descargando archivo")
                progress_placeholder.empty()
                return None
            
            # 4. Cargar parser
            parser_module = self.load_parser(module_id)
            if parser_module is None:
                progress_placeholder.empty()
                return None
            
            # 5. Procesar datos
            progress_placeholder.info("⚙️ Procesando datos...")
            
            # El parser recibe los datos descargados directamente
            parsed_data = parser_module.parse_excel(raw_data)
            
            progress_placeholder.empty()
            
            if parsed_data and parsed_data.get('status') == 'success':
                return parsed_data
            else:
                error_msg = parsed_data.get('metadata', {}).get('error', 'Error desconocido') if parsed_data else 'Sin respuesta del parser'
                if self.debug_mode:
                    st.error(f"❌ Error procesando datos: {error_msg}")
                return None
                
        except Exception as e:
            if self.debug_mode:
                st.error(f"❌ Error crítico cargando {module_id}: {e}")
            return None

# =============================================================================
# FUNCIONES PÚBLICAS SILENCIOSAS
# =============================================================================

# Instancia global silenciosa
excel_loader = ExcelLoaderSilent(debug_mode=False)  # Sin debug por defecto

@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_dataframe(module_id: str) -> Optional[Any]:
    """
    Función principal para obtener datos de un módulo silenciosamente.
    
    Args:
        module_id: ID del módulo (ej: 'KCTN_01_Produccion')
        
    Returns:
        Datos parseados del módulo o None si hay error
    """
    return excel_loader.load_module_data(module_id)

def test_sharepoint_connection() -> bool:
    """Prueba la conexión a SharePoint."""
    try:
        if not excel_loader.sharepoint_importer.is_available():
            return False
        
        return excel_loader.sharepoint_importer.sharepoint_functions['test_sharepoint_connection']()
    except:
        return False

def clear_cache():
    """Limpia el caché de datos."""
    st.cache_data.clear()
    excel_loader.parsers_cache.clear()

def get_system_status() -> Dict[str, Any]:
    """Obtiene estado simplificado del sistema."""
    return {
        'sharepoint_available': excel_loader.sharepoint_importer.is_available(),
        'parsers_cached': len(excel_loader.parsers_cache),
        'timestamp': datetime.now().isoformat()
    }

def enable_debug_mode():
    """Habilita modo debug para ver logging detallado."""
    excel_loader.debug_mode = True
    excel_loader.sharepoint_importer.debug_mode = True

def disable_debug_mode():
    """Deshabilita modo debug para interfaz limpia."""
    excel_loader.debug_mode = False
    excel_loader.sharepoint_importer.debug_mode = False

# Exportaciones
__all__ = [
    'get_dataframe',
    'test_sharepoint_connection', 
    'clear_cache',
    'get_system_status',
    'enable_debug_mode',
    'disable_debug_mode'
]
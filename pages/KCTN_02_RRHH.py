"""
KCTN_02_RRHH.py - Dashboard RRHH Garlic & Beyond COMPLETO CON DEBUG
===================================================================
Dashboard completo de Recursos Humanos para Garlic & Beyond.
INCLUYE: Funciones de debug para diagnosticar problemas de datos.

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 3.1 - Completo con Debug Integrado
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import io
import base64

# ================================================================
# CONFIGURACIÓN DE PÁGINA
# ================================================================
if 'page_config_set' not in st.session_state:
    st.set_page_config(
        page_title="Dashboard RRHH - Garlic & Beyond",
        page_icon="🧄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True

# ================================================================
# IMPORTACIONES SEGURAS DE MÓDULOS
# ================================================================
def safe_import():
    """Importa módulos de manera segura con múltiples rutas."""
    try:
        # Agregar rutas posibles
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        parent_dir = os.path.dirname(current_dir)
        utils_dir = os.path.join(parent_dir, 'utils')
        
        paths_to_add = [utils_dir, parent_dir, current_dir]
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        # Intentar importar Excel Loader
        try:
            from utils.excel_loader import get_dataframe
            excel_available = True
        except ImportError:
            try:
                from utils.excel_loader import get_dataframe
                excel_available = True
            except ImportError:
                excel_available = False
                get_dataframe = None
        
        # Intentar importar controlador
        try:
            from utils.controller_KCTN_02_RRHH import GarlicRRHHController
            controller_available = True
        except ImportError:
            try:
                from utils.controller_KCTN_02_RRHH import GarlicRRHHController
                controller_available = True
            except ImportError:
                controller_available = False
                GarlicRRHHController = None
        
        # Intentar importar parser
        try:
            from utils.parser_KCTN_02_RRHH import parse_excel
            parser_available = True
        except ImportError:
            try:
                from utils.parser_KCTN_02_RRHH import parse_excel
                parser_available = True
            except ImportError:
                parser_available = False
                parse_excel = None
        
        return excel_available, controller_available, parser_available, get_dataframe, GarlicRRHHController, parse_excel
        
    except Exception as e:
        st.error(f"Error en importaciones: {e}")
        return False, False, False, None, None, None

excel_available, controller_available, parser_available, get_dataframe, GarlicRRHHController, parse_excel = safe_import()

# ================================================================
# CSS PERSONALIZADO PARA GARLIC & BEYOND
# ================================================================
st.markdown("""
<style>
    /* Importar Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para Garlic & Beyond */
    :root {
        --primary-color: #2E7D32;
        --secondary-color: #4CAF50;
        --success-color: #66BB6A;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --info-color: #2196F3;
        --text-primary: #1B5E20;
        --text-secondary: #388E3C;
        --background-white: #ffffff;
        --background-light: #F1F8E9;
        --border-light: #C8E6C9;
        --shadow-sm: 0 1px 2px 0 rgba(46, 125, 50, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(46, 125, 50, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(46, 125, 50, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(46, 125, 50, 0.1);
    }
    
    /* Fuente global */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Fondo global */
    .main .block-container {
        background: var(--background-white);
        padding-top: 1rem;
        max-width: 1400px;
    }
    
    /* Header principal para Garlic & Beyond */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '🧄';
        position: absolute;
        top: 1rem;
        right: 2rem;
        font-size: 3rem;
        opacity: 0.2;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header h2 {
        font-size: 1.8rem;
        font-weight: 500;
        margin: 0.5rem 0;
        opacity: 0.95;
    }
    
    .main-header p {
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 1rem;
        opacity: 0.9;
    }
    
    /* KPI Cards específicas para Garlic & Beyond */
    .kpi-card {
        background: var(--background-white);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-lg);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
    }
    
    .kpi-card-fijo::before {
        background: linear-gradient(90deg, #1976D2, #42A5F5);
    }
    
    .kpi-card-produccion::before {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .kpi-card-bajas::before {
        background: linear-gradient(90deg, #F44336, #FF7043);
    }
    
    .kpi-card-total::before {
        background: linear-gradient(90deg, #673AB7, #9C27B0);
    }
    
    /* Métricas mejoradas */
    .metric-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    
    .metric-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value-large {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .metric-value-small {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin: 0.25rem 0;
        line-height: 1.3;
    }
    
    /* Secciones */
    .section-header {
        background: linear-gradient(135deg, var(--background-light) 0%, #E8F5E8 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        border-left: 5px solid var(--primary-color);
        margin: 2.5rem 0 1.5rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Status indicators */
    .status-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: 1.5rem;
        background: var(--background-white);
        border-radius: 12px;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 12px;
        box-shadow: 0 0 0 2px rgba(255,255,255,0.8);
    }
    
    .status-green { background-color: var(--success-color); }
    .status-orange { background-color: var(--warning-color); }
    .status-red { background-color: var(--error-color); }
    
    /* Alertas */
    .alert {
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 5px solid;
        box-shadow: var(--shadow-sm);
    }
    
    .alert-success {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
        border-color: var(--success-color);
        color: #2E7D32;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-color: var(--warning-color);
        color: #E65100;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-color: var(--info-color);
        color: #0D47A1;
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* Tablas mejoradas */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-light);
    }
    
    .dataframe thead th {
        background: linear-gradient(135deg, var(--background-light) 0%, #E8F5E8 100%);
        color: var(--text-primary);
        font-weight: 600;
        padding: 1rem;
        border-bottom: 2px solid var(--border-light);
    }
    
    .dataframe tbody td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border-light);
    }
    
    .dataframe tbody tr:hover {
        background-color: var(--background-light);
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem; }
        .main-header h2 { font-size: 1.5rem; }
        .kpi-card { padding: 1.5rem 1rem; }
        .section-header { padding: 1rem 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# INICIALIZACIÓN DEL CONTROLADOR
# ================================================================
@st.cache_resource
def init_controller():
    """Inicializa el controlador con cache."""
    if controller_available and GarlicRRHHController:
        return GarlicRRHHController()
    return None

if 'garlic_controller' not in st.session_state:
    st.session_state.garlic_controller = init_controller()

controller = st.session_state.garlic_controller

# ================================================================
# FUNCIONES DE UTILIDAD
# ================================================================
def export_to_excel(data, filename):
    """Exporta datos a Excel con formato profesional."""
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if not data.empty:
                data.to_excel(writer, index=False, sheet_name='Datos_RRHH')
        
        processed_data = output.getvalue()
        return processed_data
    except Exception as e:
        st.error(f"Error generando Excel: {str(e)}")
        return None

def display_kpi_card(title, main_value, sub_values, card_type="default"):
    """Muestra una KPI card con formato específico."""
    card_class = f"kpi-card kpi-card-{card_type}"
    
    sub_values_html = ""
    for label, value in sub_values:
        sub_values_html += f'<div class="metric-value-small"><strong>{label}:</strong> {value}</div>'
    
    st.markdown(f"""
    <div class="{card_class}">
        <div class="metric-container">
            <div class="metric-title">{title}</div>
            <div class="metric-value-large">{main_value}</div>
            {sub_values_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# HEADER PRINCIPAL
# ================================================================
st.markdown("""
<div class="main-header">
    <h1>🧄 Dashboard Recursos Humanos</h1>
    <h2>Garlic & Beyond - Análisis Integral de Personal</h2>
    <p>Sistema avanzado de gestión y análisis de costes de personal por departamento</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# INFORMACIÓN DE PERÍODO
# ================================================================
st.markdown("""
<div class="alert alert-info">
    <strong>📅 Período de Análisis:</strong> Enero - Diciembre 2025 (12 meses) | 
    <strong>🔄 Última Actualización:</strong> """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """
</div>
""", unsafe_allow_html=True)

# ================================================================
# PANEL DE CONTROL CON LÓGICA DE CARGA INTELIGENTE
# ================================================================
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if controller:
        status = controller.get_status()
        if status['initialized']:
            st.markdown(f"""
            <div class="status-container">
                <div style="display: flex; align-items: center;">
                    <span class="status-indicator status-green"></span>
                    <strong>✅ Sistema Activo:</strong> {status['months_with_data']} meses con datos, {status['months_empty']} pendientes
                </div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    👥 {status['total_employees_latest']} empleados | 💰 €{status['total_cost_latest']:,.0f} | 
                    🚨 {status['alerts_count']} alertas | 📅 {status['last_update']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-container">
                <div style="display: flex; align-items: center;">
                    <span class="status-indicator status-red"></span>
                    <strong>❌ Sistema Inactivo:</strong> Datos no cargados
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("❌ Controlador no disponible")

with col2:
    if st.button("🔄 Cargar desde SharePoint", help="Cargar datos reales desde SharePoint"):
        with st.spinner("Cargando datos desde SharePoint..."):
            try:
                if excel_available and get_dataframe:
                    # LÓGICA DE CARGA INTELIGENTE - DETECTA AUTOMÁTICAMENTE EL TIPO DE DATOS
                    
                    # Obtener datos desde SharePoint
                    st.info("📥 Descargando datos desde SharePoint...")
                    excel_data = get_dataframe('KCTN_02_RRHH')
                    
                    # DETECCIÓN INTELIGENTE: ¿Los datos ya están parseados o son raw?
                    def detect_data_type(data):
                        """Detecta si los datos están parseados o son raw."""
                        if data is None:
                            return 'none', 'Datos son None'
                        elif isinstance(data, str):
                            return 'error_string', f'String error: {data[:100]}...'
                        elif isinstance(data, dict):
                            # ¿Es un resultado parseado?
                            if 'status' in data and 'message' in data and 'data' in data:
                                return 'parsed', f"Datos ya parseados (status: {data.get('status')})"
                            # ¿Es dict de DataFrames raw?
                            elif all(isinstance(v, pd.DataFrame) for v in data.values()):
                                return 'raw_excel', f'Dict con {len(data)} DataFrames raw'
                            else:
                                return 'unknown_dict', f'Dict desconocido con claves: {list(data.keys())}'
                        elif isinstance(data, pd.DataFrame):
                            return 'raw_dataframe', f'DataFrame raw con shape {data.shape}'
                        else:
                            return 'unknown', f'Tipo desconocido: {type(data)}'
                    
                    # Detectar tipo de datos recibidos
                    data_type, description = detect_data_type(excel_data)
                    st.success(f"✅ Tipo detectado: {data_type}")
                    
                    # Procesar según el tipo detectado
                    if data_type == 'none':
                        st.error("❌ No se pudieron obtener datos de SharePoint")
                        st.markdown("""
                        **Posibles causas:**
                        - Error de conectividad con SharePoint  
                        - URL incorrecta en secrets.toml
                        - Credenciales incorrectas
                        - Archivo no encontrado
                        """)
                    
                    elif data_type == 'error_string':
                        st.error("❌ SharePoint devolvió un mensaje de error:")
                        with st.expander("📄 Mensaje completo"):
                            st.code(excel_data)
                        st.markdown("""
                        **Soluciones:**
                        1. Verificar URL del archivo en secrets.toml
                        2. Comprobar credenciales de SharePoint  
                        3. Verificar permisos de acceso al archivo
                        4. Comprobar que el archivo existe
                        """)
                    
                    elif data_type == 'parsed':
                        # ¡ESTE ES EL CASO PRINCIPAL! Los datos ya están parseados
                        st.success("🎉 Datos ya parseados por excel_loader - inicializando directamente")
                        
                        # Verificar el status de los datos parseados
                        if excel_data.get('status') == 'success':
                            # Inicializar controlador directamente con datos parseados
                            if controller and controller.initialize_with_data(excel_data):
                                st.success("✅ Datos cargados correctamente desde SharePoint")
                                st.balloons()
                                
                                # Mostrar resumen de datos cargados
                                metadata = excel_data.get('metadata', {})
                                st.info(f"📊 Meses procesados: {len(metadata.get('processed_months', []))}")
                                if metadata.get('processed_months'):
                                    st.write(f"Meses: {', '.join(metadata['processed_months'])}")
                                
                                st.rerun()
                            else:
                                st.error("❌ Error inicializando controlador con datos parseados")
                        
                        elif excel_data.get('status') == 'error':
                            st.error(f"❌ Error en datos parseados: {excel_data.get('message')}")
                            
                            # Mostrar detalles del error
                            metadata = excel_data.get('metadata', {})
                            
                            if 'errors' in metadata and metadata['errors']:
                                st.markdown("**Errores específicos:**")
                                for error in metadata['errors'][:5]:
                                    st.error(f"• {error}")
                            
                            if 'sheet_analysis' in metadata:
                                st.markdown("**Análisis de hojas Excel:**")
                                analysis_df = pd.DataFrame(metadata['sheet_analysis'])
                                st.dataframe(analysis_df, use_container_width=True)
                            
                            # Sugerir soluciones basadas en el análisis
                            if metadata.get('processed_months', []):
                                st.info(f"✅ Algunos meses sí se procesaron: {metadata['processed_months']}")
                            else:
                                st.warning("""
                                ⚠️ **Ningún mes se pudo procesar**
                                
                                **Posibles causas:**
                                - Nombres de hojas incorrectos (deben ser 'enero', 'febrero', etc.)
                                - Hojas vacías (meses futuros sin datos)
                                - Estructura Excel incorrecta (falta fila 'Total:')
                                - Hojas omitidas por configuración
                                """)
                        
                        else:
                            st.warning(f"⚠️ Status desconocido en datos parseados: {excel_data.get('status')}")
                    
                    elif data_type == 'raw_excel':
                        # Datos raw de Excel - necesitan parsing manual
                        st.info("⚙️ Datos raw detectados - parseando manualmente...")
                        
                        if parser_available and parse_excel:
                            try:
                                parsed_data = parse_excel(excel_data)
                                
                                if parsed_data and parsed_data.get('status') == 'success':
                                    if controller and controller.initialize_with_data(parsed_data):
                                        st.success("✅ Datos raw parseados y cargados correctamente")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error inicializando controlador")
                                else:
                                    error_msg = parsed_data.get('message', 'Error desconocido') if parsed_data else 'Sin respuesta del parser'
                                    st.error(f"❌ Error parseando datos raw: {error_msg}")
                            
                            except Exception as e:
                                st.error(f"❌ Excepción parseando datos raw: {e}")
                        else:
                            st.error("❌ Parser no disponible para datos raw")
                    
                    elif data_type == 'raw_dataframe':
                        # DataFrame simple - convertir y parsear
                        st.info("📋 DataFrame simple detectado - procesando...")
                        
                        excel_dict = {'Sheet1': excel_data}
                        
                        if parser_available and parse_excel:
                            try:
                                parsed_data = parse_excel(excel_dict)
                                
                                if parsed_data and parsed_data.get('status') == 'success':
                                    if controller and controller.initialize_with_data(parsed_data):
                                        st.success("✅ DataFrame procesado correctamente")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error inicializando controlador")
                                else:
                                    st.error(f"❌ Error parseando DataFrame: {parsed_data.get('message') if parsed_data else 'Sin respuesta'}")
                            
                            except Exception as e:
                                st.error(f"❌ Error procesando DataFrame: {e}")
                        else:
                            st.error("❌ Parser no disponible")
                    
                    else:
                        # Tipo desconocido
                        st.error(f"❌ Tipo de datos no soportado: {data_type}")
                        st.write(f"Descripción: {description}")
                        
                        # Intentar mostrar más información
                        if isinstance(excel_data, dict):
                            st.write("Claves del dict:")
                            for key, value in excel_data.items():
                                st.write(f"  • {key}: {type(value)}")
                
                else:
                    st.error("❌ Módulos no disponibles")
                    st.write(f"Excel loader available: {excel_available}")
                    st.write(f"Get dataframe function: {get_dataframe is not None}")
                    
            except Exception as e:
                st.error(f"❌ Error crítico durante carga: {e}")
                st.exception(e)

with col3:
    if st.button("📁 Subir Excel Local", help="Subir archivo Excel desde tu computadora"):
        st.info("🔄 Funcionalidad próximamente disponible")

# ================================================================
# CONTENIDO PRINCIPAL - SOLO SI HAY CONTROLADOR INICIALIZADO
# ================================================================
if controller and controller.is_initialized:
    
    # ================================================================
    # BARRA LATERAL - FILTROS
    # ================================================================
    with st.sidebar:
        st.markdown("## 🎯 Panel de Control")
        
        # Selector de modo de análisis
        analysis_mode = st.radio(
            "**Modo de Análisis:**",
            ["📊 Análisis Individual", "📈 Comparación Multi-mes"],
            help="Selecciona el tipo de análisis que deseas realizar"
        )
        
        if analysis_mode == "📊 Análisis Individual":
            st.markdown("### 📅 Análisis Individual")
            available_months = controller.get_available_months()
            selected_month = st.selectbox(
                "**Seleccionar Mes:**", 
                available_months, 
                index=len(controller.get_months_with_data())-1 if controller.get_months_with_data() else 0,
                help="Selecciona el mes para análisis detallado"
            )
            
        else:
            st.markdown("### 📈 Comparación Multi-mes")
            available_months = controller.get_available_months()
            months_with_data = controller.get_months_with_data()
            
            selected_months = st.multiselect(
                "**Meses a Comparar:**",
                available_months,
                default=months_with_data[-6:] if len(months_with_data) >= 6 else months_with_data,
                help="Selecciona múltiples meses para comparar"
            )
        
        st.markdown("---")
        
    
    # ================================================================
    # ANÁLISIS INDIVIDUAL
    # ================================================================
    if analysis_mode == "📊 Análisis Individual":
        
        # Obtener KPIs del mes seleccionado
        kpis = controller.get_monthly_kpis(selected_month)
        
        # Mostrar alertas si las hay
        alerts = controller.get_alerts()
        for alert in alerts:
            alert_class = f"alert-{alert.get('type', 'info')}"
            st.markdown(f"""
            <div class="alert {alert_class}">
                <strong>{alert.get('title', '')}</strong><br>
                {alert.get('message', '')}
            </div>
            """, unsafe_allow_html=True)
        
        # ================================================================
        # SECCIÓN 1: KPI CARDS (4 cards según especificaciones)
        # ================================================================
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">📊 KPIs Principales - """ + selected_month + """</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar mensaje si no hay datos
        if not kpis['has_data']:
            st.info(f"📅 {selected_month} - Datos pendientes de cargar")
        
        # 4 KPI Cards en 2 filas
        col1, col2 = st.columns(2)
        
        with col1:
            # KPI Card 1: Coste Personal Fijo
            display_kpi_card(
                "💼 Coste Personal Fijo",
                f"€{kpis['fijo_coste_mes']:,.0f}",
                [
                    ("Coste/Día", f"€{kpis['fijo_coste_dia']:,.0f}"),
                    ("Coste/Hora", f"€{kpis['fijo_coste_hora']:,.0f}"),
                    ("H/PAX", f"{kpis['fijo_hpax']:,.2f}")
                ],
                "fijo"
            )
        
        with col2:
            # KPI Card 2: Coste Personal Producción
            display_kpi_card(
                "🏭 Coste Personal Producción",
                f"€{kpis['produccion_coste_mes']:,.0f}",
                [
                    ("Coste/Día", f"€{kpis['produccion_coste_dia']:,.0f}"),
                    ("Coste/Hora", f"€{kpis['produccion_coste_hora']:,.0f}"),
                    ("H/PAX", f"{kpis['produccion_hpax']:,.2f}")
                ],
                "produccion"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            # KPI Card 3: Bajas
            display_kpi_card(
                "🏥 Análisis de Bajas",
                f"€{kpis['bajas_coste_total']:,.0f}",
                [
                    ("Número de Bajas", f"{kpis['bajas_numero']} empleados"),
                    ("% del Total", f"{kpis['bajas_porcentaje']:.1f}%"),
                    ("Total Empleados", f"{kpis['total_empleados']} empleados")
                ],
                "bajas"
            )
        
        with col4:
            # KPI Card 4: Gasto Personal Total
            display_kpi_card(
                "💰 Gasto Personal Total",
                f"€{kpis['total_coste_mes']:,.0f}",
                [
                    ("Coste/Día", f"€{kpis['total_coste_dia']:,.0f}"),
                    ("Coste/Hora", f"€{kpis['total_coste_hora']:,.0f}"),
                    ("Empleados Totales", f"{kpis['total_empleados']} empleados")
                ],
                "total"
            )
        
        # ================================================================
        # SECCIÓN 2: GRÁFICOS INDIVIDUALES
        # ================================================================
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">📈 Análisis Gráfico - """ + selected_month + """</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Costes Por Sección (gráfico de barras)
            st.subheader("💰 Costes por Sección")
            fig_costes_seccion = controller.create_costes_por_seccion_chart(selected_month)
            st.plotly_chart(fig_costes_seccion, use_container_width=True)
        
        with col2:
            # 2. Pie Chart de Secciones (count empleados por sección)
            st.subheader("👥 Distribución de Empleados")
            fig_pie_secciones = controller.create_pie_chart_secciones(selected_month)
            st.plotly_chart(fig_pie_secciones, use_container_width=True)
        
        # ================================================================
        # SECCIÓN 3: ANÁLISIS DE BAJAS DETALLADO
        # ================================================================
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">🏥 Análisis Detallado de Bajas - """ + selected_month + """</h3>
        </div>
        """, unsafe_allow_html=True)
        
        bajas_data = controller.get_analisis_bajas_data(selected_month)
        
        if bajas_data['cantidad_bajas'] > 0:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"""
                **📊 Resumen de Bajas:**
                
                - **Cantidad de bajas:** {bajas_data['cantidad_bajas']} empleados
                - **Coste total de bajas:** €{bajas_data['coste_total_bajas']:,.0f}
                - **% sobre coste total:** {bajas_data['porcentaje_coste_bajas']:.1f}%
                """)
            
            with col2:
                if bajas_data['empleados_baja']:
                    st.markdown("**📋 Lista de Empleados de Baja:**")
                    
                    bajas_df = pd.DataFrame(bajas_data['empleados_baja'])
                    bajas_df['coste'] = bajas_df['coste'].apply(lambda x: f"€{x:,.0f}")
                    bajas_df['porcentaje_coste'] = bajas_df['porcentaje_coste'].apply(lambda x: f"{x:.1f}%")
                    bajas_df.columns = ['Nombre', 'Sección', 'Coste', '% del Total']
                    
                    st.dataframe(bajas_df, use_container_width=True, hide_index=True)
        else:
            st.success(f"🎉 No hay empleados de baja en {selected_month}")
    
    # ================================================================
    # COMPARACIÓN MULTI-MES
    # ================================================================
    else:
        if not selected_months:
            st.warning("⚠️ Selecciona al menos un mes para comparar")
        else:
            # ================================================================
            # SECCIÓN 1: TABLA DE KPIs COMPARATIVA
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📊 Tabla Comparativa de KPIs</h3>
            </div>
            """, unsafe_allow_html=True)
            
            kpi_table = controller.create_multi_month_kpi_table(selected_months)
            
            if not kpi_table.empty:
                st.dataframe(
                    kpi_table, 
                    use_container_width=True, 
                    hide_index=True,
                    height=600
                )
                
                # Botón de descarga
                csv_data = kpi_table.to_csv(index=False)
                st.download_button(
                    label="📄 Descargar Tabla KPIs",
                    data=csv_data,
                    file_name=f"KPIs_Comparativa_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No hay datos disponibles para generar la tabla comparativa")
            
            # ================================================================
            # SECCIÓN 2: GRÁFICOS COMPARATIVOS
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📈 Análisis Comparativo entre Meses</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # 1. Evolución de Costes (líneas de mes, día, hora)
            st.subheader("📈 Evolución de Costes Totales")
            fig_evolucion = controller.create_evolucion_costes_chart(selected_months)
            st.plotly_chart(fig_evolucion, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 2. Costes por Sección Comparativo (barras agrupadas)
                st.subheader("📊 Comparación Costes por Sección")
                fig_seccion_comp = controller.create_costes_seccion_comparativo_chart(selected_months)
                st.plotly_chart(fig_seccion_comp, use_container_width=True)
            
            with col2:
                # 3. Tendencia de Bajas
                st.subheader("🏥 Tendencia de Bajas")
                fig_bajas_tendencia = controller.create_bajas_tendencia_chart(selected_months)
                st.plotly_chart(fig_bajas_tendencia, use_container_width=True)

else:
    # ================================================================
    # MODO SIN DATOS - CONFIGURACIÓN INICIAL
    # ================================================================
    st.markdown("""
    <div class="section-header">
        <h3 class="section-title">🔧 Configuración Inicial del Sistema</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 Bienvenido al Dashboard de RRHH de Garlic & Beyond
    
    Para comenzar a usar el sistema, carga los datos del Excel de costes de personal:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔗 Conexión SharePoint
        **Datos en tiempo real desde SharePoint**
        
        **Características:**
        - ✅ Datos actualizados automáticamente
        - ✅ Conexión directa con el sistema
        - ✅ Procesa todas las hojas mensuales
        
        **Requisitos:**
        - Archivo `secrets.toml` configurado
        - Acceso a SharePoint autorizado
        - Excel en ubicación correcta
        """)
        
        if st.button("🔗 Conectar SharePoint", key="connect_sp", type="primary"):
            st.info("🔄 Usar el botón 'Cargar desde SharePoint' en la parte superior")
    
    with col2:
        st.markdown("""
        #### 📁 Carga Manual
        **Subir archivo Excel local**
        
        **Formato esperado:**
        - 📋 Archivo Excel (.xlsx)
        - 📅 Hojas mensuales (Enero-Diciembre)
        - 👥 Estructura: Nombre, Sección, Tipo, Costes
        - 🏥 Observaciones de bajas
        
        **Estado:**
        Funcionalidad en desarrollo
        """)
        
        uploaded_file = st.file_uploader(
            "📎 Seleccionar archivo Excel", 
            type=['xlsx'], 
            key="upload_excel_main",
            help="Próximamente disponible"
        )
        
        if uploaded_file:
            st.info("📋 **Funcionalidad en desarrollo** - Usa SharePoint")

# ================================================================
# FOOTER
# ================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: var(--text-secondary); padding: 2rem 0;'>
    <p><strong>🧄 Garlic & Beyond Dashboard RRHH v3.1</strong></p>
    <p>Sistema avanzado de análisis de personal con datos específicos • Desarrollado por GANDB Team</p>
    <p>© 2025 Garlic & Beyond - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)

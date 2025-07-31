"""
KCTN_05_Compras_Ventas.py - Dashboard Compras y Ventas KCTN CORREGIDO
=====================================================================
Dashboard completo de Compras y Ventas para Garlic & Beyond KCTN.
Sistema con 2 tabs (Compras y Ventas) con análisis individual y comparativo.

CORRECCIONES CRÍTICAS APLICADAS:
✅ Filtros unificados mes-año para Compras Y Ventas
✅ Consistencia total entre tabs
✅ Llamadas a funciones corregidas para usar month_year_str
✅ Interfaz de usuario consistente y coherente
✅ Manejo correcto de datos multi-año

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 2.0 - CORREGIDO
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
        page_title="Dashboard Compras y Ventas - Garlic & Beyond",
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
            from utils.controller_KCTN_05_Compras_Ventas import GarlicComprasVentasController
            controller_available = True
        except ImportError:
            try:
                from utils.controller_KCTN_05_Compras_Ventas import GarlicComprasVentasController
                controller_available = True
            except ImportError:
                controller_available = False
                GarlicComprasVentasController = None
        
        # Intentar importar parser
        try:
            from utils.parser_KCTN_05_Compras_Ventas import parse_excel
            parser_available = True
        except ImportError:
            try:
                from utils.parser_KCTN_05_Compras_Ventas import parse_excel
                parser_available = True
            except ImportError:
                parser_available = False
                parse_excel = None
        
        return excel_available, controller_available, parser_available, get_dataframe, GarlicComprasVentasController, parse_excel
        
    except Exception as e:
        st.error(f"Error en importaciones: {e}")
        return False, False, False, None, None, None

excel_available, controller_available, parser_available, get_dataframe, GarlicComprasVentasController, parse_excel = safe_import()

# ================================================================
# CSS PERSONALIZADO PARA GARLIC & BEYOND (MISMO DEL ORIGINAL)
# ================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
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
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main .block-container {
        background: var(--background-white);
        padding-top: 1rem;
        max-width: 1400px;
    }
    
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
    
    .kpi-card-compras::before {
        background: linear-gradient(90deg, #1976D2, #42A5F5);
    }
    
    .kpi-card-proveedores::before {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .kpi-card-ventas::before {
        background: linear-gradient(90deg, #F44336, #FF7043);
    }
    
    .kpi-card-clientes::before {
        background: linear-gradient(90deg, #673AB7, #9C27B0);
    }
    
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
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--background-light);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background: var(--background-white);
        border-radius: 8px;
        border: 1px solid var(--border-light);
        color: var(--text-primary);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-color);
        color: white;
        box-shadow: var(--shadow-md);
    }
    
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
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
    if controller_available and GarlicComprasVentasController:
        return GarlicComprasVentasController()
    return None

if 'garlic_compras_ventas_controller' not in st.session_state:
    st.session_state.garlic_compras_ventas_controller = init_controller()

controller = st.session_state.garlic_compras_ventas_controller

# ================================================================
# FUNCIONES DE UTILIDAD
# ================================================================
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
    <h1>🧄 Dashboard Compras y Ventas</h1>
    <h2>Garlic & Beyond KCTN - Análisis Comercial Integral</h2>
    <p>Sistema avanzado de análisis de compras y ventas con datos específicos por mes-año</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# INFORMACIÓN DE PERÍODO
# ================================================================
st.markdown("""
<div class="alert alert-info">
    <strong>📅 Período de Análisis:</strong> Datos de Compras y Ventas por mes/año | 
    <strong>🔄 Última Actualización:</strong> """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """
    <br><strong>✅ SISTEMA CORREGIDO:</strong> Filtros unificados mes-año para precisión total
</div>
""", unsafe_allow_html=True)

# ================================================================
# PANEL DE CONTROL CON LÓGICA DE CARGA INTELIGENTE
# ================================================================
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
    if controller:
        status = controller.get_status()
        if status['initialized']:
            available_periods = status.get('available_months', [])
            periods_preview = available_periods[:3] if len(available_periods) > 3 else available_periods
            periods_text = ", ".join(periods_preview)
            if len(available_periods) > 3:
                periods_text += f" y {len(available_periods)-3} más"
            
            st.markdown(f"""
            <div class="status-container">
                <div style="display: flex; align-items: center;">
                    <span class="status-indicator status-green"></span>
                    <strong>✅ Sistema Activo:</strong> 
                    {'Compras ✓' if status['has_compras'] else 'Compras ✗'} | 
                    {'Ventas ✓' if status['has_ventas'] else 'Ventas ✗'}
                </div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    📊 {status['compras_records']} compras | {status['ventas_records']} ventas | 
                    📅 {len(available_periods)} períodos ({periods_text}) | 🔄 {status['last_update']}
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
                    st.info("📥 Descargando datos desde SharePoint...")
                    excel_data = get_dataframe('KCTN_05_Compras_Ventas')
                    
                    def detect_data_type(data):
                        if data is None:
                            return 'none', 'Datos son None'
                        elif isinstance(data, str):
                            return 'error_string', f'String error: {data[:100]}...'
                        elif isinstance(data, dict):
                            if 'status' in data and 'message' in data and 'data' in data:
                                return 'parsed', f"Datos ya parseados (status: {data.get('status')})"
                            elif all(isinstance(v, pd.DataFrame) for v in data.values()):
                                return 'raw_excel', f'Dict con {len(data)} DataFrames raw'
                            else:
                                return 'unknown_dict', f'Dict desconocido con claves: {list(data.keys())}'
                        elif isinstance(data, pd.DataFrame):
                            return 'raw_dataframe', f'DataFrame raw con shape {data.shape}'
                        else:
                            return 'unknown', f'Tipo desconocido: {type(data)}'
                    
                    data_type, description = detect_data_type(excel_data)
                    st.success(f"✅ Tipo detectado: {data_type}")
                    
                    if data_type == 'none':
                        st.error("❌ No se pudieron obtener datos de SharePoint")
                        
                    elif data_type == 'error_string':
                        st.error("❌ SharePoint devolvió un mensaje de error:")
                        with st.expander("📄 Mensaje completo"):
                            st.code(excel_data)
                        
                    elif data_type == 'parsed':
                        st.success("🎉 Datos ya parseados por excel_loader - inicializando directamente")
                        
                        if excel_data.get('status') == 'success':
                            with st.expander("🔍 Debug: Estructura de datos parseados"):
                                st.write("**Status:**", excel_data.get('status'))
                                st.write("**Message:**", excel_data.get('message'))
                                
                                data_content = excel_data.get('data', {})
                                st.write("**Datos disponibles:**", list(data_content.keys()))
                                
                                for key, value in data_content.items():
                                    st.write(f"**{key}:** {type(value)}")
                                    if isinstance(value, pd.DataFrame):
                                        st.write(f"  - Shape: {value.shape}")
                                        st.write(f"  - Columnas: {list(value.columns)}")
                            
                            if controller and controller.initialize_with_data(excel_data):
                                st.success("✅ Datos cargados correctamente desde SharePoint")
                                st.balloons()
                                
                                metadata = excel_data.get('metadata', {})
                                sheets_processed = metadata.get('sheets_processed', [])
                                st.info(f"📊 Hojas procesadas: {', '.join(sheets_processed)}")
                                
                                st.rerun()
                            else:
                                st.error("❌ Error inicializando controlador con datos parseados")
                                
                                if controller:
                                    with st.expander("🔍 Debug Controller Detallado"):
                                        debug_info = controller.get_debug_info()
                                        st.json(debug_info)
                        
                        elif excel_data.get('status') == 'error':
                            st.error(f"❌ Error en datos parseados: {excel_data.get('message')}")
                            metadata = excel_data.get('metadata', {})
                            
                            if 'errors' in metadata and metadata['errors']:
                                st.markdown("**Errores específicos:**")
                                for error in metadata['errors'][:5]:
                                    st.error(f"• {error}")
                    
                    elif data_type == 'raw_excel':
                        st.info("⚙️ Datos raw detectados - parseando manualmente...")
                        
                        if parser_available and parse_excel:
                            try:
                                parsed_data = parse_excel(excel_data)
                                
                                if parsed_data and parsed_data.get('status') in ['success', 'partial_success']:
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
                    
                    else:
                        st.error(f"❌ Tipo de datos no soportado: {data_type}")
                        st.write(f"Descripción: {description}")
                
                else:
                    st.error("❌ Módulos no disponibles")
                    
            except Exception as e:
                st.error(f"❌ Error crítico durante carga: {e}")
                st.exception(e)

with col3:
    if st.button("📁 Subir Excel Local", help="Subir archivo Excel desde tu computadora"):
        st.info("🔄 Funcionalidad próximamente disponible")

with col4:
    if st.button("🐛 Debug Info", help="Mostrar información de debug"):
        if controller:
            debug_info = controller.get_debug_info()
            with st.expander("🔍 Información de Debug"):
                st.json(debug_info)
        else:
            st.error("Controller no disponible")

# ================================================================
# CONTENIDO PRINCIPAL - SOLO SI HAY CONTROLADOR INICIALIZADO
# ================================================================
if controller and controller.is_initialized:
    
    # ================================================================
    # BARRA LATERAL - FILTROS ✅ CORREGIDOS
    # ================================================================
    with st.sidebar:
        st.markdown("## 🎯 Panel de Control")
        
        # ✅ CORRECCIÓN: Selector de modo de análisis unificado
        analysis_mode = st.radio(
            "**Modo de Análisis:**",
            ["📊 Análisis Individual", "📈 Comparación Multi-período"],
            help="Selecciona el tipo de análisis que deseas realizar"
        )
        
        if analysis_mode == "📊 Análisis Individual":
            st.markdown("### 📅 Análisis Individual")
            available_months = controller.get_available_months()
            months_with_data = controller.get_months_with_data()
            
            # ✅ CORRECCIÓN: Usar month_year format consistente
            selected_month = st.selectbox(
                "**Seleccionar Período (Mes-Año):**", 
                available_months, 
                index=len(months_with_data)-1 if months_with_data else 0,
                help="Selecciona el período específico para análisis detallado (ej: Enero 2024)"
            )
            
        else:
            st.markdown("### 📈 Comparación Multi-período")
            available_months = controller.get_available_months()
            months_with_data = controller.get_months_with_data()
            
            # ✅ CORRECCIÓN: Usar same format para comparación
            selected_months = st.multiselect(
                "**Períodos a Comparar (Mes-Año):**",
                available_months,
                default=months_with_data[-6:] if len(months_with_data) >= 6 else months_with_data,
                help="Selecciona múltiples períodos para comparar (ej: Enero 2024, Febrero 2024)"
            )
        
        st.markdown("---")
        
        # ✅ INFORMACIÓN ADICIONAL: Mostrar años disponibles
        if controller.is_initialized:
            st.markdown("### 📊 Información de Datos")
            
            # Obtener años únicos de los datos
            years_found = set()
            if controller.compras_data is not None and 'año' in controller.compras_data.columns:
                years_compras = controller.compras_data['año'].unique()
                years_found.update(years_compras)
            if controller.ventas_data is not None and 'año' in controller.ventas_data.columns:
                years_ventas = controller.ventas_data['año'].unique()
                years_found.update(years_ventas)
            
            if years_found:
                years_sorted = sorted([int(y) for y in years_found if pd.notna(y) and y > 0])
                st.info(f"📅 **Años con datos:** {', '.join(map(str, years_sorted))}")
                st.info(f"📊 **Total períodos:** {len(available_months)}")
    
    # ================================================================
    # TABS PRINCIPALES: COMPRAS Y VENTAS
    # ================================================================
    tab1, tab2 = st.tabs(["🛒 Compras KCTN", "💰 Ventas KCTN"])
    
    # ================================================================
    # TAB 1: COMPRAS KCTN (YA ESTABA CORRECTO)
    # ================================================================
    with tab1:
        
        if analysis_mode == "📊 Análisis Individual":
            # ================================================================
            # COMPRAS - ANÁLISIS INDIVIDUAL
            # ================================================================
            
            compras_kpis = controller.get_compras_kpis(selected_month)
            
            st.markdown(f"""
            <div class="section-header">
                <h3 class="section-title">📊 KPIs Compras - {selected_month}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not compras_kpis['has_data']:
                st.info(f"📅 {selected_month} - Datos de compras pendientes")
            
            # 4 KPI Cards en 2 filas
            col1, col2 = st.columns(2)
            
            with col1:
                display_kpi_card(
                    "💰 Total Valor de Compras",
                    f"€{compras_kpis['total_compras']:,.0f}",
                    [
                        ("Proveedores Activos", f"{compras_kpis['proveedores_activos_count']}"),
                        ("Departamentos", f"{len(compras_kpis['compras_por_departamento'])}"),
                    ],
                    "compras"
                )
            
            with col2:
                display_kpi_card(
                    "🏭 Proveedores Materia Prima",
                    f"€{compras_kpis['total_materia_prima']:,.0f}",
                    [
                        ("Proveedores M.P.", f"{compras_kpis['proveedores_materia_prima_count']}"),
                        ("% del Total", f"{(compras_kpis['total_materia_prima']/compras_kpis['total_compras']*100) if compras_kpis['total_compras'] > 0 else 0:.1f}%"),
                    ],
                    "proveedores"
                )
            
            col3, col4 = st.columns(2)
            
            with col3:
                if compras_kpis['compras_por_departamento']:
                    top_depto = max(compras_kpis['compras_por_departamento'].items(), key=lambda x: x[1])
                    display_kpi_card(
                        "📊 Departamento Principal",
                        f"€{top_depto[1]:,.0f}",
                        [
                            ("Departamento", top_depto[0]),
                            ("% del Total", f"{(top_depto[1]/compras_kpis['total_compras']*100) if compras_kpis['total_compras'] > 0 else 0:.1f}%"),
                        ],
                        "default"
                    )
                else:
                    display_kpi_card("📊 Departamento Principal", "€0", [("Sin datos", "")], "default")
            
            with col4:
                display_kpi_card(
                    "🤝 Proveedores Activos",
                    f"{compras_kpis['proveedores_activos_count']}",
                    [
                        ("Total Compras", f"€{compras_kpis['total_compras']:,.0f}"),
                        ("Promedio/Proveedor", f"€{(compras_kpis['total_compras']/compras_kpis['proveedores_activos_count']) if compras_kpis['proveedores_activos_count'] > 0 else 0:,.0f}"),
                    ],
                    "default"
                )
            
            # Gráficos Compras Individuales
            st.markdown(f"""
            <div class="section-header">
                <h3 class="section-title">📈 Análisis Gráfico Compras - {selected_month}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Compras por Departamento")
                fig_barras_depto = controller.create_compras_barras_departamento(selected_month)
                st.plotly_chart(fig_barras_depto, use_container_width=True)
            
            with col2:
                st.subheader("🏭 Materia Prima por Proveedor")
                fig_pie_materia = controller.create_compras_pie_materia_prima(selected_month)
                st.plotly_chart(fig_pie_materia, use_container_width=True)
        
        else:
            # ================================================================
            # COMPRAS - COMPARACIÓN MULTI-MES
            # ================================================================
            
            if not selected_months:
                st.warning("⚠️ Selecciona al menos un período para comparar")
            else:
                st.markdown("""
                <div class="section-header">
                    <h3 class="section-title">📊 Tabla Comparativa KPIs Compras</h3>
                </div>
                """, unsafe_allow_html=True)
                
                kpi_table = controller.create_compras_kpi_table(selected_months)
                
                if not kpi_table.empty:
                    st.dataframe(kpi_table, use_container_width=True, hide_index=True)
                    
                    csv_data = kpi_table.to_csv(index=False)
                    st.download_button(
                        label="📄 Descargar Tabla KPIs Compras",
                        data=csv_data,
                        file_name=f"KPIs_Compras_Comparativa_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No hay datos disponibles para generar la tabla comparativa")
    
    # ================================================================
    # TAB 2: VENTAS KCTN ✅ CORREGIDAS
    # ================================================================
    with tab2:
        
        if analysis_mode == "📊 Análisis Individual":
            # ================================================================
            # VENTAS - ANÁLISIS INDIVIDUAL ✅ CORREGIDO
            # ================================================================
            
            # ✅ CORRECCIÓN: Usar selected_month (que ya incluye año)
            ventas_kpis = controller.get_ventas_kpis(selected_month)
            
            st.markdown(f"""
            <div class="section-header">
                <h3 class="section-title">📊 KPIs Ventas - {selected_month}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not ventas_kpis['has_data']:
                st.info(f"📅 {selected_month} - Datos de ventas pendientes")
            
            # 4 KPI Cards en 2 filas
            col1, col2 = st.columns(2)
            
            with col1:
                display_kpi_card(
                    "💰 Total Ventas Mensuales",
                    f"€{ventas_kpis['total_ventas']:,.0f}",
                    [
                        ("Total Kg", f"{ventas_kpis['total_kgs']:,.0f} kg"),
                        ("€/Kg Promedio", f"€{(ventas_kpis['total_ventas']/ventas_kpis['total_kgs']) if ventas_kpis['total_kgs'] > 0 else 0:.2f}"),
                    ],
                    "ventas"
                )
            
            with col2:
                display_kpi_card(
                    "⚖️ Total Kg Mensuales",
                    f"{ventas_kpis['total_kgs']:,.0f} kg",
                    [
                        ("Clientes Activos", f"{ventas_kpis['clientes_activos_count']}"),
                        ("Kg/Cliente", f"{(ventas_kpis['total_kgs']/ventas_kpis['clientes_activos_count']) if ventas_kpis['clientes_activos_count'] > 0 else 0:,.0f} kg"),
                    ],
                    "default"
                )
            
            col3, col4 = st.columns(2)
            
            with col3:
                productos_count = len(ventas_kpis['categorias_vendidas'])
                display_kpi_card(
                    "📦 Productos Vendidos",
                    f"{productos_count}",
                    [
                        ("Categorías", f"{productos_count} tipos"),
                        ("Diversificación", "Alta" if productos_count > 3 else "Media" if productos_count > 1 else "Baja"),
                    ],
                    "default"
                )
            
            with col4:
                display_kpi_card(
                    "🤝 Clientes Activos",
                    f"{ventas_kpis['clientes_activos_count']}",
                    [
                        ("Total Ventas", f"€{ventas_kpis['total_ventas']:,.0f}"),
                        ("€/Cliente", f"€{(ventas_kpis['total_ventas']/ventas_kpis['clientes_activos_count']) if ventas_kpis['clientes_activos_count'] > 0 else 0:,.0f}"),
                    ],
                    "clientes"
                )
            
            # Lista de clientes (si hay datos)
            if ventas_kpis['clientes_lista']:
                st.markdown("**📋 Lista de Clientes Activos:**")
                clientes_text = ", ".join(ventas_kpis['clientes_lista'][:10])
                if len(ventas_kpis['clientes_lista']) > 10:
                    clientes_text += f" y {len(ventas_kpis['clientes_lista'])-10} más..."
                st.info(clientes_text)
            
            # ================================================================
            # GRÁFICOS VENTAS INDIVIDUALES ✅ CORREGIDOS
            # ================================================================
            st.markdown(f"""
            <div class="section-header">
                <h3 class="section-title">📈 Análisis Gráfico Ventas - {selected_month}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # ✅ CORRECCIÓN: Usar selected_month en todos los gráficos
            st.subheader("📈 Tendencia de Facturación")
            fig_tendencia = controller.create_ventas_tendencia_facturado(selected_month)
            st.plotly_chart(fig_tendencia, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🤝 Ventas por Cliente")
                fig_barras_cliente = controller.create_ventas_barras_cliente(selected_month)
                st.plotly_chart(fig_barras_cliente, use_container_width=True)
            
            with col2:
                st.subheader("📦 Distribución por Producto")
                fig_pie_productos = controller.create_ventas_pie_productos(selected_month)
                st.plotly_chart(fig_pie_productos, use_container_width=True)
        
        else:
            # ================================================================
            # VENTAS - COMPARACIÓN MULTI-MES ✅ CORREGIDAS
            # ================================================================
            
            if not selected_months:
                st.warning("⚠️ Selecciona al menos un período para comparar")
            else:
                st.markdown("""
                <div class="section-header">
                    <h3 class="section-title">📊 Tabla Comparativa KPIs Ventas</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # ✅ CORRECCIÓN: Usar selected_months con formato month_year
                kpi_table = controller.create_ventas_kpi_table(selected_months)
                
                if not kpi_table.empty:
                    st.dataframe(kpi_table, use_container_width=True, hide_index=True)
                    
                    csv_data = kpi_table.to_csv(index=False)
                    st.download_button(
                        label="📄 Descargar Tabla KPIs Ventas",
                        data=csv_data,
                        file_name=f"KPIs_Ventas_Comparativa_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No hay datos disponibles para generar la tabla comparativa")
                
                st.markdown("""
                <div class="section-header">
                    <h3 class="section-title">📈 Análisis Comparativo Ventas</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # ✅ CORRECCIÓN: Usar selected_months con formato correcto
                st.subheader("📈 Evolución Ventas Totales")
                fig_evolucion_ventas = controller.create_ventas_evolucion_chart(selected_months)
                st.plotly_chart(fig_evolucion_ventas, use_container_width=True)

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
    ### 🚀 Bienvenido al Dashboard de Compras y Ventas KCTN ✅ CORREGIDO
    
    Para comenzar a usar el sistema, carga los datos del Excel de compras y ventas:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔗 Conexión SharePoint
        **Datos en tiempo real desde SharePoint**
        
        **Hojas esperadas:**
        - ✅ "Compras KCTN" (página 4) - Headers fila 2
        - ✅ "Ventas KCTN" (página 5) - Headers fila 2
        
        **✅ CORRECCIONES APLICADAS:**
        - 🎯 Filtros unificados mes-año para ambos tabs
        - 📊 KPIs precisos sin mezcla de años diferentes  
        - 📈 Gráficos corregidos para usar filtros mes-año
        - 🔄 Consistencia total entre Compras y Ventas
        """)
        
        if st.button("🔗 Conectar SharePoint", key="connect_sp", type="primary"):
            st.info("🔄 Usar el botón 'Cargar desde SharePoint' en la parte superior")
    
    with col2:
        st.markdown("""
        #### 📁 Carga Manual
        **Subir archivo Excel local**
        
        **Formato esperado:**
        - 📋 Archivo Excel (.xlsx)
        - 📄 Hojas: "Compras KCTN", "Ventas KCTN"
        - 📊 Headers en fila 2, datos desde fila 3
        - 📅 Columnas de Mes (D/C) y Año (E/B) para separar períodos
        - 💰 Columnas de valores numéricos
        
        **✅ VALIDACIÓN MULTI-AÑO:**
        El sistema ahora maneja correctamente múltiples años
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
    <p><strong>🧄 Garlic & Beyond Dashboard Compras y Ventas v2.0 ✅ CORREGIDO</strong></p>
    <p>Sistema avanzado de análisis comercial con filtros mes-año unificados • Desarrollado por GANDB Team</p>
    <p>© 2025 Garlic & Beyond - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
"""
CFI_11_Ventas.py - Dashboard Ventas CFI Garlic & Beyond VERSIÓN CORREGIDA
========================================================================
Dashboard completo de Ventas para CFI (Comagra Food Ingredients).
VERSIÓN CORREGIDA para manejo de 3 hojas separadas según estructura real del Excel.

Funcionalidades principales:
- TAB VENTAS: KPIs de ventas por mes individual y comparativo multi-mes
- TAB PEDIDOS: Análisis de pedidos pendientes por mes individual
- TAB CONTRATOS: Gestión de contratos abiertos
- Conexión automática a SharePoint
- Interfaz elegante con 3 tabs separados

Estructura del Excel:
- Ventas 2025: Headers fila 3, datos desde fila 4
- Pedidos 2025: Headers fila 3, datos desde fila 4  
- Contratos Abiertos 2025: Headers fila 3, datos desde fila 4

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 2.0 - Dashboard CFI Tres Hojas
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
if 'page_config_set_cfi_ventas' not in st.session_state:
    st.set_page_config(
        page_title="Dashboard Ventas CFI - Garlic & Beyond",
        page_icon="🧄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set_cfi_ventas = True

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
        
        # Importar Excel Loader
        try:
            from utils.excel_loader import get_dataframe
            excel_available = True
        except ImportError:
            excel_available = False
            get_dataframe = None
        
        # Importar controlador CFI Ventas
        try:
            from utils.controller_CFI_11_Ventas import CFIVentasController
            controller_available = True
        except ImportError:
            controller_available = False
            CFIVentasController = None
        
        # Importar parser CFI Ventas
        try:
            from utils.parser_CFI_11_Ventas import parse_excel
            parser_available = True
        except ImportError:
            parser_available = False
            parse_excel = None
        
        return excel_available, controller_available, parser_available, get_dataframe, CFIVentasController, parse_excel
        
    except Exception as e:
        st.error(f"Error en importaciones: {e}")
        return False, False, False, None, None, None

excel_available, controller_available, parser_available, get_dataframe, CFIVentasController, parse_excel = safe_import()

# ================================================================
# CSS PERSONALIZADO PARA CFI VENTAS
# ================================================================
st.markdown("""
<style>
    /* Importar Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para CFI Ventas */
    :root {
        --primary-color: #1976D2;
        --secondary-color: #42A5F5;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --info-color: #00BCD4;
        --text-primary: #0D47A1;
        --text-secondary: #1565C0;
        --background-white: #ffffff;
        --background-light: #E3F2FD;
        --border-light: #BBDEFB;
        --shadow-sm: 0 1px 2px 0 rgba(25, 118, 210, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(25, 118, 210, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(25, 118, 210, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(25, 118, 210, 0.1);
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
    
    /* Header principal para CFI Ventas */
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
        content: '📈';
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
    
    /* KPI Cards específicas para CFI Ventas */
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
    
    .kpi-card-ventas::before {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .kpi-card-clientes::before {
        background: linear-gradient(90deg, var(--success-color), #66BB6A);
    }
    
    .kpi-card-precio::before {
        background: linear-gradient(90deg, var(--warning-color), #FFB74D);
    }
    
    .kpi-card-producto::before {
        background: linear-gradient(90deg, var(--info-color), #4DD0E1);
    }
    
    .kpi-card-estrella::before {
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
        background: linear-gradient(135deg, var(--background-light) 0%, #E1F5FE 100%);
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
    
    /* Cliente cards específicas */
    .cliente-card {
        background: var(--background-white);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .cliente-card h4 {
        color: var(--primary-color);
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .cliente-metric {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .cliente-metric-label {
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .cliente-metric-value {
        color: var(--text-primary);
        font-weight: 600;
    }
    
    /* Cards para pedidos */
    .pedidos-card {
        background: var(--background-white);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-lg);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .pedidos-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--success-color), #66BB6A);
    }
    
    .pedidos-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .pedidos-list {
        max-height: 200px;
        overflow-y: auto;
        text-align: left;
    }
    
    .pedidos-item {
        padding: 0.5rem;
        border-bottom: 1px solid var(--border-light);
        font-size: 0.9rem;
        color: var(--text-secondary);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem; }
        .main-header h2 { font-size: 1.5rem; }
        .kpi-card { padding: 1.5rem 1rem; }
        .section-header { padding: 1rem 1.5rem; }
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: var(--background-light);
        border-radius: 10px 10px 0 0;
        color: var(--text-primary);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# INICIALIZACIÓN DEL CONTROLADOR
# ================================================================
@st.cache_resource
def init_controller():
    """Inicializa el controlador con cache."""
    if controller_available and CFIVentasController:
        return CFIVentasController()
    return None

if 'cfi_ventas_controller' not in st.session_state:
    st.session_state.cfi_ventas_controller = init_controller()

controller = st.session_state.cfi_ventas_controller

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

def display_cliente_promedio_card(cliente_data):
    """Muestra card de promedio por cliente."""
    st.markdown(f"""
    <div class="cliente-card">
        <h4>{cliente_data['cliente']}</h4>
        <div class="cliente-metric">
            <span class="cliente-metric-label">Kg Promedio:</span>
            <span class="cliente-metric-value">{cliente_data['kg_promedio']:,.0f} kg</span>
        </div>
        <div class="cliente-metric">
            <span class="cliente-metric-label">Precio Promedio:</span>
            <span class="cliente-metric-value">€{cliente_data['precio_promedio']:.2f}/kg</span>
        </div>
        <div class="cliente-metric">
            <span class="cliente-metric-label">Valor Total Promedio:</span>
            <span class="cliente-metric-value">€{cliente_data['total_promedio']:,.0f}</span>
        </div>
        <div class="cliente-metric">
            <span class="cliente-metric-label">Total Ventas:</span>
            <span class="cliente-metric-value">€{cliente_data['total_sum']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_pedidos_list_card(title, items_list, card_type="clientes"):
    """Muestra card con lista de items de pedidos."""
    items_html = ""
    for item in items_list[:20]:  # Límite a 20 items
        items_html += f'<div class="pedidos-item">• {item}</div>'
    
    if len(items_list) > 20:
        items_html += f'<div class="pedidos-item"><strong>... y {len(items_list) - 20} más</strong></div>'
    
    st.markdown(f"""
    <div class="pedidos-card">
        <div class="pedidos-title">{title}</div>
        <div class="pedidos-list">
            {items_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# HEADER PRINCIPAL
# ================================================================
st.markdown("""
<div class="main-header">
    <h1>📈 Dashboard Ventas, Pedidos y Contratos CFI</h1>
    <h2>Comagra Food Ingredients - Sistema Integral de Gestión</h2>
    <p>Análisis completo de ventas realizadas, pedidos pendientes y contratos abiertos</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# INFORMACIÓN DE PERÍODO
# ================================================================
st.markdown("""
<div class="alert alert-info">
    <strong>📅 Período de Análisis:</strong> Año 2025 | 
    <strong>🔄 Última Actualización:</strong> """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """
</div>
""", unsafe_allow_html=True)

# ================================================================
# PANEL DE CONTROL CON LÓGICA DE CARGA
# ================================================================
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if controller and controller.is_initialized:
        status = controller.get_status()
        st.markdown(f"""
        <div class="status-container">
            <div style="display: flex; align-items: center;">
                <span class="status-indicator status-green"></span>
                <strong>✅ Sistema Activo:</strong> {status['months_with_data']} meses con datos
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                📊 €{status['total_sales']:,.0f} ventas | 🛒 {status['total_pedidos']} pedidos | 
                📋 {status['total_contratos']} contratos | 👥 {status['unique_clients']} clientes | 
                📦 {status['unique_products']} productos
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

with col2:
    if st.button("🔄 Cargar desde SharePoint", help="Cargar datos reales desde SharePoint"):
        with st.spinner("Cargando datos desde SharePoint..."):
            try:
                if excel_available and get_dataframe:
                    st.info("📥 Descargando datos desde SharePoint...")
                    excel_data = get_dataframe('CFI_11_Ventas')
                    
                    if excel_data is None:
                        st.error("❌ No se pudieron obtener datos de SharePoint")
                    
                    elif isinstance(excel_data, str):
                        st.error(f"❌ Error de SharePoint: {excel_data}")
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'success':
                        st.success("🎉 Datos ya parseados - inicializando directamente")
                        
                        if controller and controller.initialize_with_data(excel_data):
                            st.success("✅ Datos cargados correctamente desde SharePoint")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Error inicializando controlador")
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'error':
                        st.error(f"❌ Error en datos: {excel_data.get('message')}")
                    
                    else:
                        st.info("⚙️ Parseando datos...")
                        
                        if parser_available and parse_excel:
                            try:
                                parsed_data = parse_excel(excel_data)
                                
                                if parsed_data and parsed_data.get('status') == 'success':
                                    if controller and controller.initialize_with_data(parsed_data):
                                        st.success("✅ Datos parseados y cargados correctamente")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error inicializando controlador")
                                else:
                                    error_msg = parsed_data.get('message', 'Error desconocido') if parsed_data else 'Sin respuesta del parser'
                                    st.error(f"❌ Error parseando datos: {error_msg}")
                            
                            except Exception as e:
                                st.error(f"❌ Excepción parseando datos: {e}")
                        else:
                            st.error("❌ Parser no disponible")
                
                else:
                    st.error("❌ Módulos no disponibles")
                    
            except Exception as e:
                st.error(f"❌ Error crítico: {e}")

with col3:
    if st.button("📁 Subir Excel Local", help="Subir archivo Excel desde computadora"):
        st.info("🔄 Funcionalidad próximamente disponible")

# ================================================================
# CONTENIDO PRINCIPAL - TABS
# ================================================================
if controller and controller.is_initialized:
    
    # Verificar que hay datos disponibles
    available_months = controller.get_available_months()
    
    if not available_months:
        st.warning("⚠️ No hay datos disponibles")
    else:
        # ================================================================
        # CREAR TABS PRINCIPALES
        # ================================================================
        tab1, tab2, tab3 = st.tabs(["📊 VENTAS", "🛒 PEDIDOS", "📋 CONTRATOS 2025"])
        
        # ================================================================
        # TAB 1: VENTAS 2025
        # ================================================================
        with tab1:
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📊 Análisis de Ventas 2025</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Barra lateral para filtros de ventas
            with st.sidebar:
                st.markdown("## 🎯 Filtros Ventas")
                
                # Selector de modo de análisis
                analysis_mode = st.radio(
                    "**Modo de Análisis:**",
                    ["📊 Análisis Individual", "📈 Comparación Multi-mes"],
                    help="Selecciona el tipo de análisis para ventas"
                )
                
                if analysis_mode == "📊 Análisis Individual":
                    st.markdown("### 📅 Análisis Individual")
                    default_index = len(available_months)-1 if available_months else 0
                    default_index = max(0, min(default_index, len(available_months)-1))
                    
                    selected_month = st.selectbox(
                        "**Seleccionar Mes:**", 
                        available_months, 
                        index=default_index,
                        help="Selecciona el mes para análisis detallado"
                    )
                else:
                    st.markdown("### 📈 Comparación Multi-mes")
                    default_selection = available_months[-3:] if len(available_months) >= 3 else available_months
                    
                    selected_months = st.multiselect(
                        "**Meses a Comparar:**",
                        available_months,
                        default=default_selection,
                        help="Selecciona múltiples meses para comparar"
                    )
                
                st.markdown("---")
            
            # ANÁLISIS INDIVIDUAL DE VENTAS
            if analysis_mode == "📊 Análisis Individual":
                kpis = controller.get_monthly_kpis(selected_month)
                
                # KPI Cards (5 cards según especificaciones)
                st.markdown(f"""
                <div class="section-header">
                    <h3 class="section-title">📊 KPIs Principales - {selected_month.title()}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if not kpis['has_data']:
                    st.info(f"📅 {selected_month.title()} - Datos pendientes de cargar")
                
                # 5 KPI Cards
                col1, col2 = st.columns(2)
                
                with col1:
                    display_kpi_card(
                        "💰 Ventas Totales del Mes",
                        f"€{kpis['ventas_totales']:,.0f}",
                        [
                            ("Kg Totales", f"{kpis['kg_totales']:,.0f} kg"),
                            ("Pallets Totales", f"{kpis['pallets_totales']:,.0f}"),
                            ("Registros", f"{kpis['registros_totales']}")
                        ],
                        "ventas"
                    )
                
                with col2:
                    display_kpi_card(
                        "👥 Clientes Activos",
                        f"{kpis['clientes_activos']}",
                        [
                            ("Cliente Estrella", kpis['cliente_estrella']),
                            ("Sus Ventas", f"€{kpis['cliente_estrella_ventas']:,.0f}"),
                            ("Promedio/Cliente", f"€{kpis['ventas_totales']/kpis['clientes_activos'] if kpis['clientes_activos'] > 0 else 0:,.0f}")
                        ],
                        "clientes"
                    )
                
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    display_kpi_card(
                        "🌟 Cliente Estrella",
                        kpis['cliente_estrella'],
                        [
                            ("Sus Ventas", f"€{kpis['cliente_estrella_ventas']:,.0f}"),
                            ("% del Total", f"{(kpis['cliente_estrella_ventas']/kpis['ventas_totales']*100) if kpis['ventas_totales'] > 0 else 0:.1f}%")
                        ],
                        "estrella"
                    )
                
                with col4:
                    display_kpi_card(
                        "💵 Precio Promedio",
                        f"€{kpis['precio_promedio']:.2f}/kg",
                        [
                            ("Ventas/Kg", f"€{kpis['ventas_totales']/kpis['kg_totales'] if kpis['kg_totales'] > 0 else 0:.2f}"),
                            ("Kg/Registro", f"{kpis['kg_totales']/kpis['registros_totales'] if kpis['registros_totales'] > 0 else 0:.0f}")
                        ],
                        "precio"
                    )
                
                with col5:
                    display_kpi_card(
                        "📦 Producto Estrella",
                        kpis['producto_estrella'],
                        [
                            ("Sus Ventas", f"€{kpis['producto_estrella_ventas']:,.0f}"),
                            ("% del Total", f"{(kpis['producto_estrella_ventas']/kpis['ventas_totales']*100) if kpis['ventas_totales'] > 0 else 0:.1f}%")
                        ],
                        "producto"
                    )
                
                # Gráficos de Ventas
                st.markdown(f"""
                <div class="section-header">
                    <h3 class="section-title">📈 Análisis Gráfico - {selected_month.title()}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("💰 Ventas por Producto")
                    fig_ventas_producto = controller.create_ventas_por_producto_chart(selected_month)
                    st.plotly_chart(fig_ventas_producto, use_container_width=True)
                
                with col2:
                    st.subheader("👥 Ventas por Cliente")
                    fig_ventas_cliente = controller.create_ventas_por_cliente_chart(selected_month)
                    st.plotly_chart(fig_ventas_cliente, use_container_width=True)
                
                col3, col4 = st.columns(2)
                
                with col3:
                    st.subheader("📦 Kilogramos por Producto")
                    fig_kg_producto = controller.create_kg_por_producto_chart(selected_month)
                    st.plotly_chart(fig_kg_producto, use_container_width=True)
                
                with col4:
                    st.subheader("🏭 Kilogramos por Cliente")
                    fig_kg_cliente = controller.create_kg_por_cliente_chart(selected_month)
                    st.plotly_chart(fig_kg_cliente, use_container_width=True)
                
                # Promedio por Cliente
                st.markdown(f"""
                <div class="section-header">
                    <h3 class="section-title">👥 Análisis Detallado por Cliente - {selected_month.title()}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                cliente_data = controller.get_promedio_por_cliente_data(selected_month)
                
                if not cliente_data.empty:
                    clientes_per_row = 3
                    cliente_rows = [cliente_data.iloc[i:i+clientes_per_row] for i in range(0, len(cliente_data), clientes_per_row)]
                    
                    for row in cliente_rows:
                        cols = st.columns(clientes_per_row)
                        for idx, (_, cliente) in enumerate(row.iterrows()):
                            with cols[idx]:
                                display_cliente_promedio_card(cliente)
                    
                    # Tabla resumen
                    st.markdown("### 📋 Tabla Resumen Clientes")
                    
                    cliente_display = cliente_data.copy()
                    cliente_display['kg_promedio'] = cliente_display['kg_promedio'].apply(lambda x: f"{x:,.0f} kg")
                    cliente_display['precio_promedio'] = cliente_display['precio_promedio'].apply(lambda x: f"€{x:.2f}")
                    cliente_display['total_promedio'] = cliente_display['total_promedio'].apply(lambda x: f"€{x:,.0f}")
                    cliente_display['total_sum'] = cliente_display['total_sum'].apply(lambda x: f"€{x:,.0f}")
                    
                    cliente_display.columns = ['Cliente', 'Kg Promedio', 'Kg Total', 'Precio Promedio', 'Venta Promedio', 'Ventas Totales', 'Pallets Promedio', 'Pallets Total']
                    
                    st.dataframe(cliente_display, use_container_width=True, hide_index=True)
                else:
                    st.info(f"📅 No hay datos de clientes para {selected_month}")
            
            # COMPARACIÓN MULTI-MES DE VENTAS
            else:
                if not selected_months:
                    st.warning("⚠️ Selecciona al menos un mes para comparar")
                else:
                    # KPIs Comparativos
                    st.markdown("""
                    <div class="section-header">
                        <h3 class="section-title">📊 KPIs Comparativos</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    comp_kpis = controller.get_comparative_kpis(selected_months)
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        display_kpi_card(
                            "📈 Cambio en Ventas",
                            comp_kpis.get('cambio_ventas_pct', 'N/A'),
                            [
                                ("Comparación", "Entre meses"),
                                ("Periodo", f"{len(selected_months)} meses")
                            ],
                            "ventas"
                        )
                    
                    with col2:
                        display_kpi_card(
                            "🏭 Cambio en Kg",
                            comp_kpis.get('cambio_kg_pct', 'N/A'),
                            [
                                ("Kg Totales", f"{comp_kpis.get('kg_totales_periodo', 0):,.0f}")
                            ],
                            "producto"
                        )
                    
                    with col3:
                        display_kpi_card(
                            "⭐ Cliente Estrella",
                            comp_kpis.get('cliente_estrella_periodo', 'N/A'),
                            [
                                ("Del Periodo", "Todos los meses")
                            ],
                            "estrella"
                        )
                    
                    with col4:
                        display_kpi_card(
                            "💰 Ventas Totales",
                            f"€{comp_kpis.get('ventas_totales_periodo', 0):,.0f}",
                            [
                                ("Promedio/Mes", f"€{comp_kpis.get('ventas_totales_periodo', 0)/len(selected_months) if selected_months else 0:,.0f}")
                            ],
                            "ventas"
                        )
                    
                    with col5:
                        display_kpi_card(
                            "💵 Precio Promedio",
                            f"€{comp_kpis.get('precio_promedio_periodo', 0):.2f}/kg",
                            [
                                ("Del Periodo", "Promedio ponderado")
                            ],
                            "precio"
                        )
                    
                    # Tabla Comparativa
                    st.markdown("""
                    <div class="section-header">
                        <h3 class="section-title">📋 Tabla Comparativa de KPIs</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    kpi_table = controller.create_multi_month_kpi_table(selected_months)
                    
                    if not kpi_table.empty:
                        st.dataframe(kpi_table, use_container_width=True, hide_index=True, height=400)
                        
                        csv_data = kpi_table.to_csv(index=False)
                        st.download_button(
                            label="📄 Descargar Tabla KPIs",
                            data=csv_data,
                            file_name=f"KPIs_Ventas_CFI_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    
                    # Gráficos Evolutivos
                    st.markdown("""
                    <div class="section-header">
                        <h3 class="section-title">📈 Análisis Evolutivo entre Meses</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader("📈 Evolución de Ventas Totales")
                    fig_evolucion_ventas = controller.create_evolucion_ventas_chart(selected_months)
                    st.plotly_chart(fig_evolucion_ventas, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🏭 Evolución de Kg Vendidos")
                        fig_evolucion_kg = controller.create_evolucion_kg_chart(selected_months)
                        st.plotly_chart(fig_evolucion_kg, use_container_width=True)
                    
                    with col2:
                        st.subheader("💵 Evolución de Precio Promedio")
                        fig_evolucion_precio = controller.create_evolucion_precio_chart(selected_months)
                        st.plotly_chart(fig_evolucion_precio, use_container_width=True)
        
        # ================================================================
        # TAB 2: PEDIDOS 2025
        # ================================================================
        with tab2:
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">🛒 Análisis de Pedidos Pendientes 2025</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Obtener meses disponibles para pedidos
            available_months_pedidos = controller.get_available_months_pedidos()
            
            if not available_months_pedidos:
                st.info("📅 No hay datos de pedidos disponibles")
            else:
                # Selector de mes para pedidos (solo individual)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    selected_month_pedidos = st.selectbox(
                        "**Seleccionar Mes de Pedidos:**",
                        available_months_pedidos,
                        index=0,
                        help="Los pedidos se analizan solo por mes individual"
                    )
                
                # Obtener KPIs de pedidos
                pedidos_kpis = controller.get_pedidos_kpis(selected_month_pedidos)
                
                if not pedidos_kpis['has_data']:
                    st.info(f"📅 No hay pedidos para {selected_month_pedidos}")
                else:
                    # Cards de Pedidos (3 cards según especificaciones)
                    st.markdown(f"""
                    <div class="section-header">
                        <h3 class="section-title">📊 KPIs Pedidos - {selected_month_pedidos.title()}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        clientes_list = controller.get_clientes_pedidos_list(selected_month_pedidos)
                        display_pedidos_list_card(
                            f"👥 Clientes ({len(clientes_list)})",
                            clientes_list,
                            "clientes"
                        )
                    
                    with col2:
                        productos_list = controller.get_productos_pedidos_list(selected_month_pedidos)
                        display_pedidos_list_card(
                            f"📦 Productos ({len(productos_list)})",
                            productos_list,
                            "productos"
                        )
                    
                    with col3:
                        display_kpi_card(
                            "💵 Precio Promedio Pedido",
                            f"€{pedidos_kpis['precio_promedio_pedido']:.2f}/kg",
                            [
                                ("Total Pedidos", f"€{pedidos_kpis['total_pedidos']:,.0f}"),
                                ("Kg Totales", f"{pedidos_kpis['kg_totales_pedidos']:,.0f} kg"),
                                ("Registros", f"{pedidos_kpis['registros_pedidos']}")
                            ],
                            "precio"
                        )
                    
                    # Gráfico de Pedidos por Cliente
                    st.markdown(f"""
                    <div class="section-header">
                        <h3 class="section-title">📈 Análisis Gráfico Pedidos - {selected_month_pedidos.title()}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader("🛒 Pedidos por Cliente (con detalles)")
                    fig_pedidos_cliente = controller.create_pedidos_por_cliente_chart(selected_month_pedidos)
                    st.plotly_chart(fig_pedidos_cliente, use_container_width=True)
                    
                    st.info("💡 **Interactivo:** Haz clic en las barras para ver número de pallets, kg y precio promedio")
        
        # ================================================================
        # TAB 3: CONTRATOS ABIERTOS 2025
        # ================================================================
        with tab3:
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📋 Gestión de Contratos Abiertos 2025</h3>
            </div>
            """, unsafe_allow_html=True)
            
            contratos_data = controller.get_contratos_abiertos_data()
            contratos_stats = controller.get_contratos_stats()
            
            if contratos_data.empty:
                st.info("📅 No hay contratos abiertos registrados en el sistema")
            else:
                # Estadísticas de contratos
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📋 Total Contratos", contratos_stats.get('total_contratos', 0))
                
                with col2:
                    st.metric("💰 Valor Total", f"€{contratos_stats.get('valor_total_contratos', 0):,.0f}")
                
                with col3:
                    st.metric("🏭 Kg Totales", f"{contratos_stats.get('kg_totales_contratos', 0):,.0f}")
                
                with col4:
                    st.metric("📦 Productos Únicos", contratos_stats.get('productos_en_contratos', 0))
                
                # Tabla de Contratos
                st.markdown("### 📄 Tabla Dinámica de Contratos Abiertos")
                st.dataframe(contratos_data, use_container_width=True, hide_index=True, height=400)
                
                # Botón de descarga
                csv_contratos = contratos_data.to_csv(index=False)
                st.download_button(
                    label="📄 Descargar Contratos Abiertos",
                    data=csv_contratos,
                    file_name=f"Contratos_Abiertos_CFI_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

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
    ### 🚀 Bienvenido al Dashboard de Ventas CFI
    
    Para comenzar a usar el sistema, carga los datos del Excel de ventas CFI desde SharePoint:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔗 Conexión SharePoint Recomendada
        
        **Características:**
        - ✅ Datos actualizados automáticamente
        - ✅ Procesa 3 hojas: Ventas 2025, Pedidos 2025, Contratos Abiertos 2025
        - ✅ Análisis completo con KPIs y gráficos
        
        **Datos que se cargarán:**
        - 📊 **Ventas 2025:** Análisis individual y comparativo
        - 🛒 **Pedidos 2025:** Pedidos pendientes por mes
        - 📋 **Contratos Abiertos:** Gestión de contratos
        """)
    
    with col2:
        st.markdown("""
        #### 📊 Funcionalidades Disponibles
        
        **Tab Ventas:**
        - 5 KPIs principales por mes
        - 4 gráficos de análisis
        - Comparación multi-mes
        - Análisis por cliente
        
        **Tab Pedidos:**
        - Lista de clientes y productos
        - Precio promedio por pedido
        - Gráfico interactivo por cliente
        
        **Tab Contratos:**
        - Tabla dinámica de contratos
        - Estadísticas generales
        - Descarga de reportes
        """)

# ================================================================
# FOOTER
# ================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: var(--text-secondary); padding: 2rem 0;'>
    <p><strong>📈 CFI Ventas Dashboard v2.0</strong></p>
    <p>Sistema integral de análisis de ventas, pedidos y contratos CFI</p>
    <p>© 2025 Garlic & Beyond x Pax Capital Partners - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
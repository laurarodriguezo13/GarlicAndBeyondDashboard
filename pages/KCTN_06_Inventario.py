"""
KCTN_06_Inventario.py - Dashboard de Inventario Garlic & Beyond
==============================================================
Dashboard de inventario para KCTN con KPIs principales y tabla de datos.
Diseño simple y elegante con estética Garlic & Beyond.

Funcionalidades:
- 2 KPI Cards principales (Total Kg, Total Euros)
- Tabla de inventario grande y estilizada  
- Carga desde SharePoint
- Estética corporativa Garlic & Beyond

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0 - Dashboard Inventario KCTN
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

# ================================================================
# CONFIGURACIÓN DE PÁGINA
# ================================================================
if 'page_config_set' not in st.session_state:
    st.set_page_config(
        page_title="Dashboard Inventario - Garlic & Beyond",
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
            from utils.controller_KCTN_06_Inventario import GarlicInventarioController
            controller_available = True
        except ImportError:
            try:
                from utils.controller_KCTN_06_Inventario import GarlicInventarioController
                controller_available = True
            except ImportError:
                controller_available = False
                GarlicInventarioController = None
        
        return excel_available, controller_available, get_dataframe, GarlicInventarioController
        
    except Exception as e:
        st.error(f"Error en importaciones: {e}")
        return False, False, None, None

excel_available, controller_available, get_dataframe, GarlicInventarioController = safe_import()

# ================================================================
# CSS PERSONALIZADO PARA GARLIC & BEYOND - INVENTARIO
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
        content: '📦';
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
    
    /* KPI Cards específicas para Inventario */
    .kpi-card {
        background: var(--background-white);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-xl);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .kpi-card:hover {
        transform: translateY(-8px);
        box-shadow: var(--shadow-xl);
    }
    
    .kpi-card-kg::before {
        background: linear-gradient(90deg, #1976D2, #42A5F5);
    }
    
    .kpi-card-euros::before {
        background: linear-gradient(90deg, #FF9800, #FFB74D);
    }
    
    /* Métricas para inventario */
    .kpi-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .kpi-value-huge {
        font-size: 3rem;
        font-weight: 800;
        color: var(--primary-color);
        margin: 1rem 0;
        line-height: 1;
        text-shadow: 0 2px 4px rgba(46, 125, 50, 0.1);
    }
    
    .kpi-subtitle {
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-secondary);
        margin-top: 1rem;
        opacity: 0.8;
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
        font-size: 1.5rem;
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
    
    /* Tabla de inventario SÚPER MEJORADA */
    .inventory-table-container {
        background: var(--background-white);
        border-radius: 20px;
        box-shadow: var(--shadow-xl);
        border: 1px solid var(--border-light);
        overflow: hidden;
        margin: 2rem 0;
        position: relative;
    }
    
    .inventory-table-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--success-color));
    }
    
    /* Estilo global de tabla Streamlit override */
    .inventory-table-container .stDataFrame {
        border: none !important;
    }
    
    .inventory-table-container .stDataFrame > div {
        border: none !important;
        border-radius: 0 !important;
    }
    
    /* Headers de la tabla */
    .inventory-table-container [data-testid="stDataFrame"] thead th {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 1.8rem 1.5rem !important;
        border: none !important;
        text-align: center !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-family: 'Inter', sans-serif !important;
        position: relative !important;
    }
    
    .inventory-table-container [data-testid="stDataFrame"] thead th:first-child {
        text-align: left !important;
        padding-left: 2rem !important;
    }
    
    .inventory-table-container [data-testid="stDataFrame"] thead th:first-child::before {
        content: '👤';
        margin-right: 8px;
        opacity: 0.8;
    }
    
    .inventory-table-container [data-testid="stDataFrame"] thead th:nth-child(2)::before {
        content: '⚖️';
        margin-right: 8px;
        opacity: 0.8;
    }
    
    .inventory-table-container [data-testid="stDataFrame"] thead th:nth-child(3)::before {
        content: '💰';
        margin-right: 8px;
        opacity: 0.8;
    }
    
    .inventory-table-container [data-testid="stDataFrame"] thead th:nth-child(4)::before {
        content: '📊';
        margin-right: 8px;
        opacity: 0.8;
    }
    
    /* Celdas del cuerpo de la tabla */
    .inventory-table-container [data-testid="stDataFrame"] tbody td {
        padding: 1.5rem 1.5rem !important;
        border-bottom: 1px solid #E8F5E8 !important;
        font-size: 1rem !important;
        text-align: center !important;
        vertical-align: middle !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    /* Primera columna (Proveedor) */
    .inventory-table-container [data-testid="stDataFrame"] tbody td:first-child {
        text-align: left !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        padding-left: 2rem !important;
        font-size: 1.05rem !important;
    }
    
    /* Segunda columna (Kg) */
    .inventory-table-container [data-testid="stDataFrame"] tbody td:nth-child(2) {
        font-weight: 600 !important;
        color: #1976D2 !important;
        font-family: 'Monaco', 'Menlo', monospace !important;
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 30%) !important;
        border-radius: 8px !important;
        margin: 0 4px !important;
    }
    
    /* Tercera columna (Euros) */
    .inventory-table-container [data-testid="stDataFrame"] tbody td:nth-child(3) {
        font-weight: 600 !important;
        color: #FF9800 !important;
        font-family: 'Monaco', 'Menlo', monospace !important;
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 30%) !important;
        border-radius: 8px !important;
        margin: 0 4px !important;
    }
    
    /* Cuarta columna (€/Kg) */
    .inventory-table-container [data-testid="stDataFrame"] tbody td:nth-child(4) {
        font-weight: 600 !important;
        color: var(--primary-color) !important;
        font-family: 'Monaco', 'Menlo', monospace !important;
        background: linear-gradient(135deg, var(--background-light) 0%, #C8E6C9 30%) !important;
        border-radius: 8px !important;
        margin: 0 4px !important;
    }
    
    /* Filas alternas */
    .inventory-table-container [data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background-color: #F9FBE7 !important;
    }
    
    .inventory-table-container [data-testid="stDataFrame"] tbody tr:nth-child(odd) {
        background-color: var(--background-white) !important;
    }
    
    /* Efecto hover en filas */
    .inventory-table-container [data-testid="stDataFrame"] tbody tr:hover {
        background: linear-gradient(135deg, var(--background-light) 0%, #E8F5E8 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.15) !important;
        transition: all 0.3s ease !important;
    }
    
    .inventory-table-container [data-testid="stDataFrame"] tbody tr:hover td {
        border-color: var(--border-light) !important;
    }
    
    /* Proveedores pendientes - estilo especial */
    .inventory-table-container [data-testid="stDataFrame"] tbody tr:has(td:first-child:contains("pendiente")) {
        position: relative;
    }
    
    .inventory-table-container [data-testid="stDataFrame"] tbody tr:has(td:first-child:contains("pendiente"))::before {
        content: '⏳';
        position: absolute;
        left: 0.5rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.2rem;
        opacity: 0.6;
    }
    
    /* Animación sutil para números */
    .inventory-table-container [data-testid="stDataFrame"] tbody td:nth-child(2),
    .inventory-table-container [data-testid="stDataFrame"] tbody td:nth-child(3),
    .inventory-table-container [data-testid="stDataFrame"] tbody td:nth-child(4) {
        animation: fadeInNumber 0.6s ease-out;
    }
    
    @keyframes fadeInNumber {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Scroll horizontal suave si es necesario */
    .inventory-table-container [data-testid="stDataFrame"] {
        overflow-x: auto;
        scrollbar-width: thin;
        scrollbar-color: var(--primary-color) var(--background-light);
    }
    
    .inventory-table-container [data-testid="stDataFrame"]::-webkit-scrollbar {
        height: 8px;
    }
    
    .inventory-table-container [data-testid="stDataFrame"]::-webkit-scrollbar-track {
        background: var(--background-light);
        border-radius: 10px;
    }
    
    .inventory-table-container [data-testid="stDataFrame"]::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 10px;
    }
    
    .inventory-table-container [data-testid="stDataFrame"]::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-color);
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
        .kpi-card { padding: 2rem 1.5rem; }
        .kpi-value-huge { font-size: 2.5rem; }
        .section-header { padding: 1rem 1.5rem; }
        .inventory-table tbody td { padding: 1rem 0.5rem; font-size: 0.9rem; }
        .inventory-table thead th { padding: 1rem 0.5rem; font-size: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# INICIALIZACIÓN DEL CONTROLADOR
# ================================================================
@st.cache_resource
def init_controller():
    """Inicializa el controlador con cache."""
    if controller_available and GarlicInventarioController:
        return GarlicInventarioController()
    return None

if 'inventario_controller' not in st.session_state:
    st.session_state.inventario_controller = init_controller()

controller = st.session_state.inventario_controller

# ================================================================
# FUNCIONES DE UTILIDAD
# ================================================================
def format_number(value, decimals=0):
    """Formatea números con separadores de miles europeos."""
    if decimals == 0:
        return f"{value:,.0f}".replace(',', '.')
    else:
        return f"{value:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def display_kpi_card_inventario(title, icon, value, subtitle, card_type="default"):
    """Muestra una KPI card específica para inventario."""
    card_class = f"kpi-card kpi-card-{card_type}"
    
    st.markdown(f"""
    <div class="{card_class}">
        <div class="kpi-title">{icon} {title}</div>
        <div class="kpi-value-huge">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# HEADER PRINCIPAL
# ================================================================
st.markdown("""
<div class="main-header">
    <h1>🧄 Dashboard de Inventario</h1>
    <h2>Garlic & Beyond - KCTN Campaña 2025/2026</h2>
    <p>Control total del inventario teórico de entradas de ajo por proveedor</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# INFORMACIÓN DE PERÍODO
# ================================================================
st.markdown("""
<div class="alert alert-info">
    <strong>📦 Campaña:</strong> 2025/2026 | 
    <strong>🔄 Última Actualización:</strong> """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """
</div>
""", unsafe_allow_html=True)

# ================================================================
# PANEL DE CONTROL CON LÓGICA DE CARGA
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
                    <strong>✅ Sistema Activo:</strong> {status['total_proveedores']} proveedores cargados
                </div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    📦 {format_number(status['total_kg'])} kg | 💰 €{format_number(status['total_euros'])} | 
                    📅 {status['last_update']}
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
    if st.button("🔄 Cargar desde SharePoint", help="Cargar datos de inventario desde SharePoint"):
        with st.spinner("Cargando datos de inventario desde SharePoint..."):
            try:
                if excel_available and get_dataframe:
                    # Obtener datos desde SharePoint
                    st.info("📥 Descargando datos de inventario...")
                    excel_data = get_dataframe('KCTN_06_Inventario')
                    
                    if excel_data is None:
                        st.error("❌ No se pudieron obtener datos de SharePoint")
                        st.markdown("""
                        **Posibles causas:**
                        - Error de conectividad con SharePoint
                        - URL incorrecta en secrets.toml  
                        - Archivo no encontrado
                        - Credenciales incorrectas
                        """)
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'success':
                        # Datos ya parseados
                        st.success("🎉 Datos parseados correctamente - inicializando...")
                        
                        if controller and controller.initialize_with_data(excel_data):
                            st.success("✅ Datos de inventario cargados correctamente")
                            st.balloons()
                            
                            # Mostrar resumen
                            kpis = controller.get_kpis()
                            st.info(f"📊 Cargados: {kpis['total_proveedores']} proveedores")
                            st.rerun()
                        else:
                            st.error("❌ Error inicializando controlador")
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'error':
                        st.error(f"❌ Error en datos parseados: {excel_data.get('message')}")
                        
                        # Mostrar detalles del error si están disponibles
                        metadata = excel_data.get('metadata', {})
                        if 'errors' in metadata and metadata['errors']:
                            st.markdown("**Errores específicos:**")
                            for error in metadata['errors'][:3]:
                                st.error(f"• {error}")
                    
                    else:
                        st.error("❌ Formato de datos no reconocido")
                        st.write(f"Tipo recibido: {type(excel_data)}")
                
                else:
                    st.error("❌ Excel loader no disponible")
                    
            except Exception as e:
                st.error(f"❌ Error crítico durante carga: {e}")
                st.exception(e)

with col3:
    if st.button("📊 Exportar Excel", help="Exportar datos a Excel"):
        if controller and controller.is_initialized:
            try:
                excel_data = controller.export_to_excel()
                if excel_data:
                    st.download_button(
                        label="⬇️ Descargar Excel",
                        data=excel_data,
                        file_name=f"Inventario_KCTN_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("❌ Error generando Excel")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.info("📋 Carga datos primero para exportar")

# ================================================================
# CONTENIDO PRINCIPAL - SOLO SI HAY CONTROLADOR INICIALIZADO
# ================================================================
if controller and controller.is_initialized:
    
    # Obtener KPIs
    kpis = controller.get_kpis()
    
    # ================================================================
    # SECCIÓN 1: KPI CARDS PRINCIPALES (2 cards grandes)
    # ================================================================
    st.markdown("""
    <div class="section-header">
        <h3 class="section-title">📊 KPIs Principales de Inventario</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # KPI Card 1: Total Kilogramos
        total_kg_formatted = format_number(kpis['total_kg'])
        display_kpi_card_inventario(
            "Total Inventario",
            "⚖️",
            f"{total_kg_formatted} kg",
            f"Distribuido entre {kpis['total_proveedores']} proveedores",
            "kg"
        )
    
    with col2:
        # KPI Card 2: Total Euros
        total_euros_formatted = format_number(kpis['total_euros'])
        precio_promedio = format_number(kpis['precio_promedio_kg'], 3)
        display_kpi_card_inventario(
            "Valor Total",
            "💰",
            f"€{total_euros_formatted}",
            f"Precio promedio: €{precio_promedio}/kg",
            "euros"
        )
    
    # ================================================================
    # SECCIÓN 2: TABLA PRINCIPAL DE INVENTARIO
    # ================================================================
    st.markdown("""
    <div class="section-header">
        <h3 class="section-title">📋 Detalle de Inventario por Proveedor</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener DataFrame formateado
    df_display = controller.get_inventario_dataframe()
    
    if not df_display.empty:
        # Crear contenedor estilizado para la tabla
        st.markdown('<div class="inventory-table-container">', unsafe_allow_html=True)
        
        # Mostrar tabla súper estilizada
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=500,
            column_config={
                "Proveedor": st.column_config.TextColumn(
                    "Proveedor",
                    width="large",
                    help="Nombre del proveedor de ajo"
                ),
                "Kg": st.column_config.TextColumn(
                    "Kilogramos", 
                    width="medium",
                    help="Cantidad total en kilogramos"
                ),
                "Euros": st.column_config.TextColumn(
                    "Valor Total",
                    width="medium",
                    help="Valor total en euros"
                ),
                "€/Kg": st.column_config.TextColumn(
                    "Precio/Kg",
                    width="small", 
                    help="Precio por kilogramo en euros"
                )
            }
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Métricas adicionales mejoradas
        st.markdown("""
        <div class="section-header" style="margin-top: 3rem;">
            <h3 class="section-title">🏆 Análisis de Proveedores Destacados</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Estadísticas adicionales mejoradas
        raw_df = controller.get_raw_inventario_dataframe()
        if not raw_df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                max_kg_prov = raw_df.loc[raw_df['Kg'].idxmax(), 'Proveedor']
                max_kg_val = format_number(raw_df['Kg'].max())
                
                st.markdown(f"""
                <div class="kpi-card" style="padding: 1.5rem; margin-bottom: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🥇</div>
                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Mayor Volumen</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #1976D2; margin-bottom: 0.3rem;">{max_kg_prov}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">{max_kg_val} kg</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                max_eur_prov = raw_df.loc[raw_df['Euros'].idxmax(), 'Proveedor']  
                max_eur_val = format_number(raw_df['Euros'].max())
                
                st.markdown(f"""
                <div class="kpi-card" style="padding: 1.5rem; margin-bottom: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💎</div>
                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Mayor Valor</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #FF9800; margin-bottom: 0.3rem;">{max_eur_prov}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">€{max_eur_val}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                max_precio_prov = raw_df.loc[raw_df['Euros_por_Kg'].idxmax(), 'Proveedor']
                max_precio_val = format_number(raw_df['Euros_por_Kg'].max(), 3)
                
                st.markdown(f"""
                <div class="kpi-card" style="padding: 1.5rem; margin-bottom: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💰</div>
                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">Mayor Precio/Kg</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: var(--primary-color); margin-bottom: 0.3rem;">{max_precio_prov}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">€{max_precio_val}/kg</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ No hay datos de inventario para mostrar")

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
    ### 🚀 Bienvenido al Dashboard de Inventario KCTN
    
    Para comenzar a usar el sistema, carga los datos del Excel de inventario teórico:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔗 Conexión SharePoint
        **Datos en tiempo real desde SharePoint**
        
        **Características:**
        - ✅ Datos actualizados automáticamente
        - ✅ Conexión directa con el sistema
        - ✅ Procesa hoja "Inventario teorico"
        
        **Requisitos:**
        - Archivo `secrets.toml` configurado
        - Acceso a SharePoint autorizado
        - Excel en ubicación correcta
        """)
        
        if st.button("🔗 Conectar SharePoint", key="connect_sp_inv", type="primary"):
            st.info("🔄 Usar el botón 'Cargar desde SharePoint' en la parte superior")
    
    with col2:
        st.markdown("""
        #### 📦 Estructura Esperada
        **Formato del archivo Excel**
        
        **Hoja 4 - "Inventario teorico":**
        - 📊 Fila 1: Total Inventario, Total Kg, Total €
        - 📋 Fila 3: Headers (Proveedor, Kgs, €, €/kg)
        - 📝 Fila 4+: Datos de proveedores
        
        **Formato números:**
        - ⚖️ Kg: 2.703.695 kg (punto = miles)
        - 💰 €: 1,30 € (coma = decimal)
        """)

# ================================================================
# FOOTER
# ================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: var(--text-secondary); padding: 2rem 0;'>
    <p><strong>🧄 Garlic & Beyond Dashboard Inventario KCTN v1.0</strong></p>
    <p>Sistema de control de inventario teórico por proveedor • Campaña 2025/2026</p>
    <p>© 2025 Garlic & Beyond - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
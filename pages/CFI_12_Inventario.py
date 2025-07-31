"""
CFI_12_Inventario.py - Dashboard Inventario CFI
===============================================
Dashboard completo de Inventario para CFI (Comagra Food Ingredients).
Sistema integral de análisis de existencias de productos.

Funcionalidades principales:
- Análisis por mes individual con KPIs detallados
- Comparación multi-mes con tendencias y cambios porcentuales
- Análisis de productos por tipo (ajo vs no ajo)
- Insights configurables y alertas personalizables
- Gráficas interactivas y exportación de datos
- Seguimiento de productos estrella y evolución de precios

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0
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
        page_title="Dashboard Inventario CFI - Garlic & Beyond",
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
        
        # Intentar importar controlador CFI Inventario
        try:
            from utils.controller_CFI_12_Inventario import CFIInventarioController
            controller_available = True
        except ImportError:
            try:
                from utils.controller_CFI_12_Inventario import CFIInventarioController
                controller_available = True
            except ImportError:
                controller_available = False
                CFIInventarioController = None
        
        # Intentar importar parser CFI Inventario
        try:
            from utils.parser_CFI_12_Inventario import parse_excel
            parser_available = True
        except ImportError:
            try:
                from utils.parser_CFI_12_Inventario import parse_excel
                parser_available = True
            except ImportError:
                parser_available = False
                parse_excel = None
        
        return excel_available, controller_available, parser_available, get_dataframe, CFIInventarioController, parse_excel
        
    except Exception as e:
        st.error(f"Error en importaciones: {e}")
        return False, False, False, None, None, None

excel_available, controller_available, parser_available, get_dataframe, CFIInventarioController, parse_excel = safe_import()

# ================================================================
# CSS PERSONALIZADO PARA CFI INVENTARIO - GARLIC & BEYOND
# ================================================================
st.markdown("""
<style>
    /* Importar Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para CFI Inventario - Garlic & Beyond */
    :root {
        --primary-color: #2563EB;
        --secondary-color: #1D4ED8;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --error-color: #EF4444;
        --info-color: #06B6D4;
        --text-primary: #1F2937;
        --text-secondary: #6B7280;
        --background-white: #ffffff;
        --background-light: #F0F9FF;
        --border-light: #DBEAFE;
        --shadow-sm: 0 1px 2px 0 rgba(37, 99, 235, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(37, 99, 235, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(37, 99, 235, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(37, 99, 235, 0.1);
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
    
    /* Header principal para CFI Inventario */
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
        content: '🌱';
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
    
    /* KPI Cards específicas para CFI Inventario */
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
    
    .kpi-card-productos::before {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .kpi-card-kilos::before {
        background: linear-gradient(90deg, #10B981, #34D399);
    }
    
    .kpi-card-valor::before {
        background: linear-gradient(90deg, #F59E0B, #FBBF24);
    }
    
    .kpi-card-precio::before {
        background: linear-gradient(90deg, #8B5CF6, #A78BFA);
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
        background: linear-gradient(135deg, var(--background-light) 0%, #E0F2FE 100%);
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
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-color: var(--success-color);
        color: #065F46;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-color: var(--warning-color);
        color: #92400E;
    }
    
    .alert-error {
        background: linear-gradient(135deg, #FEF2F2 0%, #FECACA 100%);
        border-color: var(--error-color);
        color: #991B1B;
    }
    
    .alert-info {
        background: linear-gradient(135deg, var(--background-light) 0%, #BFDBFE 100%);
        border-color: var(--info-color);
        color: var(--text-primary);
    }
    
    /* Insights container */
    .insights-container {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #BBF7D0;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .insights-container h4 {
        color: #15803D;
        margin-bottom: 1rem;
        font-weight: 600;
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
        background: linear-gradient(135deg, var(--background-light) 0%, #DBEAFE 100%);
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
    
    /* Footer personalizado */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
        color: white;
        border-radius: 12px;
        box-shadow: var(--shadow-lg);
    }
    
    .footer h3 {
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .footer p {
        margin: 0;
        opacity: 0.9;
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
    if controller_available and CFIInventarioController:
        return CFIInventarioController()
    return None

if 'cfi_inventario_controller' not in st.session_state:
    st.session_state.cfi_inventario_controller = init_controller()

controller = st.session_state.cfi_inventario_controller

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

def export_to_excel(data, filename):
    """Exporta datos a Excel con formato profesional."""
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if not data.empty:
                data.to_excel(writer, index=False, sheet_name='Inventario_CFI')
        
        processed_data = output.getvalue()
        return processed_data
    except Exception as e:
        st.error(f"Error generando Excel: {str(e)}")
        return None

# ================================================================
# HEADER PRINCIPAL
# ================================================================
st.markdown("""
<div class="main-header">
    <h1>🌱 Dashboard Inventario CFI</h1>
    <h2>Comagra Food Ingredients - Análisis de Existencias</h2>
    <p>Sistema integral de gestión y análisis de inventario de productos</p>
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
                    <strong>✅ Sistema CFI Inventario Activo:</strong> {status['months_with_data']} meses con datos, {status['months_empty']} pendientes
                </div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    📦 {status['total_products']} productos | 🏷️ {status['total_tipos']} tipos | 📅 {status['last_update']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-container">
                <div style="display: flex; align-items: center;">
                    <span class="status-indicator status-red"></span>
                    <strong>❌ Sistema CFI Inventario Inactivo:</strong> Datos no cargados
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("❌ Controlador CFI Inventario no disponible")

with col2:
    if st.button("🔄 Actualizar SharePoint", help="Cargar datos CFI Inventario desde SharePoint"):
        with st.spinner("Cargando datos CFI Inventario desde SharePoint..."):
            try:
                if excel_available and get_dataframe:
                    st.info("📥 Descargando datos CFI Inventario desde SharePoint...")
                    excel_data = get_dataframe('CFI_12_Inventario')
                    
                    if excel_data is None:
                        st.error("❌ No se pudieron obtener datos de SharePoint")
                        st.markdown("""
                        **Posibles causas:**
                        - Error de conectividad con SharePoint  
                        - URL incorrecta en secrets.toml para CFI_12_Inventario
                        - Credenciales incorrectas
                        - Archivo Excel CFI Inventario no encontrado
                        """)
                    
                    elif isinstance(excel_data, str):
                        st.error("❌ SharePoint devolvió un mensaje de error:")
                        with st.expander("📄 Mensaje completo"):
                            st.code(excel_data)
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'success':
                        # Datos ya parseados por excel_loader
                        st.success("🎉 Datos CFI Inventario ya parseados por excel_loader - inicializando directamente")
                        
                        if controller and controller.initialize_with_data(excel_data):
                            st.success("✅ Datos CFI Inventario cargados correctamente desde SharePoint")
                            st.balloons()
                            
                            # Mostrar resumen de datos cargados
                            metadata = excel_data.get('metadata', {})
                            st.info(f"📦 Productos procesados: {metadata.get('total_productos', 0)}")
                            if metadata.get('tipos_productos_count'):
                                st.write(f"🏷️ Tipos de productos: {metadata['tipos_productos_count']}")
                            if metadata.get('meses_con_datos'):
                                st.write(f"📅 Meses: {metadata['meses_con_datos']}")
                            
                            st.rerun()
                        else:
                            st.error("❌ Error inicializando controlador CFI Inventario con datos parseados")
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'error':
                        st.error(f"❌ Error en datos parseados CFI Inventario: {excel_data.get('message')}")
                        
                        # Mostrar detalles del error
                        metadata = excel_data.get('metadata', {})
                        if 'errors' in metadata and metadata['errors']:
                            st.markdown("**Errores específicos:**")
                            for error in metadata['errors'][:5]:
                                st.error(f"• {error}")
                    
                    elif isinstance(excel_data, dict):
                        # Datos raw de Excel - necesitan parsing manual
                        st.info("⚙️ Datos CFI Inventario raw detectados - parseando manualmente...")
                        
                        if parser_available and parse_excel:
                            try:
                                parsed_data = parse_excel(excel_data)
                                
                                if parsed_data and parsed_data.get('status') == 'success':
                                    if controller and controller.initialize_with_data(parsed_data):
                                        st.success("✅ Datos CFI Inventario raw parseados y cargados correctamente")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error inicializando controlador CFI Inventario")
                                else:
                                    error_msg = parsed_data.get('message', 'Error desconocido') if parsed_data else 'Sin respuesta del parser'
                                    st.error(f"❌ Error parseando datos CFI Inventario raw: {error_msg}")
                            
                            except Exception as e:
                                st.error(f"❌ Excepción parseando datos CFI Inventario raw: {e}")
                        else:
                            st.error("❌ Parser CFI Inventario no disponible para datos raw")
                    
                    else:
                        st.error("❌ Tipo de datos CFI Inventario no soportado")
                        st.write(f"Tipo recibido: {type(excel_data)}")
                
                else:
                    st.error("❌ Módulos Excel Loader no disponibles")
                    
            except Exception as e:
                st.error(f"❌ Error crítico durante carga CFI Inventario: {e}")
                st.exception(e)

with col3:
    if st.button("📁 Cargar Local", help="Cargar archivo Excel CFI Inventario desde archivo local"):
        st.info("🔄 Funcionalidad próximamente disponible")

# ================================================================
# CONTENIDO PRINCIPAL - SOLO SI HAY CONTROLADOR INICIALIZADO
# ================================================================
if controller and controller.is_initialized:
    
    # ================================================================
    # BARRA LATERAL - FILTROS
    # ================================================================
    with st.sidebar:
        st.markdown("## 🎯 Panel de Control CFI")
        
        # Selector de modo de análisis
        analysis_mode = st.radio(
            "**Modo de Análisis:**",
            ["📊 Selección por Mes", "📈 Comparación entre Meses"],
            help="Selecciona el tipo de análisis que deseas realizar"
        )
        
        if analysis_mode == "📊 Selección por Mes":
            st.markdown("### 📅 Análisis Individual")
            available_months = controller.get_available_months()
            months_with_data = controller.get_months_with_data()
            
            # Crear opciones con indicadores
            opciones_mes = []
            for mes in available_months:
                if mes in months_with_data:
                    opciones_mes.append(f"{mes} ✅")
                else:
                    opciones_mes.append(f"{mes} ⚠️ Sin datos")
            
            # Seleccionar el último mes con datos por defecto
            default_index = 0
            if months_with_data:
                latest_month = months_with_data[-1]
                for i, opcion in enumerate(opciones_mes):
                    if latest_month in opcion:
                        default_index = i
                        break
            
            mes_seleccionado_display = st.selectbox(
                "**Seleccionar Mes:**", 
                opciones_mes,
                index=default_index,
                help="Selecciona el mes para análisis detallado"
            )
            
            mes_seleccionado = mes_seleccionado_display.split(" ")[0]
            
        else:
            st.markdown("### 📈 Comparación entre Meses")
            available_months = controller.get_available_months()
            months_with_data = controller.get_months_with_data()
            
            # Por defecto seleccionar los últimos 3 meses con datos
            default_selection = months_with_data[-3:] if len(months_with_data) >= 3 else months_with_data
            
            meses_comparacion = st.multiselect(
                "**Meses a Comparar:**",
                available_months,
                default=default_selection,
                help="Selecciona múltiples meses para comparar tendencias"
            )
        
        st.markdown("---")
        
        # Información del sistema
        st.markdown("### 📊 Estado del Sistema")
        status = controller.get_status()
        st.metric("Meses con Datos", status['months_with_data'])
        st.metric("Total Productos", status['total_products'])
        st.metric("Tipos de Productos", status['total_tipos'])
    
    # ================================================================
    # ANÁLISIS POR MES INDIVIDUAL
    # ================================================================
    if analysis_mode == "📊 Selección por Mes":
        
        if mes_seleccionado in controller.get_months_with_data():
            # Obtener KPIs del mes seleccionado
            kpis = controller.calculate_monthly_kpis(mes_seleccionado)
            
            # ================================================================
            # SECCIÓN 1: KPI CARDS POR TIPO DE PRODUCTO
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📊 KPIs Principales CFI - """ + mes_seleccionado.title() + """</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar KPI cards dinámicamente según tipos disponibles
            if not kpis['tipos_agrupados'].empty:
                tipos_ordenados = kpis['tipos_agrupados'].sort_values('valor', ascending=False)
                
                # Mostrar top 6 tipos en cards (2 filas de 3)
                tipos_top = tipos_ordenados.head(6)
                
                # Primera fila
                col1, col2, col3 = st.columns(3)
                cols = [col1, col2, col3]
                
                for i, (tipo, datos) in enumerate(tipos_top.head(3).iterrows()):
                    with cols[i]:
                        display_kpi_card(
                            f"🏷️ {tipo.title()}",
                            f"{datos['kilos']:,.0f} kg",
                            [
                                ("Suma Precio", f"€{datos['precio']:,.0f}"),
                                ("Suma Valor", f"€{datos['valor']:,.0f}")
                            ],
                            ["productos", "kilos", "valor"][i % 3]
                        )
                
                # Segunda fila si hay más tipos
                if len(tipos_top) > 3:
                    col4, col5, col6 = st.columns(3)
                    cols = [col4, col5, col6]
                    
                    for i, (tipo, datos) in enumerate(tipos_top.tail(3).iterrows()):
                        with cols[i]:
                            display_kpi_card(
                                f"🏷️ {tipo.title()}",
                                f"{datos['kilos']:,.0f} kg",
                                [
                                    ("Suma Precio", f"€{datos['precio']:,.0f}"),
                                    ("Suma Valor", f"€{datos['valor']:,.0f}")
                                ],
                                ["precio", "productos", "kilos"][i % 3]
                            )
            
            # ================================================================
            # SECCIÓN 2: GRÁFICOS PRINCIPALES
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📈 Análisis Gráfico - """ + mes_seleccionado.title() + """</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart de kilos por tipo
                st.subheader("📊 Kilos Totales por Tipo de Producto")
                fig_kilos = controller.create_kilos_por_tipo_chart(mes_seleccionado)
                st.plotly_chart(fig_kilos, use_container_width=True)
            
            with col2:
                # Pie chart de valor por tipo
                st.subheader("💰 Distribución de Valor por Tipo")
                fig_valor = controller.create_valor_distribucion_chart(mes_seleccionado)
                st.plotly_chart(fig_valor, use_container_width=True)
            
            # ================================================================
            # SECCIÓN 3: PRECIO PROMEDIO SOLO AJO
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">🧄 Precio Promedio por Tipo de Ajo - """ + mes_seleccionado.title() + """</h3>
            </div>
            """, unsafe_allow_html=True)
            
            fig_ajo = controller.create_precio_ajo_chart(mes_seleccionado)
            st.plotly_chart(fig_ajo, use_container_width=True)
            
            # ================================================================
            # SECCIÓN 4: INSIGHTS CLAVES
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">💡 Insights Claves - """ + mes_seleccionado.title() + """</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Producto estrella
                st.markdown(f"""
                <div class="insights-container">
                    <h4>⭐ Producto Estrella</h4>
                    <p><strong>{kpis['producto_estrella']}</strong></p>
                    <p>Valor total: <strong>€{kpis['valor_estrella']:,.0f}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Parámetros configurables para alertas "no ajo"
                st.markdown("### ⚙️ Configuración de Alertas")
                limite_no_ajo = st.number_input(
                    "Cantidad alarmante de 'No Ajo' (kg):",
                    min_value=0.0,
                    value=200000.0,  # 200,000 kg por defecto
                    step=10000.0
                )
                
                no_ajo_actual = kpis['no_ajo_kilos']
                
                if no_ajo_actual > limite_no_ajo:
                    alert_class = "alert-error"
                    alert_msg = f"🚨 ALERTA: {no_ajo_actual:,.0f} kg de 'No Ajo' (>{limite_no_ajo:,.0f} kg). Debemos solucionar esto lo antes posible."
                elif no_ajo_actual > limite_no_ajo * 0.8:
                    alert_class = "alert-warning"
                    alert_msg = f"⚠️ WARNING: {no_ajo_actual:,.0f} kg de 'No Ajo' (cerca del límite)"
                else:
                    alert_class = "alert-success"
                    alert_msg = f"✅ OK: {no_ajo_actual:,.0f} kg de 'No Ajo' (distancia sana)"
                
                st.markdown(f"""
                <div class="{alert_class}">
                    {alert_msg}
                </div>
                """, unsafe_allow_html=True)
            
            # ================================================================
            # SECCIÓN 5: SELECTOR DE TIPO PARA ANÁLISIS DETALLADO
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">🔍 Análisis Detallado por Tipo de Producto</h3>
            </div>
            """, unsafe_allow_html=True)
            
            tipos_disponibles = controller.get_available_tipos(mes_seleccionado)
            tipo_seleccionado = st.selectbox("Seleccionar tipo de producto:", tipos_disponibles)
            
            if tipo_seleccionado:
                productos_info = controller.get_productos_por_tipo(mes_seleccionado, tipo_seleccionado)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.metric("Existencias actuales", f"{productos_info['cantidad_articulos']} artículos")
                    st.metric("Nombres únicos", f"{productos_info['nombres_unicos']} nombres")
                
                with col2:
                    st.markdown(f"**Existen:** {productos_info['cantidad_articulos']} artículos en la cámara con {productos_info['nombres_unicos']} nombres únicos")
                    
                    if not productos_info['productos'].empty:
                        tabla_productos = productos_info['productos'].copy()
                        tabla_productos.columns = ['Código', 'Nombre', 'Kilos', 'Precio €/kg', 'Valor €']
                        
                        # Formatear números
                        tabla_productos['Kilos'] = tabla_productos['Kilos'].round(2)
                        tabla_productos['Precio €/kg'] = tabla_productos['Precio €/kg'].round(3)
                        tabla_productos['Valor €'] = tabla_productos['Valor €'].round(2)
                        
                        st.dataframe(tabla_productos, use_container_width=True, hide_index=True)
        
        else:
            st.markdown(f"""
            <div class="alert alert-warning">
                ⚠️ <strong>{mes_seleccionado.title()}</strong>: No hay datos disponibles todavía para este mes.
            </div>
            """, unsafe_allow_html=True)
    
    # ================================================================
    # COMPARACIÓN ENTRE MESES
    # ================================================================
    else:
        if not meses_comparacion:
            st.warning("⚠️ Selecciona al menos un mes para comparar")
        elif len(meses_comparacion) < 2:
            st.warning("⚠️ Selecciona al menos 2 meses para realizar comparaciones")
        else:
            # ================================================================
            # SECCIÓN 1: TABLA DE CAMBIOS PORCENTUALES
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📊 Cambios Porcentuales por Tipo de Producto</h3>
            </div>
            """, unsafe_allow_html=True)
            
            df_cambios = controller.calculate_percentage_changes(meses_comparacion)
            
            if not df_cambios.empty:
                st.dataframe(df_cambios, use_container_width=True, hide_index=True, height=400)
                
                # Botón de descarga
                csv_cambios = df_cambios.to_csv(index=False)
                st.download_button(
                    label="📄 Descargar Tabla de Cambios",
                    data=csv_cambios,
                    file_name=f"Cambios_Porcentuales_CFI_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No hay suficientes datos para calcular cambios porcentuales")
            
            # ================================================================
            # SECCIÓN 2: GRÁFICA DE EVOLUCIÓN DEL VALOR
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📈 Evolución del Valor por Tipo de Producto</h3>
            </div>
            """, unsafe_allow_html=True)
            
            todos_tipos = controller.get_available_tipos()
            tipos_para_grafico = st.multiselect(
                "Seleccionar tipos a mostrar:",
                sorted(todos_tipos),
                default=sorted(todos_tipos)[:5] if len(todos_tipos) > 5 else sorted(todos_tipos)
            )
            
            if tipos_para_grafico:
                fig_evolucion = controller.create_evolution_chart(meses_comparacion, tipos_para_grafico)
                st.plotly_chart(fig_evolucion, use_container_width=True)
            
            # ================================================================
            # SECCIÓN 3: GRÁFICAS DE BARRAS POR PRODUCTO
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📊 Precio Medio por Tipo - Comparación Mensual</h3>
            </div>
            """, unsafe_allow_html=True)
            
            fig_comparacion_precios = controller.create_comparison_price_charts(meses_comparacion)
            st.plotly_chart(fig_comparacion_precios, use_container_width=True)

else:
    # ================================================================
    # MODO SIN DATOS - CONFIGURACIÓN INICIAL
    # ================================================================
    st.markdown("""
    <div class="section-header">
        <h3 class="section-title">🔧 Configuración Inicial del Sistema CFI Inventario</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 Bienvenido al Dashboard de Inventario CFI
    
    Para comenzar a usar el sistema, carga los datos del Excel de existencias CFI:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔗 Conexión SharePoint CFI
        **Datos en tiempo real desde SharePoint CFI**
        
        **Características:**
        - ✅ Datos CFI actualizados automáticamente  
        - ✅ Conexión directa con sistema de inventario CFI
        - ✅ Procesa 12 hojas mensuales (Enero-Diciembre)
        
        **Formato esperado del Excel CFI:**
        - 📋 Hojas: Enero, Febrero, Marzo... Diciembre
        - 🏷️ Columnas: A(Código), B(Tipo), C(Nombre), D(Kilos), E(Precio), F(Valor)  
        - 🧄 Tipos: productos de ajo, "no ajo", maquila, etc.
        
        **Requisitos:**
        - Archivo `secrets.toml` configurado con CFI_12_Inventario
        - Acceso a SharePoint autorizado
        - Excel CFI en ubicación correcta
        """)
        
        if st.button("🔗 Conectar SharePoint CFI", key="connect_sp_cfi_inv", type="primary"):
            st.info("🔄 Usar el botón 'Actualizar SharePoint' en la parte superior")
    
    with col2:
        st.markdown("""
        #### 📁 Carga Manual CFI  
        **Subir archivo Excel CFI local**
        
        **Formato esperado:**
        - 📋 Archivo Excel (.xlsx) 
        - 🏷️ 12 hojas mensuales con estructura CFI
        - 🧄 Productos por tipo (ajo, no ajo, etc.)
        
        **Columnas importantes:**
        - A: Código del producto
        - B: Tipo (ajo dado conv., no ajo, etc.)
        - C: Nombre del producto  
        - D: Kilos en existencia
        - E: Precio por kg
        - F: Valor total
        
        **Estado:**
        Funcionalidad en desarrollo
        """)
        
        uploaded_file = st.file_uploader(
            "📎 Seleccionar archivo Excel CFI", 
            type=['xlsx'], 
            key="upload_excel_cfi_inv",
            help="Próximamente disponible"
        )
        
        if uploaded_file:
            st.info("📋 **Funcionalidad en desarrollo** - Usa SharePoint CFI")

# ================================================================
# FOOTER PERSONALIZADO
# ================================================================
st.markdown("""
<div class="footer">
    <h3>Pax Capital Partners × Garlic and Beyond</h3>
    <p>——— Existencias Comagra Food Ingredients ———</p>
</div>
""", unsafe_allow_html=True)
"""
CFI_13_Compras.py - Dashboard Compras CFI
==========================================
Dashboard completo de Compras para CFI (Conagra Food Ingredients).
Sistema integral de análisis de compras por proveedor y gestión de pedidos.

Funcionalidades:
- Análisis por mes individual con KPIs detallados
- Comparación multi-mes con tendencias y cambios porcentuales
- Análisis de proveedores y precios por kilogramo
- Seguimiento de estados de entrega
- Análisis de tiempos de conexión y distribución de pagos
- Gráficas interactivas y exportación de datos

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
        page_title="Dashboard Compras CFI - Garlic & Beyond",
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
        
        # Intentar importar controlador CFI Compras
        try:
            from utils.controller_CFI_13_Compras import CFIComprasController
            controller_available = True
        except ImportError:
            try:
                from utils.controller_CFI_13_Compras import CFIComprasController
                controller_available = True
            except ImportError:
                controller_available = False
                CFIComprasController = None
        
        # Intentar importar parser CFI Compras
        try:
            from utils.parser_CFI_13_Compras import parse_excel
            parser_available = True
        except ImportError:
            try:
                from utils.parser_CFI_13_Compras import parse_excel
                parser_available = True
            except ImportError:
                parser_available = False
                parse_excel = None
        
        return excel_available, controller_available, parser_available, get_dataframe, CFIComprasController, parse_excel
        
    except Exception as e:
        st.error(f"Error en importaciones: {e}")
        return False, False, False, None, None, None

excel_available, controller_available, parser_available, get_dataframe, CFIComprasController, parse_excel = safe_import()

# ================================================================
# CSS PERSONALIZADO PARA CFI COMPRAS - GARLIC & BEYOND
# ================================================================
st.markdown("""
<style>
    /* Importar Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para CFI Compras - Garlic & Beyond */
    :root {
        --primary-color: #2E7D32;
        --secondary-color: #66BB6A;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --info-color: #2196F3;
        --text-primary: #1B5E20;
        --text-secondary: #2E7D32;
        --background-white: #ffffff;
        --background-light: #E8F5E8;
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
    
    /* Header principal para CFI Compras */
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
        content: '🛒';
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
    
    /* KPI Cards específicas para CFI Compras */
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
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .kpi-card-proveedores::before {
        background: linear-gradient(90deg, #4CAF50, #66BB6A);
    }
    
    .kpi-card-precios::before {
        background: linear-gradient(90deg, #FF9800, #FFB74D);
    }
    
    .kpi-card-estados::before {
        background: linear-gradient(90deg, #9C27B0, #BA68C8);
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
        background: linear-gradient(135deg, var(--background-light) 0%, #F1F8E9 100%);
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
        background: linear-gradient(135deg, var(--background-light) 0%, #E3F2FD 100%);
        border-color: var(--info-color);
        color: var(--text-primary);
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
        background: linear-gradient(135deg, var(--background-light) 0%, #F1F8E9 100%);
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
    if controller_available and CFIComprasController:
        return CFIComprasController()
    return None

if 'cfi_compras_controller' not in st.session_state:
    st.session_state.cfi_compras_controller = init_controller()

controller = st.session_state.cfi_compras_controller

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
                data.to_excel(writer, index=False, sheet_name='Datos_Compras_CFI')
        
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
    <h1>🛒 Dashboard Compras CFI</h1>
    <h2>Conagra Food Ingredients - Análisis de Compras</h2>
    <p>Sistema integral de análisis de compras por proveedor y gestión de pedidos</p>
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
                    <strong>✅ Sistema CFI Compras Activo:</strong> {status['months_with_data']} meses con datos, {status['months_empty']} pendientes
                </div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    🏭 {status['total_proveedores']} proveedores | 💰 €{status['total_compras_latest']:,.0f} | 
                    🚨 {status['alerts_count']} alertas | 📅 {status['last_update']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-container">
                <div style="display: flex; align-items: center;">
                    <span class="status-indicator status-red"></span>
                    <strong>❌ Sistema CFI Compras Inactivo:</strong> Datos no cargados
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("❌ Controlador CFI Compras no disponible")

with col2:
    if st.button("🔄 Cargar desde SharePoint", help="Cargar datos CFI Compras desde SharePoint"):
        with st.spinner("Cargando datos CFI Compras desde SharePoint..."):
            try:
                if excel_available and get_dataframe:
                    st.info("📥 Descargando datos CFI Compras desde SharePoint...")
                    excel_data = get_dataframe('CFI_13_Compras')
                    
                    if excel_data is None:
                        st.error("❌ No se pudieron obtener datos de SharePoint")
                        st.markdown("""
                        **Posibles causas:**
                        - Error de conectividad con SharePoint  
                        - URL incorrecta en secrets.toml para CFI_Compras_13
                        - Credenciales incorrectas
                        - Archivo Excel CFI Compras no encontrado
                        """)
                    
                    elif isinstance(excel_data, str):
                        st.error("❌ SharePoint devolvió un mensaje de error:")
                        with st.expander("📄 Mensaje completo"):
                            st.code(excel_data)
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'success':
                        # Datos ya parseados por excel_loader
                        st.success("🎉 Datos CFI Compras ya parseados por excel_loader - inicializando directamente")
                        
                        if controller and controller.initialize_with_data(excel_data):
                            st.success("✅ Datos CFI Compras cargados correctamente desde SharePoint")
                            st.balloons()
                            
                            # Mostrar resumen de datos cargados
                            metadata = excel_data.get('metadata', {})
                            st.info(f"📊 Registros procesados: {metadata.get('total_records', 0)}")
                            if metadata.get('proveedores_count'):
                                st.write(f"🏭 Proveedores: {metadata['proveedores_count']}")
                            if metadata.get('months_count'):
                                st.write(f"📅 Meses: {metadata['months_count']}")
                            
                            st.rerun()
                        else:
                            st.error("❌ Error inicializando controlador CFI Compras con datos parseados")
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'error':
                        st.error(f"❌ Error en datos parseados CFI Compras: {excel_data.get('message')}")
                        
                        # Mostrar detalles del error
                        metadata = excel_data.get('metadata', {})
                        if 'errors' in metadata and metadata['errors']:
                            st.markdown("**Errores específicos:**")
                            for error in metadata['errors'][:5]:
                                st.error(f"• {error}")
                    
                    elif isinstance(excel_data, dict):
                        # Datos raw de Excel - necesitan parsing manual
                        st.info("⚙️ Datos CFI Compras raw detectados - parseando manualmente...")
                        
                        if parser_available and parse_excel:
                            try:
                                parsed_data = parse_excel(excel_data)
                                
                                if parsed_data and parsed_data.get('status') == 'success':
                                    if controller and controller.initialize_with_data(parsed_data):
                                        st.success("✅ Datos CFI Compras raw parseados y cargados correctamente")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error inicializando controlador CFI Compras")
                                else:
                                    error_msg = parsed_data.get('message', 'Error desconocido') if parsed_data else 'Sin respuesta del parser'
                                    st.error(f"❌ Error parseando datos CFI Compras raw: {error_msg}")
                            
                            except Exception as e:
                                st.error(f"❌ Excepción parseando datos CFI Compras raw: {e}")
                        else:
                            st.error("❌ Parser CFI Compras no disponible para datos raw")
                    
                    else:
                        st.error("❌ Tipo de datos CFI Compras no soportado")
                        st.write(f"Tipo recibido: {type(excel_data)}")
                
                else:
                    st.error("❌ Módulos Excel Loader no disponibles")
                    
            except Exception as e:
                st.error(f"❌ Error crítico durante carga CFI Compras: {e}")
                st.exception(e)

with col3:
    if st.button("📁 Subir Excel Local", help="Subir archivo Excel CFI Compras desde tu computadora"):
        st.info("🔄 Funcionalidad próximamente disponible")

# ================================================================
# CONTENIDO PRINCIPAL - SOLO SI HAY CONTROLADOR INICIALIZADO
# ================================================================
if controller and controller.is_initialized():
    
    # ================================================================
    # BARRA LATERAL - FILTROS (SIN PROVEEDORES)
    # ================================================================
    with st.sidebar:
        st.markdown("## 🎯 Panel de Control CFI Compras")
        
        # Selector de modo de análisis (sin filtros de proveedor)
        analysis_mode = st.radio(
            "**Modo de Análisis:**",
            ["📊 Mes Individual", "📈 Comparación de Meses"],
            help="Selecciona el tipo de análisis que deseas realizar"
        )
        
        if analysis_mode == "📊 Mes Individual":
            st.markdown("### 📅 Análisis por Mes Individual")
            available_months = controller.get_available_months()
            months_with_data = controller.get_months_with_data()
            
            # Seleccionar el último mes con datos por defecto
            default_index = 0
            if months_with_data:
                latest_month = months_with_data[-1]
                if latest_month in available_months:
                    default_index = available_months.index(latest_month)
            
            selected_month = st.selectbox(
                "**Seleccionar Mes:**", 
                available_months,
                index=default_index,
                help="Selecciona el mes para análisis detallado"
            )
            
        else:
            st.markdown("### 📈 Comparación entre Meses")
            available_months = controller.get_available_months()
            months_with_data = controller.get_months_with_data()
            
            # Por defecto seleccionar los últimos 6 meses con datos, o todos si hay menos de 6
            default_selection = months_with_data[-6:] if len(months_with_data) >= 6 else months_with_data
            
            selected_months = st.multiselect(
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
        st.metric("Proveedores", status['total_proveedores'])
        st.metric("Total Compras (último mes)", f"€{status['total_compras_latest']:,.0f}")
    
    # ================================================================
    # ANÁLISIS INDIVIDUAL
    # ================================================================
    if analysis_mode == "📊 Mes Individual":
        
        # Obtener KPIs del mes seleccionado (sin filtro de proveedores)
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
        # SECCIÓN 1: KPI CARDS SEGÚN ESPECIFICACIONES
        # ================================================================
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">📊 KPIs Principales CFI Compras - """ + selected_month.title() + """</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar mensaje si no hay datos
        if not kpis['has_data']:
            st.info(f"📅 {selected_month.title()} - Datos pendientes de cargar")
        
        # 6 KPI Cards en 3 filas según especificaciones
        col1, col2 = st.columns(2)
        
        with col1:
            # KPI Card A: Total Compras (Ventas totales por mes suma de Total factura)
            display_kpi_card(
                "💰 Total Compras",
                f"€{kpis['total_compras']:,.0f}",
                [
                    ("Peso Total", f"{kpis['total_peso_kg']:,.0f} kg"),
                    ("Precio Promedio/kg", f"€{kpis['precio_promedio_kg']:.2f}")
                ],
                "compras"
            )
        
        with col2:
            # KPI Card B: Proveedores Activos por mes
            display_kpi_card(
                "🏭 Proveedores Activos",
                f"{kpis['proveedores_activos']} proveedores",
                [
                    ("Proveedor Estrella", kpis['proveedor_estrella']),
                    ("Tiempo Conexión Promedio", f"{kpis['tiempo_conexion_promedio']:.1f} días")
                ],
                "proveedores"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            # KPI Card C: Precio promedio por kilogramo por ese mes
            display_kpi_card(
                "📊 Precio Promedio por KG",
                f"€{kpis['precio_promedio_kg']:.2f}/kg",
                [
                    ("Peso Total", f"{kpis['total_peso_kg']:,.0f} kg"),
                    ("Total Compras", f"€{kpis['total_compras']:,.0f}")
                ],
                "precios"
            )
        
        with col4:
            # KPI Card D: Average de tiempo de conexión
            display_kpi_card(
                "⏱️ Tiempo de Conexión",
                f"{kpis['tiempo_conexion_promedio']:.1f} días",
                [
                    ("Proveedores Activos", f"{kpis['proveedores_activos']}"),
                    ("Proveedor Estrella", kpis['proveedor_estrella'])
                ],
                "estados"
            )
        
        # ================================================================
        # SECCIÓN 2: GRÁFICOS INDIVIDUALES SEGÚN ESPECIFICACIONES
        # ================================================================
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">📈 Análisis Gráfico - """ + selected_month.title() + """</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 2. Gráfica de barras: Proveedores vs KG vendidos
            st.subheader("📦 Kilogramos por Proveedor")
            fig_kg = controller.create_kg_por_proveedor_chart(selected_month)
            st.plotly_chart(fig_kg, use_container_width=True, key=f"kg_chart_{selected_month}")
        
        with col2:
            # 3. Gráfica de barras: Proveedores vs Total Factura
            st.subheader("💰 Total Factura por Proveedor")
            fig_factura = controller.create_factura_por_proveedor_chart(selected_month)
            st.plotly_chart(fig_factura, use_container_width=True, key=f"factura_chart_{selected_month}")
        
        # 4. Gráfica de precio promedio por proveedor
        st.subheader("📊 Precio Promedio por KG por Proveedor")
        fig_precio = controller.create_precio_promedio_proveedor_chart(selected_month)
        st.plotly_chart(fig_precio, use_container_width=True, key=f"precio_chart_{selected_month}")
        
        # ================================================================
        # SECCIÓN 3: ESTADOS DEL PEDIDO SEGÚN ESPECIFICACIONES
        # ================================================================
        st.markdown("""
        <div class="section-header">
            <h3 class="section-title">📋 Estados de Pedidos - """ + selected_month.title() + """</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # A. Pedidos entregados
            display_kpi_card(
                "✅ Pedidos Entregados",
                f"{kpis['pedidos_entregados']}",
                [
                    ("Estado", "ENTREGADO")
                ],
                "compras"
            )
        
        with col2:
            # B. Pedidos embarcados
            display_kpi_card(
                "🚢 Pedidos Embarcados",
                f"{kpis['pedidos_embarcados']}",
                [
                    ("Estado", "EMBARCADO")
                ],
                "proveedores"
            )
        
        with col3:
            # C. En preparación
            display_kpi_card(
                "⏳ En Preparación",
                f"{kpis['pedidos_preparacion']}",
                [
                    ("Estado", "EN PREPARACION")
                ],
                "estados"
            )
    
    # ================================================================
    # COMPARACIÓN MULTI-MES
    # ================================================================
    else:
        if not selected_months:
            st.warning("⚠️ Selecciona al menos un mes para comparar")
        else:
            # ================================================================
            # SECCIÓN 1: KPIs COMPARATIVOS SEGÚN ESPECIFICACIONES
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📊 KPIs Comparativos CFI Compras</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Calcular cambios porcentuales
            changes = controller.calculate_month_changes(selected_months)
            
            if changes:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # A. Cambio en % de total compras por mes
                    change_compras = changes['compras_change']
                    display_kpi_card(
                        "💰 Cambio Total Compras",
                        f"{change_compras:+.1f}%",
                        [
                            ("Desde", changes['first_month'].title()),
                            ("Hasta", changes['last_month'].title())
                        ],
                        "compras"
                    )
                
                with col2:
                    # B. Ventas totales en periodos seleccionados
                    all_kpis = [controller.get_monthly_kpis(m) for m in selected_months]
                    valid_kpis = [k for k in all_kpis if k['has_data']]
                    
                    if valid_kpis:
                        total_compras_periodo = sum(k['total_compras'] for k in valid_kpis)
                        display_kpi_card(
                            "💰 Compras Totales Período",
                            f"€{total_compras_periodo:,.0f}",
                            [
                                ("Meses", f"{len(valid_kpis)}"),
                                ("Promedio/Mes", f"€{total_compras_periodo/len(valid_kpis):,.0f}")
                            ],
                            "compras"
                        )
                
                with col3:
                    # C. Kg totales vendidos
                    if valid_kpis:
                        total_kg_periodo = sum(k['total_peso_kg'] for k in valid_kpis)
                        display_kpi_card(
                            "📦 KG Totales Período",
                            f"{total_kg_periodo:,.0f} kg",
                            [
                                ("Cambio KG", f"{changes['peso_change']:+.1f}%"),
                                ("Promedio/Mes", f"{total_kg_periodo/len(valid_kpis):,.0f} kg")
                            ],
                            "proveedores"
                        )
                
                with col4:
                    # G. Cantidad de Proveedores activos durante el periodo
                    if valid_kpis:
                        # Obtener todos los proveedores únicos del período
                        all_months_df = pd.concat([
                            controller.compras_df[controller.compras_df['mes'] == m] 
                            for m in selected_months if m in controller.monthly_data
                        ])
                        
                        proveedores_activos_periodo = all_months_df['proveedor'].nunique() if not all_months_df.empty else 0
                        
                        display_kpi_card(
                            "🏭 Proveedores Activos",
                            f"{proveedores_activos_periodo}",
                            [
                                ("Período", f"{len(valid_kpis)} meses"),
                                ("Promedio/Mes", f"{sum(k['proveedores_activos'] for k in valid_kpis)/len(valid_kpis):.1f}")
                            ],
                            "proveedores"
                        )
            
            # ================================================================
            # SECCIÓN 2: TABLA COMPARATIVA
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
                    height=400
                )
                
                # Botón de descarga
                csv_data = kpi_table.to_csv(index=False)
                st.download_button(
                    label="📄 Descargar Tabla KPIs CFI Compras",
                    data=csv_data,
                    file_name=f"KPIs_CFI_Compras_Comparativa_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No hay datos disponibles para generar la tabla comparativa")
            
            # ================================================================
            # SECCIÓN 3: GRÁFICOS COMPARATIVOS SEGÚN ESPECIFICACIONES
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📈 Análisis Comparativo entre Meses</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Tendencia en total factura y peso a través de los meses
            st.subheader("📈 Tendencias CFI Compras")
            fig_evolucion = controller.create_evolucion_compras_chart(selected_months)
            st.plotly_chart(fig_evolucion, use_container_width=True, key="evolucion_compras_multi")

else:
    # ================================================================
    # MODO SIN DATOS - CONFIGURACIÓN INICIAL
    # ================================================================
    st.markdown("""
    <div class="section-header">
        <h3 class="section-title">🔧 Configuración Inicial del Sistema CFI Compras</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 Bienvenido al Dashboard de Compras CFI
    
    Para comenzar a usar el sistema, carga los datos del Excel de compras CFI:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔗 Conexión SharePoint CFI
        **Datos en tiempo real desde SharePoint CFI**
        
        **Características:**
        - ✅ Datos CFI actualizados automáticamente
        - ✅ Conexión directa con el sistema CFI
        - ✅ Procesa hojas de datos de compras y proveedores
        
        **Formato esperado del Excel CFI:**
        - 📋 Hoja 1: "Datos principales" (C-R)
        - 🏭 Hoja 2: "Información de proveedores"
        - 🛒 Estructura: Proveedor, Fecha, Total Factura, Peso, Precio
        
        **Requisitos:**
        - Archivo `secrets.toml` configurado con CFI_Compras_13
        - Acceso a SharePoint autorizado
        - Excel CFI en ubicación correcta
        """)
        
        if st.button("🔗 Conectar SharePoint CFI", key="connect_sp_cfi", type="primary"):
            st.info("🔄 Usar el botón 'Cargar desde SharePoint' en la parte superior")
    
    with col2:
        st.markdown("""
        #### 📁 Carga Manual CFI
        **Subir archivo Excel CFI local**
        
        **Formato esperado:**
        - 📋 Archivo Excel (.xlsx)
        - 🛒 Hoja 1: Datos de compras (columnas C a R)
        - 🏭 Hoja 2: Información de proveedores
        - 💰 Estructura de compras CFI
        
        **Columnas importantes:**
        - C: Proveedor
        - F: Fecha Factura | G: Total Factura
        - I: Peso en kg | J: Precio por kg
        - O: Demora | P: Distribución pago | Q: Día pago
        - R: Estado entrega
        
        **Estado:**
        Funcionalidad en desarrollo
        """)
        
        uploaded_file = st.file_uploader(
            "📎 Seleccionar archivo Excel CFI", 
            type=['xlsx'], 
            key="upload_excel_cfi",
            help="Próximamente disponible"
        )
        
        if uploaded_file:
            st.info("📋 **Funcionalidad en desarrollo** - Usa SharePoint CFI")

# ================================================================
# FOOTER
# ================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: var(--text-secondary); padding: 2rem 0;'>
    <p><strong>🛒 CFI Dashboard Compras v1.0</strong></p>
    <p>Sistema integral de análisis de compras CFI • Desarrollado por GANDB Team</p>
    <p>© 2025 Garlic & Beyond - Conagra Food Ingredients - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
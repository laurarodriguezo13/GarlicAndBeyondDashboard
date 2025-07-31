"""
CFI_08_RRHH.py - Dashboard Recursos Humanos CFI CORREGIDO
========================================================
Dashboard completo de Recursos Humanos para CFI (Centro de Formación Industrial).
Sistema integral de análisis de costes de personal por departamento.

CORRECCIONES APLICADAS:
- Eliminadas alertas de "datos incompletos"
- Filtros incluyen todos los 12 meses
- Código debug removido
- Títulos de gráficas corregidos

Funcionalidades:
- Análisis por mes individual con KPIs detallados
- Comparación multi-mes con tendencias y cambios porcentuales
- Análisis de costes por departamento
- Seguimiento de aportaciones a la seguridad social
- Análisis detallado de bajas y altas (sin filtros)
- Gráficas interactivas y exportación de datos

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0 (Corregida)
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
        page_title="Dashboard RRHH CFI - Garlic & Beyond",
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
        
        # Intentar importar controlador CFI
        try:
            from utils.controller_CFI_08_RRHH import CFIRRHHController
            controller_available = True
        except ImportError:
            try:
                from utils.controller_CFI_08_RRHH import CFIRRHHController
                controller_available = True
            except ImportError:
                controller_available = False
                CFIRRHHController = None
        
        # Intentar importar parser CFI
        try:
            from utils.parser_CFI_08_RRHH import parse_excel
            parser_available = True
        except ImportError:
            try:
                from utils.parser_CFI_08_RRHH import parse_excel
                parser_available = True
            except ImportError:
                parser_available = False
                parse_excel = None
        
        return excel_available, controller_available, parser_available, get_dataframe, CFIRRHHController, parse_excel
        
    except Exception as e:
        st.error(f"Error en importaciones: {e}")
        return False, False, False, None, None, None

excel_available, controller_available, parser_available, get_dataframe, CFIRRHHController, parse_excel = safe_import()

# ================================================================
# CSS PERSONALIZADO PARA CFI - GARLIC & BEYOND
# ================================================================
st.markdown("""
<style>
    /* Importar Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para CFI - Garlic & Beyond */
    :root {
        --primary-color: #1976D2;
        --secondary-color: #42A5F5;
        --success-color: #66BB6A;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --info-color: #29B6F6;
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
    
    /* Header principal para CFI */
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
        content: '🎓';
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
    
    /* KPI Cards específicas para CFI */
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
    
    .kpi-card-personal::before {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .kpi-card-empleados::before {
        background: linear-gradient(90deg, #4CAF50, #66BB6A);
    }
    
    .kpi-card-departamento::before {
        background: linear-gradient(90deg, #FF9800, #FFB74D);
    }
    
    .kpi-card-seguridad::before {
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
        background: linear-gradient(135deg, var(--background-light) 0%, #B3E5FC 100%);
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
        background: linear-gradient(135deg, var(--background-light) 0%, #E1F5FE 100%);
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
    if controller_available and CFIRRHHController:
        return CFIRRHHController()
    return None

if 'cfi_controller' not in st.session_state:
    st.session_state.cfi_controller = init_controller()

controller = st.session_state.cfi_controller

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
                data.to_excel(writer, index=False, sheet_name='Datos_RRHH_CFI')
        
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
    <h1>🎓 Dashboard Recursos Humanos CFI</h1>
    <h2>Centro de Formación Industrial - Análisis de Personal</h2>
    <p>Sistema integral de análisis de costes de personal y gestión de recursos humanos</p>
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
                    <strong>✅ Sistema CFI Activo:</strong> {status['months_with_data']} meses con datos, {status['months_empty']} pendientes
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
                    <strong>❌ Sistema CFI Inactivo:</strong> Datos no cargados
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("❌ Controlador CFI no disponible")

with col2:
    if st.button("🔄 Cargar desde SharePoint", help="Cargar datos CFI desde SharePoint"):
        with st.spinner("Cargando datos CFI desde SharePoint..."):
            try:
                if excel_available and get_dataframe:
                    st.info("📥 Descargando datos CFI desde SharePoint...")
                    excel_data = get_dataframe('CFI_08_RRHH')
                    
                    if excel_data is None:
                        st.error("❌ No se pudieron obtener datos de SharePoint")
                        st.markdown("""
                        **Posibles causas:**
                        - Error de conectividad con SharePoint  
                        - URL incorrecta en secrets.toml para CFI_08_RRHH
                        - Credenciales incorrectas
                        - Archivo Excel CFI no encontrado
                        """)
                    
                    elif isinstance(excel_data, str):
                        st.error("❌ SharePoint devolvió un mensaje de error:")
                        with st.expander("📄 Mensaje completo"):
                            st.code(excel_data)
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'success':
                        # Datos ya parseados por excel_loader
                        st.success("🎉 Datos CFI ya parseados por excel_loader - inicializando directamente")
                        
                        if controller and controller.initialize_with_data(excel_data):
                            st.success("✅ Datos CFI cargados correctamente desde SharePoint")
                            st.balloons()
                            
                            # Mostrar resumen de datos cargados
                            metadata = excel_data.get('metadata', {})
                            st.info(f"📊 Registros procesados: {metadata.get('total_records', 0)}")
                            if metadata.get('departments_count'):
                                st.write(f"🏢 Departamentos: {metadata['departments_count']}")
                            if metadata.get('months_count'):
                                st.write(f"📅 Meses: {metadata['months_count']}")
                            
                            st.rerun()
                        else:
                            st.error("❌ Error inicializando controlador CFI con datos parseados")
                    
                    elif isinstance(excel_data, dict) and excel_data.get('status') == 'error':
                        st.error(f"❌ Error en datos parseados CFI: {excel_data.get('message')}")
                        
                        # Mostrar detalles del error
                        metadata = excel_data.get('metadata', {})
                        if 'errors' in metadata and metadata['errors']:
                            st.markdown("**Errores específicos:**")
                            for error in metadata['errors'][:5]:
                                st.error(f"• {error}")
                    
                    elif isinstance(excel_data, dict):
                        # Datos raw de Excel - necesitan parsing manual
                        st.info("⚙️ Datos CFI raw detectados - parseando manualmente...")
                        
                        if parser_available and parse_excel:
                            try:
                                parsed_data = parse_excel(excel_data)
                                
                                if parsed_data and parsed_data.get('status') == 'success':
                                    if controller and controller.initialize_with_data(parsed_data):
                                        st.success("✅ Datos CFI raw parseados y cargados correctamente")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error inicializando controlador CFI")
                                else:
                                    error_msg = parsed_data.get('message', 'Error desconocido') if parsed_data else 'Sin respuesta del parser'
                                    st.error(f"❌ Error parseando datos CFI raw: {error_msg}")
                            
                            except Exception as e:
                                st.error(f"❌ Excepción parseando datos CFI raw: {e}")
                        else:
                            st.error("❌ Parser CFI no disponible para datos raw")
                    
                    else:
                        st.error("❌ Tipo de datos CFI no soportado")
                        st.write(f"Tipo recibido: {type(excel_data)}")
                
                else:
                    st.error("❌ Módulos Excel Loader no disponibles")
                    
            except Exception as e:
                st.error(f"❌ Error crítico durante carga CFI: {e}")
                st.exception(e)

with col3:
    if st.button("📁 Subir Excel Local", help="Subir archivo Excel CFI desde tu computadora"):
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
            ["📊 Análisis Individual", "📈 Comparación Multi-mes"],
            help="Selecciona el tipo de análisis que deseas realizar"
        )
        
        if analysis_mode == "📊 Análisis Individual":
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
        st.metric("Empleados (último mes)", status['total_employees_latest'])
        st.metric("Coste Total (último mes)", f"€{status['total_cost_latest']:,.0f}")
    
    # ================================================================
    # ANÁLISIS INDIVIDUAL
    # ================================================================
    if analysis_mode == "📊 Análisis Individual":
        
        # Obtener KPIs del mes seleccionado
        kpis = controller.get_monthly_kpis(selected_month)
        
        # Mostrar alertas si las hay (CORREGIDO - sin alertas de datos incompletos)
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
            <h3 class="section-title">📊 KPIs Principales CFI - """ + selected_month.title() + """</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar mensaje si no hay datos
        if not kpis['has_data']:
            st.info(f"📅 {selected_month.title()} - Datos pendientes de cargar")
        
        # 4 KPI Cards en 2 filas según especificaciones
        col1, col2 = st.columns(2)
        
        with col1:
            # KPI Card 1: Total Gasto en Personal
            display_kpi_card(
                "💰 Total Gasto Personal",
                f"€{kpis['total_gasto_personal']:,.0f}",
                [
                    ("Promedio/Empleado", f"€{kpis['promedio_coste_empleado']:,.0f}"),
                    ("Total Devengado", f"€{kpis['total_devengado']:,.0f}"),
                    ("Total Líquido", f"€{kpis['total_liquido']:,.0f}")
                ],
                "personal"
            )
        
        with col2:
            # KPI Card 2: Cantidad de Trabajadores
            display_kpi_card(
                "👥 Trabajadores por Mes",
                f"{kpis['total_empleados']} empleados",
                [
                    ("Departamentos", f"{kpis['departamentos_activos']} activos"),
                    ("Promedio Devengado", f"€{kpis['promedio_devengado_empleado']:,.0f}"),
                    ("Total Deducciones", f"€{kpis['total_deducciones']:,.0f}")
                ],
                "empleados"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            # KPI Card 3: Trabajadores por Departamento
            if kpis['analisis_departamentos']:
                dept_info = kpis['analisis_departamentos'][0]  # Mostrar el departamento con más empleados
                dept_sorted = sorted(kpis['analisis_departamentos'], key=lambda x: x['cantidad_empleados'], reverse=True)
                main_dept = dept_sorted[0]
                
                dept_details = []
                for dept in dept_sorted[:3]:  # Top 3 departamentos
                    dept_details.append((dept['departamento'], f"{dept['cantidad_empleados']} empleados"))
                
                display_kpi_card(
                    "🏢 Distribución por Departamento",
                    f"{main_dept['departamento']}",
                    dept_details,
                    "departamento"
                )
            else:
                display_kpi_card(
                    "🏢 Distribución por Departamento",
                    "Sin datos",
                    [("Total Departamentos", "0")],
                    "departamento"
                )
        
        with col4:
            # KPI Card 4: Aportaciones a la Seguridad Social
            display_kpi_card(
                "🏥 Aportaciones Seguridad Social",
                f"€{kpis['total_ss_empresa'] + kpis['total_ss_trabajador']:,.0f}",
                [
                    ("SS Empresa", f"€{kpis['total_ss_empresa']:,.0f}"),
                    ("SS Trabajador", f"€{kpis['total_ss_trabajador']:,.0f}"),
                    ("IRPF", f"€{kpis['total_irpf']:,.0f}")
                ],
                "seguridad"
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
            # 1. Gráfica de barras: Coste total por departamento
            st.subheader("💰 Coste Total por Departamento")
            fig_costes = controller.create_costes_por_departamento_chart(selected_month)
            st.plotly_chart(fig_costes, use_container_width=True)
        
        with col2:
            # 2. Gráfica pie: Distribución de empleados por departamento
            st.subheader("🏢 Distribución de Empleados por Departamento")
            fig_dist = controller.create_departamentos_distribucion_chart(selected_month)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 3. Gráfica de barras: Deducciones por departamento
            st.subheader("📊 Deducciones por Departamento")
            fig_deducciones = controller.create_deducciones_por_departamento_chart(selected_month)
            st.plotly_chart(fig_deducciones, use_container_width=True)
        
        with col4:
            # 4. Gráfica de barras agrupadas: Aportaciones SS por departamento
            st.subheader("🏥 Aportaciones SS por Departamento")
            fig_ss = controller.create_aportaciones_ss_por_departamento_chart(selected_month)
            st.plotly_chart(fig_ss, use_container_width=True)
    
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
                <h3 class="section-title">📊 KPIs Comparativos CFI</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Calcular cambios porcentuales
            changes = controller.calculate_month_changes(selected_months)
            
            if changes:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Cambio en % de cantidad de trabajadores
                    change_empleados = changes['empleados_change']
                    color = "green" if change_empleados >= 0 else "red"
                    display_kpi_card(
                        "👥 Cambio Trabajadores",
                        f"{change_empleados:+.1f}%",
                        [
                            ("Desde", changes['first_month'].title()),
                            ("Hasta", changes['last_month'].title())
                        ],
                        "empleados"
                    )
                
                with col2:
                    # Cambio en % de coste total
                    change_coste = changes['coste_total_change']
                    display_kpi_card(
                        "💰 Cambio Coste Total",
                        f"{change_coste:+.1f}%",
                        [
                            ("Desde", changes['first_month'].title()),
                            ("Hasta", changes['last_month'].title())
                        ],
                        "personal"
                    )
                
                with col3:
                    # Cantidad media de trabajadores por mes
                    all_kpis = [controller.get_monthly_kpis(m) for m in selected_months]
                    valid_kpis = [k for k in all_kpis if k['has_data']]
                    
                    if valid_kpis:
                        media_trabajadores = sum(k['total_empleados'] for k in valid_kpis) / len(valid_kpis)
                        display_kpi_card(
                            "👥 Media Trabajadores/Mes",
                            f"{media_trabajadores:.0f}",
                            [
                                ("Meses Analizados", f"{len(valid_kpis)}"),
                                ("Rango", f"{len(selected_months)} seleccionados")
                            ],
                            "empleados"
                        )
                
                with col4:
                    # Aportación media SS por mes
                    if valid_kpis:
                        media_ss_empresa = sum(k['total_ss_empresa'] for k in valid_kpis) / len(valid_kpis)
                        media_ss_trabajador = sum(k['total_ss_trabajador'] for k in valid_kpis) / len(valid_kpis)
                        display_kpi_card(
                            "🏥 Media Aportaciones SS",
                            f"€{media_ss_empresa + media_ss_trabajador:,.0f}",
                            [
                                ("SS Empresa", f"€{media_ss_empresa:,.0f}"),
                                ("SS Trabajador", f"€{media_ss_trabajador:,.0f}")
                            ],
                            "seguridad"
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
                    label="📄 Descargar Tabla KPIs CFI",
                    data=csv_data,
                    file_name=f"KPIs_CFI_Comparativa_{datetime.now().strftime('%Y%m%d')}.csv",
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
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 1. Gráfica de líneas: Evolución de costes totales por mes
                st.subheader("📈 Evolución de Costes Totales")
                fig_evolucion = controller.create_evolucion_costes_chart(selected_months)
                st.plotly_chart(fig_evolucion, use_container_width=True)
            
            with col2:
                # 2. Gráfica de líneas: Aportaciones SS empresa y trabajador
                st.subheader("🏥 Evolución Aportaciones SS")
                fig_ss_evolucion = controller.create_aportaciones_ss_evolucion_chart(selected_months)
                st.plotly_chart(fig_ss_evolucion, use_container_width=True)

# ================================================================
# SECCIÓN DE BAJAS - SIN FILTROS (SIEMPRE VISIBLE)
# ================================================================
st.markdown("""
<div class="section-header">
    <h3 class="section-title">🏥 Análisis de Bajas y Altas - Información General</h3>
</div>
""", unsafe_allow_html=True)

if controller and controller.is_initialized:
    # Obtener resumen completo de bajas
    bajas_summary = controller.get_bajas_summary_all_months()
    
    if not bajas_summary.empty:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Estadísticas generales
            total_empleados_con_movimientos = len(bajas_summary)
            empleados_activos = len(bajas_summary[bajas_summary['Estado Actual'] == 'ACTIVO'])
            empleados_baja = len(bajas_summary[bajas_summary['Estado Actual'] == 'DE BAJA'])
            
            st.markdown(f"""
            **📊 Resumen General de Movimientos:**
            
            - **Total empleados con movimientos:** {total_empleados_con_movimientos}
            - **Empleados actualmente activos:** {empleados_activos}
            - **Empleados actualmente de baja:** {empleados_baja}
            - **Porcentaje de empleados activos:** {(empleados_activos/total_empleados_con_movimientos*100):.1f}%
            """)
            
            # Mostrar empleados actualmente de baja
            if empleados_baja > 0:
                st.markdown("**🚨 Empleados Actualmente de Baja:**")
                empleados_baja_df = bajas_summary[bajas_summary['Estado Actual'] == 'DE BAJA']
                for _, emp in empleados_baja_df.iterrows():
                    st.markdown(f"• **{emp['Empleado']}** - {emp['Motivo Último']}")
        
        with col2:
            st.markdown("**📋 Tabla Completa de Movimientos:**")
            st.dataframe(bajas_summary, use_container_width=True, hide_index=True, height=400)
            
            # Botón de descarga para bajas
            csv_bajas = bajas_summary.to_csv(index=False)
            st.download_button(
                label="📄 Descargar Análisis de Bajas",
                data=csv_bajas,
                file_name=f"Analisis_Bajas_CFI_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("📋 No se encontraron registros de bajas y altas en el sistema.")

else:
    # ================================================================
    # MODO SIN DATOS - CONFIGURACIÓN INICIAL
    # ================================================================
    st.markdown("""
    <div class="section-header">
        <h3 class="section-title">🔧 Configuración Inicial del Sistema CFI</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 Bienvenido al Dashboard de RRHH CFI
    
    Para comenzar a usar el sistema, carga los datos del Excel de costes de personal CFI:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔗 Conexión SharePoint CFI
        **Datos en tiempo real desde SharePoint CFI**
        
        **Características:**
        - ✅ Datos CFI actualizados automáticamente
        - ✅ Conexión directa con el sistema CFI
        - ✅ Procesa hojas "Listado de costes" y "Observaciones"
        
        **Formato esperado del Excel CFI:**
        - 📋 Hoja 1: "Listado de costes de empresa"
        - 🏥 Hoja 2: "Observaciones" (bajas y altas)
        - 👥 Estructura: Nombre, Departamento, Costes, SS
        
        **Requisitos:**
        - Archivo `secrets.toml` configurado con CFI_08_RRHH
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
        - 🏢 Hoja 1: Listado de costes (columnas C a U)
        - 🏥 Hoja 2: Observaciones de bajas/altas
        - 👥 Estructura de personal CFI
        
        **Columnas importantes:**
        - C: Nombre empleado
        - D: Mes (enero, febrero, etc.)
        - F: Departamento
        - H: Devengado | I: Líquido | J: Deducciones
        - M: SS Empresa | N: SS Trabajador | S: Coste Total
        
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
    <p><strong>🎓 CFI Dashboard RRHH v1.0</strong></p>
    <p>Sistema integral de análisis de recursos humanos CFI • Desarrollado por GANDB Team</p>
    <p>© 2025 Garlic & Beyond - Centro de Formación Industrial - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
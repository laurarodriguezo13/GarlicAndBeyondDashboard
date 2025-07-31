"""
KCTN_04_Costos.py - Dashboard Costos Garlic & Beyond COMPLETO MEJORADO
======================================================================
Dashboard completo de Costos para Garlic & Beyond.
Estilo cohesivo con el resto de la aplicación siguiendo la estética RRHH.

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 4.0 - Cohesivo con Estética Garlic & Beyond
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
        page_title="Dashboard Costos - Garlic & Beyond",
        page_icon="💰",
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
            from utils.controller_KCTN_04_Costos import CostosKCTNController
            controller_available = True
        except ImportError:
            try:
                from utils.controller_KCTN_04_Costos import CostosKCTNController
                controller_available = True
            except ImportError:
                controller_available = False
                CostosKCTNController = None
        
        return excel_available, controller_available, get_dataframe, CostosKCTNController
        
    except Exception as e:
        st.error(f"Error en importaciones: {e}")
        return False, False, None, None

excel_available, controller_available, get_dataframe, CostosKCTNController = safe_import()

# ================================================================
# CSS PERSONALIZADO PARA GARLIC & BEYOND - TEMA COSTOS
# ================================================================
st.markdown("""
<style>
    /* Importar Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para Garlic & Beyond - Tema Costos */
    :root {
        --primary-color: #D32F2F;
        --secondary-color: #F44336;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --info-color: #2196F3;
        --text-primary: #B71C1C;
        --text-secondary: #D32F2F;
        --background-white: #ffffff;
        --background-light: #FFEBEE;
        --border-light: #FFCDD2;
        --shadow-sm: 0 1px 2px 0 rgba(211, 47, 47, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(211, 47, 47, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(211, 47, 47, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(211, 47, 47, 0.1);
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
    
    /* Header principal para Garlic & Beyond - Tema Costos */
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
        content: '💰';
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
    
    /* KPI Cards específicas para Costos */
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
    
    .kpi-card-desgrane::before {
        background: linear-gradient(90deg, #4CAF50, #66BB6A);
    }
    
    .kpi-card-categoria1::before {
        background: linear-gradient(90deg, #2196F3, #42A5F5);
    }
    
    .kpi-card-corredor::before {
        background: linear-gradient(90deg, #FF9800, #FFB74D);
    }
    
    .kpi-card-porte::before {
        background: linear-gradient(90deg, #9C27B0, #BA68C8);
    }
    
    .kpi-card-coste-promedio::before {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
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
    
    /* Diferencia positiva/negativa */
    .metric-positive {
        color: #4CAF50 !important;
    }
    
    .metric-negative {
        color: #F44336 !important;
    }
    
    /* Secciones */
    .section-header {
        background: linear-gradient(135deg, var(--background-light) 0%, #FCE4EC 100%);
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
        background: linear-gradient(135deg, var(--background-light) 0%, #FCE4EC 100%);
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
    return None  # Se inicializará cuando se carguen datos

if 'costos_controller' not in st.session_state:
    st.session_state.costos_controller = init_controller()

controller = st.session_state.costos_controller

# ================================================================
# FUNCIONES DE UTILIDAD
# ================================================================
def display_kpi_card(title, main_value, sub_values, card_type="default"):
    """Muestra una KPI card con formato específico."""
    card_class = f"kpi-card kpi-card-{card_type}"
    
    sub_values_html = ""
    for label, value, style in sub_values:
        style_class = f' class="{style}"' if style else ''
        sub_values_html += f'<div class="metric-value-small"{style_class}><strong>{label}:</strong> {value}</div>'
    
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
    <h1>💰 Dashboard Costos KCTN</h1>
    <h2>Garlic & Beyond - Control de Materia Prima</h2>
    <p>Sistema avanzado de control de costes y análisis de rendimiento de materia prima</p>
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
                    📊 {status['total_records']} registros | 📅 {status['date_range']} | 🕒 {status['last_update']}
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
        st.markdown("""
        <div class="status-container">
            <div style="display: flex; align-items: center;">
                <span class="status-indicator status-red"></span>
                <strong>⚙️ Sistema Inicializando:</strong> Controlador no disponible
            </div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    if st.button("🔄 Cargar desde SharePoint", help="Cargar datos reales desde SharePoint"):
        with st.spinner("Cargando datos desde SharePoint..."):
            try:
                if excel_available and get_dataframe:
                    st.info("📥 Descargando datos desde SharePoint...")
                    excel_data = get_dataframe('KCTN_04_Costos')
                    
                    if excel_data and excel_data.get('status') == 'success':
                        # Inicializar controlador con datos
                        if CostosKCTNController:
                            st.session_state.costos_controller = CostosKCTNController(excel_data)
                            controller = st.session_state.costos_controller
                            
                            st.success("✅ Datos cargados correctamente desde SharePoint")
                            st.balloons()
                            
                            # Mostrar resumen de datos cargados
                            metadata = excel_data.get('metadata', {})
                            st.info(f"📊 Total registros: {metadata.get('total_records', 0)}")
                            
                            st.rerun()
                        else:
                            st.error("❌ Controlador no disponible")
                    else:
                        error_msg = excel_data.get('metadata', {}).get('error', 'Error desconocido') if excel_data else 'Sin respuesta'
                        st.error(f"❌ Error obteniendo datos: {error_msg}")
                else:
                    st.error("❌ Excel loader no disponible")
                    
            except Exception as e:
                st.error(f"❌ Error crítico durante carga: {e}")

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
            months_with_data = controller.get_months_with_data()
            
            # Seleccionar el último mes con datos por defecto
            default_index = 0
            if months_with_data:
                try:
                    last_month = months_with_data[-1]
                    default_index = available_months.index(last_month)
                except:
                    default_index = 0
            
            selected_month = st.selectbox(
                "**Seleccionar Mes:**", 
                available_months, 
                index=default_index,
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
        
        # ================================================================
        # SECCIÓN 1: KPI CARDS (5 cards según especificaciones)
        # ================================================================
        st.markdown(f"""
        <div class="section-header">
            <h3 class="section-title">📊 KPIs Principales - {selected_month}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar mensaje si no hay datos
        if not kpis['has_data']:
            st.info(f"📅 {selected_month} - Datos pendientes de cargar")
        
        # Primera fila: Desgrane y Categoría 1
        col1, col2 = st.columns(2)
        
        with col1:
            # KPI Card 1: Desgrane
            display_kpi_card(
                "🌾 Desgrane",
                f"{kpis['total_kg_desgranado']:,.0f} kg",
                [
                    ("% Desgrane", f"{kpis['promedio_porcentaje_desg']*100:.1f}%", ""),
                ],
                "desgrane"
            )
        
        with col2:
            # KPI Card 2: Categoría 1
            diferencia = kpis['promedio_diferencia']
            diferencia_style = "metric-positive" if diferencia >= 0 else "metric-negative"
            diferencia_icon = "📈" if diferencia >= 0 else "📉"
            
            display_kpi_card(
                "🥇 Categoría 1",
                f"{kpis['total_kg_cat1']:,.0f} kg",
                [
                    ("% Real", f"{kpis['promedio_porcentaje_cat1']*100:.1f}%", ""),
                    ("% Esperado", f"{kpis['promedio_porcentaje_estimado']*100:.1f}%", ""),
                    ("Diferencia", f"{diferencia_icon} {diferencia*100:.1f}%", diferencia_style)
                ],
                "categoria1"
            )
        
        # Segunda fila: Corredor y Porte
        col3, col4 = st.columns(2)
        
        with col3:
            # KPI Card 3: Coste de corredor
            display_kpi_card(
                "🤝 Coste de Corredor",
                f"€{kpis['promedio_coste_kg_corredor']:.3f}/kg",
                [
                    ("Total", f"€{kpis['total_coste_corredor']:,.2f}", ""),
                ],
                "corredor"
            )
        
        with col4:
            # KPI Card 4: Porte
            display_kpi_card(
                "🚛 Porte",
                f"€{kpis['promedio_coste_kg_porte']:.3f}/kg",
                [
                    ("Total", f"€{kpis['total_porte']:,.2f}", ""),
                ],
                "porte"
            )
        
        # Tercera fila: Coste promedio (centrado)
        col_center = st.columns([1, 2, 1])
        with col_center[1]:
            # KPI Card 5: Promedio de Coste por Kg diente Cat 1
            display_kpi_card(
                "💰 Promedio Coste/Kg Diente Cat 1",
                f"€{kpis['promedio_coste_kg_diente_cat1']:.3f}",
                [
                    ("por kilogramo", "", ""),
                ],
                "coste-promedio"
            )
        
        # ================================================================
        # SECCIÓN 2: GRÁFICOS INDIVIDUALES
        # ================================================================
        st.markdown(f"""
        <div class="section-header">
            <h3 class="section-title">📈 Análisis Gráfico - {selected_month}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Tendencia de Coste por Kg diente Cat 1
            st.subheader("📈 Evolución Coste/Kg Diente Cat 1")
            fig_coste_trend = controller.create_coste_cat1_trend_chart(selected_month)
            st.plotly_chart(fig_coste_trend, use_container_width=True)
        
        with col2:
            # 2. Comparación por Proveedor
            st.subheader("🏭 Inversión por Proveedor")
            fig_proveedor_comp = controller.create_proveedor_comparison_chart(selected_month)
            st.plotly_chart(fig_proveedor_comp, use_container_width=True)
        
        # ================================================================
        # SECCIÓN 3: MATRIZ DE RENDIMIENTO
        # ================================================================
        st.markdown(f"""
        <div class="section-header">
            <h3 class="section-title">📊 Matriz de Rendimiento - {selected_month}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Generar matriz con indicadores de color
        matrix_df = controller.create_performance_matrix_styled(selected_month)
        
        if isinstance(matrix_df, pd.DataFrame) and not matrix_df.empty:
            # Mostrar la matriz con emojis de colores
            st.dataframe(
                matrix_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Información de umbrales
            st.markdown("""
            **📋 Umbrales de Rendimiento:**
            - 🟢 **ÓPTIMO**: % DESG ≥85% | % CAT I ≥55% | % CAT II ≥25% | % DAG ≥20% | % MERMA ≤10%
            - 🔴 **FUERA DE UMBRAL**: Valores que no cumplen los requisitos mínimos
            """)
        else:
            st.info(f"No hay datos disponibles para la matriz de rendimiento en {selected_month}")
        
        # ================================================================
        # SECCIÓN 4: ANÁLISIS DETALLADO DE PROVEEDORES
        # ================================================================
        st.markdown(f"""
        <div class="section-header">
            <h3 class="section-title">🏭 Análisis Detallado de Proveedores - {selected_month}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        proveedor_data = controller.get_analisis_proveedor_data(selected_month)
        
        if proveedor_data['has_data']:
            # Crear DataFrame de proveedores
            proveedores_df = pd.DataFrame(proveedor_data['proveedores'])
            
            # Formatear columnas
            proveedores_df['kg_mp'] = proveedores_df['kg_mp'].apply(lambda x: f"{x:,.0f} kg")
            proveedores_df['total_inversion'] = proveedores_df['total_inversion'].apply(lambda x: f"€{x:,.2f}")
            proveedores_df['coste_kg_cat1'] = proveedores_df['coste_kg_cat1'].apply(lambda x: f"€{x:.3f}")
            proveedores_df['porcentaje_cat1'] = proveedores_df['porcentaje_cat1'].apply(lambda x: f"{x*100:.1f}%")
            proveedores_df['coste_corredor'] = proveedores_df['coste_corredor'].apply(lambda x: f"€{x:.2f}")
            proveedores_df['coste_porte'] = proveedores_df['coste_porte'].apply(lambda x: f"€{x:.2f}")
            
            # Renombrar columnas
            proveedores_df.columns = [
                'Proveedor', 'kg M.P.', 'Inversión Total', 'Coste/Kg Cat 1', 
                '% Cat 1', 'Coste Corredor', 'Coste Porte'
            ]
            
            st.dataframe(
                proveedores_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"No hay datos de proveedores para {selected_month}")
    
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
                # Mostrar tabla con estilo
                st.dataframe(
                    kpi_table, 
                    use_container_width=True, 
                    hide_index=True,
                    height=400
                )
                
                # Botón de descarga
                csv_data = kpi_table.to_csv(index=False)
                st.download_button(
                    label="📄 Descargar Tabla KPIs",
                    data=csv_data,
                    file_name=f"KPIs_Comparativa_Costos_{datetime.now().strftime('%Y%m%d')}.csv",
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
            
            # Dashboard de evolución integral
            st.subheader("📊 Dashboard de Evolución Integral")
            try:
                fig_comprehensive = controller.create_comprehensive_evolution_chart(selected_months)
                st.plotly_chart(fig_comprehensive, use_container_width=True)
            except Exception as e:
                st.error(f"Error creando dashboard integral: {e}")
                # Fallback a gráficos individuales
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Evolución Coste/Kg Diente Cat 1")
                    fig_coste_evolution = controller.create_multi_month_comparison_chart(selected_months, 'coste_cat1')
                    st.plotly_chart(fig_coste_evolution, use_container_width=True)
                
                with col2:
                    st.subheader("🤝 Evolución Coste Total Corredor")
                    fig_corredor_evolution = controller.create_multi_month_comparison_chart(selected_months, 'total_corredor')
                    st.plotly_chart(fig_corredor_evolution, use_container_width=True)
                
                st.subheader("🚛 Evolución Coste Total Porte")
                fig_porte_evolution = controller.create_multi_month_comparison_chart(selected_months, 'total_porte')
                st.plotly_chart(fig_porte_evolution, use_container_width=True)
            
            # ================================================================
            # SECCIÓN 3: RESUMEN ESTADÍSTICO MULTI-MES
            # ================================================================
            st.markdown("""
            <div class="section-header">
                <h3 class="section-title">📊 Resumen Estadístico</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Calcular estadísticas agregadas
            total_months_with_data = len([m for m in selected_months if m in controller.monthly_data and controller.monthly_data[m]['has_data']])
            
            if total_months_with_data > 0:
                # Obtener todos los KPIs de los meses seleccionados
                all_kpis = [controller.get_monthly_kpis(m) for m in selected_months if m in controller.monthly_data and controller.monthly_data[m]['has_data']]
                
                if all_kpis:
                    # Calcular totales y promedios
                    total_records = sum(kpi['total_records'] for kpi in all_kpis)
                    total_kg_mp = sum(kpi['total_kg_mp'] for kpi in all_kpis)
                    total_inversion = sum(kpi['total_inversion'] for kpi in all_kpis)
                    avg_coste_cat1 = sum(kpi['promedio_coste_kg_diente_cat1'] for kpi in all_kpis) / len(all_kpis)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📋 Total Registros", f"{total_records:,}")
                    
                    with col2:
                        st.metric("⚖️ Total kg M.P.", f"{total_kg_mp:,.0f} kg")
                    
                    with col3:
                        st.metric("💶 Total Inversión", f"€{total_inversion:,.0f}")
                    
                    with col4:
                        st.metric("💰 Coste Promedio Cat 1", f"€{avg_coste_cat1:.3f}/kg")
            else:
                st.info("No hay datos para mostrar resumen estadístico")

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
    ### 🚀 Bienvenido al Dashboard de Costos KCTN de Garlic & Beyond
    
    Para comenzar a usar el sistema, carga los datos del Excel de control de materia prima:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔗 Conexión SharePoint
        **Datos en tiempo real desde SharePoint**
        
        **Características:**
        - ✅ Datos de control M.P. actualizados
        - ✅ Análisis de costes automatizado
        - ✅ Matriz de rendimiento en tiempo real
        
        **Requisitos:**
        - Archivo `secrets.toml` configurado
        - Acceso a SharePoint autorizado
        - Excel "Control entrada M.P. Planta pelado" disponible
        """)
        
        if st.button("🔗 Conectar SharePoint", key="connect_sp", type="primary"):
            st.info("🔄 Usar el botón 'Cargar desde SharePoint' en la parte superior")
    
    with col2:
        st.markdown("""
        #### 📁 Carga Manual
        **Subir archivo Excel local**
        
        **Formato esperado:**
        - 📋 Archivo Excel (.xlsx)
        - 📊 Hoja "Desgrane Datos"
        - 🌾 Columnas A-AC según especificación
        - 📅 Fechas de entrega válidas
        
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
    <p><strong>💰 Garlic & Beyond Dashboard Costos KCTN v4.0</strong></p>
    <p>Sistema avanzado de control de materia prima y análisis de costes • Desarrollado por GANDB Team</p>
    <p>© 2025 Garlic & Beyond - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
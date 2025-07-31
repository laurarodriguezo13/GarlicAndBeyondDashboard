"""
🏭 Dashboard Producción KCTN - VERSIÓN VISUAL Y LIMPIA
=====================================================
Dashboard completamente visual para análisis de procesamiento de ajos.
Interface limpia sin logging molesto y siguiendo instrucciones exactas.

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 2.1 (Visual y Limpia)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# ================================================================
# CONFIGURACIÓN DE PÁGINA
# ================================================================

st.set_page_config(
    page_title="🏭 Producción KCTN",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# IMPORTACIONES DEL SISTEMA
# ================================================================

# Configurar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
utils_dir = os.path.join(project_root, 'utils')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if utils_dir not in sys.path:
    sys.path.insert(0, utils_dir)

# Importaciones con manejo de errores
SYSTEM_READY = True
try:
    from utils.excel_loader import get_dataframe, get_system_status, clear_cache
    from utils.controller_KCTN_01_Produccion import create_controller, MESES_NOMBRES, COLORS
except ImportError as e:
    st.error(f"❌ Error importando sistema: {e}")
    SYSTEM_READY = False

# ================================================================
# CONFIGURACIÓN GLOBAL
# ================================================================

MESES_NOMBRES_LOCAL = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

# Estilos CSS mejorados
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1f4e79 0%, #2e7d32 50%, #1565c0 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.main-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
}

.main-header h3 {
    margin: 0.5rem 0;
    font-weight: 300;
    opacity: 0.9;
}

.kpi-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-left: 5px solid #1f4e79;
    margin-bottom: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.kpi-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #1f4e79;
    margin-bottom: 0.5rem;
}

.kpi-label {
    font-size: 1rem;
    color: #666;
    font-weight: 500;
    margin-bottom: 0.5rem;
}

.kpi-detail {
    font-size: 0.85rem;
    color: #888;
    line-height: 1.4;
}

.delta-excelente { 
    color: #2e7d32; 
    font-weight: bold; 
    font-size: 0.9rem;
    padding: 0.25rem 0.5rem;
    background: rgba(46, 125, 50, 0.1);
    border-radius: 6px;
    display: inline-block;
}

.delta-bueno { 
    color: #ff9800; 
    font-weight: bold; 
    font-size: 0.9rem;
    padding: 0.25rem 0.5rem;
    background: rgba(255, 152, 0, 0.1);
    border-radius: 6px;
    display: inline-block;
}

.delta-regular { 
    color: #f44336; 
    font-weight: bold; 
    font-size: 0.9rem;
    padding: 0.25rem 0.5rem;
    background: rgba(244, 67, 54, 0.1);
    border-radius: 6px;
    display: inline-block;
}

.delta-optimo { 
    color: #4caf50; 
    font-weight: bold; 
    font-size: 0.9rem;
    padding: 0.25rem 0.5rem;
    background: rgba(76, 175, 80, 0.1);
    border-radius: 6px;
    display: inline-block;
}

.delta-atencion { 
    color: #e91e63; 
    font-weight: bold; 
    font-size: 0.9rem;
    padding: 0.25rem 0.5rem;
    background: rgba(233, 30, 99, 0.1);
    border-radius: 6px;
    display: inline-block;
}

.status-panel {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    margin-bottom: 1rem;
}

.metric-section {
    margin: 2rem 0;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1f4e79;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e9ecef;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
# FUNCIONES DE CARGA DE DATOS (CON LOGGING OCULTO)
# ================================================================

@st.cache_data(ttl=300)
def load_production_data_silent():
    """Carga datos de producción silenciosamente."""
    if not SYSTEM_READY:
        return None
    
    try:
        # Capturar todo el output en un container oculto
        with st.spinner("🔄 Cargando datos de producción..."):
            raw_data = get_dataframe('KCTN_01_Produccion')
        
        if raw_data is None:
            return None
        
        if raw_data.get('status') != 'success':
            return None
        
        return raw_data
        
    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        return None

# ================================================================
# FUNCIONES DE INTERFAZ
# ================================================================

def render_header():
    """Renderiza el header principal con estilo mejorado."""
    st.markdown("""
    <div class="main-header">
        <h1>🏭 Dashboard Producción KCTN</h1>
        <h3>Análisis Integral de Procesamiento de Ajos</h3>
        <p style="margin: 0; opacity: 0.8;">Control de Rendimiento, Calidad y Productividad</p>
    </div>
    """, unsafe_allow_html=True)

def render_system_status_compact():
    """Renderiza estado del sistema de forma compacta."""
    
    if not SYSTEM_READY:
        st.error("❌ **Sistema no operativo** - Verificar configuración")
        return False
    
    # Panel de estado compacto
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            system_status = get_system_status()
            
            with col1:
                if st.button("🔄 **Actualizar**", use_container_width=True):
                    clear_cache()
                    st.rerun()
            
            with col2:
                sharepoint_status = "🟢 Online" if system_status.get('sharepoint_available', False) else "🔴 Offline"
                st.markdown(f"**SharePoint:** {sharepoint_status}")
            
            with col3:
                st.markdown(f"**Parsers:** {system_status.get('parsers_cached', 0)}")
            
            with col4:
                current_time = datetime.now()
                st.markdown(f"**Hora:** {current_time.strftime('%H:%M')}")
            
            return system_status.get('sharepoint_available', False)
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return False

def render_sidebar_filters_fixed():
    """Renderiza filtros en el sidebar (SIN format_func para evitar error)."""
    st.sidebar.markdown("# 🎯 **Configuración Producción**")
    
    # Modo de análisis
    modo = st.sidebar.radio(
        "**Modo de Análisis:**",
        ["Individual", "Comparación Multi-Mes"],
        index=0
    )
    
    if modo == "Individual":
        # Selector de mes individual
        mes_seleccionado = st.sidebar.selectbox(
            "**Mes a Analizar:**",
            MESES_NOMBRES_LOCAL,
            index=6  # Julio por defecto
        )
        
        st.sidebar.markdown(f"**Mes seleccionado:** {mes_seleccionado}")
        
        return {
            'modo': 'individual',
            'mes': mes_seleccionado,
            'meses': None
        }
    
    else:
        # Slider para múltiples meses (SIN format_func)
        st.sidebar.markdown("**Rango de Meses:**")
        
        inicio_idx = st.sidebar.slider(
            "Mes Inicio:",
            0, len(MESES_NOMBRES_LOCAL) - 1,
            0  # Enero
        )
        
        fin_idx = st.sidebar.slider(
            "Mes Fin:",
            inicio_idx, len(MESES_NOMBRES_LOCAL) - 1,
            min(6, len(MESES_NOMBRES_LOCAL) - 1)  # Julio
        )
        
        meses_seleccionados = MESES_NOMBRES_LOCAL[inicio_idx:fin_idx + 1]
        
        # Mostrar nombres de meses seleccionados
        st.sidebar.markdown("**Meses seleccionados:**")
        for mes in meses_seleccionados:
            st.sidebar.markdown(f"• {mes}")
        
        return {
            'modo': 'comparison',
            'mes': None,
            'meses': meses_seleccionados
        }

def render_kpi_cards_visual(controller, filtros):
    """Renderiza cards de KPIs de forma más visual."""
    st.markdown('<div class="section-title">📊 Indicadores Clave de Rendimiento</div>', unsafe_allow_html=True)
    
    # Calcular KPIs según modo
    if filtros['modo'] == 'individual':
        kpis = controller.calculate_kpis_individual(filtros['mes'])
        subtitle = f"📅 **Mes:** {filtros['mes']} 2025"
    else:
        kpis = controller.calculate_kpis_comparison(filtros['meses'])
        subtitle = f"📅 **Período:** {filtros['meses'][0]} - {filtros['meses'][-1]} 2025"
    
    st.markdown(subtitle)
    st.markdown("---")
    
    if not kpis or kpis.get('mp_total', 0) == 0:
        st.warning("⚠️ No hay datos disponibles para el período seleccionado")
        return
    
    # === PRIMERA FILA: MATERIA PRIMA, DESGRANADO, CAT I ===
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Card 1: Materia Prima
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis.get('mp_total', 0):,.0f} kg</div>
            <div class="kpi-label">Materia Prima Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card 2: Desgranado
        desgr_pct = kpis.get('desgr_percentage', 0)
        delta_class = f"delta-{kpis.get('desgr_delta', 'regular').lower()}"
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis.get('desgr_total', 0):,.0f} kg</div>
            <div class="kpi-label">Rendimiento Desgranado</div>
            <div class="{delta_class}">{desgr_pct:.1f}% - {kpis.get('desgr_delta', 'Regular')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Card 3: CAT I
        cat_i_pct = kpis.get('cat_i_percentage', 0)
        delta_class = f"delta-{kpis.get('cat_i_delta', 'regular').lower()}"
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis.get('cat_i_total', 0):,.0f} kg</div>
            <div class="kpi-label">Categoría I</div>
            <div class="{delta_class}">{cat_i_pct:.1f}% - {kpis.get('cat_i_delta', 'Regular')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # === SEGUNDA FILA: CAT II, DAG, MERMA ===
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Card 4: CAT II
        cat_ii_pct = kpis.get('cat_ii_percentage', 0)
        delta_class = f"delta-{kpis.get('cat_ii_delta', 'regular').lower()}"
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis.get('cat_ii_total', 0):,.0f} kg</div>
            <div class="kpi-label">Categoría II</div>
            <div class="{delta_class}">{cat_ii_pct:.1f}% - {kpis.get('cat_ii_delta', 'Regular')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card 5: DAG
        dag_pct = kpis.get('dag_percentage', 0)
        delta_class = f"delta-{kpis.get('dag_delta', 'regular').lower()}"
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis.get('dag_total', 0):,.0f} kg</div>
            <div class="kpi-label">DAG</div>
            <div class="{delta_class}">{dag_pct:.1f}% - {kpis.get('dag_delta', 'Regular')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Card 6: Merma
        merma_pct = kpis.get('merma_percentage', 0)
        delta_class = f"delta-{kpis.get('merma_delta', 'regular').lower()}"
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpis.get('merma_total', 0):,.0f} kg</div>
            <div class="kpi-label">Merma</div>
            <div class="{delta_class}">{merma_pct:.1f}% - {kpis.get('merma_delta', 'Regular')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # === TERCERA FILA: PRODUCTIVIDAD, PROMEDIO DIARIO, PROMEDIO HORA ===
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Card 7: Productividad Personal
        productividad = kpis.get('productividad_personal', 0)
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{productividad:,.0f} kg</div>
            <div class="kpi-label">Productividad por Trabajador</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card 8: Promedio Diario
        promedio_diario = kpis.get('promedio_diario', {})
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label"><strong>Promedio Diario</strong></div>
            <div class="kpi-detail">
                <strong>MP:</strong> {promedio_diario.get('mp', 0):,.0f} kg<br>
                <strong>DESGR:</strong> {promedio_diario.get('desgr', 0):,.0f} kg<br>
                <strong>CAT I:</strong> {promedio_diario.get('cat_i', 0):,.0f} kg<br>
                <strong>CAT II:</strong> {promedio_diario.get('cat_ii', 0):,.0f} kg<br>
                <strong>DAG:</strong> {promedio_diario.get('dag', 0):,.0f} kg
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Card 9: Promedio por Hora
        promedio_hora = kpis.get('promedio_hora', {})
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label"><strong>Promedio por Hora</strong></div>
            <div class="kpi-detail">
                <strong>MP:</strong> {promedio_hora.get('mp', 0):,.0f} kg<br>
                <strong>DESGR:</strong> {promedio_hora.get('desgr', 0):,.0f} kg<br>
                <strong>CAT I:</strong> {promedio_hora.get('cat_i', 0):,.0f} kg<br>
                <strong>CAT II:</strong> {promedio_hora.get('cat_ii', 0):,.0f} kg<br>
                <strong>DAG:</strong> {promedio_hora.get('dag', 0):,.0f} kg
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_line_chart_enhanced(controller, filtros):
    """Renderiza gráfico de líneas mejorado."""
    st.markdown('<div class="section-title">📈 Evolución de Producción</div>', unsafe_allow_html=True)
    
    # Obtener datos
    if filtros['modo'] == 'individual':
        chart_data = controller.get_line_chart_data(mes=filtros['mes'])
    else:
        chart_data = controller.get_line_chart_data(meses=filtros['meses'])
    
    if 'error' in chart_data:
        st.warning(f"⚠️ {chart_data['error']}")
        return
    
    # Crear gráfico mejorado
    fig = go.Figure()
    
    data = chart_data['data']
    colors = {
        'MP': '#1f77b4',
        'DESGR': '#ff7f0e',
        'CAT I': '#2ca02c',
        'CAT II': '#d62728',
        'DAG': '#9467bd'
    }
    
    for metric in ['MP', 'DESGR', 'CAT I', 'CAT II', 'DAG']:
        fig.add_trace(go.Scatter(
            x=data['fechas'],
            y=data[metric],
            mode='lines+markers',
            name=metric,
            line=dict(color=colors[metric], width=3),
            marker=dict(size=8, line=dict(width=2, color='white')),
            hovertemplate=f'<b>{metric}</b><br>' +
                         'Fecha: %{x}<br>' +
                         'Cantidad: %{y:,.0f} kg<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=chart_data['title'],
            font=dict(size=20, color='#1f4e79'),
            x=0.5
        ),
        xaxis_title=chart_data['xaxis_title'],
        yaxis_title=chart_data['yaxis_title'],
        hovermode='x unified',
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="center", 
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        height=500,
        template='plotly_white',
        plot_bgcolor='rgba(248,249,250,0.8)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_stacked_bar_chart_enhanced(controller, filtros):
    """Renderiza gráfico de barras apiladas mejorado."""
    st.markdown('<div class="section-title">📊 Composición de Producción</div>', unsafe_allow_html=True)
    
    # Obtener datos
    if filtros['modo'] == 'individual':
        chart_data = controller.get_stacked_bar_data(mes=filtros['mes'])
    else:
        chart_data = controller.get_stacked_bar_data(meses=filtros['meses'])
    
    if 'error' in chart_data:
        st.warning(f"⚠️ {chart_data['error']}")
        return
    
    # Preparar datos
    data = chart_data['data']
    
    if chart_data['type'] == 'daily':
        x_values = [d['fecha'] for d in data]
    else:
        x_values = [d['mes'] for d in data]
    
    # Crear gráfico mejorado
    fig = go.Figure()
    
    colors_stack = {
        'CAT I': '#2ca02c',
        'CAT II': '#d62728', 
        'DAG': '#9467bd',
        'MERMA': '#8c564b'
    }
    
    for categoria in ['CAT I', 'CAT II', 'DAG', 'MERMA']:
        y_values = [d[categoria] for d in data]
        
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            name=categoria,
            marker_color=colors_stack[categoria],
            hovertemplate=f'<b>{categoria}</b><br>' +
                         ('Fecha: %{x}<br>' if chart_data['type'] == 'daily' else 'Mes: %{x}<br>') +
                         'Cantidad: %{y:,.0f} kg<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=chart_data['title'],
            font=dict(size=20, color='#1f4e79'),
            x=0.5
        ),
        xaxis_title=chart_data['xaxis_title'],
        yaxis_title=chart_data['yaxis_title'],
        barmode='stack',
        hovermode='x unified',
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="center", 
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        height=500,
        template='plotly_white',
        plot_bgcolor='rgba(248,249,250,0.8)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_summary_table_enhanced(controller, filtros):
    """Renderiza tabla de resumen mejorada."""
    st.markdown('<div class="section-title">📋 Tabla de Resumen</div>', unsafe_allow_html=True)
    
    # Obtener datos
    if filtros['modo'] == 'individual':
        table_data = controller.get_summary_table(mes=filtros['mes'])
    else:
        table_data = controller.get_summary_table(meses=filtros['meses'])
    
    if 'error' in table_data:
        st.warning(f"⚠️ {table_data['error']}")
        return
    
    # Mostrar tabla mejorada
    st.markdown(f"### {table_data['title']}")
    
    df_table = pd.DataFrame(table_data['data'])
    
    st.dataframe(
        df_table,
        use_container_width=True,
        hide_index=True,
        height=400
    )

def render_debug_info(production_data):
    """Renderiza información de debug en un expander oculto."""
    with st.expander("🔧 **Información Técnica del Sistema**", expanded=False):
        if production_data:
            metadata = production_data.get('metadata', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Estadísticas de Procesamiento:**")
                st.write(f"• Tiempo de procesamiento: {metadata.get('processing_time_seconds', 0):.2f}s")
                st.write(f"• Total de hojas: {metadata.get('total_sheets', 0)}")
                st.write(f"• Meses con datos: {metadata.get('months_with_data', 0)}")
                st.write(f"• Calidad de datos: {metadata.get('data_quality_score', 0)}%")
            
            with col2:
                st.markdown("**⚠️ Avisos y Errores:**")
                warnings = metadata.get('warnings', [])
                errors = metadata.get('errors', [])
                
                if warnings:
                    for warning in warnings:
                        st.warning(f"⚠️ {warning}")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                
                if not warnings and not errors:
                    st.success("✅ Sin avisos ni errores")

def render_footer_enhanced():
    """Renderiza footer mejorado."""
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 2rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>🧄 Garlic And Beyond</strong><br>
                <small>Private Equity Firm</small>
            </div>
            <div>
                <strong>📊 Dashboard KCTN Producción</strong><br>
                <small>Versión 2.1 - 2025</small>
            </div>
            <div>
                <strong>📅 Última actualización:</strong><br>
                <small>{}</small>
            </div>
        </div>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')), unsafe_allow_html=True)

# ================================================================
# FUNCIÓN PRINCIPAL
# ================================================================

def main():
    """Función principal del dashboard."""
    try:
        # Header principal
        render_header()
        
        # Panel de control compacto
        system_ready = render_system_status_compact()
        
        if not system_ready:
            st.error("❌ **SharePoint no disponible** - Verificar configuración en secrets.toml")
            st.stop()
        
        # Cargar datos silenciosamente
        production_data = load_production_data_silent()
        
        if production_data is None:
            st.error("❌ **No se pudieron cargar los datos de producción**")
            st.info("💡 **Solución:** Verificar URL SharePoint y configuración del parser")
            
            # Mostrar información de debug
            render_debug_info(None)
            st.stop()
        
        # Crear controller
        controller = create_controller(production_data)
        
        # Filtros corregidos (sin error de slider)
        filtros = render_sidebar_filters_fixed()
        
        # Configurar controller
        if filtros['modo'] == 'individual':
            controller.set_filter_mode('individual', month=filtros['mes'])
        else:
            controller.set_filter_mode('comparison', months=filtros['meses'])
        
        # === CONTENIDO PRINCIPAL VISUAL ===
        
        # KPIs principales
        render_kpi_cards_visual(controller, filtros)
        
        st.markdown("---")
        
        # Gráficos mejorados
        col1, col2 = st.columns([1, 1])
        
        with col1:
            render_line_chart_enhanced(controller, filtros)
        
        with col2:
            render_stacked_bar_chart_enhanced(controller, filtros)
        
        st.markdown("---")
        
        # Tabla de resumen
        render_summary_table_enhanced(controller, filtros)
        
        # Información de debug oculta
        render_debug_info(production_data)
        
        # Footer mejorado
        render_footer_enhanced()
        
    except Exception as e:
        st.error(f"❌ **Error crítico:** {e}")
        
        with st.expander("🔧 **Información de Debugging**", expanded=False):
            st.write("**System Ready:**", SYSTEM_READY)
            st.write("**Error Type:**", type(e).__name__)
            st.write("**Current Time:**", datetime.now())
            st.code(str(e))

if __name__ == "__main__":
    main()
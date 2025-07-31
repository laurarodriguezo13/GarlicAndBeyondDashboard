"""
🧄 Garlic and Beyond Dashboard
==============================
Dashboard corporativo integral para la evaluación operativa y estratégica
de las subsidiarias KCTN y CFI con datos en tiempo real desde SharePoint.

Autor: GANDB Dashboard Team
Fecha: 2025
"""

import streamlit as st
import datetime

# ========== DEBUG AVANZADO TEMPORAL ==========
st.write("🔍 **DEBUG AVANZADO - SharePoint Connectivity**")

# Importar el sistema SharePoint
from auth.sharepoint_auth import sharepoint_system

# HABILITAR logging detallado
sharepoint_system.disable_silent_mode()

# Test 1: Información del sistema
st.write("**1. Info del sistema:**")
info = sharepoint_system.get_system_info()
st.json(info)

# Test 2: Test de token
st.write("**2. Test de token:**")
token = sharepoint_system.get_access_token(force_refresh=True)
if token:
    st.write("✅ Token obtenido:", token[:20] + "...")
else:
    st.write("❌ NO se pudo obtener token")

# Test 3: URL específica CFI RRHH
st.write("**3. Test URL CFI RRHH:**")
test_url = st.secrets["sharepoint_links"]["cfi"]["rrhh"]
st.write("URL original:", test_url)

# Convertir a Graph URL
graph_url = sharepoint_system.convert_sharepoint_url_to_graph_api(test_url)
st.write("Graph URL:", graph_url)

# Test 4: Descarga real
st.write("**4. Test de descarga:**")
with st.spinner("Descargando..."):
    result = sharepoint_system.download_excel_from_sharepoint(test_url, all_sheets=False)

if result is not None:
    st.write("✅ ¡DESCARGA EXITOSA!")
    st.write("Tipo de resultado:", type(result))
    if hasattr(result, 'shape'):
        st.write("Dimensiones:", result.shape)
        st.write("Primeras 5 filas:")
        st.dataframe(result.head())
else:
    st.write("❌ DESCARGA FALLÓ")

st.write("========== FIN DEBUG ==========")
# ========== FIN DEBUG AVANZADO ==========

# ================================================================
# CONFIGURACIÓN DE PÁGINA
# ================================================================

st.set_page_config(
    page_title="🧄 Garlic and Beyond Dashboard",
    page_icon="🧄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# ESTILOS CSS PERSONALIZADOS
# ================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1f4e79 0%, #2e7d32 50%, #ff6b35 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .info-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #2e7d32;
        margin: 1rem 0;
    }
    
    .navigation-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .nav-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e9ecef;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .nav-card:hover {
        border-color: #2e7d32;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
    }
    
    .status-active {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-info {
        background-color: #cce7ff;
        color: #004085;
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# FUNCIONES AUXILIARES
# ================================================================

def render_main_header():
    """Renderiza el header principal del dashboard."""
    st.markdown("""
    <div class="main-header">
        <h1>🧄 Garlic and Beyond</h1>
        <h2>Dashboard Corporativo Integral</h2>
        <p style="font-size: 1.1rem; margin-top: 1rem;">
            Consolidación de información operativa y estratégica en tiempo real<br>
            <strong>KCTN • CFI • Análisis Integrado</strong>
        </p>
        <div style="margin-top: 1.5rem;">
            <span class="status-badge status-active">🟢 Sistema Activo</span>
            <span class="status-badge status-info">📊 Datos Actualizados</span>
            <span class="status-badge status-info">🔗 SharePoint Conectado</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_system_overview():
    """Renderiza la vista general del sistema."""
    st.markdown("""
    <div class="info-section">
        <h3>📋 Acerca del Sistema</h3>
        <p>
            Este dashboard corporativo fue diseñado específicamente para <strong>Garlic and Beyond</strong> 
            con el objetivo de consolidar y visualizar información crítica de las subsidiarias 
            <strong>KCTN (Keep Close to Nature)</strong> y <strong>CFI (Conagra Food Ingredients)</strong>.
        </p>
        <ul>
            <li><strong>Automatización Total:</strong> Conexión directa con archivos Excel en OneDrive/SharePoint</li>
            <li><strong>Tiempo Real:</strong> Actualización automática de datos operativos</li>
            <li><strong>Modular:</strong> 15 módulos especializados por área funcional</li>
            <li><strong>Seguro:</strong> Autenticación integrada con SharePoint</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def render_architecture_info():
    """Renderiza información sobre la arquitectura del sistema."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🏗️ Arquitectura del Sistema</h4>
            <ul>
                <li><strong>Frontend:</strong> Streamlit con diseño responsive</li>
                <li><strong>Backend:</strong> Python con módulos especializados</li>
                <li><strong>Datos:</strong> Excel files via SharePoint API</li>
                <li><strong>Autenticación:</strong> Azure AD / SharePoint</li>
                <li><strong>Parsing:</strong> Pandas + Controllers personalizados</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>⚙️ Componentes Principales</h4>
            <ul>
                <li><strong>Parser Modules:</strong> 15 analizadores de datos</li>
                <li><strong>Controller Layer:</strong> Lógica de negocio</li>
                <li><strong>Excel Loader:</strong> Carga automática de archivos</li>
                <li><strong>SharePoint Auth:</strong> Gestión de credenciales</li>
                <li><strong>Secrets Management:</strong> Configuración segura</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_navigation_dashboard():
    """Renderiza el panel de navegación principal."""
    st.markdown("## 🚀 Navegación del Dashboard")
    
    # KCTN Modules
    st.markdown("### 🏭 KCTN - Keep Close to Nature")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <h4>📊 KCTN - Producción</h4>
            <p>Métricas de producción, eficiencia, rendimiento y KPIs operativos en tiempo real.</p>
            <small>Módulo: KCTN_01_Produccion.py</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="nav-card">
            <h4>👥 KCTN - RRHH</h4>
            <p>Gestión de recursos humanos, nómina, ausencias y métricas de personal.</p>
            <small>Módulo: KCTN_02_RRHH.py</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="nav-card">
            <h4>🚛 KCTN - Logística</h4>
            <p>Seguimiento de envíos, inventario en tránsito y optimización de rutas.</p>
            <small>Módulo: KCTN_03_Logistica.py</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="nav-card">
            <h4>💰 KCTN - Costos</h4>
            <p>Análisis de costos operativos, márgenes y control presupuestario.</p>
            <small>Módulo: KCTN_04_Costos.py</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="nav-card">
            <h4>🛒 KCTN - Compras & Ventas</h4>
            <p>Gestión de proveedores, órdenes de compra y análisis de ventas.</p>
            <small>Módulo: KCTN_05_Compras_Ventas.py</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="nav-card">
            <h4>📦 KCTN - Inventario</h4>
            <p>Control de stock, rotación, valoración y gestión de almacenes.</p>
            <small>Módulo: KCTN_06_Inventario.py</small>
        </div>
        """, unsafe_allow_html=True)

    # CFI Modules
    st.markdown("### 🏢 CFI - Conagra Food Ingredients")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <h4>📊 CFI - Producción</h4>
            <p>Métricas de producción y eficiencia operativa de la planta CFI.</p>
            <small>Módulo: CFI_07_Produccion.py</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="nav-card">
            <h4>👥 CFI - RRHH</h4>
            <p>Recursos humanos, gestión de personal y métricas laborales CFI.</p>
            <small>Módulo: CFI_08_RRHH.py</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="nav-card">
            <h4>🚛 CFI - Logística</h4>
            <p>Operaciones logísticas, distribución y cadena de suministro CFI.</p>
            <small>Módulo: CFI_09_Logistica.py</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="nav-card">
            <h4>💰 CFI - Costos</h4>
            <p>Estructura de costos, análisis financiero y control presupuestario.</p>
            <small>Módulo: CFI_10_Costos.py</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="nav-card">
            <h4>💼 CFI - Ventas</h4>
            <p>Análisis de ventas, clientes y performance comercial.</p>
            <small>Módulo: CFI_11_Ventas.py</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="nav-card">
            <h4>📦 CFI - Inventario</h4>
            <p>Gestión de inventarios, stock y control de almacenes CFI.</p>
            <small>Módulo: CFI_12_Inventario.py</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="nav-card">
            <h4>🛒 CFI - Compras</h4>
            <p>Gestión de compras, proveedores y procurement CFI.</p>
            <small>Módulo: CFI_13_Compras.py</small>
        </div>
        """, unsafe_allow_html=True)

    # Estudios Especiales
    st.markdown("### 📊 Análisis Estratégicos")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <h4>📈 Estudio de Ventas Pasado</h4>
            <p>Análisis histórico de ventas, tendencias y proyecciones estratégicas.</p>
            <small>Módulo: Estudio_Ventas_Pasado_14.py</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="nav-card">
            <h4>💬 Comentarios Comité Operativo</h4>
            <p>Seguimiento de decisiones, acciones y comentarios del comité directivo.</p>
            <small>Módulo: Comentarios_comite_operativo_15.py</small>
        </div>
        """, unsafe_allow_html=True)

def render_instructions():
    """Renderiza las instrucciones de uso del sistema."""
    st.markdown("## 📖 Instrucciones de Uso")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🚀 Primeros Pasos</h4>
            <ol>
                <li><strong>Navegación:</strong> Utiliza el menú lateral para acceder a los módulos</li>
                <li><strong>Autenticación:</strong> El sistema se conecta automáticamente a SharePoint</li>
                <li><strong>Datos:</strong> Los archivos Excel se cargan automáticamente desde OneDrive</li>
                <li><strong>Visualización:</strong> Cada módulo presenta dashboards específicos</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Funcionalidades Clave</h4>
            <ul>
                <li><strong>Actualización automática</strong> de datos</li>
                <li><strong>Filtros interactivos</strong> por fecha y categoría</li>
                <li><strong>Exportación</strong> de reportes en PDF/Excel</li>
                <li><strong>Análisis comparativo</strong> entre subsidiarias</li>
                <li><strong>Alertas</strong> de indicadores críticos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_technical_specs():
    """Renderiza las especificaciones técnicas."""
    st.markdown("## 🔧 Especificaciones Técnicas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>15</h3>
            <p>Módulos Funcionales</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>30+</h3>
            <p>Archivos Parser/Controller</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>100%</h3>
            <p>Automatización</p>
        </div>
        """, unsafe_allow_html=True)

def render_footer():
    """Renderiza el footer con información adicional."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p>
            <strong>🧄 Garlic and Beyond Dashboard</strong> | 
            Desarrollado para Private Equity Operations | 
            Última actualización: {}
        </p>
        <p>
            <small>
                Sistema integrado con OneDrive/SharePoint • 
                Datos en tiempo real • 
                Arquitectura modular escalable
            </small>
        </p>
    </div>
    """.format(datetime.datetime.now().strftime("%B %Y")), unsafe_allow_html=True)

# ================================================================
# PÁGINA PRINCIPAL
# ================================================================

def main():
    """Función principal que renderiza toda la homepage."""
    
    # Header principal
    render_main_header()
    
    # Vista general del sistema
    render_system_overview()
    
    # Información de arquitectura
    render_architecture_info()
    
    # Especificaciones técnicas
    render_technical_specs()
    
    # Panel de navegación
    render_navigation_dashboard()
    
    # Instrucciones de uso
    render_instructions()
    
    # Footer
    render_footer()

if __name__ == "__main__":
    main()

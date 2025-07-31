"""
Comentarios_comite_operativo_15.py - Sistema de Comentarios para Comité Operativo
================================================================================
Sistema integral para recopilar comentarios y sugerencias previas al comité operativo.
Permite a los miembros del equipo registrar sus comentarios, editarlos y visualizarlos
de manera organizada y estética.

Funcionalidades:
- Formulario de comentarios con nombre, fecha del comité, título y descripción
- Visualización de comentarios en cards elegantes con colores únicos por persona
- Sistema de edición y eliminación de comentarios
- Reporte final con fecha del comité
- Contador de participantes y estadísticas
- Exportación de comentarios

Autor: GANDB Dashboard Team  
Fecha: 2025
Versión: 1.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import hashlib
import json
import time
import io

# ================================================================
# CONFIGURACIÓN DE PÁGINA
# ================================================================
if 'page_config_set' not in st.session_state:
    st.set_page_config(
        page_title="Comentarios Comité Operativo - Garlic & Beyond",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True

# ================================================================
# CSS PERSONALIZADO PARA COMITÉ OPERATIVO - GARLIC & BEYOND
# ================================================================
st.markdown("""
<style>
    /* Importar Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para Comité Operativo - Garlic & Beyond */
    :root {
        --primary-color: #6366F1;
        --secondary-color: #8B5CF6;
        --accent-color: #EC4899;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --error-color: #EF4444;
        --info-color: #3B82F6;
        --text-primary: #1F2937;
        --text-secondary: #6B7280;
        --background-white: #ffffff;
        --background-light: #F8FAFC;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --border-light: #E5E7EB;
        --agenda-primary: #1e3a8a;
        --agenda-secondary: #3b82f6;
        --agenda-light: #dbeafe;
    }
    
    /* Fuente global */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Fondo global */
    .main .block-container {
        background: var(--background-light);
        padding-top: 1rem;
        max-width: 1400px;
    }
    
    /* Header principal para Comité Operativo */
    .comite-header {
        background: var(--background-gradient);
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .comite-header::before {
        content: '💬';
        position: absolute;
        top: 1.5rem;
        right: 2rem;
        font-size: 4rem;
        opacity: 0.2;
    }
    
    .comite-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(45deg, #ffffff, #f0f8ff);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .comite-header h2 {
        font-size: 1.5rem;
        font-weight: 500;
        margin: 1rem 0;
        opacity: 0.95;
    }
    
    .comite-header p {
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 1rem;
        opacity: 0.9;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Formulario de comentarios */
    .comment-form {
        background: var(--background-white);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: var(--card-shadow);
        margin-bottom: 2rem;
        border: 1px solid var(--border-light);
    }
    
    .form-header {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 2px solid var(--background-light);
    }
    
    .form-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .form-subtitle {
        color: var(--text-secondary);
        font-size: 1rem;
    }
    
    /* Cards de comentarios */
    .comment-card {
        background: var(--background-white);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .comment-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow);
    }
    
    .comment-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .comment-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        flex-grow: 1;
    }
    
    .comment-actions {
        display: flex;
        gap: 0.5rem;
        opacity: 0.6;
        transition: opacity 0.3s ease;
    }
    
    .comment-card:hover .comment-actions {
        opacity: 1;
    }
    
    .comment-content {
        color: var(--text-secondary);
        line-height: 1.6;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    
    .comment-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 1rem;
        border-top: 1px solid var(--background-light);
    }
    
    .comment-author {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .author-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .author-name {
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .comment-date {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    /* Reporte final */
    .final-report {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-top: 3rem;
        box-shadow: var(--card-shadow);
    }
    
    .report-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .report-date {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Autenticación */
    .auth-container {
        background: var(--background-white);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: var(--card-shadow);
        max-width: 400px;
        margin: 0 auto;
        text-align: center;
        border: 1px solid var(--border-light);
    }
    
    .auth-title {
        color: var(--agenda-primary);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Agenda Cards */
    .agenda-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .agenda-item {
        background: linear-gradient(135deg, var(--agenda-primary) 0%, var(--agenda-secondary) 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: var(--card-shadow);
        position: relative;
        transition: transform 0.3s ease;
    }
    
    .agenda-item:hover {
        transform: translateY(-4px);
    }
    
    .agenda-item-number {
        position: absolute;
        top: 1rem;
        left: 1rem;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .agenda-item-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .agenda-item-date {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    
    .add-agenda-button {
        background: linear-gradient(135deg, var(--agenda-primary), var(--agenda-secondary));
        color: white;
        border: 2px dashed rgba(255, 255, 255, 0.3);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .add-agenda-button:hover {
        background: linear-gradient(135deg, var(--agenda-secondary), var(--agenda-primary));
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    .add-agenda-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    /* Notas de reunión */
    .notes-section {
        background: var(--agenda-light);
        padding: 2rem;
        border-radius: 16px;
        margin: 2rem 0;
        border: 1px solid var(--agenda-secondary);
    }
    
    .notes-header {
        text-align: center;
        margin-bottom: 2rem;
        color: var(--agenda-primary);
    }
    
    .note-item {
        background: var(--background-white);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid var(--agenda-primary);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .note-agenda-ref {
        font-size: 0.9rem;
        color: var(--agenda-primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .note-content {
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    .note-timestamp {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
        text-align: right;
    }
    
    /* Secciones mejoradas con más diferenciación */
    .section-header {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin: 3rem 0 2rem 0;
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: none;
        position: relative;
        overflow: hidden;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899, #10b981);
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        flex-grow: 1;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--text-secondary), transparent);
        margin-left: 1rem;
    }
    
    /* Secciones específicas con colores únicos */
    .section-agenda {
        border-left: 8px solid var(--agenda-primary);
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    }
    
    .section-agenda .section-title {
        color: var(--agenda-primary);
    }
    
    .section-comments {
        border-left: 8px solid var(--accent-color);
        background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%);
    }
    
    .section-comments .section-title {
        color: var(--accent-color);
    }
    
    .section-notes {
        border-left: 8px solid var(--success-color);
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
    
    .section-notes .section-title {
        color: var(--success-color);
    }
    
    .section-report {
        border-left: 8px solid var(--warning-color);
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }
    
    .section-report .section-title {
        color: var(--warning-color);
    }
    
    /* Botones personalizados */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Alertas */
    .alert {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-success {
        background: #F0FDF4;
        border-color: var(--success-color);
        color: #166534;
    }
    
    .alert-info {
        background: #EFF6FF;
        border-color: var(--info-color);
        color: #1E40AF;
    }
    
    .alert-warning {
        background: #FFFBEB;
        border-color: var(--warning-color);
        color: #92400E;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .comite-header h1 { font-size: 2rem; }
        .comite-header h2 { font-size: 1.2rem; }
        .comment-form { padding: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# FUNCIONES DE UTILIDAD
# ================================================================
def generate_color_for_name(name):
    """Genera un color único basado en el nombre."""
    colors = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", 
        "#FF9FF3", "#54A0FF", "#5F27CD", "#00D2D3", "#FF9F43",
        "#10AC84", "#EE5A24", "#0652DD", "#9C88FF", "#FFC312",
        "#C4E538", "#12CBC4", "#FDA7DF", "#ED4C67", "#F79F1F"
    ]
    hash_object = hashlib.md5(name.encode())
    hash_hex = hash_object.hexdigest()
    color_index = int(hash_hex, 16) % len(colors)
    return colors[color_index]

def get_initials(name):
    """Obtiene las iniciales de un nombre."""
    words = name.strip().split()
    if len(words) >= 2:
        return f"{words[0][0]}{words[-1][0]}".upper()
    elif len(words) == 1:
        return words[0][:2].upper()
    return "??"

def export_comments_to_csv(comments, committee_date):
    """Exporta los comentarios a CSV."""
    if not comments:
        return None
    
    df_data = []
    for comment in comments:
        df_data.append({
            'Fecha_Comite': comment.get('fecha_comite', committee_date.strftime('%d/%m/%Y')),
            'Nombre': comment['nombre'],
            'Titulo': comment['titulo'],
            'Comentario': comment['comentario'],
            'Fecha_Creacion': comment['timestamp'],
            'ID': comment['id']
        })
    
    df = pd.DataFrame(df_data)
    return df.to_csv(index=False)

def export_complete_report(agenda_items, comments, meeting_notes, committee_date):
    """Exporta el reporte completo del comité a Excel."""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Agenda
        if agenda_items:
            agenda_data = []
            for item in agenda_items:
                agenda_data.append({
                    'Orden': item['orden'],
                    'Título': item['titulo'],
                    'Fecha_Comite': item.get('fecha_agenda', committee_date.strftime('%d/%m/%Y')),
                    'Creado': item['timestamp']
                })
            df_agenda = pd.DataFrame(agenda_data)
            df_agenda.to_excel(writer, sheet_name='Agenda', index=False)
        
        # Hoja 2: Comentarios Previos
        if comments:
            df_comments = pd.DataFrame([{
                'Fecha_Comite': comment.get('fecha_comite', committee_date.strftime('%d/%m/%Y')),
                'Nombre': comment['nombre'],
                'Titulo': comment['titulo'],
                'Comentario': comment['comentario'],
                'Fecha_Creacion': comment['timestamp']
            } for comment in comments])
            df_comments.to_excel(writer, sheet_name='Comentarios_Previos', index=False)
        
        # Hoja 3: Notas de Reunión
        if meeting_notes:
            df_notes = pd.DataFrame([{
                'Punto_Agenda': note['agenda_item'],
                'Notas': note['notes'],
                'Fecha_Comite': note.get('fecha_comite', committee_date.strftime('%d/%m/%Y')),
                'Timestamp': note['timestamp']
            } for note in meeting_notes])
            df_notes.to_excel(writer, sheet_name='Notas_Reunion', index=False)
        
        # Hoja 4: Resumen
        summary_data = [{
            'Fecha_Comite': committee_date.strftime('%d/%m/%Y'),
            'Total_Puntos_Agenda': len(agenda_items),
            'Total_Comentarios': len(comments),
            'Total_Notas': len(meeting_notes),
            'Participantes_Comentarios': len(set(c['nombre'] for c in comments)) if comments else 0,
            'Generado': datetime.now().strftime('%d/%m/%Y %H:%M')
        }]
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Resumen', index=False)
    
    processed_data = output.getvalue()
    return processed_data

def authenticate_user(username, password):
    """Autentica usuario para acceso a agenda."""
    return username == "paxcp" and password == "paxcp"

# ================================================================
# INICIALIZACIÓN DEL SESSION STATE
# ================================================================
if 'comments' not in st.session_state:
    st.session_state.comments = []

if 'committee_date' not in st.session_state:
    st.session_state.committee_date = date.today() + timedelta(days=1)

if 'editing_comment' not in st.session_state:
    st.session_state.editing_comment = None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'agenda_items' not in st.session_state:
    st.session_state.agenda_items = []

if 'agenda_date' not in st.session_state:
    st.session_state.agenda_date = date.today() + timedelta(days=1)

if 'meeting_notes' not in st.session_state:
    st.session_state.meeting_notes = []

# ================================================================
# HEADER PRINCIPAL
# ================================================================
st.markdown("""
<div class="comite-header">
    <h1>💬 Sistema de Comentarios</h1>
    <h2>Comité Operativo - Garlic & Beyond</h2>
    <p>Comparte tus ideas, observaciones y sugerencias antes del comité operativo. 
    Tu participación es clave para una reunión más productiva y enfocada.</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# FORMULARIO DE COMENTARIOS
# ================================================================
st.markdown("""
<div class="section-header">
    <h3 class="section-title">✍️ Agregar Nuevo Comentario</h3>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="comment-form">', unsafe_allow_html=True)
    
    # Header del formulario
    st.markdown("""
    <div class="form-header">
        <h3 class="form-title">📝 Nuevo Comentario para el Comité</h3>
        <p class="form-subtitle">Completa todos los campos para agregar tu comentario</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Campos del formulario
    col1, col2 = st.columns([1, 1])
    
    with col1:
        nombre = st.text_input(
            "👤 **Tu Nombre Completo:**",
            placeholder="Ej: María García López",
            help="Ingresa tu nombre completo tal como aparece en el equipo"
        )
    
    with col2:
        fecha_comite = st.date_input(
            "📅 **Fecha del Comité Operativo:**",
            value=st.session_state.committee_date,
            min_value=date.today(),
            help="Selecciona la fecha del próximo comité operativo"
        )
    
    titulo = st.text_input(
        "📋 **Título del Comentario:**",
        placeholder="Ej: Propuesta de mejora en proceso de producción",
        help="Un título descriptivo que resuma tu comentario"
    )
    
    comentario = st.text_area(
        "💭 **Tu Comentario/Sugerencia:**",
        placeholder="Describe detalladamente tu comentario, sugerencia o punto a discutir en el comité operativo...",
        height=120,
        help="Sé específico y constructivo en tu comentario"
    )
    
    # Botones de acción
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 **Guardar Comentario**", type="primary"):
            if nombre and titulo and comentario:
                # Actualizar fecha del comité en session state
                st.session_state.committee_date = fecha_comite
                
                # Crear nuevo comentario
                nuevo_comentario = {
                    'id': len(st.session_state.comments) + 1,
                    'nombre': nombre.strip(),
                    'titulo': titulo.strip(),
                    'comentario': comentario.strip(),
                    'fecha_comite': fecha_comite.strftime('%d/%m/%Y'),
                    'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'color': generate_color_for_name(nombre.strip())
                }
                
                st.session_state.comments.append(nuevo_comentario)
                
                st.success("✅ ¡Comentario guardado exitosamente!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Por favor completa todos los campos obligatorios")
    
    with col2:
        if st.button("🗑️ **Limpiar Formulario**"):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================================================================
# SECCIÓN DE AGENDA - SOLO PARA USUARIO AUTORIZADO
# ================================================================
st.markdown("""
<div class="section-header">
    <h3 class="section-title">📋 Gestión de Agenda del Comité</h3>
</div>
""", unsafe_allow_html=True)

# Sistema de autenticación
if not st.session_state.authenticated:
    st.markdown("""
    <div class="auth-container">
        <h3 class="auth-title">🔐 Acceso Restringido</h3>
        <p>Solo usuarios autorizados pueden gestionar la agenda</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("👤 Usuario:", placeholder="Ingresa tu usuario")
        password = st.text_input("🔒 Contraseña:", type="password", placeholder="Ingresa tu contraseña")
        
        if st.button("🚪 Iniciar Sesión", type="primary"):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.success("✅ Autenticación exitosa")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")

else:
    # Usuario autenticado - mostrar gestión de agenda
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
    
    with col2:
        st.markdown("### 📅 Configurar Agenda del Comité")
        agenda_date = st.date_input(
            "**Fecha del Comité para la Agenda:**",
            value=st.session_state.agenda_date,
            min_value=date.today(),
            help="Selecciona la fecha del comité para esta agenda"
        )
        st.session_state.agenda_date = agenda_date
    
    # Formulario para agregar nuevo punto de agenda
    with st.expander("➕ **Agregar Nuevo Punto de Agenda**", expanded=False):
        new_agenda_title = st.text_input(
            "📝 **Título del Punto de Agenda:**",
            placeholder="Ej: Revisión de KPIs del mes anterior"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 **Agregar a Agenda**", type="primary"):
                if new_agenda_title.strip():
                    nuevo_punto = {
                        'id': len(st.session_state.agenda_items) + 1,
                        'orden': len(st.session_state.agenda_items) + 1,
                        'titulo': new_agenda_title.strip(),
                        'fecha_agenda': agenda_date.strftime('%d/%m/%Y'),
                        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M')
                    }
                    st.session_state.agenda_items.append(nuevo_punto)
                    st.success("✅ Punto agregado a la agenda")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Por favor ingresa un título")
        
        with col2:
            if st.button("🗑️ **Limpiar Agenda**"):
                st.session_state.agenda_items = []
                st.success("✅ Agenda limpiada")
                time.sleep(1)
                st.rerun()
    
    # Mostrar agenda actual
    if st.session_state.agenda_items:
        st.markdown("### 📋 **Agenda del Comité**")
        
        # Filtrar agenda por fecha seleccionada
        agenda_filtrada = [item for item in st.session_state.agenda_items 
                          if item.get('fecha_agenda') == agenda_date.strftime('%d/%m/%Y')]
        
        if agenda_filtrada:
            st.markdown('<div class="agenda-container">', unsafe_allow_html=True)
            
            # Crear columnas para mostrar las cards
            cols = st.columns(2)  # 2 columnas por fila
            
            for i, item in enumerate(agenda_filtrada):
                col_index = i % 2
                with cols[col_index]:
                    agenda_card = f"""
                    <div class="agenda-item">
                        <div class="agenda-item-number">{item['orden']}</div>
                        <h4 class="agenda-item-title">{item['titulo']}</h4>
                        <div class="agenda-item-date">📅 {item['fecha_agenda']}</div>
                    </div>
                    """
                    st.markdown(agenda_card, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botón para publicar agenda
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🚀 **Publicar Agenda**", type="primary"):
                    st.success("✅ ¡Agenda publicada exitosamente!")
                    st.balloons()
        else:
            st.info(f"📅 No hay puntos de agenda para la fecha {agenda_date.strftime('%d/%m/%Y')}")
    else:
        st.info("📝 No hay puntos en la agenda. Usa el botón '+' para agregar el primer punto.")

# ================================================================
# SECCIÓN ELIMINADA - ESTADÍSTICAS NO NECESARIAS
# ================================================================

# ================================================================
# VISUALIZACIÓN DE COMENTARIOS
# ================================================================
if st.session_state.comments:
    st.markdown("""
    <div class="section-header">
        <h3 class="section-title">💬 Comentarios Registrados</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        nombres_unicos = sorted(list(set(comment['nombre'] for comment in st.session_state.comments)))
        filtro_nombre = st.selectbox(
            "🔍 **Filtrar por Participante:**",
            ["Todos"] + nombres_unicos
        )
    
    with col2:
        fechas_comite_unicas = sorted(list(set(comment['fecha_comite'] for comment in st.session_state.comments)), reverse=True)
        filtro_fecha = st.selectbox(
            "📅 **Filtrar por Fecha del Comité:**",
            ["Todas las fechas"] + fechas_comite_unicas
        )
    
    with col3:
        if st.button("📥 **Exportar CSV**"):
            csv_data = export_comments_to_csv(st.session_state.comments, st.session_state.committee_date)
            if csv_data:
                st.download_button(
                    label="💾 Descargar Comentarios",
                    data=csv_data,
                    file_name=f"Comentarios_Comite_{st.session_state.committee_date.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    # Aplicar filtros
    comments_to_show = st.session_state.comments.copy()
    
    if filtro_nombre != "Todos":
        comments_to_show = [c for c in comments_to_show if c['nombre'] == filtro_nombre]
    
    if filtro_fecha != "Todas las fechas":
        comments_to_show = [c for c in comments_to_show if c['fecha_comite'] == filtro_fecha]
    
    # Ordenar por más reciente por defecto
    comments_to_show = sorted(comments_to_show, key=lambda x: x['id'], reverse=True)
    
    # Mostrar comentarios
    for comment in comments_to_show:
        color = comment['color']
        initials = get_initials(comment['nombre'])
        
        # Crear el HTML de la card
        card_html = f"""
        <div class="comment-card" style="border-left-color: {color};">
            <div class="comment-header">
                <h4 class="comment-title">{comment['titulo']}</h4>
                <div style="font-size: 0.8rem; color: var(--text-secondary); font-weight: 500;">
                    📅 Comité: {comment.get('fecha_comite', 'Sin fecha')}
                </div>
            </div>
            <div class="comment-content">
                {comment['comentario']}
            </div>
            <div class="comment-footer">
                <div class="comment-author">
                    <div class="author-avatar" style="background-color: {color};">
                        {initials}
                    </div>
                    <span class="author-name">- {comment['nombre']}</span>
                </div>
                <div class="comment-date">{comment['timestamp']}</div>
            </div>
        </div>
        """
        
        # Mostrar la card con botones de acción
        col1, col2, col3 = st.columns([8, 1, 1])
        
        with col1:
            st.markdown(card_html, unsafe_allow_html=True)
        
        with col2:
            if st.button("✏️", key=f"edit_{comment['id']}", help="Editar comentario"):
                st.session_state.editing_comment = comment['id']
                st.rerun()
        
        with col3:
            if st.button("🗑️", key=f"delete_{comment['id']}", help="Eliminar comentario"):
                st.session_state.comments = [c for c in st.session_state.comments if c['id'] != comment['id']]
                st.success("✅ Comentario eliminado")
                time.sleep(1)
                st.rerun()
        
        # Modal de edición
        if st.session_state.editing_comment == comment['id']:
            with st.expander("✏️ **Editando Comentario**", expanded=True):
                nuevo_titulo = st.text_input("Título:", value=comment['titulo'], key=f"edit_title_{comment['id']}")
                nuevo_comentario = st.text_area("Comentario:", value=comment['comentario'], key=f"edit_comment_{comment['id']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Guardar Cambios", key=f"save_{comment['id']}"):
                        # Actualizar comentario
                        for i, c in enumerate(st.session_state.comments):
                            if c['id'] == comment['id']:
                                st.session_state.comments[i]['titulo'] = nuevo_titulo
                                st.session_state.comments[i]['comentario'] = nuevo_comentario
                                break
                        st.session_state.editing_comment = None
                        st.success("✅ Comentario actualizado")
                        time.sleep(1)
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancelar", key=f"cancel_{comment['id']}"):
                        st.session_state.editing_comment = None
                        st.rerun()

else:
    # Mensaje cuando no hay comentarios
    st.markdown("""
    <div class="alert alert-info">
        <strong>📝 ¡Sé el primero en comentar!</strong><br>
        Aún no hay comentarios registrados para el comité operativo. 
        Utiliza el formulario de arriba para agregar el primer comentario.
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# SECCIÓN DE TOMA DE NOTAS DURANTE EL COMITÉ
# ================================================================
st.markdown("""
<div class="section-header">
    <h3 class="section-title">📝 Toma de Notas del Comité</h3>
</div>
""", unsafe_allow_html=True)

# Verificar si hay agenda disponible
agenda_available = [item for item in st.session_state.agenda_items]

if agenda_available:
    st.markdown("""
    <div class="notes-section">
        <div class="notes-header">
            <h4>✍️ Registrar Notas por Punto de Agenda</h4>
            <p>Selecciona el punto de agenda y registra las notas de la discusión</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Selector de punto de agenda
            agenda_options = []
            for item in agenda_available:
                agenda_options.append(f"{item['orden']}. {item['titulo']} ({item.get('fecha_agenda', 'Sin fecha')})")
            
            selected_agenda_point = st.selectbox(
                "📋 **Seleccionar Punto de Agenda:**",
                agenda_options,
                help="Selecciona el punto de agenda sobre el que quieres tomar notas"
            )
        
        with col2:
            notes_date = st.date_input(
                "📅 **Fecha de las Notas:**",
                value=date.today(),
                help="Fecha cuando se toman estas notas"
            )
        
        # Campo de notas
        meeting_notes_text = st.text_area(
            "📝 **Notas de la Discusión:**",
            placeholder="Registra aquí las notas, decisiones, acuerdos o puntos importantes discutidos sobre este tema...",
            height=120,
            help="Sé detallado y registra decisiones clave y próximos pasos"
        )
        
        # Botones de acción
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("💾 **Guardar Notas**", type="primary"):
                if selected_agenda_point and meeting_notes_text.strip():
                    nueva_nota = {
                        'id': len(st.session_state.meeting_notes) + 1,
                        'agenda_item': selected_agenda_point,
                        'notes': meeting_notes_text.strip(),
                        'fecha_comite': notes_date.strftime('%d/%m/%Y'),
                        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M')
                    }
                    st.session_state.meeting_notes.append(nueva_nota)
                    st.success("✅ Notas guardadas exitosamente")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Por favor completa todos los campos")
    
    # Mostrar notas existentes
    if st.session_state.meeting_notes:
        st.markdown("### 📚 **Notas Registradas**")
        
        # Filtros para notas
        col1, col2 = st.columns([2, 2])
        with col1:
            fechas_notas = sorted(list(set(note['fecha_comite'] for note in st.session_state.meeting_notes)), reverse=True)
            filtro_fecha_notas = st.selectbox(
                "📅 **Filtrar por Fecha:**",
                ["Todas las fechas"] + fechas_notas
            )
        
        with col2:
            puntos_agenda_notas = sorted(list(set(note['agenda_item'] for note in st.session_state.meeting_notes)))
            filtro_agenda_notas = st.selectbox(
                "📋 **Filtrar por Punto de Agenda:**",
                ["Todos los puntos"] + puntos_agenda_notas
            )
        
        # Aplicar filtros
        notas_filtradas = st.session_state.meeting_notes.copy()
        
        if filtro_fecha_notas != "Todas las fechas":
            notas_filtradas = [n for n in notas_filtradas if n['fecha_comite'] == filtro_fecha_notas]
        
        if filtro_agenda_notas != "Todos los puntos":
            notas_filtradas = [n for n in notas_filtradas if n['agenda_item'] == filtro_agenda_notas]
        
        # Mostrar notas filtradas
        for note in sorted(notas_filtradas, key=lambda x: x['id'], reverse=True):
            note_html = f"""
            <div class="note-item">
                <div class="note-agenda-ref">📋 {note['agenda_item']}</div>
                <div class="note-content">{note['notes']}</div>
                <div class="note-timestamp">📅 {note['fecha_comite']} | 🕒 {note['timestamp']}</div>
            </div>
            """
            
            col1, col2 = st.columns([10, 1])
            with col1:
                st.markdown(note_html, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"delete_note_{note['id']}", help="Eliminar nota"):
                    st.session_state.meeting_notes = [n for n in st.session_state.meeting_notes if n['id'] != note['id']]
                    st.success("✅ Nota eliminada")
                    time.sleep(1)
                    st.rerun()

else:
    st.markdown("""
    <div class="alert alert-warning">
        <strong>⚠️ No hay agenda disponible</strong><br>
        Para tomar notas, primero debe crearse una agenda. Solo usuarios autorizados pueden crear la agenda.
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# REPORTE FINAL COMPLETO
# ================================================================
st.markdown("""
<div class="section-header">
    <h3 class="section-title">📊 Reporte Completo del Comité</h3>
</div>
""", unsafe_allow_html=True)

# Estadísticas del reporte completo
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📋 Puntos de Agenda", len(st.session_state.agenda_items))

with col2:
    st.metric("💬 Comentarios Previos", len(st.session_state.comments))

with col3:
    st.metric("📝 Notas de Reunión", len(st.session_state.meeting_notes))

with col4:
    participantes = len(set(c['nombre'] for c in st.session_state.comments)) if st.session_state.comments else 0
    st.metric("👥 Participantes", participantes)

# Botón de descarga del reporte completo
if st.session_state.agenda_items or st.session_state.comments or st.session_state.meeting_notes:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📥 **Descargar Reporte Completo (Excel)**", type="primary", help="Descarga agenda, comentarios y notas en Excel"):
            excel_data = export_complete_report(
                st.session_state.agenda_items,
                st.session_state.comments,
                st.session_state.meeting_notes,
                st.session_state.committee_date
            )
            
            if excel_data:
                st.download_button(
                    label="💾 **Generar y Descargar Reporte**",
                    data=excel_data,
                    file_name=f"Reporte_Comite_Completo_{st.session_state.committee_date.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("✅ Reporte generado exitosamente")

if st.session_state.comments:
    fechas_comites = list(set(comment.get('fecha_comite', '') for comment in st.session_state.comments if comment.get('fecha_comite')))
    proxima_fecha = max(fechas_comites) if fechas_comites else st.session_state.committee_date.strftime('%d/%m/%Y')
    
    st.markdown(f"""
    <div class="final-report">
        <h2 class="report-title">📋 Reporte Comités Operativos</h2>
        <p class="report-date">Próxima fecha: {proxima_fecha}</p>
        <p style="margin-top: 1rem; opacity: 0.9;">
            Total de comentarios registrados: {len(st.session_state.comments)}<br>
            Participantes únicos: {len(set(comment['nombre'] for comment in st.session_state.comments))}<br>
            Comités con comentarios: {len(fechas_comites)}
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="final-report">
        <h2 class="report-title">📋 Reporte Comité Operativo</h2>
        <p class="report-date">{st.session_state.committee_date.strftime('%A, %d de %B del %Y')}</p>
        <p style="margin-top: 1rem; opacity: 0.9;">
            No hay comentarios registrados aún
        </p>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# SIDEBAR - INFORMACIÓN ADICIONAL
# ================================================================
with st.sidebar:
    st.markdown("### 💡 **Consejos para Comentarios Efectivos**")
    
    st.markdown("""
    **✅ Comentarios Constructivos:**
    - Sé específico y claro
    - Incluye datos o ejemplos
    - Propón soluciones, no solo problemas
    - Mantén un tono profesional
    
    **📋 Temas Sugeridos:**
    - Mejoras en procesos
    - Propuestas de eficiencia  
    - Observaciones de calidad
    - Sugerencias de equipo
    - Análisis de KPIs
    - Oportunidades de crecimiento
    """)
    
    st.markdown("---")
    
    if st.session_state.comments:
        st.markdown("### 📊 **Resumen Rápido**")
        
        # Obtener fechas únicas de comités
        fechas_comites = list(set(comment.get('fecha_comite', '') for comment in st.session_state.comments if comment.get('fecha_comite')))
        
        st.metric("Fechas de Comités", len(fechas_comites))
        st.metric("Total Comentarios", len(st.session_state.comments))
        st.metric("Participantes", len(set(comment['nombre'] for comment in st.session_state.comments)))
        
        # Mostrar fechas de comités registradas
        if fechas_comites:
            st.markdown("**📅 Comités con Comentarios:**")
            for fecha in sorted(fechas_comites, reverse=True):
                count = len([c for c in st.session_state.comments if c.get('fecha_comite') == fecha])
                st.markdown(f"• **{fecha}**: {count} comentarios")
    
    # Información de agenda
    if st.session_state.agenda_items:
        st.markdown("---")
        st.markdown("### 📋 **Estado de la Agenda**")
        st.metric("Puntos de Agenda", len(st.session_state.agenda_items))
        
        # Mostrar fechas de agenda
        fechas_agenda = list(set(item.get('fecha_agenda', '') for item in st.session_state.agenda_items if item.get('fecha_agenda')))
        if fechas_agenda:
            st.markdown("**📅 Fechas con Agenda:**")
            for fecha in sorted(fechas_agenda, reverse=True):
                count = len([a for a in st.session_state.agenda_items if a.get('fecha_agenda') == fecha])
                st.markdown(f"• **{fecha}**: {count} puntos")
    
    # Información de notas
    if st.session_state.meeting_notes:
        st.markdown("---")
        st.markdown("### 📝 **Notas de Reunión**")
        st.metric("Total Notas", len(st.session_state.meeting_notes))
        
        # Mostrar fechas de notas
        fechas_notas = list(set(note.get('fecha_comite', '') for note in st.session_state.meeting_notes if note.get('fecha_comite')))
        if fechas_notas:
            st.markdown("**📅 Fechas con Notas:**")
            for fecha in sorted(fechas_notas, reverse=True):
                count = len([n for n in st.session_state.meeting_notes if n.get('fecha_comite') == fecha])
                st.markdown(f"• **{fecha}**: {count} notas")
    
    st.markdown("---")
    
    # Botón de reset
    if st.button("🔄 **Reiniciar Sistema Completo**", help="Elimina todos los datos: comentarios, agenda y notas"):
        if st.session_state.comments or st.session_state.agenda_items or st.session_state.meeting_notes:
            st.session_state.comments = []
            st.session_state.agenda_items = []
            st.session_state.meeting_notes = []
            st.session_state.editing_comment = None
            st.session_state.authenticated = False
            st.success("✅ Sistema completamente reiniciado")
            time.sleep(1)
            st.rerun()
        else:
            st.info("ℹ️ No hay datos para reiniciar")

# ================================================================
# FOOTER
# ================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: var(--text-secondary); padding: 2rem 0;'>
    <p><strong>💬 Sistema de Comentarios Comité Operativo v1.0</strong></p>
    <p>Facilita la comunicación y mejora la productividad de nuestras reuniones</p>
    <p>© 2025 Garlic & Beyond - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
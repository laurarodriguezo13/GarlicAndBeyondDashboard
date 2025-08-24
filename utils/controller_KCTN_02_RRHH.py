"""
controller_KCTN_02_RRHH.py - Controlador Garlic & Beyond COMPLETO
================================================================
Controlador completo para datos de RRHH de Garlic & Beyond.
Maneja KPIs exactos, gráficos específicos y análisis según especificaciones.

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 3.0 - Completo y Funcional
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import warnings

warnings.filterwarnings('ignore')

class GarlicRRHHController:
    """Controlador completo para RRHH de Garlic & Beyond."""
    
    def __init__(self):
        """Inicializa el controlador con configuración específica."""
        self.data = None
        self.monthly_data = {}
        self.employees = []
        self.kpis = {}
        self.alerts = []
        self.is_initialized = False
        self.last_update = None
        self.processed_months = []
        
        # Configuración de colores específica para Garlic & Beyond
        self.colors = {
            'primary': '#2E7D32',      # Verde oscuro principal
            'secondary': '#4CAF50',     # Verde medio
            'success': '#66BB6A',       # Verde claro
            'warning': '#FF9800',       # Naranja
            'danger': '#F44336',        # Rojo
            'info': '#2196F3',          # Azul
            'fijo': '#1976D2',          # Azul para personal fijo
            'produccion': '#388E3C',    # Verde para producción
            'baja': '#FF5722',          # Rojo para bajas
            'activo': '#4CAF50',        # Verde para activos
            'gray': '#757575'
        }
        
        # Meses válidos en orden
        self.meses_orden = [
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        
        # Nombres de meses para display
        self.meses_nombres = {
            'enero': 'Enero', 'febrero': 'Febrero', 'marzo': 'Marzo',
            'abril': 'Abril', 'mayo': 'Mayo', 'junio': 'Junio',
            'julio': 'Julio', 'agosto': 'Agosto', 'septiembre': 'Septiembre',
            'octubre': 'Octubre', 'noviembre': 'Noviembre', 'diciembre': 'Diciembre'
        }
    
    def initialize_with_data(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Inicializa el controlador con datos parseados del Excel.
        
        Args:
            parsed_data: Datos procesados por el parser
            
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            if parsed_data.get('status') != 'success':
                st.error(f"Error en datos parseados: {parsed_data.get('message')}")
                return False
            
            # Extraer datos del parser
            self.data = parsed_data['data']
            self.monthly_data = self.data.get('monthly_data', {})
            self.employees = self.data.get('employees', [])
            self.kpis = self.data.get('kpis', {})
            self.alerts = self.data.get('alerts', [])
            
            # Obtener meses procesados
            metadata = parsed_data.get('metadata', {})
            self.processed_months = metadata.get('processed_months', [])
            
            self.is_initialized = True
            self.last_update = datetime.now()
            
            return True
            
        except Exception as e:
            st.error(f"Error inicializando controlador: {e}")
            return False
    
    def get_available_months(self) -> List[str]:
        """Obtiene lista de meses disponibles para mostrar."""
        return [self.meses_nombres[mes] for mes in self.meses_orden]
    
    def get_months_with_data(self) -> List[str]:
        """Obtiene solo los meses que tienen datos reales."""
        months_with_data = []
        for mes in self.meses_orden:
            if (mes in self.monthly_data and 
                self.monthly_data[mes]['stats']['total_empleados'] > 0):
                months_with_data.append(self.meses_nombres[mes])
        return months_with_data
    
    def _normalize_month_name(self, month_display_name: str) -> Optional[str]:
        """Convierte nombre de mes para display a clave interna."""
        for key, display in self.meses_nombres.items():
            if display.lower() == month_display_name.lower():
                return key
        return None
    
    def get_monthly_kpis(self, selected_month: str) -> Dict[str, Any]:
        """
        Obtiene KPIs específicos para un mes según especificaciones de Garlic & Beyond.
        
        Args:
            selected_month: Mes seleccionado (nombre display)
            
        Returns:
            Dict con KPIs del mes
        """
        month_key = self._normalize_month_name(selected_month)
        
        if not month_key or month_key not in self.monthly_data:
            # Devolver estructura vacía para meses futuros
            return {
                'month_name': selected_month,
                'has_data': False,
                # KPI Card 1: Coste Personal Fijo
                'fijo_coste_mes': 0,
                'fijo_coste_dia': 0,
                'fijo_coste_hora': 0,
                'fijo_hpax': 0,
                # KPI Card 2: Coste Personal Producción
                'produccion_coste_mes': 0,
                'produccion_coste_dia': 0,
                'produccion_coste_hora': 0,
                'produccion_hpax': 0,
                # KPI Card 3: Bajas
                'bajas_coste_total': 0,
                'bajas_numero': 0,
                'bajas_porcentaje': 0,
                # KPI Card 4: Gasto Personal Total
                'total_coste_mes': 0,
                'total_coste_dia': 0,
                'total_coste_hora': 0,
                # Datos adicionales
                'total_empleados': 0,
                'empleados_baja_detalle': []
            }
        
        month_data = self.monthly_data[month_key]
        totales = month_data['totales']
        stats = month_data['stats']
        
        return {
            'month_name': selected_month,
            'has_data': True,
            # KPI Card 1: Coste Personal Fijo
            'fijo_coste_mes': totales['fijo_mes'],
            'fijo_coste_dia': totales['fijo_dia'],
            'fijo_coste_hora': totales['fijo_hora'],
            'fijo_hpax': totales['fijo_hpax'],
            # KPI Card 2: Coste Personal Producción
            'produccion_coste_mes': totales['produccion_mes'],
            'produccion_coste_dia': totales['produccion_dia'],
            'produccion_coste_hora': totales['produccion_hora'],
            'produccion_hpax': totales['produccion_hpax'],
            # KPI Card 3: Bajas
            'bajas_coste_total': stats['coste_bajas'],
            'bajas_numero': stats['empleados_baja'],
            'bajas_porcentaje': stats['porcentaje_bajas'],
            # KPI Card 4: Gasto Personal Total
            'total_coste_mes': totales['coste_total_mes'],
            'total_coste_dia': totales['coste_total_dia'],
            'total_coste_hora': totales['coste_total_hora'],
            # Datos adicionales
            'total_empleados': stats['total_empleados'],
            'empleados_baja_detalle': stats['empleados_baja_detalle']
        }
    
    def create_costes_por_seccion_chart(self, selected_month: str) -> go.Figure:
        """
        Crea gráfico de barras de costes por sección para un mes.
        Eje X: Sección, Eje Y: Coste
        """
        month_key = self._normalize_month_name(selected_month)
        
        if not month_key or month_key not in self.monthly_data:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No hay datos disponibles para {selected_month}",
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title=f"Costes por Sección - {selected_month}")
            return fig
        
        month_data = self.monthly_data[month_key]
        costes_seccion = month_data['stats']['costes_seccion']
        
        if not costes_seccion:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No hay datos de secciones para {selected_month}",
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title=f"Costes por Sección - {selected_month}")
            return fig
        
        # Ordenar secciones por coste descendente
        secciones_ordenadas = sorted(costes_seccion.items(), key=lambda x: x[1], reverse=True)
        secciones = [item[0] for item in secciones_ordenadas]
        costes = [item[1] for item in secciones_ordenadas]
        
        fig = go.Figure(data=[
            go.Bar(
                x=secciones,
                y=costes,
                marker_color=self.colors['primary'],
                text=[f"€{coste:,.0f}" for coste in costes],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Coste: €%{y:,.0f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=f"💰 Costes por Sección - {selected_month}",
            xaxis_title="Sección",
            yaxis_title="Coste (€)",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        return fig
    
    def create_pie_chart_secciones(self, selected_month: str) -> go.Figure:
        """
        Crea pie chart de empleados por sección.
        Cada sección es un color, valor = count de empleados.
        """
        month_key = self._normalize_month_name(selected_month)
        
        if not month_key or month_key not in self.monthly_data:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No hay datos disponibles para {selected_month}",
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title=f"Distribución de Empleados - {selected_month}")
            return fig
        
        month_data = self.monthly_data[month_key]
        count_seccion = month_data['stats']['count_seccion']
        
        if not count_seccion:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No hay datos de empleados para {selected_month}",
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title=f"Distribución de Empleados - {selected_month}")
            return fig
        
        secciones = list(count_seccion.keys())
        counts = list(count_seccion.values())
        
        fig = go.Figure(data=[
            go.Pie(
                labels=secciones,
                values=counts,
                hovertemplate='<b>%{label}</b><br>' +
                            'Empleados: %{value}<br>' +
                            'Porcentaje: %{percent}<extra></extra>',
                textinfo='label+value',
                marker=dict(
                    colors=px.colors.qualitative.Set3
                )
            )
        ])
        
        fig.update_layout(
            title=f"👥 Distribución de Empleados por Sección - {selected_month}",
            showlegend=True,
            height=400
        )
        
        return fig
    
    def get_analisis_bajas_data(self, selected_month: str) -> Dict[str, Any]:
        """
        Obtiene datos detallados de análisis de bajas para un mes.
        """
        month_key = self._normalize_month_name(selected_month)
        
        if not month_key or month_key not in self.monthly_data:
            return {
                'cantidad_bajas': 0,
                'empleados_baja': [],
                'coste_total_bajas': 0,
                'porcentaje_coste_bajas': 0
            }
        
        month_data = self.monthly_data[month_key]
        stats = month_data['stats']
        totales = month_data['totales']
        
        # Calcular porcentaje de coste de bajas sobre total
        porcentaje_coste = 0
        if totales['coste_total_mes'] > 0:
            porcentaje_coste = (stats['coste_bajas'] / totales['coste_total_mes']) * 100
        
        # Preparar lista detallada de empleados de baja
        empleados_baja_detalle = []
        for emp in stats['empleados_baja_detalle']:
            empleados_baja_detalle.append({
                'nombre': emp['nombre'],
                'seccion': emp['seccion'],
                'coste': emp['coste_total'],
                'porcentaje_coste': (emp['coste_total'] / totales['coste_total_mes'] * 100) if totales['coste_total_mes'] > 0 else 0
            })
        
        return {
            'cantidad_bajas': stats['empleados_baja'],
            'empleados_baja': empleados_baja_detalle,
            'coste_total_bajas': stats['coste_bajas'],
            'porcentaje_coste_bajas': porcentaje_coste
        }
    
    def create_multi_month_kpi_table(self, selected_months: List[str]) -> pd.DataFrame:
        """
        Crea tabla de KPIs para comparación multi-mes.
        Columnas = meses, Filas = componentes de KPI cards.
        """
        # Filtrar solo meses que existen
        valid_months = [mes for mes in selected_months if mes in self.get_available_months()]
        
        if not valid_months:
            return pd.DataFrame()
        
        # Definir las métricas (filas de la tabla)
        metricas = [
            ('💼 Coste Personal Fijo (Mes)', 'fijo_coste_mes', '€'),
            ('💼 Coste Personal Fijo (Día)', 'fijo_coste_dia', '€'),
            ('💼 Coste Personal Fijo (Hora)', 'fijo_coste_hora', '€'),
            ('💼 H/PAX Personal Fijo', 'fijo_hpax', ''),
            ('🏭 Coste Personal Producción (Mes)', 'produccion_coste_mes', '€'),
            ('🏭 Coste Personal Producción (Día)', 'produccion_coste_dia', '€'),
            ('🏭 Coste Personal Producción (Hora)', 'produccion_coste_hora', '€'),
            ('🏭 H/PAX Personal Producción', 'produccion_hpax', ''),
            ('🏥 Coste Total Bajas', 'bajas_coste_total', '€'),
            ('🏥 Número de Bajas', 'bajas_numero', ''),
            ('🏥 Porcentaje de Bajas', 'bajas_porcentaje', '%'),
            ('💰 Coste Total Personal (Mes)', 'total_coste_mes', '€'),
            ('💰 Coste Total Personal (Día)', 'total_coste_dia', '€'),
            ('💰 Coste Total Personal (Hora)', 'total_coste_hora', '€'),
        ]
        
        # Construir datos de la tabla
        table_data = []
        
        for metrica_nombre, metrica_key, unidad in metricas:
            row = {'Métrica': metrica_nombre}
            
            for month in valid_months:
                kpis = self.get_monthly_kpis(month)
                value = kpis.get(metrica_key, 0)
                
                if unidad == '€':
                    row[month] = f"€{value:,.0f}" if value > 0 else "€0"
                elif unidad == '%':
                    row[month] = f"{value:.1f}%" if value > 0 else "0%"
                else:
                    row[month] = f"{value:,.1f}" if value > 0 else "0"
            
            table_data.append(row)
        
        return pd.DataFrame(table_data)
    
    def create_evolucion_costes_chart(self, selected_months: List[str]) -> go.Figure:
        """
        Crea gráfico de líneas para evolución de costes (mes, día, hora).
        """
        valid_months = [mes for mes in selected_months if mes in self.get_available_months()]
        
        if not valid_months:
            fig = go.Figure()
            fig.add_annotation(text="No hay meses seleccionados", showarrow=False)
            return fig
        
        # Obtener datos para cada mes
        months = []
        coste_mes = []
        coste_dia = []
        coste_hora = []
        
        for month in valid_months:
            kpis = self.get_monthly_kpis(month)
            if kpis.get('has_data', False):
                months.append(month)
                coste_mes.append(kpis['total_coste_mes'])
                coste_dia.append(kpis['total_coste_dia'])
                coste_hora.append(kpis['total_coste_hora'])
        
        if not months:
            fig = go.Figure()
            fig.add_annotation(text="No hay datos disponibles para los meses seleccionados", showarrow=False)
            return fig
        
        # Crear subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Coste Total por Mes', 'Coste Total por Día', 'Coste Total por Hora'),
            vertical_spacing=0.1
        )
        
        # Línea de coste por mes
        fig.add_trace(
            go.Scatter(
                x=months, y=coste_mes,
                mode='lines+markers+text',
                name='Coste Mes',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8),
                text=[f"€{c:,.0f}" for c in coste_mes],
                textposition='top center'
            ),
            row=1, col=1
        )
        
        # Línea de coste por día
        fig.add_trace(
            go.Scatter(
                x=months, y=coste_dia,
                mode='lines+markers+text',
                name='Coste Día',
                line=dict(color=self.colors['info'], width=3),
                marker=dict(size=8),
                text=[f"€{c:,.0f}" for c in coste_dia],
                textposition='top center'
            ),
            row=2, col=1
        )
        
        # Línea de coste por hora
        fig.add_trace(
            go.Scatter(
                x=months, y=coste_hora,
                mode='lines+markers+text',
                name='Coste Hora',
                line=dict(color=self.colors['warning'], width=3),
                marker=dict(size=8),
                text=[f"€{c:,.0f}" for c in coste_hora],
                textposition='top center'
            ),
            row=3, col=1
        )
        
        fig.update_layout(
            title="📈 Evolución de Costes Totales",
            showlegend=False,
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_costes_seccion_comparativo_chart(self, selected_months: List[str]) -> go.Figure:
        """
        Crea gráfico de barras agrupadas para comparar costes por sección entre meses.
        """
        valid_months = [mes for mes in selected_months if mes in self.get_available_months()]
        months_with_data = []
        
        # Filtrar solo meses con datos
        for month in valid_months:
            kpis = self.get_monthly_kpis(month)
            if kpis.get('has_data', False):
                months_with_data.append(month)
        
        if not months_with_data:
            fig = go.Figure()
            fig.add_annotation(text="No hay datos disponibles para comparación", showarrow=False)
            return fig
        
        # Obtener todas las secciones únicas
        all_secciones = set()
        month_section_data = {}
        
        for month in months_with_data:
            month_key = self._normalize_month_name(month)
            if month_key and month_key in self.monthly_data:
                costes_seccion = self.monthly_data[month_key]['stats']['costes_seccion']
                month_section_data[month] = costes_seccion
                all_secciones.update(costes_seccion.keys())
        
        secciones = sorted(list(all_secciones))
        
        if not secciones:
            fig = go.Figure()
            fig.add_annotation(text="No hay datos de secciones para comparar", showarrow=False)
            return fig
        
        fig = go.Figure()
        
        # Crear una barra para cada mes
        colors = px.colors.qualitative.Set3
        for i, month in enumerate(months_with_data):
            costes = []
            for seccion in secciones:
                coste = month_section_data[month].get(seccion, 0)
                costes.append(coste)
            
            fig.add_trace(
                go.Bar(
                    x=secciones,
                    y=costes,
                    name=month,
                    marker_color=colors[i % len(colors)],
                    hovertemplate=f'<b>{month}</b><br>' +
                                'Sección: %{x}<br>' +
                                'Coste: €%{y:,.0f}<extra></extra>'
                )
            )
        
        fig.update_layout(
            title="📊 Comparación de Costes por Sección entre Meses",
            xaxis_title="Sección",
            yaxis_title="Coste (€)",
            barmode='group',
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_bajas_tendencia_chart(self, selected_months: List[str]) -> go.Figure:
        """
        Crea línea de tendencia de costes de bajas a través del tiempo.
        """
        valid_months = [mes for mes in selected_months if mes in self.get_available_months()]
        
        months = []
        costes_bajas = []
        numero_bajas = []
        
        for month in valid_months:
            kpis = self.get_monthly_kpis(month)
            if kpis.get('has_data', False):
                months.append(month)
                costes_bajas.append(kpis['bajas_coste_total'])
                numero_bajas.append(kpis['bajas_numero'])
        
        if not months:
            fig = go.Figure()
            fig.add_annotation(text="No hay datos de bajas disponibles", showarrow=False)
            return fig
        
        # Crear subplot con eje Y secundario
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Línea de coste de bajas
        fig.add_trace(
            go.Scatter(
                x=months, y=costes_bajas,
                mode='lines+markers+text',
                name='Coste Bajas',
                line=dict(color=self.colors['danger'], width=3),
                marker=dict(size=10),
                text=[f"€{c:,.0f}" for c in costes_bajas],
                textposition='top center'
            ),
            secondary_y=False
        )
        
        # Línea de número de bajas
        fig.add_trace(
            go.Scatter(
                x=months, y=numero_bajas,
                mode='lines+markers+text',
                name='Número Bajas',
                line=dict(color=self.colors['warning'], width=3, dash='dash'),
                marker=dict(size=10, symbol='square'),
                text=[f"{n}" for n in numero_bajas],
                textposition='bottom center'
            ),
            secondary_y=True
        )
        
        # Configurar ejes
        fig.update_yaxes(title_text="Coste de Bajas (€)", secondary_y=False)
        fig.update_yaxes(title_text="Número de Empleados de Baja", secondary_y=True)
        fig.update_xaxes(title_text="Mes")
        
        fig.update_layout(
            title="🏥 Tendencia de Bajas a través del Tiempo",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del controlador."""
        if not self.is_initialized:
            return {
                'initialized': False,
                'message': 'Controlador no inicializado'
            }
        
        # Contar meses con datos reales
        months_with_data = len(self.get_months_with_data())
        total_months = len(self.processed_months)
        
        return {
            'initialized': True,
            'last_update': self.last_update.strftime('%d/%m/%Y %H:%M'),
            'total_months_processed': total_months,
            'months_with_data': months_with_data,
            'months_empty': total_months - months_with_data,
            'latest_month_with_data': self.get_months_with_data()[-1] if self.get_months_with_data() else None,
            'total_employees_latest': self.kpis.get('total_employees', 0),
            'total_cost_latest': self.kpis.get('total_cost', 0),
            'alerts_count': len(self.alerts)
        }
    
    def get_alerts(self) -> List[Dict[str, str]]:
        """Obtiene alertas del sistema."""
        return self.alerts if self.is_initialized else []

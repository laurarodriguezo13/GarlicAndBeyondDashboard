"""
Controller CFI Compras - Sistema de Control de Compras CFI
==========================================================
Controlador principal para gestión de datos de compras CFI.
Maneja KPIs, filtros, gráficas y análisis comparativos.

Funcionalidades:
- Análisis por mes individual con KPIs detallados
- Comparación multi-mes con tendencias
- Análisis de proveedores y precios
- Estados de entrega y pagos
- Gráficas interactivas

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import warnings

warnings.filterwarnings('ignore')

class CFIComprasController:
    """Controlador principal para el módulo de compras CFI."""
    
    def __init__(self):
        """Inicializa el controlador."""
        self.data = None
        self.compras_df = pd.DataFrame()
        self.proveedores_info = {}
        self.monthly_data = {}
        self.metrics = {}
        self.initialized = False
        
        # Mapeo de meses
        self.month_mapping = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        # Orden de meses para mostrar
        self.months_order = [
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
    
    def initialize_with_data(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Inicializa el controlador con datos parseados.
        
        Args:
            parsed_data: Datos parseados del parser CFI Compras
            
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            if parsed_data.get('status') != 'success':
                return False
            
            data = parsed_data.get('data', {})
            
            self.data = data
            self.compras_df = data.get('compras_data', pd.DataFrame())
            self.proveedores_info = data.get('proveedores_info', {})
            self.monthly_data = data.get('monthly_data', {})
            self.metrics = data.get('metrics', {})
            
            if self.compras_df.empty:
                return False
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Error inicializando controlador CFI Compras: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Verifica si el controlador está inicializado."""
        return self.initialized and not self.compras_df.empty
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del controlador."""
        if not self.initialized:
            return {
                'initialized': False,
                'months_with_data': 0,
                'months_empty': 12,
                'total_compras_latest': 0,
                'total_proveedores': 0,
                'alerts_count': 0,
                'last_update': 'Sin datos'
            }
        
        months_with_data = len(self.monthly_data)
        latest_month_data = self._get_latest_month_data()
        
        return {
            'initialized': True,
            'months_with_data': months_with_data,
            'months_empty': 12 - months_with_data,
            'total_compras_latest': latest_month_data.get('total_compras', 0),
            'total_proveedores': self.compras_df['proveedor'].nunique() if not self.compras_df.empty else 0,
            'alerts_count': 0,  # Sin alertas por ahora
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
    
    def get_available_months(self) -> List[str]:
        """Obtiene lista de todos los meses disponibles."""
        return self.months_order
    
    def get_months_with_data(self) -> List[str]:
        """Obtiene lista de meses que tienen datos."""
        if not self.initialized:
            return []
        
        months_with_data = list(self.monthly_data.keys())
        # Ordenar según months_order
        ordered_months = []
        for month in self.months_order:
            if month in months_with_data:
                ordered_months.append(month)
        
        return ordered_months
    
    def get_available_proveedores(self) -> List[str]:
        """Obtiene lista de proveedores disponibles."""
        if not self.initialized:
            return []
        
        return sorted(self.compras_df['proveedor'].unique().tolist())
    
    def get_monthly_kpis(self, month: str) -> Dict[str, Any]:
        """
        Obtiene KPIs para un mes específico según especificaciones.
        
        Args:
            month: Mes a analizar
            
        Returns:
            dict: KPIs del mes
        """
        if not self.initialized or month not in self.monthly_data:
            return {
                'has_data': False,
                'total_compras': 0,
                'proveedores_activos': 0,
                'precio_promedio_kg': 0,
                'tiempo_conexion_promedio': 0,
                'proveedor_estrella': 'N/A',
                'total_peso_kg': 0,
                'pedidos_entregados': 0,
                'pedidos_embarcados': 0,
                'pedidos_preparacion': 0
            }
        
        # Filtrar datos del mes
        month_df = self.compras_df[self.compras_df['mes'] == month].copy()
        
        if month_df.empty:
            return {
                'has_data': False,
                'total_compras': 0,
                'proveedores_activos': 0,
                'precio_promedio_kg': 0,
                'tiempo_conexion_promedio': 0,
                'proveedor_estrella': 'N/A',
                'total_peso_kg': 0,
                'pedidos_entregados': 0,
                'pedidos_embarcados': 0,
                'pedidos_preparacion': 0
            }
        
        # Calcular KPIs según especificaciones
        total_compras = month_df['total_factura'].sum()
        proveedores_activos = month_df['proveedor'].nunique()
        precio_promedio_kg = month_df['precio_kg'].mean()
        tiempo_conexion_promedio = month_df['tiempo_conexion'].mean()
        total_peso_kg = month_df['peso_kg'].sum()
        
        # Proveedor estrella (mayor valor en total factura)
        proveedor_estrella = 'N/A'
        if not month_df.empty:
            proveedor_ventas = month_df.groupby('proveedor')['total_factura'].sum()
            if not proveedor_ventas.empty:
                proveedor_estrella = proveedor_ventas.idxmax()
        
        # Estados de pedidos
        pedidos_entregados = len(month_df[month_df['estado_entrega'] == 'ENTREGADO'])
        pedidos_embarcados = len(month_df[month_df['estado_entrega'] == 'EMBARCADO'])
        pedidos_preparacion = len(month_df[month_df['estado_entrega'] == 'EN PREPARACION'])
        
        return {
            'has_data': True,
            'total_compras': total_compras,
            'proveedores_activos': proveedores_activos,
            'precio_promedio_kg': precio_promedio_kg,
            'tiempo_conexion_promedio': tiempo_conexion_promedio,
            'proveedor_estrella': proveedor_estrella,
            'total_peso_kg': total_peso_kg,
            'pedidos_entregados': pedidos_entregados,
            'pedidos_embarcados': pedidos_embarcados,
            'pedidos_preparacion': pedidos_preparacion
        }
    
    def create_kg_por_proveedor_chart(self, month: str):
        """Crea gráfica de barras: Proveedores vs KG vendidos."""
        month_df = self.compras_df[self.compras_df['mes'] == month].copy()
        
        if month_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos para mostrar", 
                             xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        # Agrupar por proveedor
        kg_por_proveedor = month_df.groupby('proveedor')['peso_kg'].sum().sort_values(ascending=False)
        
        fig = px.bar(
            x=kg_por_proveedor.index,
            y=kg_por_proveedor.values,
            title=f"Kilogramos por Proveedor - {month.title()}",
            labels={'x': 'Proveedor', 'y': 'Kilogramos (kg)'},
            color=kg_por_proveedor.values,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_factura_por_proveedor_chart(self, month: str):
        """Crea gráfica de barras: Proveedores vs Total Factura."""
        month_df = self.compras_df[self.compras_df['mes'] == month].copy()
        
        if month_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos para mostrar", 
                             xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        # Agrupar por proveedor
        factura_por_proveedor = month_df.groupby('proveedor')['total_factura'].sum().sort_values(ascending=False)
        
        fig = px.bar(
            x=factura_por_proveedor.index,
            y=factura_por_proveedor.values,
            title=f"Total Factura por Proveedor - {month.title()}",
            labels={'x': 'Proveedor', 'y': 'Total Factura (€)'},
            color=factura_por_proveedor.values,
            color_continuous_scale='Greens'
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_tickangle=-45
        )
        
        # Formatear eje Y como moneda
        fig.update_yaxes(tickformat="€,.0f")
        
        return fig
    
    def create_precio_promedio_proveedor_chart(self, month: str):
        """Crea gráfica de barras: Proveedores vs Precio Promedio por KG."""
        month_df = self.compras_df[self.compras_df['mes'] == month].copy()
        
        if month_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos para mostrar", 
                             xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        # Calcular precio promedio por proveedor
        precio_por_proveedor = month_df.groupby('proveedor')['precio_kg'].mean().sort_values(ascending=False)
        
        fig = px.bar(
            x=precio_por_proveedor.index,
            y=precio_por_proveedor.values,
            title=f"Precio Promedio por KG por Proveedor - {month.title()}",
            labels={'x': 'Proveedor', 'y': 'Precio por KG (€)'},
            color=precio_por_proveedor.values,
            color_continuous_scale='Oranges'
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_tickangle=-45
        )
        
        # Formatear eje Y como moneda
        fig.update_yaxes(tickformat="€.2f")
        
        return fig
    
    def calculate_month_changes(self, selected_months: List[str]) -> Optional[Dict[str, Any]]:
        """Calcula cambios porcentuales entre meses."""
        if len(selected_months) < 2:
            return None
        
        # Ordenar meses cronológicamente
        ordered_months = []
        for month in self.months_order:
            if month in selected_months:
                ordered_months.append(month)
        
        if len(ordered_months) < 2:
            return None
        
        first_month = ordered_months[0]
        last_month = ordered_months[-1]
        
        first_kpis = self.get_monthly_kpis(first_month)
        last_kpis = self.get_monthly_kpis(last_month)
        
        # Calcular cambios porcentuales
        compras_change = 0
        peso_change = 0
        
        if first_kpis['total_compras'] > 0:
            compras_change = ((last_kpis['total_compras'] - first_kpis['total_compras']) / first_kpis['total_compras']) * 100
        
        if first_kpis['total_peso_kg'] > 0:
            peso_change = ((last_kpis['total_peso_kg'] - first_kpis['total_peso_kg']) / first_kpis['total_peso_kg']) * 100
        
        return {
            'first_month': first_month,
            'last_month': last_month,
            'compras_change': compras_change,
            'peso_change': peso_change,
            'first_month_data': first_kpis,
            'last_month_data': last_kpis
        }
    
    def create_multi_month_kpi_table(self, selected_months: List[str]) -> pd.DataFrame:
        """Crea tabla comparativa de KPIs multi-mes."""
        if not selected_months:
            return pd.DataFrame()
        
        # Ordenar meses
        ordered_months = []
        for month in self.months_order:
            if month in selected_months:
                ordered_months.append(month)
        
        table_data = []
        
        for month in ordered_months:
            kpis = self.get_monthly_kpis(month)
            
            table_data.append({
                'Mes': month.title(),
                'Total Compras (€)': f"€{kpis['total_compras']:,.0f}",
                'Peso Total (kg)': f"{kpis['total_peso_kg']:,.0f} kg",
                'Precio Promedio/kg (€)': f"€{kpis['precio_promedio_kg']:.2f}",
                'Proveedores Activos': kpis['proveedores_activos'],
                'Tiempo Conexión Promedio': f"{kpis['tiempo_conexion_promedio']:.1f} días",
                'Proveedor Estrella': kpis['proveedor_estrella'],
                'Pedidos Entregados': kpis['pedidos_entregados'],
                'Pedidos Embarcados': kpis['pedidos_embarcados'],
                'Pedidos en Preparación': kpis['pedidos_preparacion']
            })
        
        return pd.DataFrame(table_data)
    
    def create_evolucion_compras_chart(self, selected_months: List[str]):
        """Crea gráfica de evolución de compras totales."""
        if not selected_months:
            return go.Figure()
        
        # Ordenar meses
        ordered_months = []
        for month in self.months_order:
            if month in selected_months:
                ordered_months.append(month)
        
        compras_data = []
        peso_data = []
        
        for month in ordered_months:
            kpis = self.get_monthly_kpis(month)
            compras_data.append(kpis['total_compras'])
            peso_data.append(kpis['total_peso_kg'])
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Evolución Total Factura', 'Evolución Peso Total'),
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Gráfica de compras
        fig.add_trace(
            go.Scatter(
                x=ordered_months,
                y=compras_data,
                mode='lines+markers',
                name='Total Factura (€)',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Gráfica de peso
        fig.add_trace(
            go.Scatter(
                x=ordered_months,
                y=peso_data,
                mode='lines+markers',
                name='Peso Total (kg)',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Tendencias de Compras CFI",
            height=600,
            showlegend=True
        )
        
        # Formatear ejes
        fig.update_yaxes(tickformat="€,.0f", row=1, col=1)
        fig.update_yaxes(tickformat=",.0f", row=2, col=1)
        
        return fig
    
    def get_alerts(self) -> List[Dict[str, str]]:
        """Obtiene alertas del sistema."""
        alerts = []
        
        if not self.initialized:
            alerts.append({
                'type': 'warning',
                'title': 'Sistema no inicializado',
                'message': 'Carga los datos de compras CFI para comenzar el análisis.'
            })
            return alerts
        
        # Alertas basadas en datos
        months_with_data = len(self.monthly_data)
        if months_with_data < 3:
            alerts.append({
                'type': 'info',
                'title': 'Datos limitados',
                'message': f'Solo hay datos para {months_with_data} mes(es). Para análisis comparativos se recomiendan al menos 3 meses.'
            })
        
        return alerts
    
    def _get_latest_month_data(self) -> Dict[str, Any]:
        """Obtiene datos del mes más reciente."""
        if not self.monthly_data:
            return {}
        
        # Buscar el último mes con datos
        for month in reversed(self.months_order):
            if month in self.monthly_data:
                return self.monthly_data[month]
        
        return {}
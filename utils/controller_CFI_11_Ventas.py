"""
Controller CFI_11_Ventas - VERSIÓN CORREGIDA PARA 3 HOJAS
==========================================================
Controlador especializado para gestionar las 3 hojas del Excel CFI:
1. Ventas 2025 - Análisis completo con KPIs y comparaciones
2. Pedidos 2025 - Análisis de pedidos pendientes por mes
3. Contratos Abiertos 2025 - Gestión de contratos abiertos

Funcionalidades principales:
- KPIs individuales y comparativos para Ventas
- Análisis de Pedidos por mes individual
- Gestión de Contratos Abiertos
- Gráficos interactivos con Plotly

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 2.0 - Tres Hojas Separadas
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import calendar

class CFIVentasController:
    """Controlador principal para datos de ventas CFI con 3 hojas separadas."""
    
    def __init__(self):
        """Inicializa el controlador."""
        self.data = None
        self.ventas_df = pd.DataFrame()
        self.pedidos_df = pd.DataFrame()
        self.contratos_df = pd.DataFrame()
        self.monthly_summaries = {}
        self.general_stats = {}
        self.is_initialized = False
        
        # Configuración de colores para CFI
        self.colors = {
            'primary': '#1976D2',      # Azul principal CFI
            'secondary': '#42A5F5',    # Azul secundario
            'success': '#4CAF50',      # Verde éxito
            'warning': '#FF9800',      # Naranja advertencia
            'error': '#F44336',        # Rojo error
            'info': '#00BCD4',         # Cian información
            'chart_palette': ['#1976D2', '#42A5F5', '#2196F3', '#64B5F6', '#90CAF9', 
                             '#BBDEFB', '#FF9800', '#FFB74D', '#FFCC80', '#4CAF50']
        }
    
    def initialize_with_data(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Inicializa el controlador con datos parseados de las 3 hojas.
        
        Args:
            parsed_data: Datos parseados del Excel CFI
            
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            if not parsed_data or parsed_data.get('status') != 'success':
                return False
            
            data = parsed_data.get('data', {})
            
            # Cargar DataFrames de las 3 hojas
            self.ventas_df = data.get('ventas', pd.DataFrame())
            self.pedidos_df = data.get('pedidos', pd.DataFrame())
            self.contratos_df = data.get('contratos_abiertos', pd.DataFrame())
            self.monthly_summaries = data.get('monthly_summaries', {})
            self.general_stats = data.get('general_stats', {})
            
            # Validar datos críticos
            if self.ventas_df.empty:
                return False
            
            # Verificar columnas esenciales en ventas
            required_columns = ['fecha_carga', 'cliente', 'producto', 'total', 'kg', 'precio', 'mes_nombre']
            for col in required_columns:
                if col not in self.ventas_df.columns:
                    return False
            
            self.data = parsed_data
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.is_initialized = False
            return False
    
    def get_available_months(self) -> List[str]:
        """Obtiene lista de meses disponibles en ventas."""
        if not self.is_initialized:
            return []
        
        try:
            # Obtener meses únicos de ventas y ordenarlos
            meses_nombres = self.ventas_df['mes_nombre'].dropna().unique()
            
            # Ordenar por orden cronológico
            month_order = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            
            meses_ordenados = sorted(meses_nombres, key=lambda x: month_order.get(x.lower(), 13))
            return meses_ordenados
            
        except Exception as e:
            return []
    
    def get_months_with_data(self) -> List[str]:
        """Obtiene meses que tienen datos de ventas."""
        return self.get_available_months()
    
    def get_available_months_pedidos(self) -> List[str]:
        """Obtiene lista de meses disponibles en pedidos."""
        if not self.is_initialized or self.pedidos_df.empty:
            return []
        
        try:
            return self.pedidos_df['mes_nombre'].dropna().unique().tolist()
        except Exception as e:
            return []
    
    # ================================================================
    # MÉTODOS PARA VENTAS 2025
    # ================================================================
    
    def get_monthly_kpis(self, mes_nombre: str) -> Dict[str, Any]:
        """
        Obtiene KPIs para un mes específico de ventas.
        """
        default_kpis = {
            'has_data': False,
            'ventas_totales': 0,
            'clientes_activos': 0,
            'cliente_estrella': 'N/A',
            'cliente_estrella_ventas': 0,
            'precio_promedio': 0,
            'producto_estrella': 'N/A',
            'producto_estrella_ventas': 0,
            'kg_totales': 0,
            'pallets_totales': 0,
            'registros_totales': 0
        }
        
        if not self.is_initialized:
            return default_kpis
        
        try:
            # Obtener datos del mes desde monthly_summaries
            if mes_nombre in self.monthly_summaries:
                month_data = self.monthly_summaries[mes_nombre]
                return {
                    'has_data': True,
                    'ventas_totales': month_data.get('ventas_totales', 0),
                    'clientes_activos': month_data.get('clientes_activos', 0),
                    'cliente_estrella': month_data.get('cliente_estrella', 'N/A'),
                    'cliente_estrella_ventas': month_data.get('cliente_estrella_ventas', 0),
                    'precio_promedio': month_data.get('precio_promedio', 0),
                    'producto_estrella': month_data.get('producto_estrella', 'N/A'),
                    'producto_estrella_ventas': month_data.get('producto_estrella_ventas', 0),
                    'kg_totales': month_data.get('kg_totales', 0),
                    'pallets_totales': month_data.get('pallets_totales', 0),
                    'registros_totales': month_data.get('registros_totales', 0)
                }
            
            # Si no está en summaries, calcular directamente
            mes_data = self.ventas_df[self.ventas_df['mes_nombre'] == mes_nombre]
            
            if mes_data.empty:
                return default_kpis
            
            # Calcular KPIs
            kpis = default_kpis.copy()
            kpis['has_data'] = True
            kpis['ventas_totales'] = float(mes_data['total'].sum())
            kpis['kg_totales'] = float(mes_data['kg'].sum())
            kpis['pallets_totales'] = float(mes_data['pallets'].sum())
            kpis['clientes_activos'] = int(mes_data['cliente'].nunique())
            kpis['precio_promedio'] = float(mes_data['precio'].mean()) if len(mes_data) > 0 else 0
            kpis['registros_totales'] = len(mes_data)
            
            # Cliente estrella
            if not mes_data.empty:
                cliente_ventas = mes_data.groupby('cliente')['total'].sum()
                if not cliente_ventas.empty:
                    kpis['cliente_estrella'] = cliente_ventas.idxmax()
                    kpis['cliente_estrella_ventas'] = float(cliente_ventas.max())
            
            # Producto estrella
            if not mes_data.empty:
                producto_ventas = mes_data.groupby('producto')['total'].sum()
                if not producto_ventas.empty:
                    kpis['producto_estrella'] = producto_ventas.idxmax()
                    kpis['producto_estrella_ventas'] = float(producto_ventas.max())
            
            return kpis
            
        except Exception as e:
            return default_kpis
    
    def create_ventas_por_producto_chart(self, mes_nombre: str) -> go.Figure:
        """Crea gráfico de barras de ventas por producto."""
        try:
            mes_data = self.ventas_df[self.ventas_df['mes_nombre'] == mes_nombre]
            
            if mes_data.empty:
                fig = go.Figure()
                fig.update_layout(title=f"Ventas por Producto - {mes_nombre.title()} (Sin datos)")
                return fig
            
            # Agrupar por producto
            producto_ventas = mes_data.groupby('producto')['total'].sum().reset_index()
            producto_ventas = producto_ventas.sort_values('total', ascending=False)
            
            fig = px.bar(
                producto_ventas,
                x='producto',
                y='total',
                title=f'Ventas por Producto - {mes_nombre.title()}',
                labels={'total': 'Ventas Totales (€)', 'producto': 'Producto'},
                color='total',
                color_continuous_scale=['#E3F2FD', '#1976D2']
            )
            
            fig.update_layout(
                template='plotly_white',
                showlegend=False,
                height=400,
                xaxis_tickangle=-45
            )
            
            # Formato de valores en euros
            fig.update_traces(
                texttemplate='€%{y:,.0f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Ventas: €%{y:,.0f}<extra></extra>'
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error generando gráfico: {str(e)}")
            return fig
    
    def create_ventas_por_cliente_chart(self, mes_nombre: str) -> go.Figure:
        """Crea gráfico de barras de ventas por cliente."""
        try:
            mes_data = self.ventas_df[self.ventas_df['mes_nombre'] == mes_nombre]
            
            if mes_data.empty:
                fig = go.Figure()
                fig.update_layout(title=f"Ventas por Cliente - {mes_nombre.title()} (Sin datos)")
                return fig
            
            # Agrupar por cliente
            cliente_ventas = mes_data.groupby('cliente')['total'].sum().reset_index()
            cliente_ventas = cliente_ventas.sort_values('total', ascending=False)
            
            # Limitar a top 10 clientes para visualización
            if len(cliente_ventas) > 10:
                cliente_ventas = cliente_ventas.head(10)
            
            fig = px.bar(
                cliente_ventas,
                x='cliente',
                y='total',
                title=f'Ventas por Cliente - {mes_nombre.title()}',
                labels={'total': 'Ventas Totales (€)', 'cliente': 'Cliente'},
                color='total',
                color_continuous_scale=['#E8F5E8', '#4CAF50']
            )
            
            fig.update_layout(
                template='plotly_white',
                showlegend=False,
                height=400,
                xaxis_tickangle=-45
            )
            
            fig.update_traces(
                texttemplate='€%{y:,.0f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Ventas: €%{y:,.0f}<extra></extra>'
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error generando gráfico: {str(e)}")
            return fig
    
    def create_kg_por_producto_chart(self, mes_nombre: str) -> go.Figure:
        """Crea gráfico de barras de kilogramos por producto."""
        try:
            mes_data = self.ventas_df[self.ventas_df['mes_nombre'] == mes_nombre]
            
            if mes_data.empty:
                fig = go.Figure()
                fig.update_layout(title=f"Kilogramos por Producto - {mes_nombre.title()} (Sin datos)")
                return fig
            
            # Agrupar por producto
            producto_kg = mes_data.groupby('producto')['kg'].sum().reset_index()
            producto_kg = producto_kg.sort_values('kg', ascending=False)
            
            fig = px.bar(
                producto_kg,
                x='producto',
                y='kg',
                title=f'Kilogramos por Producto - {mes_nombre.title()}',
                labels={'kg': 'Kilogramos Totales', 'producto': 'Producto'},
                color='kg',
                color_continuous_scale=['#FFE0B2', '#FF9800']
            )
            
            fig.update_layout(
                template='plotly_white',
                showlegend=False,
                height=400,
                xaxis_tickangle=-45
            )
            
            fig.update_traces(
                texttemplate='%{y:,.0f} kg',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Kilogramos: %{y:,.0f} kg<extra></extra>'
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error generando gráfico: {str(e)}")
            return fig
    
    def create_kg_por_cliente_chart(self, mes_nombre: str) -> go.Figure:
        """Crea gráfico de barras de kilogramos por cliente."""
        try:
            mes_data = self.ventas_df[self.ventas_df['mes_nombre'] == mes_nombre]
            
            if mes_data.empty:
                fig = go.Figure()
                fig.update_layout(title=f"Kilogramos por Cliente - {mes_nombre.title()} (Sin datos)")
                return fig
            
            # Agrupar por cliente
            cliente_kg = mes_data.groupby('cliente')['kg'].sum().reset_index()
            cliente_kg = cliente_kg.sort_values('kg', ascending=False)
            
            # Limitar a top 10 clientes
            if len(cliente_kg) > 10:
                cliente_kg = cliente_kg.head(10)
            
            fig = px.bar(
                cliente_kg,
                x='cliente',
                y='kg',
                title=f'Kilogramos por Cliente - {mes_nombre.title()}',
                labels={'kg': 'Kilogramos Totales', 'cliente': 'Cliente'},
                color='kg',
                color_continuous_scale=['#BBDEFB', '#2196F3']
            )
            
            fig.update_layout(
                template='plotly_white',
                showlegend=False,
                height=400,
                xaxis_tickangle=-45
            )
            
            fig.update_traces(
                texttemplate='%{y:,.0f} kg',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Kilogramos: %{y:,.0f} kg<extra></extra>'
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error generando gráfico: {str(e)}")
            return fig
    
    def get_promedio_por_cliente_data(self, mes_nombre: str) -> pd.DataFrame:
        """Obtiene datos de promedio por cliente para el mes."""
        try:
            mes_data = self.ventas_df[self.ventas_df['mes_nombre'] == mes_nombre]
            
            if mes_data.empty:
                return pd.DataFrame()
            
            # Calcular promedios por cliente
            cliente_stats = mes_data.groupby('cliente').agg({
                'kg': ['mean', 'sum'],
                'precio': 'mean',
                'total': ['mean', 'sum'],
                'pallets': ['mean', 'sum']
            }).round(2)
            
            # Aplanar columnas
            cliente_stats.columns = ['kg_promedio', 'kg_total', 'precio_promedio', 'total_promedio', 'total_sum', 'pallets_promedio', 'pallets_total']
            cliente_stats = cliente_stats.reset_index()
            
            # Ordenar por total de ventas
            cliente_stats = cliente_stats.sort_values('total_sum', ascending=False)
            
            return cliente_stats
            
        except Exception as e:
            return pd.DataFrame()
    
    # ================================================================
    # MÉTODOS PARA PEDIDOS 2025
    # ================================================================
    
    def get_pedidos_kpis(self, mes_nombre: str) -> Dict[str, Any]:
        """Obtiene KPIs para pedidos de un mes específico."""
        default_kpis = {
            'has_data': False,
            'clientes_unicos': 0,
            'productos_unicos': 0,
            'precio_promedio_pedido': 0,
            'total_pedidos': 0,
            'kg_totales_pedidos': 0,
            'pallets_totales_pedidos': 0
        }
        
        if not self.is_initialized or self.pedidos_df.empty:
            return default_kpis
        
        try:
            mes_data = self.pedidos_df[self.pedidos_df['mes_nombre'].str.lower() == mes_nombre.lower()]
            
            if mes_data.empty:
                return default_kpis
            
            return {
                'has_data': True,
                'clientes_unicos': int(mes_data['cliente'].nunique()),
                'productos_unicos': int(mes_data['producto'].nunique()),
                'precio_promedio_pedido': float(mes_data['precio'].mean()) if len(mes_data) > 0 else 0,
                'total_pedidos': float(mes_data['total'].sum()),
                'kg_totales_pedidos': float(mes_data['kg'].sum()),
                'pallets_totales_pedidos': float(mes_data['pallets'].sum()),
                'registros_pedidos': len(mes_data)
            }
            
        except Exception as e:
            return default_kpis
    
    def get_clientes_pedidos_list(self, mes_nombre: str) -> List[str]:
        """Obtiene lista de clientes únicos en pedidos del mes."""
        try:
            if self.pedidos_df.empty:
                return []
            
            mes_data = self.pedidos_df[self.pedidos_df['mes_nombre'].str.lower() == mes_nombre.lower()]
            return mes_data['cliente'].dropna().unique().tolist()
            
        except Exception as e:
            return []
    
    def get_productos_pedidos_list(self, mes_nombre: str) -> List[str]:
        """Obtiene lista de productos únicos en pedidos del mes."""
        try:
            if self.pedidos_df.empty:
                return []
            
            mes_data = self.pedidos_df[self.pedidos_df['mes_nombre'].str.lower() == mes_nombre.lower()]
            return mes_data['producto'].dropna().unique().tolist()
            
        except Exception as e:
            return []
    
    def create_pedidos_por_cliente_chart(self, mes_nombre: str) -> go.Figure:
        """Crea gráfico de barras de pedidos por cliente con detalles."""
        try:
            mes_data = self.pedidos_df[self.pedidos_df['mes_nombre'].str.lower() == mes_nombre.lower()]
            
            if mes_data.empty:
                fig = go.Figure()
                fig.update_layout(title=f"Pedidos por Cliente - {mes_nombre.title()} (Sin datos)")
                return fig
            
            # Agrupar por cliente con detalles adicionales
            cliente_stats = mes_data.groupby('cliente').agg({
                'total': 'sum',
                'kg': 'sum',
                'pallets': 'sum',
                'precio': 'mean'
            }).reset_index()
            
            cliente_stats = cliente_stats.sort_values('total', ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=cliente_stats['cliente'],
                    y=cliente_stats['total'],
                    text=[f'€{val:,.0f}' for val in cliente_stats['total']],
                    textposition='outside',
                    hovertemplate=(
                        '<b>%{x}</b><br>' +
                        'Total: €%{y:,.0f}<br>' +
                        'Kg: %{customdata[0]:,.0f}<br>' +
                        'Pallets: %{customdata[1]:,.0f}<br>' +
                        'Precio Promedio: €%{customdata[2]:.2f}/kg' +
                        '<extra></extra>'
                    ),
                    customdata=np.column_stack((cliente_stats['kg'], cliente_stats['pallets'], cliente_stats['precio'])),
                    marker_color=self.colors['primary']
                )
            ])
            
            fig.update_layout(
                title=f'Pedidos por Cliente - {mes_nombre.title()}',
                xaxis_title='Cliente',
                yaxis_title='Total Pedidos (€)',
                template='plotly_white',
                height=400,
                xaxis_tickangle=-45
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error generando gráfico: {str(e)}")
            return fig
    
    # ================================================================
    # MÉTODOS PARA CONTRATOS ABIERTOS
    # ================================================================
    
    def get_contratos_abiertos_data(self) -> pd.DataFrame:
        """Obtiene datos de contratos abiertos formateados."""
        try:
            if self.contratos_df.empty:
                return pd.DataFrame()
            
            # Formatear datos para mostrar
            contratos_display = self.contratos_df.copy()
            
            # Formatear columnas numéricas
            if 'total' in contratos_display.columns:
                contratos_display['total'] = contratos_display['total'].apply(
                    lambda x: f"€{x:,.0f}" if pd.notnull(x) and x != 0 else "€0"
                )
            
            if 'precio' in contratos_display.columns:
                contratos_display['precio'] = contratos_display['precio'].apply(
                    lambda x: f"€{x:.2f}" if pd.notnull(x) and x != 0 else "€0.00"
                )
            
            if 'kg' in contratos_display.columns:
                contratos_display['kg'] = contratos_display['kg'].apply(
                    lambda x: f"{x:,.0f} kg" if pd.notnull(x) and x != 0 else "0 kg"
                )
            
            # Renombrar columnas para visualización
            column_names = {
                'fecha': 'Fecha',
                'estado': 'Estado',
                'producto': 'Producto',
                'medidas': 'Medidas',
                'incoterm': 'Incoterm',
                'kg': 'Kilogramos',
                'precio': 'Precio (€/kg)',
                'total': 'Total (€)'
            }
            
            contratos_display = contratos_display.rename(columns=column_names)
            
            return contratos_display
            
        except Exception as e:
            return pd.DataFrame()
    
    def get_contratos_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de contratos abiertos."""
        try:
            if self.contratos_df.empty:
                return {}
            
            return {
                'total_contratos': len(self.contratos_df),
                'valor_total_contratos': float(self.contratos_df['total'].sum()),
                'kg_totales_contratos': float(self.contratos_df['kg'].sum()),
                'precio_promedio_contratos': float(self.contratos_df['precio'].mean()),
                'productos_en_contratos': int(self.contratos_df['producto'].nunique()),
                'estados_unicos': self.contratos_df['estado'].nunique() if 'estado' in self.contratos_df.columns else 0
            }
            
        except Exception as e:
            return {}
    
    # ================================================================
    # MÉTODOS COMPARATIVOS MULTI-MES (SOLO VENTAS)
    # ================================================================
    
    def create_multi_month_kpi_table(self, selected_months: List[str]) -> pd.DataFrame:
        """Crea tabla comparativa de KPIs multi-mes para ventas."""
        try:
            if not selected_months:
                return pd.DataFrame()
            
            kpi_data = []
            
            for mes in selected_months:
                kpis = self.get_monthly_kpis(mes)
                
                if kpis['has_data']:
                    kpi_data.append({
                        'Mes': mes.title(),
                        'Ventas Totales (€)': f"€{kpis['ventas_totales']:,.0f}",
                        'Kg Totales': f"{kpis['kg_totales']:,.0f}",
                        'Clientes Activos': kpis['clientes_activos'],
                        'Cliente Estrella': kpis['cliente_estrella'],
                        'Producto Estrella': kpis['producto_estrella'],
                        'Precio Promedio (€/kg)': f"€{kpis['precio_promedio']:.2f}",
                        'Pallets Totales': f"{kpis['pallets_totales']:,.0f}",
                        'Registros': kpis['registros_totales']
                    })
            
            return pd.DataFrame(kpi_data)
            
        except Exception as e:
            return pd.DataFrame()
    
    def create_evolucion_ventas_chart(self, selected_months: List[str]) -> go.Figure:
        """Crea gráfico de evolución de ventas totales."""
        try:
            if not selected_months:
                fig = go.Figure()
                fig.update_layout(title="Evolución de Ventas (Sin datos)")
                return fig
            
            # Obtener datos de ventas por mes
            months_data = []
            for mes in selected_months:
                kpis = self.get_monthly_kpis(mes)
                if kpis['has_data']:
                    months_data.append({
                        'mes': mes.title(),
                        'ventas': kpis['ventas_totales']
                    })
            
            if not months_data:
                fig = go.Figure()
                fig.update_layout(title="Evolución de Ventas (Sin datos)")
                return fig
            
            df = pd.DataFrame(months_data)
            
            fig = px.line(
                df,
                x='mes',
                y='ventas',
                title='Evolución de Ventas Totales',
                labels={'ventas': 'Ventas Totales (€)', 'mes': 'Mes'},
                markers=True
            )
            
            fig.update_traces(
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8, color=self.colors['secondary'])
            )
            
            fig.update_layout(
                template='plotly_white',
                height=400,
                hovermode='x'
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error: {str(e)}")
            return fig
    
    def create_evolucion_kg_chart(self, selected_months: List[str]) -> go.Figure:
        """Crea gráfico de evolución de kilogramos vendidos."""
        try:
            if not selected_months:
                fig = go.Figure()
                fig.update_layout(title="Evolución de Kg Vendidos (Sin datos)")
                return fig
            
            # Obtener datos de kg por mes
            months_data = []
            for mes in selected_months:
                kpis = self.get_monthly_kpis(mes)
                if kpis['has_data']:
                    months_data.append({
                        'mes': mes.title(),
                        'kg': kpis['kg_totales']
                    })
            
            if not months_data:
                fig = go.Figure()
                fig.update_layout(title="Evolución de Kg Vendidos (Sin datos)")
                return fig
            
            df = pd.DataFrame(months_data)
            
            fig = px.line(
                df,
                x='mes',
                y='kg',
                title='Evolución de Kilogramos Vendidos',
                labels={'kg': 'Kilogramos Totales', 'mes': 'Mes'},
                markers=True
            )
            
            fig.update_traces(
                line=dict(color=self.colors['warning'], width=3),
                marker=dict(size=8, color='#FFB74D')
            )
            
            fig.update_layout(
                template='plotly_white',
                height=400,
                hovermode='x'
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error: {str(e)}")
            return fig
    
    def create_evolucion_precio_chart(self, selected_months: List[str]) -> go.Figure:
        """Crea gráfico de evolución de precio promedio."""
        try:
            if not selected_months:
                fig = go.Figure()
                fig.update_layout(title="Evolución de Precio Promedio (Sin datos)")
                return fig
            
            # Obtener datos de precio por mes
            months_data = []
            for mes in selected_months:
                kpis = self.get_monthly_kpis(mes)
                if kpis['has_data']:
                    months_data.append({
                        'mes': mes.title(),
                        'precio': kpis['precio_promedio']
                    })
            
            if not months_data:
                fig = go.Figure()
                fig.update_layout(title="Evolución de Precio Promedio (Sin datos)")
                return fig
            
            df = pd.DataFrame(months_data)
            
            fig = px.line(
                df,
                x='mes',
                y='precio',
                title='Evolución de Precio Promedio',
                labels={'precio': 'Precio Promedio (€/kg)', 'mes': 'Mes'},
                markers=True
            )
            
            fig.update_traces(
                line=dict(color=self.colors['info'], width=3),
                marker=dict(size=8, color='#42A5F5')
            )
            
            fig.update_layout(
                template='plotly_white',
                height=400,
                hovermode='x'
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.update_layout(title=f"Error: {str(e)}")
            return fig
    
    def get_comparative_kpis(self, selected_months: List[str]) -> Dict[str, Any]:
        """Obtiene KPIs comparativos para múltiples meses."""
        try:
            if not selected_months:
                return {}
            
            # Calcular cambios porcentuales
            ventas_por_mes = []
            kg_por_mes = []
            
            for mes in selected_months:
                kpis = self.get_monthly_kpis(mes)
                if kpis['has_data']:
                    ventas_por_mes.append(kpis['ventas_totales'])
                    kg_por_mes.append(kpis['kg_totales'])
            
            # Cliente estrella general
            all_months_data = []
            for mes in selected_months:
                mes_data = self.ventas_df[self.ventas_df['mes_nombre'] == mes]
                all_months_data.append(mes_data)
            
            combined_data = pd.concat(all_months_data, ignore_index=True) if all_months_data else pd.DataFrame()
            
            cliente_estrella = ''
            if not combined_data.empty:
                cliente_ventas = combined_data.groupby('cliente')['total'].sum()
                if not cliente_ventas.empty:
                    cliente_estrella = cliente_ventas.idxmax()
            
            return {
                'cambio_ventas_pct': self._calculate_percentage_changes(ventas_por_mes),
                'cambio_kg_pct': self._calculate_percentage_changes(kg_por_mes),
                'cliente_estrella_periodo': cliente_estrella,
                'ventas_totales_periodo': sum(ventas_por_mes),
                'kg_totales_periodo': sum(kg_por_mes),
                'precio_promedio_periodo': sum(ventas_por_mes) / sum(kg_por_mes) if sum(kg_por_mes) > 0 else 0
            }
            
        except Exception as e:
            return {}
    
    def _calculate_percentage_changes(self, values: List[float]) -> str:
        """Calcula cambios porcentuales entre valores."""
        try:
            if len(values) < 2:
                return "N/A"
            
            changes = []
            for i in range(1, len(values)):
                if values[i-1] != 0:
                    change = ((values[i] - values[i-1]) / values[i-1]) * 100
                    changes.append(f"{change:+.1f}%")
                else:
                    changes.append("N/A")
            
            return " | ".join(changes)
            
        except Exception as e:
            return "Error"
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del controlador."""
        if not self.is_initialized:
            return {
                'initialized': False,
                'message': 'Controlador no inicializado'
            }
        
        return {
            'initialized': True,
            'total_records': len(self.ventas_df),
            'total_pedidos': len(self.pedidos_df),
            'total_contratos': len(self.contratos_df),
            'months_with_data': len(self.get_months_with_data()),
            'total_sales': float(self.ventas_df['total'].sum()) if not self.ventas_df.empty else 0,
            'total_kg': float(self.ventas_df['kg'].sum()) if not self.ventas_df.empty else 0,
            'unique_clients': int(self.ventas_df['cliente'].nunique()) if not self.ventas_df.empty else 0,
            'unique_products': int(self.ventas_df['producto'].nunique()) if not self.ventas_df.empty else 0,
            'contratos_abiertos': len(self.contratos_df),
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
"""
controller_CFI_12_Inventario.py - Controlador para Dashboard CFI Inventario
==========================================================================
Controlador principal para el dashboard de inventario CFI.
Maneja toda la lógica de negocio, cálculos de KPIs y generación de gráficos.

Funcionalidades principales:
- Gestión de datos de inventario por mes
- Cálculo de KPIs individuales y comparativos
- Generación de gráficos interactivos
- Análisis de productos ajo vs no ajo
- Comparaciones entre meses con cambios porcentuales
- Alertas configurables

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

class CFIInventarioController:
    """Controlador principal para el dashboard de inventario CFI."""
    
    def __init__(self):
        """Inicializar controlador."""
        self.data = {}
        self.metadata = {}
        self.is_initialized = False
        self.last_update = None
        
        # Configuración de colores para gráficos
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
        ]
        
        # Meses en orden
        self.meses_orden = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
    
    def initialize_with_data(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Inicializa el controlador con datos parseados.
        
        Args:
            parsed_data: Datos parseados del parser
            
        Returns:
            bool: True si inicialización exitosa
        """
        try:
            if parsed_data.get('status') != 'success':
                return False
            
            self.data = parsed_data.get('data', {})
            self.metadata = parsed_data.get('metadata', {})
            self.is_initialized = True
            self.last_update = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error inicializando controlador CFI: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del controlador."""
        if not self.is_initialized:
            return {
                'initialized': False,
                'months_with_data': 0,
                'months_empty': 12,
                'total_products': 0,
                'total_tipos': 0,
                'last_update': 'No inicializado'
            }
        
        months_with_data = len(self.data)
        months_empty = 12 - months_with_data
        total_products = sum(len(df) for df in self.data.values())
        
        return {
            'initialized': True,
            'months_with_data': months_with_data,
            'months_empty': months_empty,
            'total_products': total_products,
            'total_tipos': self.metadata.get('tipos_productos_count', 0),
            'tipos_disponibles': self.metadata.get('tipos_productos', []),
            'last_update': self.last_update.strftime('%d/%m/%Y %H:%M') if self.last_update else 'Desconocido'
        }
    
    def get_available_months(self) -> List[str]:
        """Obtiene lista de todos los meses (con y sin datos)."""
        return self.meses_orden
    
    def get_months_with_data(self) -> List[str]:
        """Obtiene solo meses que tienen datos."""
        return [mes for mes in self.meses_orden if mes in self.data and not self.data[mes].empty]
    
    def get_available_tipos(self, mes: Optional[str] = None) -> List[str]:
        """Obtiene tipos de productos disponibles."""
        if not self.is_initialized:
            return []
        
        if mes and mes in self.data:
            return sorted(self.data[mes]['tipo'].unique().tolist())
        else:
            return self.metadata.get('tipos_productos', [])
    
    def get_month_dataframe(self, mes: str) -> Optional[pd.DataFrame]:
        """Obtiene DataFrame de un mes específico."""
        if not self.is_initialized or mes not in self.data:
            return None
        return self.data[mes].copy()
    
    def calculate_monthly_kpis(self, mes: str) -> Dict[str, Any]:
        """
        Calcula KPIs para un mes específico.
        
        Args:
            mes: Nombre del mes
            
        Returns:
            Dict con KPIs del mes
        """
        if not self.is_initialized or mes not in self.data:
            return {
                'has_data': False,
                'total_productos': 0,
                'total_kilos': 0,
                'total_valor': 0,
                'precio_promedio_general': 0,
                'tipos_agrupados': pd.DataFrame(),
                'precio_promedio_ajo': pd.DataFrame(),
                'producto_estrella': 'N/A',
                'valor_estrella': 0,
                'no_ajo_kilos': 0,
                'analisis_tipos': {}
            }
        
        df = self.data[mes]
        
        # KPIs básicos
        kpis = {
            'has_data': True,
            'mes': mes,
            'total_productos': len(df),
            'total_kilos': df['kilos'].sum(),
            'total_valor': df['valor'].sum(),
            'precio_promedio_general': df['precio'].mean() if len(df) > 0 else 0
        }
        
        # Agrupación por tipo (para KPI cards)
        tipos_agrupados = df.groupby('tipo').agg({
            'kilos': 'sum',
            'precio': 'sum',  # Suma de precios como especificaste
            'valor': 'sum'
        }).round(2)
        
        kpis['tipos_agrupados'] = tipos_agrupados
        
        # Precio promedio SOLO de productos de ajo (excluyendo "no ajo")
        df_ajo = df[df['tipo'] != 'no ajo']
        if not df_ajo.empty:
            precio_promedio_ajo = df_ajo.groupby('tipo')['precio'].mean().round(3)
            kpis['precio_promedio_ajo'] = precio_promedio_ajo
        else:
            kpis['precio_promedio_ajo'] = pd.Series(dtype=float)
        
        # Producto estrella (tipo con mayor valor total)
        if not tipos_agrupados.empty:
            tipo_estrella = tipos_agrupados['valor'].idxmax()
            valor_estrella = tipos_agrupados.loc[tipo_estrella, 'valor']
            kpis['producto_estrella'] = tipo_estrella
            kpis['valor_estrella'] = valor_estrella
        else:
            kpis['producto_estrella'] = 'N/A'
            kpis['valor_estrella'] = 0
        
        # Análisis de productos "no ajo"
        productos_no_ajo = df[df['tipo'] == 'no ajo']
        kpis['no_ajo_kilos'] = productos_no_ajo['kilos'].sum()
        
        # Análisis detallado por tipo
        analisis_tipos = {}
        for tipo in df['tipo'].unique():
            productos_tipo = df[df['tipo'] == tipo]
            analisis_tipos[tipo] = {
                'cantidad_productos': len(productos_tipo),
                'nombres_unicos': productos_tipo['nombre'].nunique(),
                'kilos_total': productos_tipo['kilos'].sum(),
                'valor_total': productos_tipo['valor'].sum(),
                'precio_promedio': productos_tipo['precio'].mean()
            }
        
        kpis['analisis_tipos'] = analisis_tipos
        
        return kpis
    
    def create_kilos_por_tipo_chart(self, mes: str) -> go.Figure:
        """Crea gráfico de barras de kilos totales por tipo."""
        kpis = self.calculate_monthly_kpis(mes)
        
        if not kpis['has_data'] or kpis['tipos_agrupados'].empty:
            fig = go.Figure()
            fig.update_layout(
                title=f'Kilos Totales por Tipo - {mes}',
                annotations=[dict(text="No hay datos disponibles", 
                                xref="paper", yref="paper", x=0.5, y=0.5,
                                showarrow=False, font=dict(size=16))]
            )
            return fig
        
        tipos_agrupados = kpis['tipos_agrupados'].sort_values('kilos', ascending=False)
        
        fig = px.bar(
            x=tipos_agrupados.index,
            y=tipos_agrupados['kilos'],
            title=f'Kilos Totales por Tipo de Producto - {mes}',
            labels={'x': 'Tipo de Producto', 'y': 'Kilos'},
            color=tipos_agrupados['kilos'],
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            template='plotly_white',
            height=400,
            showlegend=False,
            xaxis_tickangle=-45,
            xaxis_title="Tipo de Producto",
            yaxis_title="Kilos"
        )
        
        return fig
    
    def create_valor_distribucion_chart(self, mes: str) -> go.Figure:
        """Crea gráfico pie de distribución de valor por tipo."""
        kpis = self.calculate_monthly_kpis(mes)
        
        if not kpis['has_data'] or kpis['tipos_agrupados'].empty:
            fig = go.Figure()
            fig.update_layout(
                title=f'Distribución de Valor - {mes}',
                annotations=[dict(text="No hay datos disponibles", 
                                xref="paper", yref="paper", x=0.5, y=0.5,
                                showarrow=False, font=dict(size=16))]
            )
            return fig
        
        tipos_agrupados = kpis['tipos_agrupados']
        
        fig = px.pie(
            values=tipos_agrupados['valor'],
            names=tipos_agrupados.index,
            title=f'Distribución de Valor por Tipo - {mes}',
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_precio_ajo_chart(self, mes: str) -> go.Figure:
        """Crea gráfico de precio promedio solo para productos de ajo."""
        kpis = self.calculate_monthly_kpis(mes)
        
        if not kpis['has_data'] or kpis['precio_promedio_ajo'].empty:
            fig = go.Figure()
            fig.update_layout(
                title=f'Precio Promedio por Tipo de Ajo - {mes}',
                annotations=[dict(text="No hay productos de ajo disponibles", 
                                xref="paper", yref="paper", x=0.5, y=0.5,
                                showarrow=False, font=dict(size=16))]
            )
            return fig
        
        precio_ajo = kpis['precio_promedio_ajo'].sort_values(ascending=False)
        
        fig = px.bar(
            x=precio_ajo.index,
            y=precio_ajo.values,
            title=f'Precio Promedio por Tipo de Ajo - {mes}',
            labels={'x': 'Tipo de Ajo', 'y': 'Precio Promedio (€/kg)'},
            color=precio_ajo.values,
            color_continuous_scale='Greens'
        )
        
        fig.update_layout(
            template='plotly_white',
            height=400,
            showlegend=False,
            xaxis_tickangle=-45,
            xaxis_title="Tipo de Ajo",
            yaxis_title="Precio Promedio (€/kg)"
        )
        
        return fig
    
    def get_productos_por_tipo(self, mes: str, tipo: str) -> Dict[str, Any]:
        """Obtiene productos de un tipo específico en un mes."""
        if not self.is_initialized or mes not in self.data:
            return {
                'productos': pd.DataFrame(),
                'cantidad_articulos': 0,
                'nombres_unicos': 0
            }
        
        df = self.data[mes]
        productos_tipo = df[df['tipo'] == tipo]
        
        return {
            'productos': productos_tipo[['codigo', 'nombre', 'kilos', 'precio', 'valor']].copy(),
            'cantidad_articulos': len(productos_tipo),
            'nombres_unicos': productos_tipo['nombre'].nunique()
        }
    
    def calculate_percentage_changes(self, meses: List[str]) -> pd.DataFrame:
        """
        Calcula cambios porcentuales entre meses por tipo de producto.
        
        Args:
            meses: Lista de meses a comparar
            
        Returns:
            DataFrame con cambios porcentuales
        """
        if len(meses) < 2:
            return pd.DataFrame()
        
        # Obtener datos agregados por tipo para cada mes
        datos_comparacion = {}
        
        for mes in meses:
            if mes in self.data:
                kpis_mes = self.calculate_monthly_kpis(mes)
                if kpis_mes['has_data']:
                    datos_comparacion[mes] = kpis_mes['tipos_agrupados']
        
        if len(datos_comparacion) < 2:
            return pd.DataFrame()
        
        # Crear DataFrame de comparación
        meses_disponibles = list(datos_comparacion.keys())
        todos_tipos = set()
        
        for datos in datos_comparacion.values():
            todos_tipos.update(datos.index)
        
        # Calcular cambios porcentuales
        cambios_data = []
        
        for tipo in todos_tipos:
            fila = {'Tipo': tipo}
            
            # Obtener valores para cada mes
            valores_kilos = {}
            valores_precio = {}
            valores_valor = {}
            
            for mes in meses_disponibles:
                if tipo in datos_comparacion[mes].index:
                    valores_kilos[mes] = datos_comparacion[mes].loc[tipo, 'kilos']
                    valores_precio[mes] = datos_comparacion[mes].loc[tipo, 'precio']
                    valores_valor[mes] = datos_comparacion[mes].loc[tipo, 'valor']
                else:
                    valores_kilos[mes] = 0
                    valores_precio[mes] = 0
                    valores_valor[mes] = 0
            
            # Calcular cambios porcentuales entre meses consecutivos
            for i in range(len(meses_disponibles) - 1):
                mes_inicial = meses_disponibles[i]
                mes_final = meses_disponibles[i + 1]
                
                # Cambio en kilos
                cambio_kilos = self._calcular_cambio_porcentual(
                    valores_kilos[mes_inicial], valores_kilos[mes_final]
                )
                fila[f'Δ Kilos {mes_inicial[:3]}-{mes_final[:3]}'] = f"{cambio_kilos:+.1f}%"
                
                # Cambio en precio
                cambio_precio = self._calcular_cambio_porcentual(
                    valores_precio[mes_inicial], valores_precio[mes_final]
                )
                fila[f'Δ Precio {mes_inicial[:3]}-{mes_final[:3]}'] = f"{cambio_precio:+.1f}%"
                
                # Cambio en valor
                cambio_valor = self._calcular_cambio_porcentual(
                    valores_valor[mes_inicial], valores_valor[mes_final]
                )
                fila[f'Δ Valor {mes_inicial[:3]}-{mes_final[:3]}'] = f"{cambio_valor:+.1f}%"
            
            cambios_data.append(fila)
        
        return pd.DataFrame(cambios_data)
    
    def _calcular_cambio_porcentual(self, valor_inicial: float, valor_final: float) -> float:
        """Calcula cambio porcentual entre dos valores."""
        if valor_inicial == 0:
            return 100.0 if valor_final > 0 else 0.0
        return ((valor_final - valor_inicial) / valor_inicial) * 100
    
    def create_evolution_chart(self, meses: List[str], tipos_seleccionados: List[str]) -> go.Figure:
        """
        Crea gráfico de evolución del valor por tipo a través de los meses.
        
        Args:
            meses: Lista de meses
            tipos_seleccionados: Tipos de productos a mostrar
            
        Returns:
            Gráfico de líneas de evolución
        """
        fig = go.Figure()
        
        # Obtener datos de cada mes
        datos_evolucion = {}
        meses_con_datos = []
        
        for mes in meses:
            if mes in self.data:
                kpis_mes = self.calculate_monthly_kpis(mes)
                if kpis_mes['has_data']:
                    datos_evolucion[mes] = kpis_mes['tipos_agrupados']
                    meses_con_datos.append(mes)
        
        if not meses_con_datos:
            fig.update_layout(
                title='Evolución del Valor por Tipo',
                annotations=[dict(text="No hay datos disponibles", 
                                xref="paper", yref="paper", x=0.5, y=0.5,
                                showarrow=False, font=dict(size=16))]
            )
            return fig
        
        # Crear línea para cada tipo seleccionado
        for i, tipo in enumerate(tipos_seleccionados):
            valores = []
            for mes in meses_con_datos:
                if tipo in datos_evolucion[mes].index:
                    valores.append(datos_evolucion[mes].loc[tipo, 'valor'])
                else:
                    valores.append(0)
            
            fig.add_trace(go.Scatter(
                x=meses_con_datos,
                y=valores,
                mode='lines+markers',
                name=tipo,
                line=dict(color=self.color_palette[i % len(self.color_palette)], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title='Evolución del Valor por Tipo de Producto',
            xaxis_title='Mes',
            yaxis_title='Valor Total (€)',
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_comparison_price_charts(self, meses: List[str]) -> go.Figure:
        """
        Crea gráficos de barras de precio medio por tipo para comparación mensual.
        
        Args:
            meses: Lista de meses a comparar
            
        Returns:
            Gráfico de barras agrupadas
        """
        # Obtener todos los tipos de productos
        todos_tipos = set()
        datos_precio = {}
        
        meses_con_datos = []
        for mes in meses:
            if mes in self.data:
                kpis_mes = self.calculate_monthly_kpis(mes)
                if kpis_mes['has_data']:
                    # Calcular precio medio por tipo (valor total / kilos total)
                    tipos_agrupados = kpis_mes['tipos_agrupados']
                    precio_medio = (tipos_agrupados['valor'] / tipos_agrupados['kilos']).fillna(0)
                    
                    datos_precio[mes] = precio_medio
                    todos_tipos.update(precio_medio.index)
                    meses_con_datos.append(mes)
        
        if not meses_con_datos:
            fig = go.Figure()
            fig.update_layout(
                title='Precio Medio por Tipo - Comparación Mensual',
                annotations=[dict(text="No hay datos disponibles", 
                                xref="paper", yref="paper", x=0.5, y=0.5,
                                showarrow=False, font=dict(size=16))]
            )
            return fig
        
        # Crear subplots para cada tipo de producto
        tipos_ordenados = sorted(list(todos_tipos))
        n_tipos = len(tipos_ordenados)
        
        # Calcular dimensiones de subplots
        cols = min(3, n_tipos)
        rows = (n_tipos + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=tipos_ordenados,
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        for i, tipo in enumerate(tipos_ordenados):
            row = i // cols + 1
            col = i % cols + 1
            
            precios_tipo = []
            for mes in meses_con_datos:
                if tipo in datos_precio[mes].index:
                    precios_tipo.append(datos_precio[mes][tipo])
                else:
                    precios_tipo.append(0)
            
            fig.add_trace(
                go.Bar(
                    x=meses_con_datos,
                    y=precios_tipo,
                    name=tipo,
                    showlegend=False,
                    marker_color=self.color_palette[i % len(self.color_palette)]
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title='Precio Medio por Tipo de Producto - Comparación Mensual',
            template='plotly_white',
            height=300 * rows,
            showlegend=False
        )
        
        # Actualizar ejes Y para mostrar precio
        for i in range(1, rows * cols + 1):
            fig.update_yaxes(title_text="€/kg", row=(i-1)//cols + 1, col=(i-1)%cols + 1)
        
        return fig
    
    def test_sharepoint_connection(self) -> bool:
        """Prueba conexión con SharePoint (placeholder)."""
        # Esta función sería implementada con la lógica real de SharePoint
        return self.is_initialized

# Exportaciones
__all__ = ['CFIInventarioController']
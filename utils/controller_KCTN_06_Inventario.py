"""
KCTN_06_Inventario Controller - Sistema de Control de Inventario
===============================================================
Controlador para gestionar datos de inventario de KCTN.
Proporciona funcionalidades para análisis y visualización.

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0 - Controller Inventario KCTN
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import warnings
import io

warnings.filterwarnings('ignore')

class GarlicInventarioController:
    """Controlador principal para gestión de inventario KCTN."""
    
    def __init__(self):
        """Inicializa el controlador."""
        self.data = {}
        self.inventario_df = pd.DataFrame()
        self.totals = {}
        self.statistics = {}
        self.is_initialized = False
        self.last_update = None
        
        # Colores corporativos Garlic & Beyond
        self.colors = {
            'primary': '#2E7D32',      # Verde principal
            'secondary': '#4CAF50',    # Verde secundario
            'success': '#66BB6A',      # Verde éxito
            'warning': '#FF9800',      # Naranja advertencia
            'error': '#F44336',        # Rojo error
            'info': '#2196F3',         # Azul información
            'light': '#F1F8E9',        # Verde claro
            'dark': '#1B5E20'          # Verde oscuro
        }
    
    def initialize_with_data(self, parsed_data: Dict[str, Any]) -> bool:
        """Inicializa el controlador con datos parseados."""
        try:
            if parsed_data.get('status') != 'success':
                return False
            
            data_content = parsed_data.get('data', {})
            
            # Cargar datos principales
            self.inventario_df = data_content.get('inventario_dataframe', pd.DataFrame())
            self.totals = data_content.get('totals', {})
            self.statistics = data_content.get('statistics', {})
            self.data = data_content
            
            # Verificar que hay datos válidos
            if self.inventario_df.empty:
                return False
            
            self.is_initialized = True
            self.last_update = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Error inicializando controlador: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado del controlador."""
        return {
            'initialized': self.is_initialized,
            'total_proveedores': len(self.inventario_df) if self.is_initialized else 0,
            'total_kg': self.totals.get('total_kg_archivo', 0) if self.is_initialized else 0,
            'total_euros': self.totals.get('total_euros_archivo', 0) if self.is_initialized else 0,
            'last_update': self.last_update.strftime('%Y-%m-%d %H:%M:%S') if self.last_update else None,
            'has_data': not self.inventario_df.empty if self.is_initialized else False
        }
    
    def get_kpis(self) -> Dict[str, Any]:
        """Obtiene los KPIs principales del inventario."""
        if not self.is_initialized:
            return {
                'total_kg': 0,
                'total_euros': 0,
                'total_proveedores': 0,
                'precio_promedio_kg': 0,
                'has_data': False
            }
        
        # Usar totales del archivo (más precisos)
        total_kg = self.totals.get('total_kg_archivo', 0)
        total_euros = self.totals.get('total_euros_archivo', 0)
        
        # Si no hay totales del archivo, usar calculados
        if total_kg == 0:
            total_kg = self.statistics.get('total_kg_calculado', 0)
        if total_euros == 0:
            total_euros = self.statistics.get('total_euros_calculado', 0)
        
        precio_promedio = total_euros / total_kg if total_kg > 0 else 0
        
        return {
            'total_kg': total_kg,
            'total_euros': total_euros,
            'total_proveedores': self.statistics.get('total_proveedores', 0),
            'precio_promedio_kg': precio_promedio,
            'proveedor_mayor_volumen': self.statistics.get('proveedor_mayor_volumen', ''),
            'proveedor_mayor_valor': self.statistics.get('proveedor_mayor_valor', ''),
            'kg_promedio_por_proveedor': self.statistics.get('kg_promedio_por_proveedor', 0),
            'euros_promedio_por_proveedor': self.statistics.get('euros_promedio_por_proveedor', 0),
            'has_data': True
        }
    
    def get_inventario_dataframe(self) -> pd.DataFrame:
        """Obtiene el DataFrame de inventario formateado para mostrar."""
        if not self.is_initialized or self.inventario_df.empty:
            return pd.DataFrame()
        
        # Crear copia para formatear
        df_display = self.inventario_df.copy()
        
        # Formatear columnas numéricas
        df_display['Kg'] = df_display['Kg'].apply(lambda x: f"{x:,.0f}".replace(',', '.'))
        df_display['Euros'] = df_display['Euros'].apply(lambda x: f"€{x:,.0f}".replace(',', '.'))
        df_display['Euros_por_Kg'] = df_display['Euros_por_Kg'].apply(lambda x: f"€{x:.2f}".replace('.', ','))
        
        # Renombrar columnas para display
        df_display.columns = ['Proveedor', 'Kg', 'Euros', '€/Kg']
        
        return df_display
    
    def get_raw_inventario_dataframe(self) -> pd.DataFrame:
        """Obtiene el DataFrame de inventario sin formatear."""
        if not self.is_initialized:
            return pd.DataFrame()
        return self.inventario_df.copy()
    
    def create_proveedores_chart(self) -> go.Figure:
        """Crea gráfico de barras de proveedores por volumen (Kg)."""
        if not self.is_initialized or self.inventario_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font_size=16, font_color="gray"
            )
            return fig
        
        # Ordenar por kg descendente y tomar top 15
        df_sorted = self.inventario_df.nlargest(15, 'Kg')
        
        fig = px.bar(
            df_sorted,
            x='Proveedor',
            y='Kg',
            title='Top 15 Proveedores por Volumen (Kg)',
            labels={'Kg': 'Kilogramos', 'Proveedor': 'Proveedor'},
            color='Kg',
            color_continuous_scale=['#C8E6C9', '#4CAF50', '#2E7D32']
        )
        
        fig.update_layout(
            font_family="Inter",
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=16,
            title_font_color=self.colors['dark'],
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            showlegend=False,
            height=500
        )
        
        fig.update_xaxes(
            tickangle=45,
            title_font_color=self.colors['dark'],
            tickfont_color=self.colors['dark']
        )
        
        fig.update_yaxes(
            title_font_color=self.colors['dark'],
            tickfont_color=self.colors['dark'],
            tickformat=',.0f'
        )
        
        return fig
    
    def create_valor_chart(self) -> go.Figure:
        """Crea gráfico de barras de proveedores por valor (Euros)."""
        if not self.is_initialized or self.inventario_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font_size=16, font_color="gray"
            )
            return fig
        
        # Ordenar por euros descendente y tomar top 15
        df_sorted = self.inventario_df.nlargest(15, 'Euros')
        
        fig = px.bar(
            df_sorted,
            x='Proveedor',
            y='Euros',
            title='Top 15 Proveedores por Valor (€)',
            labels={'Euros': 'Euros (€)', 'Proveedor': 'Proveedor'},
            color='Euros',
            color_continuous_scale=['#FFECB3', '#FF9800', '#E65100']
        )
        
        fig.update_layout(
            font_family="Inter",
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=16,
            title_font_color=self.colors['dark'],
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            showlegend=False,
            height=500
        )
        
        fig.update_xaxes(
            tickangle=45,
            title_font_color=self.colors['dark'],
            tickfont_color=self.colors['dark']
        )
        
        fig.update_yaxes(
            title_font_color=self.colors['dark'],
            tickfont_color=self.colors['dark'],
            tickformat='€,.0f'
        )
        
        return fig
    
    def create_precio_kg_chart(self) -> go.Figure:
        """Crea gráfico de precio por kg de proveedores."""
        if not self.is_initialized or self.inventario_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font_size=16, font_color="gray"
            )
            return fig
        
        # Filtrar proveedores con precio válido y ordenar
        df_precio = self.inventario_df[self.inventario_df['Euros_por_Kg'] > 0].copy()
        df_sorted = df_precio.nlargest(15, 'Euros_por_Kg')
        
        fig = px.bar(
            df_sorted,
            x='Proveedor',
            y='Euros_por_Kg',
            title='Top 15 Proveedores por Precio/Kg (€)',
            labels={'Euros_por_Kg': 'Precio por Kg (€)', 'Proveedor': 'Proveedor'},
            color='Euros_por_Kg',
            color_continuous_scale=['#E1F5FE', '#2196F3', '#0D47A1']
        )
        
        fig.update_layout(
            font_family="Inter",
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=16,
            title_font_color=self.colors['dark'],
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            showlegend=False,
            height=500
        )
        
        fig.update_xaxes(
            tickangle=45,
            title_font_color=self.colors['dark'],
            tickfont_color=self.colors['dark']
        )
        
        fig.update_yaxes(
            title_font_color=self.colors['dark'],
            tickfont_color=self.colors['dark'],
            tickformat='€.3f'
        )
        
        return fig
    
    def create_distribucion_pie_chart(self) -> go.Figure:
        """Crea gráfico pie de distribución por valor."""
        if not self.is_initialized or self.inventario_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font_size=16, font_color="gray"
            )
            return fig
        
        # Tomar top 10 proveedores por euros y agrupar el resto
        df_sorted = self.inventario_df.nlargest(10, 'Euros')
        otros_euros = self.inventario_df.iloc[10:]['Euros'].sum() if len(self.inventario_df) > 10 else 0
        
        # Preparar datos para el pie chart
        labels = df_sorted['Proveedor'].tolist()
        values = df_sorted['Euros'].tolist()
        
        if otros_euros > 0:
            labels.append('Otros')
            values.append(otros_euros)
        
        # Colores verdes para el tema Garlic & Beyond
        colors = px.colors.sequential.Greens_r[:len(labels)]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title='Distribución de Valor por Proveedor (Top 10)',
            font_family="Inter",
            title_font_size=16,
            title_font_color=self.colors['dark'],
            showlegend=False,
            height=500
        )
        
        return fig
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas resumidas para el dashboard."""
        if not self.is_initialized:
            return {}
        
        kpis = self.get_kpis()
        
        # Calcular estadísticas adicionales
        df = self.inventario_df
        
        # Percentiles de precio
        precio_p25 = df['Euros_por_Kg'].quantile(0.25) if not df.empty else 0
        precio_p75 = df['Euros_por_Kg'].quantile(0.75) if not df.empty else 0
        
        # Distribución de volumen
        kg_p25 = df['Kg'].quantile(0.25) if not df.empty else 0
        kg_p75 = df['Kg'].quantile(0.75) if not df.empty else 0
        
        return {
            'kpis_basicos': kpis,
            'percentiles_precio': {
                'p25': precio_p25,
                'p50': df['Euros_por_Kg'].median() if not df.empty else 0,
                'p75': precio_p75
            },
            'percentiles_volumen': {
                'p25': kg_p25,
                'p50': df['Kg'].median() if not df.empty else 0,
                'p75': kg_p75
            },
            'rangos': {
                'precio_min': df['Euros_por_Kg'].min() if not df.empty else 0,
                'precio_max': df['Euros_por_Kg'].max() if not df.empty else 0,
                'kg_min': df['Kg'].min() if not df.empty else 0,
                'kg_max': df['Kg'].max() if not df.empty else 0
            }
        }
    
    def export_to_excel(self) -> bytes:
        """Exporta datos de inventario a Excel."""
        if not self.is_initialized:
            return None
        
        try:
            # Usar pandas para crear Excel
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Hoja principal con datos
                df_export = self.inventario_df.copy()
                df_export.to_excel(writer, sheet_name='Inventario_KCTN', index=False)
                
                # Hoja con resumen
                kpis = self.get_kpis()
                summary_data = {
                    'Métrica': [
                        'Total Kg',
                        'Total Euros',
                        'Total Proveedores',
                        'Precio Promedio €/Kg',
                        'Proveedor Mayor Volumen',
                        'Proveedor Mayor Valor'
                    ],
                    'Valor': [
                        f"{kpis['total_kg']:,.0f}",
                        f"€{kpis['total_euros']:,.0f}",
                        kpis['total_proveedores'],
                        f"€{kpis['precio_promedio_kg']:.3f}",
                        kpis['proveedor_mayor_volumen'],
                        kpis['proveedor_mayor_valor']
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            processed_data = output.getvalue()
            return processed_data
            
        except Exception as e:
            print(f"Error generando Excel: {e}")
            return None


# Exportaciones
__all__ = [
    'GarlicInventarioController'
]
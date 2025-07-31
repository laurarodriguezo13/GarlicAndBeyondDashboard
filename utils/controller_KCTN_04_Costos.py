"""
Controller para KCTN_04_Costos - Control entrada M.P. Planta pelado
===================================================================
Maneja la lógica de negocio, filtros y visualizaciones para el módulo de Costos KCTN.
Estilo mejorado siguiendo la estética de Garlic & Beyond.

Autor: GANDB Dashboard Team
Fecha: 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import calendar
import numpy as np

# Meses en español
MESES_ESPANOL = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

MESES_ESPANOL_REVERSE = {v: k for k, v in MESES_ESPANOL.items()}

class CostosKCTNController:
    """Controller principal para el módulo de Costos KCTN."""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Inicializa el controller con datos parseados.
        
        Args:
            data: Datos procesados del parser
        """
        self.raw_data = data
        self.df = data.get('data', pd.DataFrame())
        self.metrics = data.get('metrics', {})
        self.metadata = data.get('metadata', {})
        self.filtered_df = self.df.copy() if not self.df.empty else pd.DataFrame()
        self.is_initialized = not self.df.empty
        
        # Preparar datos por mes si hay datos
        if self.is_initialized:
            self._prepare_monthly_data()
    
    def _prepare_monthly_data(self):
        """Prepara los datos organizados por mes."""
        try:
            self.monthly_data = {}
            
            if 'fecha_entrega' in self.df.columns:
                # Agrupar por mes usando nombres en español
                for month_num in range(1, 13):
                    month_name = MESES_ESPANOL[month_num]
                    month_data = self.df[self.df['mes'] == month_num].copy()
                    
                    self.monthly_data[month_name] = {
                        'data': month_data,
                        'has_data': not month_data.empty,
                        'count': len(month_data),
                        'month_num': month_num
                    }
            
        except Exception as e:
            st.error(f"Error preparando datos mensuales: {e}")
            self.monthly_data = {}
    
    def get_available_months(self) -> List[str]:
        """Obtiene lista de meses disponibles en español y en orden."""
        if hasattr(self, 'monthly_data'):
            # Devolver meses en orden cronológico
            return [MESES_ESPANOL[i] for i in range(1, 13)]
        return [MESES_ESPANOL[i] for i in range(1, 13)]
    
    def get_months_with_data(self) -> List[str]:
        """Obtiene meses que tienen datos reales."""
        if hasattr(self, 'monthly_data'):
            return [month for month, info in self.monthly_data.items() if info['has_data']]
        return []
    
    def get_monthly_kpis(self, month: str) -> Dict[str, Any]:
        """Calcula KPIs para un mes específico con filtrado de datos válidos."""
        try:
            if not hasattr(self, 'monthly_data') or month not in self.monthly_data:
                return self._empty_kpis()
            
            month_info = self.monthly_data[month]
            if not month_info['has_data']:
                return self._empty_kpis()
            
            month_df = month_info['data'].copy()
            
            # FILTRAR DATOS VÁLIDOS ANTES DE CALCULAR KPIs
            # Datos básicos válidos
            valid_basic = month_df[
                (month_df['proveedor'].notna()) &
                (month_df['proveedor'] != '') &
                (month_df['fecha_entrega'].notna())
            ]
            
            if valid_basic.empty:
                return self._empty_kpis()
            
            # Filtrar para cada métrica específica
            valid_desgrane = valid_basic[
                (valid_basic['kg_desgranado'] >= 0) &
                (valid_basic['kg_desgranado'].notna()) &
                (valid_basic['porcentaje_desg'].between(0, 1))
            ]
            
            valid_cat1 = valid_basic[
                (valid_basic['kg_cat1_diente'] >= 0) &
                (valid_basic['kg_cat1_diente'].notna()) &
                (valid_basic['porcentaje_cat1'].between(0, 1))
            ]
            
            valid_coste_cat1 = valid_basic[
                (valid_basic['coste_kg_diente_cat1'] > 0) &
                (valid_basic['coste_kg_diente_cat1'].notna())
            ]
            
            valid_corredor = valid_basic[
                (valid_basic['total_coste_corredor'] >= 0) &
                (valid_basic['total_coste_corredor'].notna()) &
                (valid_basic['coste_kg_corredor'] >= 0) &
                (valid_basic['coste_kg_corredor'].notna())
            ]
            
            valid_porte = valid_basic[
                (valid_basic['porte'] >= 0) &
                (valid_basic['porte'].notna()) &
                (valid_basic['coste_kg_porte'] >= 0) &
                (valid_basic['coste_kg_porte'].notna())
            ]
            
            valid_mp = valid_basic[
                (valid_basic['kg_mp'] > 0) &
                (valid_basic['kg_mp'].notna()) &
                (valid_basic['total_fra'] > 0) &
                (valid_basic['total_fra'].notna())
            ]
            
            # Calcular KPIs con datos filtrados
            kpis = {
                'has_data': True,
                'total_records': len(valid_basic),
                
                # Desgrane
                'total_kg_desgranado': valid_desgrane['kg_desgranado'].sum() if not valid_desgrane.empty else 0,
                'promedio_porcentaje_desg': valid_desgrane['porcentaje_desg'].mean() if not valid_desgrane.empty else 0,
                
                # Categoría 1
                'total_kg_cat1': valid_cat1['kg_cat1_diente'].sum() if not valid_cat1.empty else 0,
                'promedio_porcentaje_cat1': valid_cat1['porcentaje_cat1'].mean() if not valid_cat1.empty else 0,
                'promedio_porcentaje_estimado': valid_cat1['porcentaje_estimado'].mean() if not valid_cat1.empty else 0,
                'promedio_diferencia': valid_cat1['diferencia'].mean() if not valid_cat1.empty else 0,
                
                # Corredor
                'promedio_coste_kg_corredor': valid_corredor['coste_kg_corredor'].mean() if not valid_corredor.empty else 0,
                'total_coste_corredor': valid_corredor['total_coste_corredor'].sum() if not valid_corredor.empty else 0,
                
                # Porte
                'promedio_coste_kg_porte': valid_porte['coste_kg_porte'].mean() if not valid_porte.empty else 0,
                'total_porte': valid_porte['porte'].sum() if not valid_porte.empty else 0,
                
                # Coste promedio Cat 1
                'promedio_coste_kg_diente_cat1': valid_coste_cat1['coste_kg_diente_cat1'].mean() if not valid_coste_cat1.empty else 0,
                
                # Totales
                'total_kg_mp': valid_mp['kg_mp'].sum() if not valid_mp.empty else 0,
                'total_inversion': valid_mp['total_fra'].sum() if not valid_mp.empty else 0,
                'total_proveedores': valid_basic['proveedor'].nunique() if not valid_basic.empty else 0
            }
            
            return kpis
            
        except Exception as e:
            st.error(f"Error calculando KPIs mensuales: {e}")
            return self._empty_kpis()
    
    def _empty_kpis(self) -> Dict[str, Any]:
        """Retorna KPIs vacíos."""
        return {
            'has_data': False,
            'total_records': 0,
            'total_kg_desgranado': 0,
            'promedio_porcentaje_desg': 0,
            'total_kg_cat1': 0,
            'promedio_porcentaje_cat1': 0,
            'promedio_porcentaje_estimado': 0,
            'promedio_diferencia': 0,
            'promedio_coste_kg_corredor': 0,
            'total_coste_corredor': 0,
            'promedio_coste_kg_porte': 0,
            'total_porte': 0,
            'promedio_coste_kg_diente_cat1': 0,
            'total_kg_mp': 0,
            'total_inversion': 0,
            'total_proveedores': 0
        }
    
    def get_analisis_proveedor_data(self, month: str) -> Dict[str, Any]:
        """Obtiene datos de análisis por proveedor para un mes."""
        try:
            if not hasattr(self, 'monthly_data') or month not in self.monthly_data:
                return {'proveedores': [], 'has_data': False}
            
            month_info = self.monthly_data[month]
            if not month_info['has_data']:
                return {'proveedores': [], 'has_data': False}
            
            month_df = month_info['data'].copy()
            
            # FILTRAR DATOS VÁLIDOS ANTES DE AGRUPAR
            valid_data = month_df[
                (month_df['proveedor'].notna()) &
                (month_df['proveedor'] != '') &
                (month_df['kg_mp'] > 0) &
                (month_df['kg_mp'].notna()) &
                (month_df['total_fra'] > 0) &
                (month_df['total_fra'].notna())
            ]
            
            if valid_data.empty:
                return {'proveedores': [], 'has_data': False}
            
            # Agrupar por proveedor con datos válidos
            proveedor_stats = valid_data.groupby('proveedor').agg({
                'kg_mp': 'sum',
                'total_fra': 'sum',
                'coste_kg_diente_cat1': lambda x: x[x > 0].mean() if (x > 0).any() else 0,  # Solo promediar valores > 0
                'porcentaje_cat1': lambda x: x[(x >= 0) & (x <= 1)].mean() if ((x >= 0) & (x <= 1)).any() else 0,  # Porcentajes válidos
                'total_coste_corredor': lambda x: x[x >= 0].sum(),  # Solo sumar valores >= 0
                'porte': lambda x: x[x >= 0].sum()  # Solo sumar valores >= 0
            }).round(2)
            
            # Filtrar proveedores con datos mínimos válidos
            proveedor_stats = proveedor_stats[
                (proveedor_stats['kg_mp'] > 0) & 
                (proveedor_stats['total_fra'] > 0)
            ]
            
            proveedores = []
            for proveedor, stats in proveedor_stats.iterrows():
                proveedores.append({
                    'nombre': proveedor,
                    'kg_mp': stats['kg_mp'],
                    'total_inversion': stats['total_fra'],
                    'coste_kg_cat1': stats['coste_kg_diente_cat1'],
                    'porcentaje_cat1': stats['porcentaje_cat1'], 
                    'coste_corredor': stats['total_coste_corredor'],
                    'coste_porte': stats['porte']
                })
            
            return {
                'proveedores': proveedores,
                'has_data': len(proveedores) > 0,
                'total_proveedores': len(proveedores)
            }
            
        except Exception as e:
            st.error(f"Error análisis proveedores: {e}")
            return {'proveedores': [], 'has_data': False}
    
    def create_coste_cat1_trend_chart(self, month: str):
        """Crea gráfico de tendencia de coste Cat 1 para un mes específico."""
        try:
            if not hasattr(self, 'monthly_data') or month not in self.monthly_data:
                return self._empty_chart("Sin datos disponibles")
            
            month_info = self.monthly_data[month]
            if not month_info['has_data']:
                return self._empty_chart(f"No hay datos para {month}")
            
            month_df = month_info['data'].copy()
            
            # FILTRAR DATOS PROBLEMÁTICOS - AQUÍ ESTÁ EL FIX
            # Excluir registros con valores 0, nulos o negativos
            month_df = month_df[
                (month_df['coste_kg_diente_cat1'] > 0) & 
                (month_df['coste_kg_diente_cat1'].notna()) &
                (month_df['fecha_entrega'].notna())
            ]
            
            if month_df.empty:
                return self._empty_chart(f"No hay datos válidos para {month}")
            
            month_df = month_df.sort_values('fecha_entrega')
            
            fig = px.line(
                month_df,
                x='fecha_entrega',
                y='coste_kg_diente_cat1',
                title=f"Evolución Coste/Kg Diente Cat 1 - {month}",
                labels={
                    'fecha_entrega': 'Fecha de Entrega',
                    'coste_kg_diente_cat1': 'Coste/Kg (€)'
                },
                hover_data=['proveedor', 'kg_mp']
            )
            
            fig.update_traces(
                line=dict(color='#2E7D32', width=3),
                mode='lines+markers',
                marker=dict(size=8, color='#4CAF50')
            )
            
            fig.update_layout(
                template="plotly_white",
                height=400,
                xaxis_title="Fecha de Entrega",
                yaxis_title="Coste/Kg (€)",
                font=dict(family="Inter, sans-serif")
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creando gráfico coste Cat 1: {e}")
            return self._empty_chart("Error en datos")
    
    def create_proveedor_comparison_chart(self, month: str):
        """Crea gráfico comparativo por proveedor."""
        try:
            if not hasattr(self, 'monthly_data') or month not in self.monthly_data:
                return self._empty_chart("Sin datos disponibles")
            
            month_info = self.monthly_data[month]
            if not month_info['has_data']:
                return self._empty_chart(f"No hay datos para {month}")
            
            month_df = month_info['data'].copy()
            
            # FILTRAR DATOS PROBLEMÁTICOS - MISMO FIX AQUÍ
            month_df = month_df[
                (month_df['total_fra'] > 0) & 
                (month_df['total_fra'].notna()) &
                (month_df['kg_mp'] > 0) &
                (month_df['kg_mp'].notna())
            ]
            
            if month_df.empty:
                return self._empty_chart(f"No hay datos válidos para {month}")
            
            # Agrupar por proveedor
            proveedor_data = month_df.groupby('proveedor').agg({
                'total_fra': 'sum',
                'kg_mp': 'sum'
            }).round(0)
            
            # Filtrar proveedores con valores válidos
            proveedor_data = proveedor_data[proveedor_data['total_fra'] > 0]
            
            if proveedor_data.empty:
                return self._empty_chart(f"No hay datos de proveedores válidos para {month}")
            
            fig = px.bar(
                x=proveedor_data.index,
                y=proveedor_data['total_fra'],
                title=f"Inversión Total por Proveedor - {month}",
                labels={'x': 'Proveedor', 'y': 'Inversión Total (€)'},
                color=proveedor_data['total_fra'],
                color_continuous_scale='Greens'
            )
            
            fig.update_layout(
                template="plotly_white",
                height=400,
                showlegend=False,
                font=dict(family="Inter, sans-serif")
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creando gráfico proveedores: {e}")
            return self._empty_chart("Error en datos")
    
    def create_performance_matrix_styled(self, month: str):
        """Crea matriz de rendimiento estilizada con pandas styler."""
        try:
            if not hasattr(self, 'monthly_data') or month not in self.monthly_data:
                return pd.DataFrame()
            
            month_info = self.monthly_data[month]
            if not month_info['has_data']:
                return pd.DataFrame()
            
            month_df = month_info['data'].copy()
            
            # Filtrar datos válidos
            month_df = month_df[
                (month_df['proveedor'].notna()) &
                (month_df['proveedor'] != '') &
                (month_df['fecha_entrega'].notna())
            ]
            
            if month_df.empty:
                return pd.DataFrame()
            
            # Crear DataFrame para la matriz
            matrix_data = []
            
            for idx, row in month_df.iterrows():
                fecha_str = row['fecha_entrega'].strftime('%d/%m/%Y') if pd.notna(row['fecha_entrega']) else 'N/A'
                
                # Formatear valores con colores usando emojis
                def format_with_color(value, column):
                    if pd.isna(value):
                        return "N/A"
                    
                    pct_value = value * 100
                    formatted = f"{pct_value:.1f}%"
                    
                    # Determinar color según umbrales
                    if column == 'desg':
                        return f"🟢 {formatted}" if value >= 0.85 else f"🔴 {formatted}"
                    elif column == 'cat1':
                        return f"🟢 {formatted}" if value >= 0.55 else f"🔴 {formatted}"
                    elif column == 'cat2':
                        return f"🟢 {formatted}" if value >= 0.25 else f"🔴 {formatted}"
                    elif column == 'dag':
                        return f"🟢 {formatted}" if value >= 0.20 else f"🔴 {formatted}"
                    elif column == 'merma':
                        return f"🟢 {formatted}" if value <= 0.10 else f"🔴 {formatted}"
                    else:
                        return formatted
                
                # Crear fila con valores formateados y coloreados
                matrix_row = {
                    'Proveedor': row['proveedor'],
                    'Fecha': fecha_str,
                    '% DESG': format_with_color(row['porcentaje_desg'], 'desg'),
                    '% CAT I': format_with_color(row['porcentaje_cat1'], 'cat1'),
                    '% CAT II': format_with_color(row['porcentaje_cat2'], 'cat2'),
                    '% DAG': format_with_color(row['porcentaje_dag'], 'dag'),
                    '% MERMA': format_with_color(row['porcentaje_merma'], 'merma')
                }
                
                matrix_data.append(matrix_row)
            
            if not matrix_data:
                return pd.DataFrame()
            
            # Crear DataFrame
            df_matrix = pd.DataFrame(matrix_data)
            
            return df_matrix
            
        except Exception as e:
            st.error(f"Error creando matriz estilizada: {e}")
            return pd.DataFrame()
    
    def create_multi_month_kpi_table(self, months: List[str]) -> pd.DataFrame:
        """Crea tabla comparativa de KPIs para múltiples meses con datos filtrados."""
        try:
            if not months:
                return pd.DataFrame()
            
            # Lista para almacenar datos de cada mes
            table_data = []
            
            for month in months:
                if month in self.monthly_data and self.monthly_data[month]['has_data']:
                    # Usar KPIs ya filtrados
                    kpis = self.get_monthly_kpis(month)
                    
                    # Solo incluir el mes si tiene datos válidos
                    if kpis['total_records'] > 0 and (kpis['total_kg_mp'] > 0 or kpis['total_inversion'] > 0):
                        # Preparar fila de datos
                        row = {
                            'Mes': month,
                            'Total Registros': kpis['total_records'],
                            'Total Proveedores': kpis['total_proveedores'],
                            'Total kg M.P.': f"{kpis['total_kg_mp']:,.0f}",
                            'Total Inversión': f"€{kpis['total_inversion']:,.0f}",
                            'kg Desgranado': f"{kpis['total_kg_desgranado']:,.0f}",
                            '% Desgrane': f"{kpis['promedio_porcentaje_desg']*100:.1f}%",
                            'kg Cat 1': f"{kpis['total_kg_cat1']:,.0f}",
                            '% Cat 1 Real': f"{kpis['promedio_porcentaje_cat1']*100:.1f}%",
                            '% Cat 1 Esperado': f"{kpis['promedio_porcentaje_estimado']*100:.1f}%",
                            'Diferencia %': f"{kpis['promedio_diferencia']*100:.1f}%",
                            'Coste/kg Corredor': f"€{kpis['promedio_coste_kg_corredor']:.3f}",
                            'Total Corredor': f"€{kpis['total_coste_corredor']:,.0f}",
                            'Coste/kg Porte': f"€{kpis['promedio_coste_kg_porte']:.3f}",
                            'Total Porte': f"€{kpis['total_porte']:,.0f}",
                            'Coste/kg Cat 1': f"€{kpis['promedio_coste_kg_diente_cat1']:.3f}"
                        }
                        
                        table_data.append(row)
                # Si no hay datos válidos para el mes, no lo incluimos en la tabla
            
            # Crear DataFrame
            if table_data:
                df_table = pd.DataFrame(table_data)
                
                # Ordenar por mes cronológicamente
                month_order = {month: i for i, month in enumerate([MESES_ESPANOL[i] for i in range(1, 13)])}
                df_table['month_order'] = df_table['Mes'].map(month_order)
                df_table = df_table.sort_values('month_order').drop('month_order', axis=1)
                
                return df_table
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error creando tabla comparativa: {e}")
            return pd.DataFrame()
        """Crea gráfico comparativo multi-mes."""
        try:
            if not months:
                return self._empty_chart("Selecciona meses para comparar")
            
            comparison_data = []
            
            for month in months:
                if month in self.monthly_data and self.monthly_data[month]['has_data']:
                    kpis = self.get_monthly_kpis(month)
                    
                    if metric == 'coste_cat1':
                        value = kpis['promedio_coste_kg_diente_cat1']
                        label = 'Coste/Kg Diente Cat 1 (€)'
                    elif metric == 'total_corredor':
                        value = kpis['total_coste_corredor']
                        label = 'Coste Total Corredor (€)'
                    elif metric == 'total_porte':
                        value = kpis['total_porte']
                        label = 'Coste Total Porte (€)'
                    else:
                        continue
                    
                    comparison_data.append({
                        'Mes': month,
                        'Valor': value,
                        'Métrica': label
                    })
            
            if not comparison_data:
                return self._empty_chart("No hay datos para los meses seleccionados")
            
            df_comp = pd.DataFrame(comparison_data)
            
            fig = px.line(
                df_comp,
                x='Mes',
                y='Valor',
                title=f"Evolución {df_comp['Métrica'].iloc[0]}",
                markers=True
            )
            
            fig.update_traces(
                line=dict(color='#2E7D32', width=3),
                marker=dict(size=10, color='#4CAF50')
            )
            
            fig.update_layout(
                template="plotly_white",
                height=400,
                font=dict(family="Inter, sans-serif")
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creando gráfico comparativo: {e}")
            return self._empty_chart("Error en datos")
    
    def create_comprehensive_evolution_chart(self, months: List[str]) -> go.Figure:
        """Crea gráfico de evolución comprehensivo con múltiples métricas."""
        try:
            if not months:
                return self._empty_chart("Selecciona meses para comparar")
            
            # Recopilar datos de todos los meses
            evolution_data = []
            
            for month in months:
                if month in self.monthly_data and self.monthly_data[month]['has_data']:
                    month_df = self.monthly_data[month]['data'].copy()
                    month_num = self.monthly_data[month]['month_num']
                    
                    # FILTRAR DATOS VÁLIDOS PARA CADA MÉTRICA
                    # Coste/Kg Cat 1
                    valid_coste = month_df[
                        (month_df['coste_kg_diente_cat1'] > 0) & 
                        (month_df['coste_kg_diente_cat1'].notna())
                    ]
                    coste_cat1 = valid_coste['coste_kg_diente_cat1'].mean() if not valid_coste.empty else 0
                    
                    # Total Corredor
                    valid_corredor = month_df[
                        (month_df['total_coste_corredor'] >= 0) & 
                        (month_df['total_coste_corredor'].notna())
                    ]
                    total_corredor = valid_corredor['total_coste_corredor'].sum() if not valid_corredor.empty else 0
                    
                    # Total Porte
                    valid_porte = month_df[
                        (month_df['porte'] >= 0) & 
                        (month_df['porte'].notna())
                    ]
                    total_porte = valid_porte['porte'].sum() if not valid_porte.empty else 0
                    
                    # Porcentajes (filtrar valores entre 0 y 1)
                    valid_percentages = month_df[
                        (month_df['porcentaje_desg'].between(0, 1)) &
                        (month_df['porcentaje_cat1'].between(0, 1)) &
                        (month_df['kg_mp'] > 0)
                    ]
                    
                    pct_desg = valid_percentages['porcentaje_desg'].mean() * 100 if not valid_percentages.empty else 0
                    pct_cat1 = valid_percentages['porcentaje_cat1'].mean() * 100 if not valid_percentages.empty else 0
                    kg_mp_total = valid_percentages['kg_mp'].sum() / 1000 if not valid_percentages.empty else 0  # En miles
                    
                    # Solo agregar el mes si tiene al menos algunos datos válidos
                    if coste_cat1 > 0 or total_corredor > 0 or total_porte > 0 or kg_mp_total > 0:
                        evolution_data.append({
                            'Mes': month,
                            'month_order': month_num,
                            'Coste/Kg Cat 1': coste_cat1,
                            'Total Corredor': total_corredor,
                            'Total Porte': total_porte,
                            '% Desgrane': pct_desg,
                            '% Cat 1': pct_cat1,
                            'kg M.P. Total': kg_mp_total
                        })
            
            if not evolution_data:
                return self._empty_chart("No hay datos válidos para los meses seleccionados")
            
            df_evolution = pd.DataFrame(evolution_data)
            df_evolution = df_evolution.sort_values('month_order')
            
            # Crear figura con subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Coste/Kg Diente Cat 1', 'Costes Totales', 'Porcentajes de Calidad', 'Volumen M.P.'),
                specs=[[{'secondary_y': False}, {'secondary_y': False}],
                       [{'secondary_y': False}, {'secondary_y': False}]]
            )
            
            # Gráfico 1: Coste/Kg Cat 1 (solo valores > 0)
            coste_data = df_evolution[df_evolution['Coste/Kg Cat 1'] > 0]
            if not coste_data.empty:
                fig.add_trace(
                    go.Scatter(x=coste_data['Mes'], y=coste_data['Coste/Kg Cat 1'],
                              mode='lines+markers', name='Coste/Kg Cat 1',
                              line=dict(color='#D32F2F', width=3)),
                    row=1, col=1
                )
            
            # Gráfico 2: Costes Totales (solo valores > 0)
            corredor_data = df_evolution[df_evolution['Total Corredor'] > 0]
            porte_data = df_evolution[df_evolution['Total Porte'] > 0]
            
            if not corredor_data.empty:
                fig.add_trace(
                    go.Scatter(x=corredor_data['Mes'], y=corredor_data['Total Corredor'],
                              mode='lines+markers', name='Total Corredor',
                              line=dict(color='#FF9800', width=2)),
                    row=1, col=2
                )
            if not porte_data.empty:
                fig.add_trace(
                    go.Scatter(x=porte_data['Mes'], y=porte_data['Total Porte'],
                              mode='lines+markers', name='Total Porte',
                              line=dict(color='#9C27B0', width=2)),
                    row=1, col=2
                )
            
            # Gráfico 3: Porcentajes (solo valores > 0)
            desg_data = df_evolution[df_evolution['% Desgrane'] > 0]
            cat1_data = df_evolution[df_evolution['% Cat 1'] > 0]
            
            if not desg_data.empty:
                fig.add_trace(
                    go.Scatter(x=desg_data['Mes'], y=desg_data['% Desgrane'],
                              mode='lines+markers', name='% Desgrane',
                              line=dict(color='#4CAF50', width=2)),
                    row=2, col=1
                )
            if not cat1_data.empty:
                fig.add_trace(
                    go.Scatter(x=cat1_data['Mes'], y=cat1_data['% Cat 1'],
                              mode='lines+markers', name='% Cat 1',
                              line=dict(color='#2196F3', width=2)),
                    row=2, col=1
                )
            
            # Gráfico 4: Volumen (solo valores > 0)
            volume_data = df_evolution[df_evolution['kg M.P. Total'] > 0]
            if not volume_data.empty:
                fig.add_trace(
                    go.Scatter(x=volume_data['Mes'], y=volume_data['kg M.P. Total'],
                              mode='lines+markers', name='kg M.P. (miles)',
                              line=dict(color='#795548', width=3)),
                    row=2, col=2
                )
            
            # Actualizar layout
            fig.update_layout(
                height=600,
                showlegend=True,
                title_text="Dashboard de Evolución Integral - Costos KCTN",
                template="plotly_white",
                font=dict(family="Inter, sans-serif")
            )
            
            # Actualizar ejes
            fig.update_xaxes(title_text="Mes")
            fig.update_yaxes(title_text="€/kg", row=1, col=1)
            fig.update_yaxes(title_text="€", row=1, col=2)
            fig.update_yaxes(title_text="%", row=2, col=1)
            fig.update_yaxes(title_text="Miles kg", row=2, col=2)
            
            return fig
            
        except Exception as e:
            st.error(f"Error creando gráfico de evolución comprehensivo: {e}")
            return self._empty_chart("Error en datos")
        """Crea un gráfico vacío con mensaje."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template="plotly_white",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    def _empty_chart(self, message: str):
        """Crea un gráfico vacío con mensaje."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template="plotly_white",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado del controlador."""
        if not self.is_initialized:
            return {
                'initialized': False,
                'total_records': 0,
                'months_with_data': 0,
                'last_update': 'N/A'
            }
        
        months_with_data = len(self.get_months_with_data())
        
        return {
            'initialized': True,
            'total_records': len(self.df),
            'months_with_data': months_with_data,
            'months_empty': 12 - months_with_data,
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'date_range': self._get_date_range()
        }
    
    def _get_date_range(self) -> str:
        """Obtiene el rango de fechas de los datos."""
        try:
            if 'fecha_entrega' not in self.df.columns:
                return 'N/A'
            
            dates = self.df['fecha_entrega'].dropna()
            if dates.empty:
                return 'N/A'
            
            min_date = dates.min().strftime('%d/%m/%Y')
            max_date = dates.max().strftime('%d/%m/%Y')
            return f"{min_date} - {max_date}"
            
        except Exception:
            return 'N/A'
    
    def get_summary_stats(self, month: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene estadísticas de resumen."""
        try:
            if month:
                # Stats para un mes específico
                if not hasattr(self, 'monthly_data') or month not in self.monthly_data:
                    return {}
                
                month_info = self.monthly_data[month]
                if not month_info['has_data']:
                    return {}
                
                month_df = month_info['data']
                
                return {
                    'total_records': len(month_df),
                    'total_proveedores': month_df['proveedor'].nunique(),
                    'fecha_min': month_df['fecha_entrega'].min(),
                    'fecha_max': month_df['fecha_entrega'].max(),
                    'total_kg_mp': month_df['kg_mp'].sum(),
                    'total_inversión': month_df['total_fra'].sum()
                }
            else:
                # Stats globales
                if self.df.empty:
                    return {}
                
                return {
                    'total_records': len(self.df),
                    'total_proveedores': self.df['proveedor'].nunique(),
                    'fecha_min': self.df['fecha_entrega'].min(),
                    'fecha_max': self.df['fecha_entrega'].max(),
                    'total_kg_mp': self.df['kg_mp'].sum(),
                    'total_inversión': self.df['total_fra'].sum(),
                    'months_with_data': len(self.get_months_with_data())
                }
                
        except Exception as e:
            st.error(f"Error obteniendo estadísticas: {e}")
            return {}
        """Obtiene el estado del controlador."""
        if not self.is_initialized:
            return {
                'initialized': False,
                'total_records': 0,
                'months_with_data': 0,
                'last_update': 'N/A'
            }
        
        months_with_data = len(self.get_months_with_data())
        
        return {
            'initialized': True,
            'total_records': len(self.df),
            'months_with_data': months_with_data,
            'months_empty': 12 - months_with_data,
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'date_range': self._get_date_range()
        }
    
    def _get_date_range(self) -> str:
        """Obtiene el rango de fechas de los datos."""
        try:
            if 'fecha_entrega' not in self.df.columns:
                return 'N/A'
            
            dates = self.df['fecha_entrega'].dropna()
            if dates.empty:
                return 'N/A'
            
            min_date = dates.min().strftime('%d/%m/%Y')
            max_date = dates.max().strftime('%d/%m/%Y')
            return f"{min_date} - {max_date}"
            
        except Exception:
            return 'N/A'
    
    def get_summary_stats(self, month: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene estadísticas de resumen."""
        try:
            if month:
                # Stats para un mes específico
                if not hasattr(self, 'monthly_data') or month not in self.monthly_data:
                    return {}
                
                month_info = self.monthly_data[month]
                if not month_info['has_data']:
                    return {}
                
                month_df = month_info['data']
                
                return {
                    'total_records': len(month_df),
                    'total_proveedores': month_df['proveedor'].nunique(),
                    'fecha_min': month_df['fecha_entrega'].min(),
                    'fecha_max': month_df['fecha_entrega'].max(),
                    'total_kg_mp': month_df['kg_mp'].sum(),
                    'total_inversión': month_df['total_fra'].sum()
                }
            else:
                # Stats globales
                if self.df.empty:
                    return {}
                
                return {
                    'total_records': len(self.df),
                    'total_proveedores': self.df['proveedor'].nunique(),
                    'fecha_min': self.df['fecha_entrega'].min(),
                    'fecha_max': self.df['fecha_entrega'].max(),
                    'total_kg_mp': self.df['kg_mp'].sum(),
                    'total_inversión': self.df['total_fra'].sum(),
                    'months_with_data': len(self.get_months_with_data())
                }
                
        except Exception as e:
            st.error(f"Error obteniendo estadísticas: {e}")
            return {}
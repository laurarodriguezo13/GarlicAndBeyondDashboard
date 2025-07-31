"""
Controller KCTN 01 - Producción - CORREGIDO PARA DATOS REALES
=============================================================
Controlador corregido para manejar la estructura real del Excel
y calcular correctamente todos los KPIs según las instrucciones.

Funcionalidades:
- Gestión de filtros (Individual/Multi-mes)
- Cálculos de KPIs dinámicos correctos
- Preparación de datos para gráficos
- Análisis comparativo
- Formateo de datos para la interfaz

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.2 (Datos Reales)
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ================================================================
# CONFIGURACIÓN DEL CONTROLLER
# ================================================================

MESES_NOMBRES = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

MESES_MAPPING = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# Colores para gráficos
COLORS = {
    'mp': '#1f77b4',      # Azul
    'desgr': '#ff7f0e',   # Naranja
    'cat_i': '#2ca02c',   # Verde
    'cat_ii': '#d62728',  # Rojo
    'dag': '#9467bd',     # Púrpura
    'merma': '#8c564b'    # Marrón
}

# ================================================================
# CLASE PRINCIPAL DEL CONTROLLER
# ================================================================

class KCTNProduccionController:
    """Controller para el dashboard de producción KCTN con datos reales."""
    
    def __init__(self, parsed_data: Dict[str, Any]):
        """
        Inicializa el controller con datos parseados.
        
        Args:
            parsed_data: Datos procesados por el parser
        """
        self.data = parsed_data
        self.resumen = parsed_data.get('data', {}).get('resumen', {})
        self.monthly = parsed_data.get('data', {}).get('monthly', {})
        self.kpis_base = parsed_data.get('data', {}).get('kpis', {})
        self.trends = parsed_data.get('data', {}).get('trends', {})
        
        # Estado del controller
        self.current_mode = 'individual'  # 'individual' o 'comparison'
        self.selected_month = None
        self.selected_months = []
        
    def set_filter_mode(self, mode: str, month: str = None, months: List[str] = None):
        """
        Configura el modo de filtrado.
        
        Args:
            mode: 'individual' o 'comparison'
            month: Mes seleccionado para modo individual
            months: Lista de meses para modo comparación
        """
        self.current_mode = mode
        if mode == 'individual' and month:
            self.selected_month = month
        elif mode == 'comparison' and months:
            self.selected_months = months
    
    def get_available_months(self) -> List[str]:
        """Obtiene lista de meses con datos disponibles."""
        meses_con_datos = []
        
        if self.resumen and 'datos_mensuales' in self.resumen:
            for mes_data in self.resumen['datos_mensuales']:
                if mes_data.get('mp', 0) > 0:
                    meses_con_datos.append(mes_data['mes'])
        
        return meses_con_datos
    
    def get_current_month_default(self) -> str:
        """Obtiene el mes actual como default."""
        mes_actual = datetime.now().month
        return MESES_MAPPING.get(mes_actual, 'Julio')
    
    # ================================================================
    # CÁLCULO DE KPIS DINÁMICOS CORREGIDOS
    # ================================================================
    
    def calculate_kpis_individual(self, mes: str) -> Dict[str, Any]:
        """Calcula KPIs para un mes individual según estructura real."""
        try:
            if not self.monthly or mes not in self.monthly:
                return self._get_empty_kpis()
            
            mes_data = self.monthly[mes]
            if not mes_data.get('has_data', False):
                return self._get_empty_kpis()
            
            agregados = mes_data.get('agregados', {})
            por_dia = mes_data.get('por_dia', {})
            por_hora = mes_data.get('por_hora', {})
            
            # DATOS REALES DEL EXCEL:
            # agregados['mp_total'] = Suma total de MP del mes
            # agregados['desgr_total'] = Suma total de desgranado del mes
            # agregados['cat_i_total'] = Suma total de Cat I del mes
            # agregados['pct_cat_i_avg'] = Promedio % Cat I del mes (ya en %)
            
            mp_total = agregados.get('mp_total', 0)
            desgr_total = agregados.get('desgr_total', 0)
            cat_i_total = agregados.get('cat_i_total', 0)
            cat_ii_total = agregados.get('cat_ii_total', 0)
            dag_total = agregados.get('dag_total', 0)
            
            # Calcular merma total (MP - CAT I - CAT II - DAG)
            merma_total = mp_total - cat_i_total - cat_ii_total - dag_total
            
            # KPIs según instrucciones exactas
            kpis = {
                # Card 1: Materia Prima Total
                'mp_total': mp_total,
                'mp_label': 'Materia Prima Total',
                'mp_unit': 'kg',
                
                # Card 2: Desgranado
                'desgr_total': desgr_total,
                'desgr_percentage': (desgr_total / mp_total * 100) if mp_total > 0 else 0,
                'desgr_label': 'Rendimiento Desgranado',
                'desgr_delta': self._get_delta_desgranado((desgr_total / mp_total) if mp_total > 0 else 0),
                
                # Card 3: CAT I
                'cat_i_total': cat_i_total,
                'cat_i_percentage': agregados.get('pct_cat_i_avg', 0),  # Ya está en %
                'cat_i_label': 'Categoría I',
                'cat_i_delta': self._get_delta_cat_i(agregados.get('pct_cat_i_avg', 0)),
                
                # Card 4: CAT II
                'cat_ii_total': cat_ii_total,
                'cat_ii_percentage': agregados.get('pct_cat_ii_avg', 0),  # Ya está en %
                'cat_ii_label': 'Categoría II',
                'cat_ii_delta': self._get_delta_cat_ii(agregados.get('pct_cat_ii_avg', 0)),
                
                # Card 5: DAG
                'dag_total': dag_total,
                'dag_percentage': agregados.get('pct_dag_avg', 0),  # Ya está en %
                'dag_label': 'DAG',
                'dag_delta': self._get_delta_dag(agregados.get('pct_dag_avg', 0)),
                
                # Card 6: Merma
                'merma_total': merma_total,
                'merma_percentage': (100 - (agregados.get('pct_cat_i_avg', 0) + agregados.get('pct_cat_ii_avg', 0) + agregados.get('pct_dag_avg', 0))),
                'merma_label': 'Merma',
                'merma_delta': self._get_delta_merma((100 - (agregados.get('pct_cat_i_avg', 0) + agregados.get('pct_cat_ii_avg', 0) + agregados.get('pct_dag_avg', 0)))),
                
                # Card 7: Productividad Personal (DESGR / PAX promedio)
                'productividad_personal': (desgr_total / agregados.get('pax_promedio', 1)) if agregados.get('pax_promedio', 0) > 0 else 0,
                'productividad_label': 'Productividad por Trabajador',
                'productividad_unit': 'kg/persona',
                
                # Card 8: Promedio Diario
                'promedio_diario': {
                    'mp': por_dia.get('mp_por_dia', 0),
                    'desgr': por_dia.get('desgr_por_dia', 0),
                    'cat_i': por_dia.get('cat_i_por_dia', 0),
                    'cat_ii': por_dia.get('cat_ii_por_dia', 0),
                    'dag': por_dia.get('dag_por_dia', 0)
                },
                
                # Card 9: Promedio por Hora
                'promedio_hora': {
                    'mp': por_hora.get('mp_por_hora', 0),
                    'desgr': por_hora.get('desgr_por_hora', 0),
                    'cat_i': por_hora.get('cat_i_por_hora', 0),
                    'cat_ii': por_hora.get('cat_ii_por_hora', 0),
                    'dag': por_hora.get('dag_por_hora', 0)
                },
                
                # Metadata
                'mes': mes,
                'dias_trabajados': agregados.get('dias_trabajados', 0),
                'pax_promedio': agregados.get('pax_promedio', 0)
            }
            
            return kpis
            
        except Exception as e:
            st.error(f"Error calculando KPIs para {mes}: {e}")
            return self._get_empty_kpis()
    
    def calculate_kpis_comparison(self, meses: List[str]) -> Dict[str, Any]:
        """Calcula KPIs para comparación multi-mes según estructura real."""
        try:
            if not meses:
                return self._get_empty_kpis()
            
            # Agregar datos de múltiples meses
            totales = {
                'mp_total': 0,
                'desgr_total': 0,
                'cat_i_total': 0,
                'cat_ii_total': 0,
                'dag_total': 0,
                'dias_total': 0,
                'pax_total': 0
            }
            
            porcentajes_list = {
                'desgr_pct': [],
                'cat_i_pct': [],
                'cat_ii_pct': [],
                'dag_pct': []
            }
            
            meses_validos = 0
            
            for mes in meses:
                if mes in self.monthly and self.monthly[mes].get('has_data', False):
                    agregados = self.monthly[mes]['agregados']
                    
                    mp_total = agregados.get('mp_total', 0)
                    totales['mp_total'] += mp_total
                    totales['desgr_total'] += agregados.get('desgr_total', 0)
                    totales['cat_i_total'] += agregados.get('cat_i_total', 0)
                    totales['cat_ii_total'] += agregados.get('cat_ii_total', 0)
                    totales['dag_total'] += agregados.get('dag_total', 0)
                    totales['dias_total'] += agregados.get('dias_trabajados', 0)
                    totales['pax_total'] += agregados.get('pax_promedio', 0)
                    
                    # Porcentajes para promedio (usar los datos reales del Excel)
                    if mp_total > 0:
                        porcentajes_list['desgr_pct'].append((agregados.get('desgr_total', 0) / mp_total) * 100)
                    porcentajes_list['cat_i_pct'].append(agregados.get('pct_cat_i_avg', 0))
                    porcentajes_list['cat_ii_pct'].append(agregados.get('pct_cat_ii_avg', 0))
                    porcentajes_list['dag_pct'].append(agregados.get('pct_dag_avg', 0))
                    
                    meses_validos += 1
            
            if meses_validos == 0:
                return self._get_empty_kpis()
            
            # Calcular promedios y totales
            merma_total = totales['mp_total'] - totales['cat_i_total'] - totales['cat_ii_total'] - totales['dag_total']
            pax_promedio = totales['pax_total'] / meses_validos
            
            kpis = {
                # Totales agregados
                'mp_total': totales['mp_total'],
                'desgr_total': totales['desgr_total'],
                'desgr_percentage': np.mean(porcentajes_list['desgr_pct']) if porcentajes_list['desgr_pct'] else 0,
                
                'cat_i_total': totales['cat_i_total'],
                'cat_i_percentage': np.mean(porcentajes_list['cat_i_pct']) if porcentajes_list['cat_i_pct'] else 0,
                
                'cat_ii_total': totales['cat_ii_total'],
                'cat_ii_percentage': np.mean(porcentajes_list['cat_ii_pct']) if porcentajes_list['cat_ii_pct'] else 0,
                
                'dag_total': totales['dag_total'],
                'dag_percentage': np.mean(porcentajes_list['dag_pct']) if porcentajes_list['dag_pct'] else 0,
                
                'merma_total': merma_total,
                'merma_percentage': (merma_total / totales['mp_total'] * 100) if totales['mp_total'] > 0 else 0,
                
                'productividad_personal': (totales['desgr_total'] / pax_promedio) if pax_promedio > 0 else 0,
                
                # Promedios diarios agregados
                'promedio_diario': {
                    'mp': totales['mp_total'] / totales['dias_total'] if totales['dias_total'] > 0 else 0,
                    'desgr': totales['desgr_total'] / totales['dias_total'] if totales['dias_total'] > 0 else 0,
                    'cat_i': totales['cat_i_total'] / totales['dias_total'] if totales['dias_total'] > 0 else 0,
                    'cat_ii': totales['cat_ii_total'] / totales['dias_total'] if totales['dias_total'] > 0 else 0,
                    'dag': totales['dag_total'] / totales['dias_total'] if totales['dias_total'] > 0 else 0
                },
                
                'promedio_hora': {
                    'mp': (totales['mp_total'] / totales['dias_total'] / 6) if totales['dias_total'] > 0 else 0,
                    'desgr': (totales['desgr_total'] / totales['dias_total'] / 6) if totales['dias_total'] > 0 else 0,
                    'cat_i': (totales['cat_i_total'] / totales['dias_total'] / 6) if totales['dias_total'] > 0 else 0,
                    'cat_ii': (totales['cat_ii_total'] / totales['dias_total'] / 6) if totales['dias_total'] > 0 else 0,
                    'dag': (totales['dag_total'] / totales['dias_total'] / 6) if totales['dias_total'] > 0 else 0
                },
                
                # Metadata
                'meses': meses,
                'meses_validos': meses_validos,
                'dias_total': totales['dias_total'],
                'pax_promedio': pax_promedio
            }
            
            # Añadir deltas
            kpis['desgr_delta'] = self._get_delta_desgranado(kpis['desgr_percentage'] / 100)
            kpis['cat_i_delta'] = self._get_delta_cat_i(kpis['cat_i_percentage'])
            kpis['cat_ii_delta'] = self._get_delta_cat_ii(kpis['cat_ii_percentage'])
            kpis['dag_delta'] = self._get_delta_dag(kpis['dag_percentage'])
            kpis['merma_delta'] = self._get_delta_merma(kpis['merma_percentage'])
            
            # Labels
            kpis.update({
                'mp_label': 'Materia Prima Total',
                'desgr_label': 'Rendimiento Desgranado',
                'cat_i_label': 'Categoría I',
                'cat_ii_label': 'Categoría II',
                'dag_label': 'DAG',
                'merma_label': 'Merma',
                'productividad_label': 'Productividad por Trabajador'
            })
            
            return kpis
            
        except Exception as e:
            st.error(f"Error calculando KPIs multi-mes: {e}")
            return self._get_empty_kpis()
    
    # ================================================================
    # FUNCIONES DE DELTA/CALIDAD (SEGÚN INSTRUCCIONES)
    # ================================================================
    
    def _get_delta_desgranado(self, ratio: float) -> str:
        """Delta para rendimiento de desgranado."""
        if ratio > 0.90:
            return "Excelente"
        elif ratio > 0.85:
            return "Bueno"
        else:
            return "Regular"
    
    def _get_delta_cat_i(self, percentage: float) -> str:
        """Delta para Categoría I (Óptimo > 50%)."""
        return "Óptimo" if percentage > 50 else "Regular"
    
    def _get_delta_cat_ii(self, percentage: float) -> str:
        """Delta para Categoría II (Óptimo < 25%)."""
        return "Óptimo" if percentage < 25 else "Regular"
    
    def _get_delta_dag(self, percentage: float) -> str:
        """Delta para DAG (Óptimo < 20%)."""
        return "Óptimo" if percentage < 20 else "Regular"
    
    def _get_delta_merma(self, percentage: float) -> str:
        """Delta para Merma (Óptimo < 10%)."""
        if percentage < 10:
            return "Óptimo"
        elif percentage < 15:
            return "Regular"
        else:
            return "Atención"
    
    def _get_empty_kpis(self) -> Dict[str, Any]:
        """KPIs vacíos para casos de error."""
        return {
            'mp_total': 0, 'desgr_total': 0, 'desgr_percentage': 0,
            'cat_i_total': 0, 'cat_i_percentage': 0,
            'cat_ii_total': 0, 'cat_ii_percentage': 0,
            'dag_total': 0, 'dag_percentage': 0,
            'merma_total': 0, 'merma_percentage': 0,
            'productividad_personal': 0,
            'promedio_diario': {'mp': 0, 'desgr': 0, 'cat_i': 0, 'cat_ii': 0, 'dag': 0},
            'promedio_hora': {'mp': 0, 'desgr': 0, 'cat_i': 0, 'cat_ii': 0, 'dag': 0}
        }
    
    # ================================================================
    # PREPARACIÓN DE DATOS PARA GRÁFICOS
    # ================================================================
    
    def get_line_chart_data(self, mes: str = None, meses: List[str] = None) -> Dict[str, Any]:
        """Prepara datos para gráfico de líneas."""
        try:
            if mes:
                # Gráfico diario para un mes
                return self._get_daily_line_data(mes)
            elif meses:
                # Gráfico multi-día para varios meses
                return self._get_multi_month_line_data(meses)
            else:
                return {'error': 'No hay datos para gráfico de líneas'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_daily_line_data(self, mes: str) -> Dict[str, Any]:
        """Datos de líneas para un mes específico."""
        if mes not in self.monthly or not self.monthly[mes].get('has_data', False):
            return {'error': f'No hay datos para {mes}'}
        
        datos_diarios = self.monthly[mes].get('datos_diarios', [])
        
        if not datos_diarios:
            return {'error': f'No hay datos diarios para {mes}'}
        
        # Preparar datos para Plotly
        fechas = [d['fecha'] for d in datos_diarios]
        
        data = {
            'fechas': fechas,
            'MP': [d['mp'] for d in datos_diarios],
            'DESGR': [d['desgr'] for d in datos_diarios],
            'CAT I': [d['cat_i'] for d in datos_diarios],
            'CAT II': [d['cat_ii'] for d in datos_diarios],
            'DAG': [d['dag'] for d in datos_diarios],
        }
        
        return {
            'data': data,
            'title': f'Producción Diaria - {mes} 2025',
            'xaxis_title': 'Días',
            'yaxis_title': 'Kilogramos (kg)',
            'mes': mes
        }
    
    def _get_multi_month_line_data(self, meses: List[str]) -> Dict[str, Any]:
        """Datos de líneas para múltiples meses."""
        all_data = []
        
        for mes in meses:
            if mes in self.monthly and self.monthly[mes].get('has_data', False):
                datos_diarios = self.monthly[mes].get('datos_diarios', [])
                for d in datos_diarios:
                    all_data.append({
                        'fecha': d['fecha'],
                        'mes': mes,
                        'mp': d['mp'],
                        'desgr': d['desgr'],
                        'cat_i': d['cat_i'],
                        'cat_ii': d['cat_ii'],
                        'dag': d['dag']
                    })
        
        if not all_data:
            return {'error': 'No hay datos para los meses seleccionados'}
        
        # Ordenar por fecha
        all_data.sort(key=lambda x: x['fecha'])
        
        data = {
            'fechas': [d['fecha'] for d in all_data],
            'MP': [d['mp'] for d in all_data],
            'DESGR': [d['desgr'] for d in all_data],
            'CAT I': [d['cat_i'] for d in all_data],
            'CAT II': [d['cat_ii'] for d in all_data],
            'DAG': [d['dag'] for d in all_data],
        }
        
        return {
            'data': data,
            'title': f'Producción Multi-Mes: {", ".join(meses)}',
            'xaxis_title': 'Días',
            'yaxis_title': 'Kilogramos (kg)',
            'meses': meses
        }
    
    def get_stacked_bar_data(self, mes: str = None, meses: List[str] = None) -> Dict[str, Any]:
        """Prepara datos para gráfico de barras apiladas."""
        try:
            if mes:
                return self._get_daily_stacked_data(mes)
            elif meses:
                return self._get_monthly_stacked_data(meses)
            else:
                return {'error': 'No hay datos para gráfico de barras'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_daily_stacked_data(self, mes: str) -> Dict[str, Any]:
        """Datos de barras apiladas por días."""
        if mes not in self.monthly or not self.monthly[mes].get('has_data', False):
            return {'error': f'No hay datos para {mes}'}
        
        datos_diarios = self.monthly[mes].get('datos_diarios', [])
        
        if not datos_diarios:
            return {'error': f'No hay datos diarios para {mes}'}
        
        # Calcular merma para cada día
        data = []
        for d in datos_diarios:
            merma = d.get('merma', d['mp'] - d['cat_i'] - d['cat_ii'] - d['dag'])
            data.append({
                'fecha': d['fecha'],
                'CAT I': d['cat_i'],
                'CAT II': d['cat_ii'],
                'DAG': d['dag'],
                'MERMA': merma
            })
        
        return {
            'data': data,
            'title': f'Composición Diaria - {mes} 2025',
            'xaxis_title': 'Días',
            'yaxis_title': 'Kilogramos (kg)',
            'type': 'daily'
        }
    
    def _get_monthly_stacked_data(self, meses: List[str]) -> Dict[str, Any]:
        """Datos de barras apiladas por meses."""
        data = []
        
        for mes in meses:
            if mes in self.monthly and self.monthly[mes].get('has_data', False):
                agregados = self.monthly[mes]['agregados']
                
                mp_total = agregados.get('mp_total', 0)
                cat_i = agregados.get('cat_i_total', 0)
                cat_ii = agregados.get('cat_ii_total', 0)
                dag = agregados.get('dag_total', 0)
                merma = mp_total - cat_i - cat_ii - dag
                
                data.append({
                    'mes': mes,
                    'CAT I': cat_i,
                    'CAT II': cat_ii,
                    'DAG': dag,
                    'MERMA': merma
                })
        
        return {
            'data': data,
            'title': f'Composición Mensual: {", ".join(meses)}',
            'xaxis_title': 'Meses',
            'yaxis_title': 'Kilogramos (kg)',
            'type': 'monthly'
        }
    
    # ================================================================
    # TABLAS DE RESUMEN
    # ================================================================
    
    def get_summary_table(self, mes: str = None, meses: List[str] = None) -> Dict[str, Any]:
        """Prepara datos para tabla de resumen."""
        try:
            if mes:
                return self._get_monthly_summary_table(mes)
            elif meses:
                return self._get_comparative_summary_table(meses)
            else:
                return {'error': 'No hay datos para tabla'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_monthly_summary_table(self, mes: str) -> Dict[str, Any]:
        """Tabla de resumen mensual."""
        if mes not in self.monthly or not self.monthly[mes].get('has_data', False):
            return {'error': f'No hay datos para {mes}'}
        
        agregados = self.monthly[mes]['agregados']
        por_dia = self.monthly[mes].get('por_dia', {})
        por_hora = self.monthly[mes].get('por_hora', {})
        
        # Construir tabla (invertir orden fila 4 y 5 como solicitado)
        table_data = [
            {
                'Métrica': 'Días Trabajados',
                'Total Mes': f"{agregados.get('dias_trabajados', 0):.0f} días",
                'Promedio Diario': '-',
                'Promedio por Hora': '-'
            },
            {
                'Métrica': 'Materia Prima (MP)',
                'Total Mes': f"{agregados.get('mp_total', 0):,.0f} kg",
                'Promedio Diario': f"{por_dia.get('mp_por_dia', 0):,.0f} kg",
                'Promedio por Hora': f"{por_hora.get('mp_por_hora', 0):,.0f} kg"
            },
            {
                'Métrica': 'Desgranado (DESGR)',
                'Total Mes': f"{agregados.get('desgr_total', 0):,.0f} kg",
                'Promedio Diario': f"{por_dia.get('desgr_por_dia', 0):,.0f} kg",
                'Promedio por Hora': f"{por_hora.get('desgr_por_hora', 0):,.0f} kg"
            },
            {
                'Métrica': 'Categoría I',
                'Total Mes': f"{agregados.get('cat_i_total', 0):,.0f} kg",
                'Promedio Diario': f"{por_dia.get('cat_i_por_dia', 0):,.0f} kg",
                'Promedio por Hora': f"{por_hora.get('cat_i_por_hora', 0):,.0f} kg"
            },
            {
                'Métrica': 'Categoría II',
                'Total Mes': f"{agregados.get('cat_ii_total', 0):,.0f} kg",
                'Promedio Diario': f"{por_dia.get('cat_ii_por_dia', 0):,.0f} kg",
                'Promedio por Hora': f"{por_hora.get('cat_ii_por_hora', 0):,.0f} kg"
            },
            {
                'Métrica': 'DAG',
                'Total Mes': f"{agregados.get('dag_total', 0):,.0f} kg",
                'Promedio Diario': f"{por_dia.get('dag_por_dia', 0):,.0f} kg",
                'Promedio por Hora': f"{por_hora.get('dag_por_hora', 0):,.0f} kg"
            },
            {
                'Métrica': 'Personal Promedio',
                'Total Mes': f"{agregados.get('pax_promedio', 0):.1f} personas",
                'Promedio Diario': f"{agregados.get('pax_promedio', 0):.1f} personas",
                'Promedio por Hora': '-'
            }
        ]
        
        return {
            'data': table_data,
            'title': f'Resumen de Producción - {mes} 2025',
            'type': 'monthly'
        }
    
    def _get_comparative_summary_table(self, meses: List[str]) -> Dict[str, Any]:
        """Tabla comparativa multi-mes."""
        table_data = []
        
        for mes in meses:
            if mes in self.monthly and self.monthly[mes].get('has_data', False):
                agregados = self.monthly[mes]['agregados']
                
                mp_total = agregados.get('mp_total', 0)
                merma = mp_total - agregados.get('cat_i_total', 0) - agregados.get('cat_ii_total', 0) - agregados.get('dag_total', 0)
                
                table_data.append({
                    'Mes': mes,
                    'MP Total (kg)': f"{mp_total:,.0f}",
                    'Desgranado (kg)': f"{agregados.get('desgr_total', 0):,.0f}",
                    'Cat I (%)': f"{agregados.get('pct_cat_i_avg', 0):.1f}%",
                    'Cat II (%)': f"{agregados.get('pct_cat_ii_avg', 0):.1f}%",
                    'DAG (%)': f"{agregados.get('pct_dag_avg', 0):.1f}%",
                    'Merma (kg)': f"{merma:,.0f}",
                    'Días': f"{agregados.get('dias_trabajados', 0):.0f}",
                    'Personal': f"{agregados.get('pax_promedio', 0):.1f}"
                })
        
        return {
            'data': table_data,
            'title': f'Comparativa Multi-Mes: {", ".join(meses)}',
            'type': 'comparative'
        }

# ================================================================
# FUNCIONES EXPORTADAS
# ================================================================

def create_controller(parsed_data: Dict[str, Any]) -> KCTNProduccionController:
    """Crea una instancia del controller."""
    return KCTNProduccionController(parsed_data)

def get_months_list() -> List[str]:
    """Obtiene lista de meses."""
    return MESES_NOMBRES.copy()

def get_colors_dict() -> Dict[str, str]:
    """Obtiene diccionario de colores."""
    return COLORS.copy()

# Exportaciones
__all__ = [
    'KCTNProduccionController',
    'create_controller',
    'get_months_list',
    'get_colors_dict',
    'MESES_NOMBRES',
    'COLORS'
]
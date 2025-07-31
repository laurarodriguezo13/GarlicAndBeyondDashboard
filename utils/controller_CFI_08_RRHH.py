"""
Controller CFI_08_RRHH.py - Controlador de Recursos Humanos CFI CORREGIDO
=========================================================================
Controlador que maneja toda la lógica de negocio para el dashboard
de Recursos Humanos CFI, incluyendo KPIs, análisis y generación de gráficas.

Funcionalidades:
- KPIs por mes individual y comparativos
- Análisis de costes por departamento
- Seguimiento de aportaciones a la seguridad social
- Análisis detallado de bajas y altas
- Generación de gráficas interactivas con Plotly

CORRECCIONES APLICADAS:
- Eliminada alerta de "datos incompletos"
- Filtros incluyen todos los 12 meses
- Títulos de gráficas corregidos

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0 (Corregida)
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import streamlit as st

class CFIRRHHController:
    """
    Controlador principal para el dashboard de RRHH CFI.
    """
    
    def __init__(self):
        """Inicializa el controlador."""
        self.data = None
        self.costes_df = pd.DataFrame()
        self.observaciones_df = pd.DataFrame()
        self.resumen_mensual = {}
        self.departamentos = []
        self.meses_disponibles = []
        self.initialized = False
        
    def initialize_with_data(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Inicializa el controlador con datos parseados.
        
        Args:
            parsed_data: Datos parseados del Excel
            
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            if parsed_data.get('status') != 'success':
                st.error(f"Error en datos: {parsed_data.get('message', 'Desconocido')}")
                return False
            
            self.data = parsed_data['data']
            self.costes_df = self.data['costes_personal']
            self.observaciones_df = self.data['bajas_observaciones']
            self.resumen_mensual = self.data['resumen_mensual']
            self.departamentos = self.data['departamentos']
            self.meses_disponibles = self.data['meses_disponibles']
            
            self.initialized = True
            
            print(f"✅ Controlador CFI RRHH inicializado:")
            print(f"   - {len(self.costes_df)} registros de costes")
            print(f"   - {len(self.observaciones_df)} observaciones")
            print(f"   - {len(self.departamentos)} departamentos")
            print(f"   - {len(self.meses_disponibles)} meses")
            
            return True
            
        except Exception as e:
            st.error(f"Error inicializando controlador: {e}")
            return False
    
    @property
    def is_initialized(self) -> bool:
        """Verifica si el controlador está inicializado."""
        return self.initialized and not self.costes_df.empty
    
    def get_available_months(self) -> List[str]:
        """Obtiene lista completa de meses disponibles para análisis (CORREGIDO)."""
        # SIEMPRE devolver todos los 12 meses, independientemente de si hay datos o no
        return ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    def get_months_with_data(self) -> List[str]:
        """Obtiene solo los meses que tienen datos."""
        if not self.is_initialized:
            return []
        return [mes for mes in self.meses_disponibles if mes in self.costes_df['mes'].unique()]
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema."""
        if not self.is_initialized:
            return {
                'initialized': False,
                'months_with_data': 0,
                'months_empty': 12,
                'total_employees_latest': 0,
                'total_cost_latest': 0,
                'alerts_count': 0,
                'last_update': 'No inicializado'
            }
        
        months_with_data = len(self.get_months_with_data())
        months_empty = 12 - months_with_data
        
        # Datos del último mes disponible
        latest_month = self.get_months_with_data()[-1] if self.get_months_with_data() else 'enero'
        latest_data = self.costes_df[self.costes_df['mes'] == latest_month]
        
        return {
            'initialized': True,
            'months_with_data': months_with_data,
            'months_empty': months_empty,
            'total_employees_latest': len(latest_data),
            'total_cost_latest': latest_data['coste_total'].sum(),
            'alerts_count': self._count_alerts(),
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
    
    def get_alerts(self) -> List[Dict[str, str]]:
        """Genera alertas basadas en el análisis de datos (CORREGIDO)."""
        if not self.is_initialized:
            return []
        
        alerts = []
        
        # ELIMINADA: Alerta de meses sin datos - no es necesaria
        # Es normal tener meses vacíos hasta que se añadan datos
        
        # Verificar si hay empleados con costes muy altos (esta sí es útil)
        if not self.costes_df.empty:
            coste_promedio = self.costes_df['coste_total'].mean()
            empleados_altos = self.costes_df[self.costes_df['coste_total'] > coste_promedio * 2]
            
            if not empleados_altos.empty:
                alerts.append({
                    'type': 'info',
                    'title': '💰 Costes Elevados',
                    'message': f'{len(empleados_altos)} empleados con costes superiores al doble del promedio. Revisar casos específicos.'
                })
        
        return alerts
    
    def _count_alerts(self) -> int:
        """Cuenta el número total de alertas."""
        return len(self.get_alerts())
    
    # ================================================================
    # KPIs PARA MES INDIVIDUAL
    # ================================================================
    
    def get_monthly_kpis(self, month: str) -> Dict[str, Any]:
        """
        Calcula KPIs para un mes específico.
        
        Args:
            month: Nombre del mes a analizar
            
        Returns:
            Dict con todos los KPIs del mes
        """
        if not self.is_initialized:
            return self._empty_monthly_kpis()
        
        month_data = self.costes_df[self.costes_df['mes'] == month]
        
        if month_data.empty:
            return self._empty_monthly_kpis()
        
        # KPIs básicos
        total_empleados = len(month_data)
        total_gasto_personal = month_data['coste_total'].sum()
        total_devengado = month_data['devengado'].sum()
        total_liquido = month_data['liquido'].sum()
        total_deducciones = month_data['deducciones'].sum()
        total_ss_empresa = month_data['ss_empresa'].sum()
        total_ss_trabajador = month_data['ss_trabajador'].sum()
        total_irpf = month_data['irpf'].sum()
        
        # Análisis por departamento
        dept_analysis = month_data.groupby('departamento').agg({
            'coste_total': 'sum',
            'nombre': 'count',
            'ss_empresa': 'sum',
            'ss_trabajador': 'sum',
            'deducciones': 'sum',
            'devengado': 'sum'
        }).round(2)
        
        dept_analysis.columns = ['coste_total', 'cantidad_empleados', 'ss_empresa', 'ss_trabajador', 'deducciones', 'devengado']
        dept_analysis = dept_analysis.reset_index()
        
        return {
            'has_data': True,
            'mes': month,
            'total_empleados': total_empleados,
            'total_gasto_personal': total_gasto_personal,
            'total_devengado': total_devengado,
            'total_liquido': total_liquido,
            'total_deducciones': total_deducciones,
            'total_ss_empresa': total_ss_empresa,
            'total_ss_trabajador': total_ss_trabajador,
            'total_irpf': total_irpf,
            'promedio_coste_empleado': total_gasto_personal / total_empleados if total_empleados > 0 else 0,
            'promedio_devengado_empleado': total_devengado / total_empleados if total_empleados > 0 else 0,
            'departamentos_activos': len(month_data['departamento'].unique()),
            'analisis_departamentos': dept_analysis.to_dict('records')
        }
    
    def _empty_monthly_kpis(self) -> Dict[str, Any]:
        """Retorna KPIs vacíos para meses sin datos."""
        return {
            'has_data': False,
            'mes': '',
            'total_empleados': 0,
            'total_gasto_personal': 0,
            'total_devengado': 0,
            'total_liquido': 0,
            'total_deducciones': 0,
            'total_ss_empresa': 0,
            'total_ss_trabajador': 0,
            'total_irpf': 0,
            'promedio_coste_empleado': 0,
            'promedio_devengado_empleado': 0,
            'departamentos_activos': 0,
            'analisis_departamentos': []
        }
    
    # ================================================================
    # KPIs COMPARATIVOS MULTI-MES
    # ================================================================
    
    def create_multi_month_kpi_table(self, selected_months: List[str]) -> pd.DataFrame:
        """
        Crea tabla comparativa de KPIs para múltiples meses.
        
        Args:
            selected_months: Lista de meses a comparar
            
        Returns:
            DataFrame con KPIs comparativos
        """
        if not self.is_initialized or not selected_months:
            return pd.DataFrame()
        
        comparison_data = []
        
        for month in selected_months:
            kpis = self.get_monthly_kpis(month)
            
            if kpis['has_data']:
                comparison_data.append({
                    'Mes': month.title(),
                    'Empleados': kpis['total_empleados'],
                    'Gasto Total (€)': f"{kpis['total_gasto_personal']:,.0f}",
                    'Devengado (€)': f"{kpis['total_devengado']:,.0f}",
                    'Líquido (€)': f"{kpis['total_liquido']:,.0f}",
                    'Deducciones (€)': f"{kpis['total_deducciones']:,.0f}",
                    'SS Empresa (€)': f"{kpis['total_ss_empresa']:,.0f}",
                    'SS Trabajador (€)': f"{kpis['total_ss_trabajador']:,.0f}",
                    'IRPF (€)': f"{kpis['total_irpf']:,.0f}",
                    'Promedio/Empleado (€)': f"{kpis['promedio_coste_empleado']:,.0f}",
                    'Departamentos': kpis['departamentos_activos']
                })
            else:
                comparison_data.append({
                    'Mes': month.title(),
                    'Empleados': 0,
                    'Gasto Total (€)': "0",
                    'Devengado (€)': "0",
                    'Líquido (€)': "0",
                    'Deducciones (€)': "0",
                    'SS Empresa (€)': "0",
                    'SS Trabajador (€)': "0",
                    'IRPF (€)': "0",
                    'Promedio/Empleado (€)': "0",
                    'Departamentos': 0
                })
        
        return pd.DataFrame(comparison_data)
    
    def calculate_month_changes(self, selected_months: List[str]) -> Dict[str, Any]:
        """Calcula cambios porcentuales entre meses."""
        if not self.is_initialized or len(selected_months) < 2:
            return {}
        
        first_month = selected_months[0]
        last_month = selected_months[-1]
        
        first_kpis = self.get_monthly_kpis(first_month)
        last_kpis = self.get_monthly_kpis(last_month)
        
        if not first_kpis['has_data'] or not last_kpis['has_data']:
            return {}
        
        def calculate_change(old_val, new_val):
            if old_val == 0:
                return 0 if new_val == 0 else 100
            return ((new_val - old_val) / old_val) * 100
        
        return {
            'empleados_change': calculate_change(first_kpis['total_empleados'], last_kpis['total_empleados']),
            'coste_total_change': calculate_change(first_kpis['total_gasto_personal'], last_kpis['total_gasto_personal']),
            'ss_empresa_change': calculate_change(first_kpis['total_ss_empresa'], last_kpis['total_ss_empresa']),
            'ss_trabajador_change': calculate_change(first_kpis['total_ss_trabajador'], last_kpis['total_ss_trabajador']),
            'first_month': first_month,
            'last_month': last_month
        }
    
    # ================================================================
    # ANÁLISIS DE BAJAS
    # ================================================================
    
    def get_analisis_bajas_data(self, month: str) -> Dict[str, Any]:
        """
        Analiza información de bajas para un mes específico.
        
        Args:
            month: Mes a analizar
            
        Returns:
            Dict con análisis de bajas
        """
        if not self.is_initialized:
            return {
                'mes': month,
                'empleados_baja': [],
                'cantidad_bajas': 0,
                'coste_total_bajas': 0,
                'porcentaje_coste_bajas': 0
            }
        
        # Buscar observaciones de bajas en el mes
        bajas_mes = self.observaciones_df[
            (self.observaciones_df['mes'] == month) & 
            (self.observaciones_df['tipo_movimiento'] == 'baja')
        ]
        
        empleados_baja = []
        coste_total_bajas = 0
        
        # Para cada baja, buscar en datos de costes
        for _, baja in bajas_mes.iterrows():
            nombre_baja = baja['nombre_empleado'].strip()
            
            # Buscar empleado en datos de costes
            empleado_data = self.costes_df[
                (self.costes_df['mes'] == month) & 
                (self.costes_df['nombre'].str.contains(nombre_baja.split()[0], case=False, na=False))
            ]
            
            if not empleado_data.empty:
                empleado = empleado_data.iloc[0]
                coste_empleado = empleado['coste_total']
                coste_total_bajas += coste_empleado
                
                empleados_baja.append({
                    'nombre': empleado['nombre'],
                    'departamento': empleado['departamento'],
                    'coste': coste_empleado,
                    'motivo': baja['motivo']
                })
        
        # Calcular porcentajes
        kpis_mes = self.get_monthly_kpis(month)
        total_coste_mes = kpis_mes.get('total_gasto_personal', 0)
        
        porcentaje_coste_bajas = (coste_total_bajas / total_coste_mes * 100) if total_coste_mes > 0 else 0
        
        # Agregar porcentaje individual a cada empleado
        for empleado in empleados_baja:
            empleado['porcentaje_coste'] = (empleado['coste'] / total_coste_mes * 100) if total_coste_mes > 0 else 0
        
        return {
            'mes': month,
            'empleados_baja': empleados_baja,
            'cantidad_bajas': len(empleados_baja),
            'coste_total_bajas': coste_total_bajas,
            'porcentaje_coste_bajas': porcentaje_coste_bajas
        }
    
    def get_bajas_summary_all_months(self) -> pd.DataFrame:
        """
        Obtiene resumen de bajas para todos los meses con análisis de estado.
        
        Returns:
            DataFrame con resumen de bajas y altas
        """
        if not self.is_initialized or self.observaciones_df.empty:
            return pd.DataFrame()
        
        # Análizar movimientos por empleado
        empleados_movimientos = {}
        
        for _, obs in self.observaciones_df.iterrows():
            nombre = obs['nombre_empleado'].strip()
            mes = obs['mes']
            tipo = obs['tipo_movimiento']
            fecha = obs['fecha']
            motivo = obs['motivo']
            
            if nombre not in empleados_movimientos:
                empleados_movimientos[nombre] = []
            
            empleados_movimientos[nombre].append({
                'mes': mes,
                'fecha': fecha,
                'tipo': tipo,
                'motivo': motivo,
                'mes_num': self._month_to_number(mes)
            })
        
        # Determinar estado actual de cada empleado
        summary_data = []
        
        for nombre, movimientos in empleados_movimientos.items():
            # Ordenar por mes
            movimientos_ordenados = sorted(movimientos, key=lambda x: x['mes_num'])
            
            # Determinar estado actual (último movimiento)
            ultimo_movimiento = movimientos_ordenados[-1]
            estado_actual = "ACTIVO" if ultimo_movimiento['tipo'] == 'alta' else "DE BAJA"
            
            # Contar movimientos
            total_bajas = sum(1 for m in movimientos if m['tipo'] == 'baja')
            total_altas = sum(1 for m in movimientos if m['tipo'] == 'alta')
            
            # Información del último movimiento
            summary_data.append({
                'Empleado': nombre,
                'Estado Actual': estado_actual,
                'Total Bajas': total_bajas,
                'Total Altas': total_altas,
                'Último Movimiento': f"{ultimo_movimiento['tipo'].title()} en {ultimo_movimiento['mes'].title()}",
                'Fecha Último': ultimo_movimiento['fecha'],
                'Motivo Último': ultimo_movimiento['motivo']
            })
        
        return pd.DataFrame(summary_data)
    
    def _month_to_number(self, month: str) -> int:
        """Convierte nombre de mes a número para ordenamiento."""
        month_map = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        return month_map.get(month.lower(), 0)
    
    # ================================================================
    # GENERACIÓN DE GRÁFICAS (TÍTULOS CORREGIDOS)
    # ================================================================
    
    def create_costes_por_departamento_chart(self, month: str) -> go.Figure:
        """Gráfica de barras: Coste total por departamento (mes individual)."""
        if not self.is_initialized:
            return self._empty_chart("Costes por Departamento - Sin Datos")
        
        month_data = self.costes_df[self.costes_df['mes'] == month]
        
        if month_data.empty:
            return self._empty_chart(f"Costes por Departamento - {month.title()} (Sin Datos)")
        
        dept_costes = month_data.groupby('departamento')['coste_total'].sum().reset_index()
        dept_costes = dept_costes.sort_values('coste_total', ascending=False)
        
        fig = px.bar(
            dept_costes,
            x='departamento',
            y='coste_total',
            title=f'💰 Coste Total por Departamento - {month.title()}',
            labels={'coste_total': 'Coste Total (€)', 'departamento': 'Departamento'},
            color='coste_total',
            color_continuous_scale='RdYlBu_r'
        )
        
        # Personalización
        fig.update_layout(
            font={'size': 12},
            title_font={'size': 16, 'color': '#2E7D32'},
            showlegend=False,
            height=400
        )
        
        fig.update_traces(
            texttemplate='€%{y:,.0f}',
            textposition='outside'
        )
        
        return fig
    
    def create_deducciones_por_departamento_chart(self, month: str) -> go.Figure:
        """Gráfica de barras: Deducciones por departamento (mes individual)."""
        if not self.is_initialized:
            return self._empty_chart("Deducciones por Departamento - Sin Datos")
        
        month_data = self.costes_df[self.costes_df['mes'] == month]
        
        if month_data.empty:
            return self._empty_chart(f"Deducciones por Departamento - {month.title()} (Sin Datos)")
        
        dept_deducciones = month_data.groupby('departamento')['deducciones'].sum().reset_index()
        dept_deducciones = dept_deducciones.sort_values('deducciones', ascending=False)
        
        fig = px.bar(
            dept_deducciones,
            x='departamento',
            y='deducciones',
            title=f'📊 Deducciones por Departamento - {month.title()}',
            labels={'deducciones': 'Deducciones (€)', 'departamento': 'Departamento'},
            color='deducciones',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            font={'size': 12},
            title_font={'size': 16, 'color': '#2E7D32'},
            showlegend=False,
            height=400
        )
        
        fig.update_traces(
            texttemplate='€%{y:,.0f}',
            textposition='outside'
        )
        
        return fig
    
    def create_aportaciones_ss_por_departamento_chart(self, month: str) -> go.Figure:
        """Gráfica de barras agrupadas: Aportaciones SS empresa/trabajador por departamento."""
        if not self.is_initialized:
            return self._empty_chart("Aportaciones SS por Departamento - Sin Datos")
        
        month_data = self.costes_df[self.costes_df['mes'] == month]
        
        if month_data.empty:
            return self._empty_chart(f"Aportaciones SS por Departamento - {month.title()} (Sin Datos)")
        
        dept_ss = month_data.groupby('departamento').agg({
            'ss_empresa': 'sum',
            'ss_trabajador': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        
        # Barras para SS Empresa
        fig.add_trace(go.Bar(
            name='SS Empresa',
            x=dept_ss['departamento'],
            y=dept_ss['ss_empresa'],
            marker_color='#2E7D32',
            text=[f'€{val:,.0f}' for val in dept_ss['ss_empresa']],
            textposition='outside'
        ))
        
        # Barras para SS Trabajador
        fig.add_trace(go.Bar(
            name='SS Trabajador',
            x=dept_ss['departamento'],
            y=dept_ss['ss_trabajador'],
            marker_color='#4CAF50',
            text=[f'€{val:,.0f}' for val in dept_ss['ss_trabajador']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=f'🏥 Aportaciones Seguridad Social por Departamento - {month.title()}',
            xaxis_title='Departamento',
            yaxis_title='Valor de Aportación (€)',
            barmode='group',
            font={'size': 12},
            title_font={'size': 16, 'color': '#2E7D32'},
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        return fig
    
    def create_evolucion_costes_chart(self, selected_months: List[str]) -> go.Figure:
        """Gráfica de líneas: Evolución de costes totales por mes."""
        if not self.is_initialized or not selected_months:
            return self._empty_chart("Evolución de Costes - Sin Datos")
        
        evolution_data = []
        
        for month in selected_months:
            kpis = self.get_monthly_kpis(month)
            if kpis['has_data']:
                evolution_data.append({
                    'mes': month.title(),
                    'coste_total': kpis['total_gasto_personal'],
                    'coste_dia': kpis['total_gasto_personal'] / 30,  # Aproximación
                    'coste_hora': kpis['total_gasto_personal'] / (30 * 8)  # Aproximación 8h/día
                })
        
        if not evolution_data:
            return self._empty_chart("Evolución de Costes - Sin Datos para Meses Seleccionados")
        
        df_evolution = pd.DataFrame(evolution_data)
        
        fig = go.Figure()
        
        # Línea coste mensual
        fig.add_trace(go.Scatter(
            x=df_evolution['mes'],
            y=df_evolution['coste_total'],
            mode='lines+markers+text',
            name='Coste Mensual',
            line=dict(color='#2E7D32', width=3),
            marker=dict(size=8),
            text=[f'€{val:,.0f}' for val in df_evolution['coste_total']],
            textposition='top center'
        ))
        
        # Línea coste diario
        fig.add_trace(go.Scatter(
            x=df_evolution['mes'],
            y=df_evolution['coste_dia'],
            mode='lines+markers',
            name='Coste Diario (aprox.)',
            line=dict(color='#4CAF50', width=2),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='📈 Evolución de Costes Totales',
            xaxis_title='Mes',
            yaxis_title='Coste Mensual (€)',
            yaxis2=dict(
                title='Coste Diario (€)',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            font={'size': 12},
            title_font={'size': 16, 'color': '#2E7D32'},
            height=500,
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        return fig
    
    def create_aportaciones_ss_evolucion_chart(self, selected_months: List[str]) -> go.Figure:
        """Gráfica de líneas: Evolución de aportaciones SS empresa/trabajador."""
        if not self.is_initialized or not selected_months:
            return self._empty_chart("Evolución Aportaciones SS - Sin Datos")
        
        ss_evolution_data = []
        
        for month in selected_months:
            kpis = self.get_monthly_kpis(month)
            if kpis['has_data']:
                ss_evolution_data.append({
                    'mes': month.title(),
                    'ss_empresa': kpis['total_ss_empresa'],
                    'ss_trabajador': kpis['total_ss_trabajador']
                })
        
        if not ss_evolution_data:
            return self._empty_chart("Evolución Aportaciones SS - Sin Datos para Meses Seleccionados")
        
        df_ss = pd.DataFrame(ss_evolution_data)
        
        fig = go.Figure()
        
        # Línea SS Empresa
        fig.add_trace(go.Scatter(
            x=df_ss['mes'],
            y=df_ss['ss_empresa'],
            mode='lines+markers+text',
            name='SS Empresa',
            line=dict(color='#2E7D32', width=3),
            marker=dict(size=8),
            text=[f'€{val:,.0f}' for val in df_ss['ss_empresa']],
            textposition='top center'
        ))
        
        # Línea SS Trabajador
        fig.add_trace(go.Scatter(
            x=df_ss['mes'],
            y=df_ss['ss_trabajador'],
            mode='lines+markers+text',
            name='SS Trabajador',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=8),
            text=[f'€{val:,.0f}' for val in df_ss['ss_trabajador']],
            textposition='bottom center'
        ))
        
        fig.update_layout(
            title='🏥 Evolución de Aportaciones a la Seguridad Social',
            xaxis_title='Mes',
            yaxis_title='Valor de Aportación (€)',
            font={'size': 12},
            title_font={'size': 16, 'color': '#2E7D32'},
            height=500,
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        return fig
    
    def create_departamentos_distribucion_chart(self, month: str) -> go.Figure:
        """Gráfica de pie: Distribución de empleados por departamento (TÍTULO CORREGIDO)."""
        if not self.is_initialized:
            return self._empty_chart("Distribución por Departamento - Sin Datos")
        
        month_data = self.costes_df[self.costes_df['mes'] == month]
        
        if month_data.empty:
            return self._empty_chart(f"Distribución por Departamento - {month.title()} (Sin Datos)")
        
        dept_count = month_data['departamento'].value_counts().reset_index()
        dept_count.columns = ['departamento', 'cantidad']
        
        fig = px.pie(
            dept_count,
            values='cantidad',
            names='departamento',
            # TÍTULO CORREGIDO:
            title=f'🏢 Distribución de Empleados por Departamento - {month.title()}'
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Empleados: %{value}<br>Porcentaje: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            font={'size': 12},
            title_font={'size': 16, 'color': '#2E7D32'},
            height=400
        )
        
        return fig
    
    def _empty_chart(self, title: str) -> go.Figure:
        """Crea una gráfica vacía con mensaje."""
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=400
        )
        return fig

# Exportar la clase
__all__ = ['CFIRRHHController']
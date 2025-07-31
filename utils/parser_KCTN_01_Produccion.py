"""
Parser KCTN 01 - Producción - ESTRUCTURA REAL
=============================================
Parser corregido basado en la estructura real del Excel de SharePoint.

Estructura Real:
- 13 hojas: Resumen + 12 meses con nombres correctos
- Hoja Resumen: Datos de ventas (filas 0-1), agregados anuales (fila 3), datos mensuales (fila 5+)
- Hojas Mensuales: Ventas del mes (filas 0-1), agregados del mes (fila 3), datos diarios (fila 5+)

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.2 (Estructura Real)
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback
import warnings

warnings.filterwarnings('ignore')

# ================================================================
# CONFIGURACIÓN DEL PARSER
# ================================================================

MODULE_INFO = {
    'id': 'KCTN_01_Produccion',
    'name': 'Producción KCTN',
    'category': 'KCTN',
    'description': 'Parser para análisis integral de producción de ajos en planta KCTN',
    'version': '1.2',
    'author': 'GANDB Dashboard Team'
}

MESES_NOMBRES = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

# ================================================================
# CLASE PRINCIPAL DEL PARSER
# ================================================================

class KCTNProduccionParser:
    """Parser específico para producción KCTN con estructura real del Excel."""
    
    def __init__(self):
        """Inicializa el parser."""
        self.module_info = MODULE_INFO
        self.warnings = []
        self.errors = []
        self.debug_mode = False  # Controlar logging
    
    def parse_excel(self, excel_data) -> Dict[str, Any]:
        """
        Función principal de parsing para datos de producción KCTN.
        
        Args:
            excel_data: Datos del Excel (DataFrame simple o dict multi-hoja)
            
        Returns:
            Dict con estructura completa de datos procesados
        """
        
        start_time = datetime.now()
        
        try:
            if self.debug_mode:
                st.info("🏭 Iniciando parser de Producción KCTN...")
            
            # ====== FASE 1: PREPARAR DATOS ======
            all_sheets = self._prepare_excel_data(excel_data)
            
            if not all_sheets:
                return self._create_error_response("Error preparando datos del Excel", start_time)
            
            if self.debug_mode:
                st.success(f"✅ {len(all_sheets)} hojas identificadas")
            
            # ====== FASE 2: PROCESAR HOJA RESUMEN ======
            resumen_data = self._process_resumen_sheet(all_sheets)
            if not resumen_data:
                return self._create_error_response("Error procesando hoja Resumen", start_time)
            
            if self.debug_mode:
                st.success("✅ Hoja Resumen procesada")
            
            # ====== FASE 3: PROCESAR HOJAS MENSUALES ======
            monthly_data = self._process_monthly_sheets(all_sheets)
            meses_procesados = len([m for m in monthly_data.values() if m.get('has_data', False)])
            
            if self.debug_mode:
                st.success(f"✅ {meses_procesados} meses procesados con datos")
            
            # ====== FASE 4: CALCULAR MÉTRICAS ======
            kpis = self._calculate_kpis(resumen_data, monthly_data)
            trends = self._analyze_trends(resumen_data, monthly_data)
            
            # ====== RESPUESTA FINAL ======
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'status': 'success',
                'data': {
                    'resumen': resumen_data,
                    'monthly': monthly_data,
                    'kpis': kpis,
                    'trends': trends,
                    'raw_sheets': all_sheets
                },
                'metadata': {
                    'module_info': self.module_info,
                    'processed_at': datetime.now().isoformat(),
                    'processing_time_seconds': round(processing_time, 2),
                    'total_sheets': len(all_sheets),
                    'months_with_data': meses_procesados,
                    'data_quality_score': self._calculate_quality_score(resumen_data, monthly_data),
                    'warnings': self.warnings,
                    'errors': self.errors
                }
            }
            
        except Exception as e:
            return self._create_error_response(str(e), start_time, include_traceback=True)
    
    def _prepare_excel_data(self, excel_data) -> Dict[str, pd.DataFrame]:
        """Prepara los datos del Excel basado en la estructura real."""
        try:
            if isinstance(excel_data, dict):
                # Excel multi-hoja desde SharePoint
                if self.debug_mode:
                    st.info(f"📊 Procesando Excel multi-hoja: {len(excel_data)} hojas")
                    sheet_names = list(excel_data.keys())
                    st.info(f"📋 Hojas encontradas: {', '.join(sheet_names)}")
                
                return excel_data
                
            elif isinstance(excel_data, pd.DataFrame):
                # Solo una hoja - asumir Resumen
                if self.debug_mode:
                    st.warning("📊 Solo una hoja recibida, asumiendo como Resumen")
                
                if excel_data.empty:
                    if self.debug_mode:
                        st.error("❌ DataFrame está vacío")
                    return {}
                
                # Crear estructura con Resumen y hojas vacías para meses
                all_sheets = {'Resumen': excel_data}
                for mes in MESES_NOMBRES:
                    all_sheets[mes] = pd.DataFrame()
                
                return all_sheets
                
            else:
                if self.debug_mode:
                    st.error(f"❌ Tipo de datos no soportado: {type(excel_data)}")
                return {}
            
        except Exception as e:
            if self.debug_mode:
                st.error(f"❌ Error preparando datos: {e}")
            return {}
    
    def _process_resumen_sheet(self, all_sheets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Procesa la hoja de Resumen según la estructura real del Excel."""
        try:
            # Buscar hoja Resumen
            resumen_df = all_sheets.get('Resumen')
            
            if resumen_df is None or resumen_df.empty:
                if self.debug_mode:
                    st.error("❌ No se encontró hoja Resumen con datos")
                return None
            
            if self.debug_mode:
                st.info("📊 Procesando hoja Resumen...")
            
            # ESTRUCTURA REAL:
            # Fila 0: ["VENTA CAT I :", "478330.00", "% MEDIO:", "65.16%"]
            # Fila 1: ["VENTA CAT II:", "255768.90", "% MEDIO:", "34.84%"]
            # Fila 3: [12, 11, 1195636.20, 1077280.90, 90%, 680326.00, 56%, 229068.00, 20%, 218554.47, 18%, 67687.73, 6%, 26]
            # Fila 4: ["MES", "DIAS/MES", "MP", "DESGR", "%", "CAT I", "%", "CAT II", "%", "DAG", "%", "MERMA", "%", "PAX"]
            
            # Datos de ventas (filas 0 y 1)
            ventas_data = {}
            try:
                # Fila 0: VENTA CAT I
                if len(resumen_df) > 0 and pd.notna(resumen_df.iloc[0, 1]):
                    venta_cat_i = self._clean_numeric(resumen_df.iloc[0, 1])
                    pct_cat_i = self._clean_percentage(resumen_df.iloc[0, 3])
                else:
                    venta_cat_i, pct_cat_i = 0, 0
                
                # Fila 1: VENTA CAT II
                if len(resumen_df) > 1 and pd.notna(resumen_df.iloc[1, 1]):
                    venta_cat_ii = self._clean_numeric(resumen_df.iloc[1, 1])
                    pct_cat_ii = self._clean_percentage(resumen_df.iloc[1, 3])
                else:
                    venta_cat_ii, pct_cat_ii = 0, 0
                
                ventas_data = {
                    'venta_cat_i': venta_cat_i,
                    'venta_cat_ii': venta_cat_ii,
                    'pct_medio_cat_i': pct_cat_i,
                    'pct_medio_cat_ii': pct_cat_ii
                }
            except Exception as e:
                if self.debug_mode:
                    st.warning(f"⚠️ Error leyendo datos de ventas: {e}")
                ventas_data = {'venta_cat_i': 0, 'venta_cat_ii': 0, 'pct_medio_cat_i': 0, 'pct_medio_cat_ii': 0}
            
            # Datos agregados anuales (fila 3)
            agregados_anuales = {}
            try:
                if len(resumen_df) > 3:
                    fila_3 = resumen_df.iloc[3]
                    
                    agregados_anuales = {
                        'total_meses': self._clean_numeric(fila_3[0]) if pd.notna(fila_3[0]) else 0,
                        'dias_promedio': self._clean_numeric(fila_3[1]) if pd.notna(fila_3[1]) else 0,
                        'mp_total': self._clean_numeric(fila_3[2]) if pd.notna(fila_3[2]) else 0,
                        'desgr_total': self._clean_numeric(fila_3[3]) if pd.notna(fila_3[3]) else 0,
                        'pct_desgr': self._clean_percentage(fila_3[4]) if pd.notna(fila_3[4]) else 0,
                        'cat_i_total': self._clean_numeric(fila_3[5]) if pd.notna(fila_3[5]) else 0,
                        'pct_cat_i': self._clean_percentage(fila_3[6]) if pd.notna(fila_3[6]) else 0,
                        'cat_ii_total': self._clean_numeric(fila_3[7]) if pd.notna(fila_3[7]) else 0,
                        'pct_cat_ii': self._clean_percentage(fila_3[8]) if pd.notna(fila_3[8]) else 0,
                        'dag_total': self._clean_numeric(fila_3[9]) if pd.notna(fila_3[9]) else 0,
                        'pct_dag': self._clean_percentage(fila_3[10]) if pd.notna(fila_3[10]) else 0,
                        'merma_total': self._clean_numeric(fila_3[11]) if pd.notna(fila_3[11]) else 0,
                        'pct_merma': self._clean_percentage(fila_3[12]) if pd.notna(fila_3[12]) else 0,
                        'pax_promedio': self._clean_numeric(fila_3[13]) if pd.notna(fila_3[13]) else 0
                    }
            except Exception as e:
                if self.debug_mode:
                    st.warning(f"⚠️ Error leyendo datos agregados: {e}")
                agregados_anuales = {
                    'total_meses': 0, 'dias_promedio': 0, 'mp_total': 0, 'desgr_total': 0,
                    'pct_desgr': 0, 'cat_i_total': 0, 'pct_cat_i': 0, 'cat_ii_total': 0,
                    'pct_cat_ii': 0, 'dag_total': 0, 'pct_dag': 0, 'merma_total': 0,
                    'pct_merma': 0, 'pax_promedio': 0
                }
            
            # Datos mensuales (desde fila 5)
            datos_mensuales = []
            try:
                for i in range(5, len(resumen_df)):
                    fila = resumen_df.iloc[i]
                    
                    # Verificar si es una fila de mes válida
                    if pd.notna(fila[0]) and str(fila[0]) in MESES_NOMBRES:
                        mes_data = {
                            'mes': str(fila[0]),
                            'dias': self._clean_numeric(fila[1]) if pd.notna(fila[1]) else 0,
                            'mp': self._clean_numeric(fila[2]) if pd.notna(fila[2]) else 0,
                            'desgr': self._clean_numeric(fila[3]) if pd.notna(fila[3]) else 0,
                            'pct_desgr': self._clean_percentage(fila[4]) if pd.notna(fila[4]) else 0,
                            'cat_i': self._clean_numeric(fila[5]) if pd.notna(fila[5]) else 0,
                            'pct_cat_i': self._clean_percentage(fila[6]) if pd.notna(fila[6]) else 0,
                            'cat_ii': self._clean_numeric(fila[7]) if pd.notna(fila[7]) else 0,
                            'pct_cat_ii': self._clean_percentage(fila[8]) if pd.notna(fila[8]) else 0,
                            'dag': self._clean_numeric(fila[9]) if pd.notna(fila[9]) else 0,
                            'pct_dag': self._clean_percentage(fila[10]) if pd.notna(fila[10]) else 0,
                            'merma': self._clean_numeric(fila[11]) if pd.notna(fila[11]) else 0,
                            'pct_merma': self._clean_percentage(fila[12]) if pd.notna(fila[12]) else 0,
                            'pax': self._clean_numeric(fila[13]) if pd.notna(fila[13]) else 0
                        }
                        
                        # Calcular merma si no está presente
                        if mes_data['merma'] == 0 and mes_data['mp'] > 0:
                            mes_data['merma'] = mes_data['mp'] - mes_data['cat_i'] - mes_data['cat_ii'] - mes_data['dag']
                            mes_data['pct_merma'] = (mes_data['merma'] / mes_data['mp']) * 100 if mes_data['mp'] > 0 else 0
                        
                        datos_mensuales.append(mes_data)
            except Exception as e:
                if self.debug_mode:
                    st.warning(f"⚠️ Error leyendo datos mensuales: {e}")
            
            return {
                'ventas': ventas_data,
                'agregados_anuales': agregados_anuales,
                'datos_mensuales': datos_mensuales,
                'meses_con_datos': len([m for m in datos_mensuales if m['mp'] > 0])
            }
            
        except Exception as e:
            if self.debug_mode:
                st.error(f"❌ Error procesando Resumen: {e}")
            self.errors.append(f"Error procesando Resumen: {e}")
            return None
    
    def _process_monthly_sheets(self, all_sheets: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
        """Procesa todas las hojas mensuales según estructura real."""
        monthly_data = {}
        
        for mes in MESES_NOMBRES:
            if mes in all_sheets and not all_sheets[mes].empty:
                mes_data = self._process_single_month(all_sheets[mes], mes)
                monthly_data[mes] = mes_data
            else:
                # Crear entrada sin datos para meses faltantes
                monthly_data[mes] = {
                    'has_data': False,
                    'mes': mes,
                    'error': f'Hoja {mes} no disponible',
                    'ventas': {'venta_cat_i': 0, 'venta_cat_ii': 0, 'pct_cat_i': 0, 'pct_cat_ii': 0},
                    'agregados': {},
                    'datos_diarios': [],
                    'por_dia': {},
                    'por_hora': {},
                    'dias_con_datos': 0
                }
        
        return monthly_data
    
    def _process_single_month(self, mes_df: pd.DataFrame, mes_nombre: str) -> Dict[str, Any]:
        """Procesa una hoja mensual individual según estructura real."""
        try:
            if mes_df is None or mes_df.empty:
                return {'has_data': False, 'error': 'DataFrame vacío'}
            
            # ESTRUCTURA REAL HOJAS MENSUALES:
            # Fila 0: ["VENTA CAT I :", valor, "% MEDIO:", porcentaje]
            # Fila 1: ["VENTA CAT II:", valor, "% MEDIO:", porcentaje]
            # Fila 3: [días, mp_total, desgr_total, cat_i_total, %, cat_ii_total, %, dag_total, %, pax_promedio]
            # Fila 4: ["DIA", "MP", "DESGR", "CAT I", "%", "CAT II", "%", "DAG", "%", "PAX"]
            
            # Ventas del mes (filas 0 y 1)
            ventas_mes = {}
            try:
                # Fila 0: VENTA CAT I
                venta_cat_i = self._clean_numeric(mes_df.iloc[0, 1]) if len(mes_df) > 0 and pd.notna(mes_df.iloc[0, 1]) else 0
                pct_cat_i = self._clean_percentage(mes_df.iloc[0, 3]) if len(mes_df) > 0 and pd.notna(mes_df.iloc[0, 3]) else 0
                
                # Fila 1: VENTA CAT II  
                venta_cat_ii = self._clean_numeric(mes_df.iloc[1, 1]) if len(mes_df) > 1 and pd.notna(mes_df.iloc[1, 1]) else 0
                pct_cat_ii = self._clean_percentage(mes_df.iloc[1, 3]) if len(mes_df) > 1 and pd.notna(mes_df.iloc[1, 3]) else 0
                
                ventas_mes = {
                    'venta_cat_i': venta_cat_i,
                    'venta_cat_ii': venta_cat_ii,
                    'pct_cat_i': pct_cat_i,
                    'pct_cat_ii': pct_cat_ii
                }
            except:
                ventas_mes = {'venta_cat_i': 0, 'venta_cat_ii': 0, 'pct_cat_i': 0, 'pct_cat_ii': 0}
            
            # Agregados del mes (fila 3)
            agregados_mes = {}
            try:
                if len(mes_df) > 3:
                    fila_3 = mes_df.iloc[3]
                    agregados_mes = {
                        'dias_trabajados': self._clean_numeric(fila_3[0]) if pd.notna(fila_3[0]) else 0,
                        'mp_total': self._clean_numeric(fila_3[1]) if pd.notna(fila_3[1]) else 0,
                        'desgr_total': self._clean_numeric(fila_3[2]) if pd.notna(fila_3[2]) else 0,
                        'cat_i_total': self._clean_numeric(fila_3[3]) if pd.notna(fila_3[3]) else 0,
                        'pct_cat_i_avg': self._clean_percentage(fila_3[4]) if pd.notna(fila_3[4]) else 0,
                        'cat_ii_total': self._clean_numeric(fila_3[5]) if pd.notna(fila_3[5]) else 0,
                        'pct_cat_ii_avg': self._clean_percentage(fila_3[6]) if pd.notna(fila_3[6]) else 0,
                        'dag_total': self._clean_numeric(fila_3[7]) if pd.notna(fila_3[7]) else 0,
                        'pct_dag_avg': self._clean_percentage(fila_3[8]) if pd.notna(fila_3[8]) else 0,
                        'pax_promedio': self._clean_numeric(fila_3[9]) if pd.notna(fila_3[9]) else 0
                    }
            except:
                agregados_mes = {
                    'dias_trabajados': 0, 'mp_total': 0, 'desgr_total': 0,
                    'cat_i_total': 0, 'pct_cat_i_avg': 0, 'cat_ii_total': 0,
                    'pct_cat_ii_avg': 0, 'dag_total': 0, 'pct_dag_avg': 0, 'pax_promedio': 0
                }
            
            # Datos diarios (desde fila 5)
            datos_diarios = []
            por_dia_data = {}
            por_hora_data = {}
            
            try:
                for i in range(5, len(mes_df)):
                    fila = mes_df.iloc[i]
                    
                    if pd.notna(fila[0]):
                        primer_valor = str(fila[0]).lower()
                        
                        # Buscar "Por Dia" y "Por Hora"
                        if 'por día' in primer_valor or 'por dia' in primer_valor:
                            por_dia_data = {
                                'mp_por_dia': self._clean_numeric(fila[1]) if pd.notna(fila[1]) else 0,
                                'desgr_por_dia': self._clean_numeric(fila[2]) if pd.notna(fila[2]) else 0,
                                'cat_i_por_dia': self._clean_numeric(fila[3]) if pd.notna(fila[3]) else 0,
                                'cat_ii_por_dia': self._clean_numeric(fila[5]) if pd.notna(fila[5]) else 0,
                                'dag_por_dia': self._clean_numeric(fila[7]) if pd.notna(fila[7]) else 0
                            }
                        elif 'por hora' in primer_valor:
                            por_hora_data = {
                                'mp_por_hora': self._clean_numeric(fila[1]) if pd.notna(fila[1]) else 0,
                                'desgr_por_hora': self._clean_numeric(fila[2]) if pd.notna(fila[2]) else 0,
                                'cat_i_por_hora': self._clean_numeric(fila[3]) if pd.notna(fila[3]) else 0,
                                'cat_ii_por_hora': self._clean_numeric(fila[5]) if pd.notna(fila[5]) else 0,
                                'dag_por_hora': self._clean_numeric(fila[7]) if pd.notna(fila[7]) else 0
                            }
                        else:
                            # Intentar parsear como fecha para datos diarios
                            try:
                                fecha = pd.to_datetime(fila[0], errors='coerce')
                                if pd.notna(fecha):
                                    dia_data = {
                                        'fecha': fecha,
                                        'mp': self._clean_numeric(fila[1]) if pd.notna(fila[1]) else 0,
                                        'desgr': self._clean_numeric(fila[2]) if pd.notna(fila[2]) else 0,
                                        'cat_i': self._clean_numeric(fila[3]) if pd.notna(fila[3]) else 0,
                                        'pct_cat_i': self._clean_percentage(fila[4]) if pd.notna(fila[4]) else 0,
                                        'cat_ii': self._clean_numeric(fila[5]) if pd.notna(fila[5]) else 0,
                                        'pct_cat_ii': self._clean_percentage(fila[6]) if pd.notna(fila[6]) else 0,
                                        'dag': self._clean_numeric(fila[7]) if pd.notna(fila[7]) else 0,
                                        'pct_dag': self._clean_percentage(fila[8]) if pd.notna(fila[8]) else 0,
                                        'pax': self._clean_numeric(fila[9]) if pd.notna(fila[9]) else 0
                                    }
                                    
                                    # Calcular merma
                                    if dia_data['mp'] > 0:
                                        dia_data['merma'] = dia_data['mp'] - dia_data['cat_i'] - dia_data['cat_ii'] - dia_data['dag']
                                        dia_data['pct_merma'] = (dia_data['merma'] / dia_data['mp']) * 100
                                    else:
                                        dia_data['merma'] = 0
                                        dia_data['pct_merma'] = 0
                                    
                                    datos_diarios.append(dia_data)
                            except:
                                continue
            except Exception as e:
                if self.debug_mode:
                    st.warning(f"⚠️ Error procesando datos diarios de {mes_nombre}: {e}")
            
            # Calcular por día y por hora si no están disponibles
            if not por_dia_data and agregados_mes.get('dias_trabajados', 0) > 0:
                dias = agregados_mes['dias_trabajados']
                por_dia_data = {
                    'mp_por_dia': agregados_mes.get('mp_total', 0) / dias,
                    'desgr_por_dia': agregados_mes.get('desgr_total', 0) / dias,
                    'cat_i_por_dia': agregados_mes.get('cat_i_total', 0) / dias,
                    'cat_ii_por_dia': agregados_mes.get('cat_ii_total', 0) / dias,
                    'dag_por_dia': agregados_mes.get('dag_total', 0) / dias
                }
            
            if not por_hora_data and por_dia_data:
                por_hora_data = {
                    'mp_por_hora': por_dia_data.get('mp_por_dia', 0) / 6,
                    'desgr_por_hora': por_dia_data.get('desgr_por_dia', 0) / 6,
                    'cat_i_por_hora': por_dia_data.get('cat_i_por_dia', 0) / 6,
                    'cat_ii_por_hora': por_dia_data.get('cat_ii_por_dia', 0) / 6,
                    'dag_por_hora': por_dia_data.get('dag_por_dia', 0) / 6
                }
            
            # Determinar si tiene datos válidos
            has_data = agregados_mes.get('mp_total', 0) > 0
            
            return {
                'has_data': has_data,
                'mes': mes_nombre,
                'ventas': ventas_mes,
                'agregados': agregados_mes,
                'datos_diarios': datos_diarios,
                'por_dia': por_dia_data,
                'por_hora': por_hora_data,
                'dias_con_datos': len(datos_diarios)
            }
            
        except Exception as e:
            self.errors.append(f"Error procesando {mes_nombre}: {e}")
            return {'has_data': False, 'error': str(e)}
    
    def _clean_numeric(self, value) -> float:
        """Limpia y convierte valores numéricos."""
        try:
            if pd.isna(value) or value is None:
                return 0.0
            
            # Convertir a string para limpiar
            str_val = str(value).strip()
            
            # Remover caracteres no numéricos excepto punto y coma
            str_val = str_val.replace(',', '').replace(' ', '')
            
            # Convertir a float
            return float(str_val)
        except:
            return 0.0
    
    def _clean_percentage(self, value) -> float:
        """Limpia y convierte porcentajes."""
        try:
            if pd.isna(value) or value is None:
                return 0.0
            
            str_val = str(value).strip()
            
            # Si contiene %, removerlo y dividir por 100
            if '%' in str_val:
                str_val = str_val.replace('%', '').strip()
                return float(str_val)
            else:
                # Asumir que ya está como decimal (0.65 = 65%)
                return float(str_val) * 100
        except:
            return 0.0
    
    def _calculate_kpis(self, resumen_data: Dict, monthly_data: Dict) -> Dict[str, Any]:
        """Calcula KPIs básicos."""
        try:
            if not resumen_data:
                return {}
            
            agregados = resumen_data['agregados_anuales']
            
            return {
                'mp_total_año': agregados.get('mp_total', 0),
                'desgr_total_año': agregados.get('desgr_total', 0),
                'rendimiento_desgranado': agregados.get('pct_desgr', 0),
                'cat_i_total': agregados.get('cat_i_total', 0),
                'cat_i_porcentaje': agregados.get('pct_cat_i', 0),
                'cat_ii_total': agregados.get('cat_ii_total', 0),
                'cat_ii_porcentaje': agregados.get('pct_cat_ii', 0),
                'dag_total': agregados.get('dag_total', 0),
                'dag_porcentaje': agregados.get('pct_dag', 0),
                'merma_total': agregados.get('merma_total', 0),
                'merma_porcentaje': agregados.get('pct_merma', 0),
                'productividad_personal': (agregados.get('desgr_total', 0) / agregados.get('pax_promedio', 1)) if agregados.get('pax_promedio', 0) > 0 else 0,
                'meses_operativos': resumen_data.get('meses_con_datos', 0)
            }
        except:
            return {}
    
    def _analyze_trends(self, resumen_data: Dict, monthly_data: Dict) -> Dict[str, Any]:
        """Análisis básico de tendencias."""
        try:
            if not resumen_data:
                return {}
            
            meses_datos = resumen_data['datos_mensuales']
            meses_con_datos = [m for m in meses_datos if m['mp'] > 0]
            
            if len(meses_con_datos) < 2:
                return {'error': 'Insuficientes datos para análisis de tendencias'}
            
            mp_values = [m['mp'] for m in meses_con_datos]
            cat_i_pct = [m['pct_cat_i'] for m in meses_con_datos]
            
            return {
                'tendencia_mp': 'creciente' if mp_values[-1] > mp_values[0] else 'decreciente',
                'tendencia_cat_i': 'creciente' if cat_i_pct[-1] > cat_i_pct[0] else 'decreciente',
                'mejor_mes_mp': max(meses_con_datos, key=lambda x: x['mp'])['mes'],
                'mejor_mes_cat_i': max(meses_con_datos, key=lambda x: x['pct_cat_i'])['mes']
            }
        except:
            return {}
    
    def _calculate_quality_score(self, resumen_data: Dict, monthly_data: Dict) -> float:
        """Calcula score de calidad de datos."""
        try:
            if not resumen_data:
                return 0.0
            
            completeness = 100 if resumen_data.get('meses_con_datos', 0) > 0 else 0
            consistency = 95
            validity = 90 if len(self.errors) == 0 else max(50, 90 - len(self.errors) * 10)
            
            return round((completeness + consistency + validity) / 3, 1)
        except:
            return 75.0
    
    def _create_error_response(self, error_message: str, start_time: datetime, include_traceback: bool = False) -> Dict[str, Any]:
        """Crea respuesta de error estándar."""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        error_data = {
            'status': 'error',
            'data': None,
            'metadata': {
                'module_info': self.module_info,
                'error': error_message,
                'processed_at': datetime.now().isoformat(),
                'processing_time_seconds': round(processing_time, 2),
                'warnings': self.warnings,
                'errors': self.errors + [error_message]
            }
        }
        
        if include_traceback:
            error_data['metadata']['traceback'] = traceback.format_exc()
        
        if self.debug_mode:
            st.error(f"❌ Error en parser KCTN Producción: {error_message}")
        return error_data

# ================================================================
# FUNCIÓN PRINCIPAL EXPORTADA
# ================================================================

def parse_excel(excel_data) -> Dict[str, Any]:
    """
    Función principal exportada para el sistema Excel Loader.
    
    Args:
        excel_data: Datos del Excel desde SharePoint
        
    Returns:
        Dict: Respuesta estándar del parser
    """
    parser = KCTNProduccionParser()
    return parser.parse_excel(excel_data)

def get_parser_info() -> Dict[str, Any]:
    """Información sobre este parser."""
    return MODULE_INFO

# Exportaciones
__all__ = ['parse_excel', 'get_parser_info', 'KCTNProduccionParser']
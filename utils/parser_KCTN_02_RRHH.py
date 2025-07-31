"""
parser_KCTN_02_RRHH.py - Parser Excel Garlic & Beyond COMPLETO CORREGIDO
========================================================================
Parser completo y robusto para estructura exacta del Excel de RRHH.
INCLUYE: Corrección para detectar correctamente datos de Producción.

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 3.1 - Completo y Corregido
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import warnings
import streamlit as st

warnings.filterwarnings('ignore')

class GarlicExcelParser:
    """Parser completo para Excel de Garlic & Beyond con validación robusta."""
    
    def __init__(self):
        """Inicializa el parser con configuración específica para Garlic & Beyond."""
        
        # Meses válidos para procesar (Enero a Diciembre)
        self.meses_validos = [
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        
        # Múltiples variaciones de nombres de meses
        self.month_variations = {
            'enero': ['enero', 'january', 'jan', '01', '1', 'ene'],
            'febrero': ['febrero', 'february', 'feb', '02', '2'],
            'marzo': ['marzo', 'march', 'mar', '03', '3'],
            'abril': ['abril', 'april', 'apr', '04', '4', 'abr'],
            'mayo': ['mayo', 'may', '05', '5'],
            'junio': ['junio', 'june', 'jun', '06', '6'],
            'julio': ['julio', 'july', 'jul', '07', '7'],
            'agosto': ['agosto', 'august', 'aug', '08', '8', 'ago'],
            'septiembre': ['septiembre', 'september', 'sep', 'sept', '09', '9'],
            'octubre': ['octubre', 'october', 'oct', '10'],
            'noviembre': ['noviembre', 'november', 'nov', '11'],
            'diciembre': ['diciembre', 'december', 'dec', '12', 'dic']
        }
        
        # Nombres de meses para display
        self.meses_nombres = {
            'enero': 'Enero', 'febrero': 'Febrero', 'marzo': 'Marzo',
            'abril': 'Abril', 'mayo': 'Mayo', 'junio': 'Junio',
            'julio': 'Julio', 'agosto': 'Agosto', 'septiembre': 'Septiembre',
            'octubre': 'Octubre', 'noviembre': 'Noviembre', 'diciembre': 'Diciembre'
        }
        
        # Hojas a omitir completamente
        self.hojas_omitir = ['diciembre 2024', 'resumen', 'resumen 2025', 'summary', 'total', 'config']
    
    def parse_excel_file(self, excel_data: Any) -> Dict[str, Any]:
        """
        Parsea el archivo Excel con validación exhaustiva.
        
        Args:
            excel_data: Datos recibidos (puede ser cualquier tipo)
            
        Returns:
            Dict con datos procesados y metadatos
        """
        try:
            # PASO 1: Validar y normalizar entrada
            validation_result = self._validate_and_normalize_input(excel_data)
            
            if not validation_result['valid']:
                return {
                    'status': 'error',
                    'message': validation_result['message'],
                    'data': {},
                    'metadata': {
                        'input_validation_error': True,
                        'input_type': validation_result.get('input_type', 'unknown'),
                        'timestamp': datetime.now().isoformat()
                    }
                }
            
            # PASO 2: Procesar datos normalizados
            normalized_data = validation_result['data']
            
            parsed_data = {}
            processed_months = []
            errors = []
            warnings_list = []
            sheet_analysis = []
            
            # Procesar cada hoja
            for sheet_name, df in normalized_data.items():
                try:
                    # Verificar si es una hoja válida
                    month_name = self._normalize_sheet_name(sheet_name)
                    
                    if month_name and month_name in self.meses_validos:
                        # Parsear hoja mensual
                        month_data = self._parse_monthly_sheet(df, month_name, sheet_name)
                        
                        # Agregar análisis de la hoja
                        analysis = {
                            'sheet_name': sheet_name,
                            'month_detected': month_name,
                            'status': month_data.get('status', 'unknown'),
                            'reason': month_data.get('message', ''),
                            'has_data': len(month_data.get('data', {}).get('empleados', [])) > 0,
                            'shape': f"{df.shape[0]}x{df.shape[1]}" if not df.empty else "empty"
                        }
                        sheet_analysis.append(analysis)
                        
                        if month_data and month_data.get('status') == 'success':
                            parsed_data[month_name] = month_data['data']
                            processed_months.append(month_name)
                        elif month_data and month_data.get('status') == 'warning':
                            # Datos con advertencias pero válidos
                            parsed_data[month_name] = month_data['data']
                            processed_months.append(month_name)
                            warnings_list.append(f"{sheet_name}: {month_data.get('message')}")
                        else:
                            errors.append(f"Error parseando {sheet_name}: {month_data.get('message', 'Error desconocido')}")
                    else:
                        # Hoja no reconocida
                        analysis = {
                            'sheet_name': sheet_name,
                            'month_detected': None,
                            'status': 'rejected',
                            'reason': 'Nombre de mes no reconocido o hoja omitida',
                            'has_data': False,
                            'shape': f"{df.shape[0]}x{df.shape[1]}" if not df.empty else "empty"
                        }
                        sheet_analysis.append(analysis)
                
                except Exception as e:
                    errors.append(f"Error procesando hoja {sheet_name}: {str(e)}")
                    analysis = {
                        'sheet_name': sheet_name,
                        'month_detected': None,
                        'status': 'error',
                        'reason': f'Excepción: {str(e)}',
                        'has_data': False,
                        'shape': 'unknown'
                    }
                    sheet_analysis.append(analysis)
                    continue
            
            # Resultado final
            result = {
                'status': 'success' if parsed_data else 'error',
                'message': f"Procesados {len(processed_months)} meses correctamente",
                'data': {
                    'monthly_data': parsed_data,
                    'employees': self._consolidate_employees(parsed_data),
                    'kpis': self._calculate_global_kpis(parsed_data),
                    'alerts': self._generate_alerts(parsed_data)
                },
                'metadata': {
                    'processed_months': processed_months,
                    'total_sheets': len(normalized_data),
                    'valid_sheets': len(parsed_data),
                    'errors': errors,
                    'warnings': warnings_list,
                    'sheet_analysis': sheet_analysis,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error crítico parseando Excel: {str(e)}',
                'data': {},
                'metadata': {'errors': [str(e)], 'timestamp': datetime.now().isoformat()}
            }
    
    def _validate_and_normalize_input(self, excel_data: Any) -> Dict[str, Any]:
        """Valida y normaliza datos de entrada."""
        result = {'valid': False, 'message': '', 'data': {}}
        
        try:
            # Caso 1: None
            if excel_data is None:
                result['message'] = 'Datos de entrada son None'
                result['input_type'] = 'None'
                return result
            
            # Caso 2: String (error)
            if isinstance(excel_data, str):
                result['message'] = f'Datos de entrada son string (error): {excel_data[:100]}...'
                result['input_type'] = 'str'
                return result
            
            # Caso 3: DataFrame simple
            if isinstance(excel_data, pd.DataFrame):
                result['valid'] = True
                result['data'] = {'Sheet1': excel_data}
                result['input_type'] = 'DataFrame'
                return result
            
            # Caso 4: Dict
            if isinstance(excel_data, dict):
                # Verificar si es resultado parseado (tiene 'status', 'data', etc.)
                if 'status' in excel_data and 'data' in excel_data:
                    result['message'] = 'Los datos ya están parseados - no se pueden volver a parsear'
                    result['input_type'] = 'parsed_result'
                    return result
                
                # Filtrar solo DataFrames
                dataframes = {}
                for key, value in excel_data.items():
                    if isinstance(value, pd.DataFrame):
                        dataframes[str(key)] = value
                
                if dataframes:
                    result['valid'] = True
                    result['data'] = dataframes
                    result['input_type'] = 'dict_dataframes'
                    return result
                else:
                    result['message'] = 'El dict no contiene DataFrames válidos'
                    result['input_type'] = 'dict_no_dataframes'
                    return result
            
            # Caso 5: Otros tipos
            result['message'] = f'Tipo de datos no soportado: {type(excel_data)}'
            result['input_type'] = str(type(excel_data))
            return result
            
        except Exception as e:
            result['message'] = f'Error validando entrada: {str(e)}'
            result['input_type'] = 'validation_error'
            return result
    
    def _normalize_sheet_name(self, sheet_name: str) -> Optional[str]:
        """Normaliza nombre de hoja a mes válido."""
        if not sheet_name:
            return None
        
        name_lower = str(sheet_name).lower().strip()
        
        # Verificar si está en hojas a omitir
        for omit in self.hojas_omitir:
            if omit in name_lower:
                return None
        
        # Buscar coincidencias en variaciones de meses
        for month, variations in self.month_variations.items():
            for variation in variations:
                if variation in name_lower:
                    return month
        
        return None
    
    def _parse_monthly_sheet(self, df: pd.DataFrame, month_name: str, sheet_name: str) -> Dict[str, Any]:
        """Parsea una hoja mensual según estructura específica."""
        try:
            if df.empty or len(df) < 3:
                return {
                    'status': 'warning',
                    'message': f'Hoja {sheet_name} vacía o con pocos datos (mes futuro)',
                    'data': self._create_empty_month_data(month_name)
                }
            
            # Limpiar DataFrame
            df_clean = self._clean_dataframe(df)
            
            # Encontrar fila "Total:"
            total_row_idx = self._find_total_row(df_clean)
            
            if total_row_idx is None:
                return {
                    'status': 'warning',
                    'message': f'No se encontró fila "Total:" en {sheet_name} (mes futuro)',
                    'data': self._create_empty_month_data(month_name)
                }
            
            # Extraer empleados (filas antes del Total)
            empleados = self._extract_employees(df_clean, total_row_idx, month_name)
            
            # Extraer datos de totales (VERSIÓN CORREGIDA)
            totales = self._extract_totals_data(df_clean, total_row_idx)
            
            # Calcular estadísticas
            stats = self._calculate_statistics(empleados, totales)
            
            # Validar datos
            validation = self._validate_parsed_data(empleados, totales, stats)
            
            # Preparar datos finales
            month_data = {
                'month_name': self.meses_nombres[month_name],
                'month_key': month_name,
                'empleados': empleados,
                'totales': totales,
                'stats': stats,
                'validation': validation
            }
            
            status = 'success'
            message = f'Hoja {sheet_name} parseada correctamente'
            
            if not validation['valid']:
                status = 'warning'
                message = f'Datos parseados con advertencias: {", ".join(validation["warnings"])}'
            
            return {
                'status': status,
                'message': message,
                'data': month_data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error parseando {sheet_name}: {str(e)}',
                'data': self._create_empty_month_data(month_name)
            }
    
    def _create_empty_month_data(self, month_name: str) -> Dict[str, Any]:
        """Crea estructura de datos vacía para meses futuros."""
        return {
            'month_name': self.meses_nombres[month_name],
            'month_key': month_name,
            'empleados': [],
            'totales': {
                'coste_total_mes': 0,
                'coste_total_dia': 0,
                'coste_total_hora': 0,
                'total_personal': 0,
                'fijo_mes': 0,
                'fijo_dia': 0,
                'fijo_hora': 0,
                'fijo_hpax': 0,
                'produccion_mes': 0,
                'produccion_dia': 0,
                'produccion_hora': 0,
                'produccion_hpax': 0
            },
            'stats': {
                'total_empleados': 0,
                'empleados_baja': 0,
                'porcentaje_bajas': 0,
                'coste_bajas': 0,
                'costes_seccion': {},
                'count_seccion': {},
                'empleados_baja_detalle': []
            },
            'validation': {'valid': True, 'warnings': []}
        }
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia el DataFrame eliminando filas y columnas completamente vacías."""
        try:
            df_clean = df.copy()
            df_clean = df_clean.dropna(how='all')
            df_clean = df_clean.dropna(axis=1, how='all')
            df_clean = df_clean.reset_index(drop=True)
            return df_clean
        except:
            return pd.DataFrame()
    
    def _find_total_row(self, df: pd.DataFrame) -> Optional[int]:
        """Encuentra la fila que contiene 'Total:' en la columna A."""
        try:
            for idx in range(len(df)):
                if len(df.columns) > 0:
                    cell_value = df.iloc[idx, 0]
                    if pd.notna(cell_value) and 'total' in str(cell_value).lower():
                        return idx
            return None
        except:
            return None
    
    def _extract_employees(self, df: pd.DataFrame, total_row_idx: int, month_name: str) -> List[Dict[str, Any]]:
        """Extrae lista de empleados de las filas antes del Total."""
        empleados = []
        
        try:
            for idx in range(1, total_row_idx):  # Empezar desde 1 para saltar encabezado
                try:
                    row = df.iloc[idx]
                    
                    # Columna A: Nombre (obligatorio)
                    nombre = row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else None
                    if not nombre or str(nombre).strip() == '' or str(nombre).lower() == 'nan':
                        continue
                    
                    nombre = str(nombre).strip()
                    
                    # Resto de columnas con valores por defecto
                    seccion = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else 'Sin sección'
                    tipo = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else 'Producción'
                    coste_total = self._parse_numeric_value(row.iloc[3] if len(row) > 3 else 0)
                    coste_dia = self._parse_numeric_value(row.iloc[4] if len(row) > 4 else 0)
                    coste_hora = self._parse_numeric_value(row.iloc[5] if len(row) > 5 else 0)
                    observaciones = str(row.iloc[6]).strip() if len(row) > 6 and pd.notna(row.iloc[6]) else ''
                    
                    # Determinar si está de baja
                    en_baja = 'baja' in observaciones.lower()
                    
                    # Calcular H/PAX según especificación: coste_hora / 8
                    hpax = (coste_hora / 8) if coste_hora > 0 else 0
                    
                    empleado = {
                        'nombre': nombre,
                        'seccion': seccion,
                        'tipo': tipo,
                        'coste_total': round(coste_total, 2),
                        'coste_dia': round(coste_dia, 2),
                        'coste_hora': round(coste_hora, 2),
                        'hpax': round(hpax, 2),
                        'observaciones': observaciones,
                        'en_baja': en_baja,
                        'estado': 'Baja' if en_baja else 'Activo',
                        'mes': month_name
                    }
                    
                    empleados.append(empleado)
                    
                except Exception:
                    continue
        except Exception:
            pass
        
        return empleados
    
    def _extract_totals_data(self, df: pd.DataFrame, total_row_idx: int) -> Dict[str, Any]:
        """
        VERSIÓN CORREGIDA: Extrae datos de totales con búsqueda mejorada.
        
        Estructura esperada:
        Fila Ax: Total: (D=coste_total_mes, E=coste_total_dia, F=coste_total_hora)
        Fila Ax+1: Count personal + encabezados MES, DIA, HORA, H/PAX
        Fila Ax+2: Fijo (C=tipo, D=mes, E=dia, F=hora, G=H/PAX)
        Fila Ax+3: Producción (C=tipo, D=mes, E=dia, F=hora, G=H/PAX)
        """
        totales = {
            'coste_total_mes': 0,
            'coste_total_dia': 0,
            'coste_total_hora': 0,
            'total_personal': 0,
            'fijo_mes': 0,
            'fijo_dia': 0,
            'fijo_hora': 0,
            'fijo_hpax': 0,
            'produccion_mes': 0,
            'produccion_dia': 0,
            'produccion_hora': 0,
            'produccion_hpax': 0
        }
        
        try:
            # PASO 1: Fila Total: (Ax) - Totales generales
            if total_row_idx < len(df):
                total_row = df.iloc[total_row_idx]
                totales['coste_total_mes'] = self._parse_numeric_value(total_row.iloc[3] if len(total_row) > 3 else 0)
                totales['coste_total_dia'] = self._parse_numeric_value(total_row.iloc[4] if len(total_row) > 4 else 0)
                totales['coste_total_hora'] = self._parse_numeric_value(total_row.iloc[5] if len(total_row) > 5 else 0)
            
            # PASO 2: Fila Personal count (Ax+1)
            if total_row_idx + 1 < len(df):
                count_row = df.iloc[total_row_idx + 1]
                total_personal = self._parse_numeric_value(count_row.iloc[0])
                totales['total_personal'] = int(total_personal) if total_personal > 0 else 0
            
            # PASO 3: BÚSQUEDA MEJORADA de filas Fijo y Producción
            # Buscar en las siguientes 10 filas después del Total
            max_search_rows = min(len(df), total_row_idx + 10)
            
            for idx in range(total_row_idx + 2, max_search_rows):
                try:
                    row = df.iloc[idx]
                    
                    # Verificar que la fila tenga suficientes columnas
                    if len(row) < 4:
                        continue
                    
                    # Buscar texto indicador en las primeras 3 columnas
                    row_text = ""
                    for col_idx in range(min(3, len(row))):
                        cell_value = row.iloc[col_idx]
                        if pd.notna(cell_value):
                            row_text += str(cell_value).lower() + " "
                    
                    # DETECTAR FILA FIJO
                    if any(word in row_text for word in ['fijo', 'fix', 'fixed']):
                        totales['fijo_mes'] = self._parse_numeric_value(row.iloc[3] if len(row) > 3 else 0)
                        totales['fijo_dia'] = self._parse_numeric_value(row.iloc[4] if len(row) > 4 else 0)
                        totales['fijo_hora'] = self._parse_numeric_value(row.iloc[5] if len(row) > 5 else 0)
                        totales['fijo_hpax'] = self._parse_numeric_value(row.iloc[6] if len(row) > 6 else 0)
                    
                    # DETECTAR FILA PRODUCCIÓN
                    elif any(word in row_text for word in ['produccion', 'producción', 'production', 'prod']):
                        totales['produccion_mes'] = self._parse_numeric_value(row.iloc[3] if len(row) > 3 else 0)
                        totales['produccion_dia'] = self._parse_numeric_value(row.iloc[4] if len(row) > 4 else 0)
                        totales['produccion_hora'] = self._parse_numeric_value(row.iloc[5] if len(row) > 5 else 0)
                        totales['produccion_hpax'] = self._parse_numeric_value(row.iloc[6] if len(row) > 6 else 0)
                
                except Exception:
                    # Continuar con la siguiente fila si hay error
                    continue
            
            # PASO 4: Validación y fallback
            # Si no encontramos datos de Fijo/Producción, intentar método original
            if totales['fijo_mes'] == 0 and totales['produccion_mes'] == 0:
                # Método fallback: posiciones fijas
                try:
                    # Fijo en posición Ax+2
                    if total_row_idx + 2 < len(df):
                        fijo_row = df.iloc[total_row_idx + 2]
                        if len(fijo_row) > 3:
                            totales['fijo_mes'] = self._parse_numeric_value(fijo_row.iloc[3])
                            totales['fijo_dia'] = self._parse_numeric_value(fijo_row.iloc[4] if len(fijo_row) > 4 else 0)
                            totales['fijo_hora'] = self._parse_numeric_value(fijo_row.iloc[5] if len(fijo_row) > 5 else 0)
                            totales['fijo_hpax'] = self._parse_numeric_value(fijo_row.iloc[6] if len(fijo_row) > 6 else 0)
                    
                    # Producción en posición Ax+3
                    if total_row_idx + 3 < len(df):
                        prod_row = df.iloc[total_row_idx + 3]
                        if len(prod_row) > 3:
                            totales['produccion_mes'] = self._parse_numeric_value(prod_row.iloc[3])
                            totales['produccion_dia'] = self._parse_numeric_value(prod_row.iloc[4] if len(prod_row) > 4 else 0)
                            totales['produccion_hora'] = self._parse_numeric_value(prod_row.iloc[5] if len(prod_row) > 5 else 0)
                            totales['produccion_hpax'] = self._parse_numeric_value(prod_row.iloc[6] if len(prod_row) > 6 else 0)
                            
                except Exception:
                    pass
        
        except Exception:
            # Si hay error crítico, mantener valores por defecto
            pass
        
        return totales
    
    def _parse_numeric_value(self, value: Any) -> float:
        """Convierte un valor a numérico de manera robusta."""
        try:
            if pd.isna(value):
                return 0.0
            
            if isinstance(value, (int, float)):
                return float(value)
            
            value_str = str(value).strip()
            value_clean = value_str.replace('€', '').replace('$', '').replace(' ', '').replace(',', '.')
            return float(value_clean) if value_clean and value_clean.lower() != 'nan' else 0.0
            
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_statistics(self, empleados: List[Dict[str, Any]], totales: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula estadísticas adicionales por mes."""
        if not empleados:
            return {
                'total_empleados': 0,
                'empleados_baja': 0,
                'porcentaje_bajas': 0,
                'coste_bajas': 0,
                'costes_seccion': {},
                'count_seccion': {},
                'empleados_baja_detalle': []
            }
        
        # Empleados de baja
        empleados_baja = [emp for emp in empleados if emp['en_baja']]
        
        # Costes y conteos por sección
        costes_seccion = {}
        count_seccion = {}
        
        for emp in empleados:
            seccion = emp['seccion']
            if seccion not in costes_seccion:
                costes_seccion[seccion] = 0
                count_seccion[seccion] = 0
            
            costes_seccion[seccion] += emp['coste_total']
            count_seccion[seccion] += 1
        
        # Coste total de bajas
        coste_bajas = sum(emp['coste_total'] for emp in empleados_baja)
        
        stats = {
            'total_empleados': len(empleados),
            'empleados_baja': len(empleados_baja),
            'porcentaje_bajas': (len(empleados_baja) / len(empleados) * 100) if empleados else 0,
            'coste_bajas': round(coste_bajas, 2),
            'costes_seccion': costes_seccion,
            'count_seccion': count_seccion,
            'empleados_baja_detalle': empleados_baja
        }
        
        return stats
    
    def _validate_parsed_data(self, empleados: List[Dict[str, Any]], 
                            totales: Dict[str, Any], 
                            stats: Dict[str, Any]) -> Dict[str, Any]:
        """Valida los datos parseados."""
        warnings = []
        
        if not empleados:
            return {'valid': True, 'warnings': []}
        
        if totales.get('coste_total_mes', 0) == 0:
            warnings.append("Coste total mensual es 0")
        
        # Validar consistencia entre empleados y totales
        coste_calculado = sum(emp['coste_total'] for emp in empleados)
        coste_total = totales.get('coste_total_mes', 0)
        
        if coste_total > 0 and abs(coste_calculado - coste_total) > (coste_total * 0.05):  # 5% tolerancia
            warnings.append(f"Diferencia en costes: calculado {coste_calculado:.2f} vs total {coste_total:.2f}")
        
        return {
            'valid': len(warnings) == 0,
            'warnings': warnings
        }
    
    def _consolidate_employees(self, monthly_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Consolida todos los empleados de todos los meses."""
        all_employees = []
        
        for month, data in monthly_data.items():
            empleados = data.get('empleados', [])
            all_employees.extend(empleados)
        
        return all_employees
    
    def _calculate_global_kpis(self, monthly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula KPIs globales del último mes con datos."""
        if not monthly_data:
            return {}
        
        # Encontrar último mes con datos
        ultimo_mes = None
        for mes in reversed(['diciembre', 'noviembre', 'octubre', 'septiembre', 'agosto', 'julio', 'junio', 'mayo', 'abril', 'marzo', 'febrero', 'enero']):
            if mes in monthly_data and monthly_data[mes]['stats']['total_empleados'] > 0:
                ultimo_mes = mes
                break
        
        if not ultimo_mes:
            return {}
        
        ultimo_mes_data = monthly_data[ultimo_mes]
        
        return {
            'latest_month': ultimo_mes,
            'latest_month_name': ultimo_mes_data['month_name'],
            'total_employees': ultimo_mes_data['stats']['total_empleados'],
            'total_cost': ultimo_mes_data['totales']['coste_total_mes'],
            'employees_on_leave': ultimo_mes_data['stats']['empleados_baja'],
            'leave_percentage': ultimo_mes_data['stats']['porcentaje_bajas'],
            'cost_on_leave': ultimo_mes_data['stats']['coste_bajas']
        }
    
    def _generate_alerts(self, monthly_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera alertas basadas en los datos procesados."""
        alerts = []
        
        if not monthly_data:
            return alerts
        
        # Analizar último mes con datos
        for mes in reversed(['diciembre', 'noviembre', 'octubre', 'septiembre', 'agosto', 'julio', 'junio', 'mayo', 'abril', 'marzo', 'febrero', 'enero']):
            if mes in monthly_data and monthly_data[mes]['stats']['total_empleados'] > 0:
                stats = monthly_data[mes]['stats']
                
                # Alerta por alto porcentaje de bajas
                if stats['porcentaje_bajas'] > 15:
                    alerts.append({
                        'type': 'warning',
                        'title': 'Alto porcentaje de bajas',
                        'message': f"El {stats['porcentaje_bajas']:.1f}% del personal está de baja en {monthly_data[mes]['month_name']}"
                    })
                
                # Alerta por coste de bajas
                if stats['coste_bajas'] > 0:
                    impacto = (stats['coste_bajas'] / monthly_data[mes]['totales']['coste_total_mes'] * 100)
                    if impacto > 10:
                        alerts.append({
                            'type': 'info',
                            'title': 'Impacto económico de bajas',
                            'message': f"Las bajas suponen {impacto:.1f}% del coste total (€{stats['coste_bajas']:,.0f})"
                        })
                
                break
        
        return alerts


def parse_excel(excel_data: Union[pd.DataFrame, Dict[str, pd.DataFrame]]) -> Dict[str, Any]:
    """
    Función principal para parsear Excel de Garlic & Beyond.
    
    Args:
        excel_data: Datos del Excel (dict de DataFrames por hoja o cualquier tipo)
        
    Returns:
        Dict con datos procesados según especificaciones
    """
    parser = GarlicExcelParser()
    return parser.parse_excel_file(excel_data)
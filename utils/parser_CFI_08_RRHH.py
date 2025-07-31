"""
Parser CFI_08_RRHH.py - Parser de Recursos Humanos CFI
=====================================================
Parser especializado para procesar datos de costes de personal de CFI
desde Excel con hojas "Listado de costes de empresa" y "Observaciones".

Estructura del Excel:
- Hoja 1: "Listado de costes de empresa" - Datos de costes por empleado
- Hoja 2: "Observaciones" - Información de bajas y altas

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import traceback
import re

def parse_excel(excel_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Parser principal para datos de RRHH CFI.
    
    Args:
        excel_data: Diccionario con DataFrames de Excel {sheet_name: DataFrame}
        
    Returns:
        Dict con estructura:
        {
            'status': 'success'/'error',
            'message': str,
            'data': {
                'costes_personal': DataFrame,
                'bajas_observaciones': DataFrame,
                'resumen_mensual': Dict,
                'departamentos': List[str],
                'meses_disponibles': List[str]
            },
            'metadata': Dict
        }
    """
    
    try:
        print("🔍 Iniciando parser CFI_08_RRHH...")
        
        # Validar entrada
        if not isinstance(excel_data, dict):
            return {
                'status': 'error',
                'message': 'Datos de entrada deben ser un diccionario de DataFrames',
                'data': None,
                'metadata': {'error_type': 'invalid_input'}
            }
        
        print(f"📊 Hojas disponibles: {list(excel_data.keys())}")
        
        # Variables para almacenar resultados
        costes_personal_df = pd.DataFrame()
        bajas_observaciones_df = pd.DataFrame()
        errors = []
        warnings = []
        
        # ================================================================
        # PROCESAMIENTO HOJA 1: "Listado de costes de empresa"
        # ================================================================
        hoja_costes_name = None
        for sheet_name in excel_data.keys():
            if 'listado' in sheet_name.lower() and 'costes' in sheet_name.lower():
                hoja_costes_name = sheet_name
                break
        
        if hoja_costes_name:
            print(f"📋 Procesando hoja de costes: {hoja_costes_name}")
            costes_personal_df = process_costes_personal_sheet(
                excel_data[hoja_costes_name], errors, warnings
            )
        else:
            errors.append("No se encontró hoja 'Listado de costes de empresa'")
            print("❌ Hoja de costes no encontrada")
        
        # ================================================================
        # PROCESAMIENTO HOJA 2: "Observaciones"
        # ================================================================
        hoja_observaciones_name = None
        for sheet_name in excel_data.keys():
            if 'observaciones' in sheet_name.lower():
                hoja_observaciones_name = sheet_name
                break
        
        if hoja_observaciones_name:
            print(f"🏥 Procesando hoja de observaciones: {hoja_observaciones_name}")
            bajas_observaciones_df = process_observaciones_sheet(
                excel_data[hoja_observaciones_name], errors, warnings
            )
        else:
            warnings.append("No se encontró hoja 'Observaciones' - análisis de bajas limitado")
            print("⚠️ Hoja de observaciones no encontrada")
        
        # ================================================================
        # ANÁLISIS Y RESUMEN
        # ================================================================
        if costes_personal_df.empty:
            return {
                'status': 'error',
                'message': 'No se pudieron procesar datos de costes de personal',
                'data': None,
                'metadata': {
                    'errors': errors,
                    'warnings': warnings,
                    'sheets_processed': list(excel_data.keys())
                }
            }
        
        # Generar resumen mensual
        resumen_mensual = generate_monthly_summary(costes_personal_df)
        
        # Obtener listas únicas
        departamentos = sorted(costes_personal_df['departamento'].unique().tolist())
        meses_disponibles = sorted(costes_personal_df['mes'].unique().tolist(), key=month_sort_key)
        
        print(f"✅ Procesamiento completado:")
        print(f"   - {len(costes_personal_df)} registros de costes")
        print(f"   - {len(bajas_observaciones_df)} observaciones de bajas")
        print(f"   - {len(departamentos)} departamentos")
        print(f"   - {len(meses_disponibles)} meses")
        
        return {
            'status': 'success',
            'message': f'Datos procesados correctamente: {len(costes_personal_df)} registros',
            'data': {
                'costes_personal': costes_personal_df,
                'bajas_observaciones': bajas_observaciones_df,
                'resumen_mensual': resumen_mensual,
                'departamentos': departamentos,
                'meses_disponibles': meses_disponibles
            },
            'metadata': {
                'total_records': len(costes_personal_df),
                'total_observations': len(bajas_observaciones_df),
                'departments_count': len(departamentos),
                'months_count': len(meses_disponibles),
                'errors': errors,
                'warnings': warnings,
                'processed_at': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        error_msg = f"Error crítico en parser CFI_08_RRHH: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {
            'status': 'error',
            'message': error_msg,
            'data': None,
            'metadata': {'error_type': 'critical_exception', 'exception': str(e)}
        }

def process_costes_personal_sheet(df: pd.DataFrame, errors: List[str], warnings: List[str]) -> pd.DataFrame:
    """
    Procesa la hoja "Listado de costes de empresa".
    
    Estructura esperada (fila 3 = headers):
    - C: Nombre
    - D: Mes (enero, febrero, etc.)
    - F: DEPARTAMENTO  
    - H: Devengado
    - I: Líquido
    - J: Deducciones
    - M: Aportación Seg. Social empresa
    - N: Aportación Seg. Social trabajador
    - O: I.R.P.F.
    - S: Coste total
    """
    
    try:
        print("📊 Procesando hoja de costes de personal...")
        
        if df.empty:
            errors.append("Hoja de costes está vacía")
            return pd.DataFrame()
        
        print(f"   Dimensiones originales: {df.shape}")
        
        # Buscar fila de headers (fila 3, índice 2)
        if len(df) < 3:
            errors.append("Hoja de costes tiene menos de 3 filas")
            return pd.DataFrame()
        
        # Los headers están en la fila 3 (índice 2)
        # Los datos empiezan en fila 4 (índice 3)
        headers_row = 2  # Fila 3 (base 0)
        data_start_row = 3  # Fila 4 (base 0)
        
        # Extraer solo datos (desde fila 4 en adelante)
        data_df = df.iloc[data_start_row:].copy()
        
        if data_df.empty:
            errors.append("No hay datos después de headers")
            return pd.DataFrame()
        
        # Mapeo de columnas (índices base 0)
        # A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8, J=9, K=10, L=11, M=12, N=13, O=14, P=15, Q=16, R=17, S=18
        column_mapping = {
            2: 'nombre',           # C: Nombre
            3: 'mes',              # D: Mes
            5: 'departamento',     # F: DEPARTAMENTO
            7: 'devengado',        # H: Devengado
            8: 'liquido',          # I: Líquido
            9: 'deducciones',      # J: Deducciones
            12: 'ss_empresa',      # M: Aportación Seg. Social empresa
            13: 'ss_trabajador',   # N: Aportación Seg. Social trabajador
            14: 'irpf',            # O: I.R.P.F.
            18: 'coste_total'      # S: Coste total
        }
        
        # Verificar que tenemos las columnas necesarias
        max_col_needed = max(column_mapping.keys())
        if data_df.shape[1] <= max_col_needed:
            errors.append(f"Faltan columnas en hoja de costes (necesarias hasta {max_col_needed+1})")
            return pd.DataFrame()
        
        # Crear DataFrame con columnas renombradas
        processed_data = []
        
        for idx, row in data_df.iterrows():
            try:
                # Extraer datos según mapeo
                record = {}
                
                for col_idx, col_name in column_mapping.items():
                    if col_idx < len(row):
                        value = row.iloc[col_idx]
                        
                        # Limpiar valores
                        if pd.isna(value) or value == '':
                            record[col_name] = None
                        elif col_name in ['devengado', 'liquido', 'deducciones', 'ss_empresa', 'ss_trabajador', 'irpf', 'coste_total']:
                            # Campos numéricos
                            try:
                                record[col_name] = float(value) if value is not None else 0.0
                            except (ValueError, TypeError):
                                record[col_name] = 0.0
                        else:
                            # Campos de texto
                            record[col_name] = str(value).strip() if value is not None else ''
                    else:
                        record[col_name] = None if col_name in ['devengado', 'liquido', 'deducciones', 'ss_empresa', 'ss_trabajador', 'irpf', 'coste_total'] else ''
                
                # Validar registro
                if (record.get('nombre', '').strip() != '' and 
                    record.get('mes', '').strip() != '' and
                    record.get('departamento', '').strip() != ''):
                    
                    # Normalizar mes
                    record['mes'] = normalize_month_name(record['mes'])
                    
                    # Normalizar departamento
                    record['departamento'] = normalize_department_name(record['departamento'])
                    
                    processed_data.append(record)
                    
            except Exception as e:
                warnings.append(f"Error procesando fila {idx}: {str(e)}")
                continue
        
        if not processed_data:
            errors.append("No se pudieron procesar registros válidos")
            return pd.DataFrame()
        
        result_df = pd.DataFrame(processed_data)
        
        print(f"   ✅ Procesados {len(result_df)} registros válidos")
        print(f"   📊 Meses encontrados: {sorted(result_df['mes'].unique())}")
        print(f"   🏢 Departamentos: {sorted(result_df['departamento'].unique())}")
        
        return result_df
        
    except Exception as e:
        error_msg = f"Error procesando hoja de costes: {str(e)}"
        errors.append(error_msg)
        print(f"❌ {error_msg}")
        return pd.DataFrame()

def process_observaciones_sheet(df: pd.DataFrame, errors: List[str], warnings: List[str]) -> pd.DataFrame:
    """
    Procesa la hoja "Observaciones" para extraer información de bajas y altas.
    
    Formato esperado:
    - Columna A: Mes (ENERO, FEBRERO, etc.)
    - Columna B: Descripción (07/1/25 baja de Youssef Melghalagh por alta de Santiaga Sanchez)
    """
    
    try:
        print("🏥 Procesando hoja de observaciones...")
        
        if df.empty:
            warnings.append("Hoja de observaciones está vacía")
            return pd.DataFrame()
        
        print(f"   Dimensiones: {df.shape}")
        
        processed_observations = []
        current_month = None
        
        for idx, row in df.iterrows():
            try:
                # Columna A (índice 0) - Mes
                mes_cell = row.iloc[0] if len(row) > 0 else None
                
                # Columna B (índice 1) - Observación
                obs_cell = row.iloc[1] if len(row) > 1 else None
                
                # Si hay mes en columna A, actualizar mes actual
                if pd.notna(mes_cell) and str(mes_cell).strip():
                    potential_month = str(mes_cell).strip().upper()
                    if potential_month in ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
                                         'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']:
                        current_month = normalize_month_name(potential_month)
                
                # Si hay observación en columna B
                if pd.notna(obs_cell) and str(obs_cell).strip() and current_month:
                    obs_text = str(obs_cell).strip()
                    
                    # Parsear la observación
                    parsed_obs = parse_observation_text(obs_text, current_month)
                    if parsed_obs:
                        processed_observations.append(parsed_obs)
                        
            except Exception as e:
                warnings.append(f"Error procesando observación en fila {idx}: {str(e)}")
                continue
        
        if not processed_observations:
            warnings.append("No se encontraron observaciones válidas")
            return pd.DataFrame()
        
        result_df = pd.DataFrame(processed_observations)
        
        print(f"   ✅ Procesadas {len(result_df)} observaciones")
        print(f"   📅 Meses con observaciones: {sorted(result_df['mes'].unique())}")
        
        return result_df
        
    except Exception as e:
        error_msg = f"Error procesando hoja de observaciones: {str(e)}"
        warnings.append(error_msg)
        print(f"⚠️ {error_msg}")
        return pd.DataFrame()

def parse_observation_text(text: str, month: str) -> Optional[Dict[str, Any]]:
    """
    Parsea el texto de una observación para extraer información estructurada.
    
    Ejemplos:
    - "07/1/25 baja de Youssef Melghalagh por alta de Santiaga Sanchez"
    - "08/1/25 alta de Youssef Melghalagh por baja enf. comun de Leopolda Contreras"
    """
    
    try:
        # Patrón para extraer información
        # Formato: DD/M/YY [tipo] de [nombre] por [motivo]
        pattern = r'(\d{1,2}/\d{1,2}/\d{2,4})\s+(alta|baja)\s+de\s+([^p]+?)(?:\s+por\s+(.+?))?$'
        
        match = re.match(pattern, text.strip(), re.IGNORECASE)
        
        if match:
            fecha_str = match.group(1)
            tipo_movimiento = match.group(2).lower()
            nombre = match.group(3).strip()
            motivo = match.group(4).strip() if match.group(4) else 'No especificado'
            
            return {
                'mes': month,
                'fecha': fecha_str,
                'tipo_movimiento': tipo_movimiento,  # 'alta' o 'baja'
                'nombre_empleado': nombre,
                'motivo': motivo,
                'texto_original': text
            }
        else:
            # Si no coincide con patrón, guardar como observación general
            return {
                'mes': month,
                'fecha': 'No especificada',
                'tipo_movimiento': 'observacion',
                'nombre_empleado': 'No especificado',
                'motivo': text,
                'texto_original': text
            }
            
    except Exception as e:
        print(f"Error parseando observación '{text}': {str(e)}")
        return None

def normalize_month_name(month: str) -> str:
    """Normaliza nombres de meses al formato estándar."""
    if not month:
        return 'desconocido'
    
    month_map = {
        'enero': 'enero', '1': 'enero', 'jan': 'enero', 'january': 'enero',
        'febrero': 'febrero', '2': 'febrero', 'feb': 'febrero', 'february': 'febrero',
        'marzo': 'marzo', '3': 'marzo', 'mar': 'marzo', 'march': 'marzo',
        'abril': 'abril', '4': 'abril', 'apr': 'abril', 'april': 'abril',
        'mayo': 'mayo', '5': 'mayo', 'may': 'mayo',
        'junio': 'junio', '6': 'junio', 'jun': 'junio', 'june': 'junio',
        'julio': 'julio', '7': 'julio', 'jul': 'julio', 'july': 'julio',
        'agosto': 'agosto', '8': 'agosto', 'aug': 'agosto', 'august': 'agosto',
        'septiembre': 'septiembre', '9': 'septiembre', 'sep': 'septiembre', 'september': 'septiembre',
        'octubre': 'octubre', '10': 'octubre', 'oct': 'octubre', 'october': 'octubre',
        'noviembre': 'noviembre', '11': 'noviembre', 'nov': 'noviembre', 'november': 'noviembre',
        'diciembre': 'diciembre', '12': 'diciembre', 'dec': 'diciembre', 'december': 'diciembre'
    }
    
    normalized = month_map.get(month.lower().strip(), month.lower().strip())
    return normalized

def normalize_department_name(dept: str) -> str:
    """Normaliza nombres de departamentos."""
    if not dept:
        return 'Sin Departamento'
    
    dept = str(dept).strip()
    
    # Mapeo de normalizaciones comunes
    dept_map = {
        'produccion': 'Producción',
        'production': 'Producción',
        'calidad': 'Calidad',
        'quality': 'Calidad',
        'logistica': 'Logística',
        'logistics': 'Logística',
        'administracion': 'Administración',
        'administration': 'Administración',
        'ventas': 'Ventas',
        'sales': 'Ventas',
        'compras': 'Compras',
        'purchasing': 'Compras',
        'mantenimiento': 'Mantenimiento',
        'maintenance': 'Mantenimiento'
    }
    
    normalized = dept_map.get(dept.lower(), dept.title())
    return normalized

def generate_monthly_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Genera resumen mensual de los datos de costes."""
    
    if df.empty:
        return {}
    
    summary = {}
    
    for month in df['mes'].unique():
        month_data = df[df['mes'] == month]
        
        summary[month] = {
            'total_empleados': len(month_data),
            'total_coste': month_data['coste_total'].sum(),
            'total_devengado': month_data['devengado'].sum(),
            'total_liquido': month_data['liquido'].sum(),
            'total_deducciones': month_data['deducciones'].sum(),
            'total_ss_empresa': month_data['ss_empresa'].sum(),
            'total_ss_trabajador': month_data['ss_trabajador'].sum(),
            'total_irpf': month_data['irpf'].sum(),
            'departamentos': month_data['departamento'].unique().tolist(),
            'coste_promedio_empleado': month_data['coste_total'].mean()
        }
    
    return summary

def month_sort_key(month: str) -> int:
    """Clave de ordenamiento para meses."""
    month_order = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    return month_order.get(month.lower(), 99)

# Función principal de exportación
__all__ = ['parse_excel']
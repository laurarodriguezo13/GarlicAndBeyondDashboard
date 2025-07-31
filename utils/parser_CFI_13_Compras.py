"""
Parser CFI Compras - Módulo de Compras CFI
==========================================
Parser especializado para procesar datos de compras de CFI desde Excel SharePoint.
Procesa información de proveedores, facturas, pagos, y estados de entrega.

Estructura del Excel:
- Hoja 1: Datos principales (C-R)
  - C: PROVEEDOR | F: FECHA FACTURA | G: TOTAL FACTURA
  - I: PESO | J: PRECIO | N: CONEXION (tiempo en días)
  - P: PAGO (distribución) | Q: DIA PAGO | R: ESTADO
- Hoja 2: Información de proveedores

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Dict, Any, Optional, List, Tuple
import warnings

warnings.filterwarnings('ignore')

def parse_excel(excel_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Procesa datos de compras CFI desde Excel SharePoint.
    
    Args:
        excel_data: Diccionario con DataFrames de cada hoja del Excel
        
    Returns:
        dict: Datos procesados con estructura estándar
    """
    
    try:
        # Verificar que tenemos las hojas necesarias
        if not isinstance(excel_data, dict):
            return {
                'status': 'error',
                'message': 'Formato de datos incorrecto',
                'data': {},
                'metadata': {'error': 'Se esperaba diccionario con hojas Excel'}
            }
        
        # Identificar hojas principales
        sheet_names = list(excel_data.keys())
        main_sheet = None
        proveedores_sheet = None
        
        # Buscar hoja principal (datos de compras)
        for sheet_name in sheet_names:
            df = excel_data[sheet_name]
            if df.shape[1] >= 18 and df.shape[0] > 10:  # Hoja con más columnas
                main_sheet = sheet_name
                break
        
        # Buscar hoja de proveedores (más pequeña)
        for sheet_name in sheet_names:
            if sheet_name != main_sheet:
                proveedores_sheet = sheet_name
                break
        
        if main_sheet is None:
            return {
                'status': 'error',
                'message': 'No se encontró hoja principal de compras',
                'data': {},
                'metadata': {'available_sheets': sheet_names}
            }
        
        # Procesar hoja principal
        df_main = excel_data[main_sheet].copy()
        
        # Buscar fila de headers (fila 6 según especificaciones)
        header_row = None
        for i in range(min(10, len(df_main))):
            row_values = df_main.iloc[i].astype(str).str.lower()
            if 'proveedor' in ' '.join(row_values.values):
                header_row = i
                break
        
        if header_row is None:
            return {
                'status': 'error',
                'message': 'No se encontró fila de headers con PROVEEDOR',
                'data': {},
                'metadata': {'sheet_preview': df_main.head().to_dict()}
            }
        
        # Extraer headers y datos
        headers = df_main.iloc[header_row].values
        data_rows = df_main.iloc[header_row + 1:].copy()
        
        # Mapear columnas según estructura real del Excel (C-R)
        column_mapping = {
            'C': 'proveedor',           # C) proveedor
            'D': 'producto',            # D) producto 
            'E': 'factura_num',         # E) número factura
            'F': 'fecha_factura',       # F) Fecha de Factura día-mes
            'G': 'total_factura',       # G) total factura
            'H': 'container',           # H) container
            'I': 'peso_kg',             # I) peso en kg
            'J': 'precio_kg',           # J) precio por kilogramo
            'K': 'etd',                 # K) ETD 
            'L': 'eta',                 # L) ETA 
            'M': 'naviera',             # M) naviera
            'N': 'conexion',            # N) tiempo de conexión ("7 DIAS")
            'O': 'demora',              # O) demora (columna vacía)
            'P': 'distribucion_pago',   # P) distribución de pagos
            'Q': 'dia_pago',            # Q) día de pago
            'R': 'estado_entrega'       # R) estado entrega
        }
        
        # Crear DataFrame procesado
        processed_data = []
        
        for idx, row in data_rows.iterrows():
            try:
                # Obtener valores por posición (columnas B=1, C=2, etc.)
                row_data = {}
                
                # C) Proveedor
                proveedor = _safe_get_value(row, 2, '')  # Columna C = índice 2
                if not proveedor or str(proveedor).strip() == '':
                    continue  # Saltar filas sin proveedor
                
                row_data['proveedor'] = str(proveedor).strip()
                
                # F) Fecha Factura
                fecha_factura = _parse_date(_safe_get_value(row, 5))  # Columna F = índice 5
                row_data['fecha_factura'] = fecha_factura
                row_data['mes'] = _extract_month(fecha_factura)
                
                # G) Total Factura
                total_factura = _parse_numeric(_safe_get_value(row, 6))  # Columna G = índice 6
                row_data['total_factura'] = total_factura
                
                # I) Peso en kg
                peso_raw = _safe_get_value(row, 8)  # Columna I = índice 8
                peso_kg = _parse_weight(peso_raw)
                row_data['peso_kg'] = peso_kg
                
                # J) Precio por kg
                precio_raw = _safe_get_value(row, 9)  # Columna J = índice 9
                precio_kg = _parse_price(precio_raw)
                row_data['precio_kg'] = precio_kg
                
                # N) Tiempo de conexión (CONEXION - formato "7 DIAS")
                conexion = _safe_get_value(row, 13, '')  # Columna N = índice 13
                row_data['tiempo_conexion'] = _parse_connection_time(conexion)
                
                # P) Distribución de pagos (porcentajes como 0.3, 0.4)
                distribucion_pago = _parse_numeric(_safe_get_value(row, 15))  # Columna P = índice 15
                row_data['distribucion_pago'] = distribucion_pago
                
                # Q) Día de pago (fechas)
                dia_pago = _parse_date(_safe_get_value(row, 16))  # Columna Q = índice 16
                row_data['dia_pago'] = dia_pago
                
                # R) Estado de entrega
                estado = _safe_get_value(row, 17, '')  # Columna R = índice 17
                row_data['estado_entrega'] = _parse_delivery_status(estado)
                
                # Campos calculados
                row_data['factura_num'] = _safe_get_value(row, 4, '')  # Columna E
                row_data['producto'] = _safe_get_value(row, 3, '')     # Columna D
                
                processed_data.append(row_data)
                
            except Exception as e:
                print(f"Error procesando fila {idx}: {e}")
                continue
        
        # Crear DataFrame final
        df_processed = pd.DataFrame(processed_data)
        
        if df_processed.empty:
            return {
                'status': 'error',
                'message': 'No se procesaron datos válidos',
                'data': {},
                'metadata': {'rows_attempted': len(data_rows)}
            }
        
        # Procesar información de proveedores si existe
        proveedores_info = {}
        if proveedores_sheet and proveedores_sheet in excel_data:
            proveedores_info = _process_proveedores_sheet(excel_data[proveedores_sheet])
        
        # Calcular métricas agregadas
        metrics = _calculate_metrics(df_processed)
        
        # Agrupar por mes
        monthly_data = _group_by_month(df_processed)
        
        return {
            'status': 'success',
            'message': f'Datos de compras CFI procesados correctamente: {len(df_processed)} registros',
            'data': {
                'compras_data': df_processed,
                'proveedores_info': proveedores_info,
                'monthly_data': monthly_data,
                'metrics': metrics
            },
            'metadata': {
                'total_records': len(df_processed),
                'months_count': len(monthly_data),
                'proveedores_count': df_processed['proveedor'].nunique(),
                'main_sheet': main_sheet,
                'proveedores_sheet': proveedores_sheet,
                'date_range': {
                    'min_date': df_processed['fecha_factura'].min() if not df_processed.empty else None,
                    'max_date': df_processed['fecha_factura'].max() if not df_processed.empty else None
                }
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error crítico procesando Excel de compras CFI: {str(e)}',
            'data': {},
            'metadata': {'exception': str(e)}
        }

def _safe_get_value(row, index, default=None):
    """Obtiene valor de manera segura por índice."""
    try:
        if index < len(row):
            value = row.iloc[index]
            if pd.isna(value) or value == '':
                return default
            return value
        return default
    except:
        return default

def _parse_date(date_value):
    """Parsea fecha desde Excel."""
    if pd.isna(date_value) or date_value == '':
        return None
    
    try:
        # Si ya es datetime
        if isinstance(date_value, (pd.Timestamp, datetime)):
            return date_value
        
        # Si es string, intentar parsear
        if isinstance(date_value, str):
            # Limpiar string
            date_str = str(date_value).strip()
            
            # Intentar diferentes formatos
            formats = ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
        
        # Si es número (Excel date serial)
        if isinstance(date_value, (int, float)):
            # Excel epoch starts at 1900-01-01
            excel_epoch = datetime(1900, 1, 1)
            return excel_epoch + timedelta(days=float(date_value) - 2)  # -2 for Excel bug
        
        return None
    except:
        return None

def _extract_month(date_value):
    """Extrae mes en formato texto."""
    if date_value is None:
        return None
    
    try:
        if isinstance(date_value, (pd.Timestamp, datetime)):
            months = {
                1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
                5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
                9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
            }
            return months.get(date_value.month, f'mes_{date_value.month}')
        return None
    except:
        return None

def _parse_numeric(value):
    """Parsea valor numérico."""
    if pd.isna(value) or value == '':
        return 0.0
    
    try:
        # Limpiar string si es necesario
        if isinstance(value, str):
            # Remover símbolos de moneda y espacios
            clean_value = re.sub(r'[€$,\s]', '', str(value))
            return float(clean_value)
        
        return float(value)
    except:
        return 0.0

def _parse_weight(weight_value):
    """Parsea peso desde string como '25000 kg'."""
    if pd.isna(weight_value) or weight_value == '':
        return 0.0
    
    try:
        if isinstance(weight_value, str):
            # Extraer números del string
            numbers = re.findall(r'[\d,\.]+', str(weight_value))
            if numbers:
                # Limpiar y convertir
                clean_number = numbers[0].replace(',', '')
                return float(clean_number)
        
        return float(weight_value)
    except:
        return 0.0

def _parse_price(price_value):
    """Parsea precio desde string como '1,20€/kg'."""
    if pd.isna(price_value) or price_value == '':
        return 0.0
    
    try:
        if isinstance(price_value, str):
            # Remover texto y símbolos, mantener números y comas decimales
            clean_price = re.sub(r'[€$/kgKG\s]', '', str(price_value))
            # Reemplazar coma decimal por punto
            clean_price = clean_price.replace(',', '.')
            return float(clean_price)
        
        return float(price_value)
    except:
        return 0.0

def _parse_connection_time(time_value):
    """Parsea tiempo de conexión desde formatos como '7 DIAS'."""
    if pd.isna(time_value) or time_value == '':
        return 0
    
    try:
        # Convertir a string y limpiar
        time_str = str(time_value).strip().upper()
        
        # Buscar patrones como "7 DIAS", "5 DÍAS", "10 DAYS", etc.
        if 'DIA' in time_str or 'DAY' in time_str:
            # Extraer número antes de DIAS/DAYS
            numbers = re.findall(r'\d+', time_str)
            if numbers:
                return int(numbers[0])
        
        # Si es solo un número
        numbers = re.findall(r'\d+', time_str)
        if numbers:
            return int(numbers[0])
        
        # Si es número directo
        return int(float(time_value))
    except:
        return 0

def _parse_delivery_status(status_value):
    """Parsea estado de entrega."""
    if pd.isna(status_value) or status_value == '':
        return 'EN PREPARACION'
    
    status_str = str(status_value).strip().upper()
    
    if 'ENTREGADO' in status_str:
        return 'ENTREGADO'
    elif 'EMBARCADO' in status_str:
        return 'EMBARCADO'
    else:
        return 'EN PREPARACION'

def _process_proveedores_sheet(df_proveedores):
    """Procesa hoja de información de proveedores."""
    try:
        proveedores_info = {}
        
        # Buscar fila de headers
        header_row = None
        for i in range(min(5, len(df_proveedores))):
            row_values = df_proveedores.iloc[i].astype(str).str.lower()
            if 'proveedor' in ' '.join(row_values.values):
                header_row = i
                break
        
        if header_row is not None:
            data_rows = df_proveedores.iloc[header_row + 1:]
            
            for _, row in data_rows.iterrows():
                proveedor = _safe_get_value(row, 1, '')  # Columna B
                telefono = _safe_get_value(row, 2, '')   # Columna C
                contacto = _safe_get_value(row, 3, '')   # Columna D
                direccion = _safe_get_value(row, 4, '')  # Columna E
                
                if proveedor:
                    proveedores_info[str(proveedor).strip()] = {
                        'telefono': str(telefono),
                        'contacto': str(contacto),
                        'direccion': str(direccion)
                    }
        
        return proveedores_info
    except:
        return {}

def _calculate_metrics(df):
    """Calcula métricas agregadas."""
    try:
        return {
            'total_compras': df['total_factura'].sum(),
            'total_peso_kg': df['peso_kg'].sum(),
            'precio_promedio_kg': df['precio_kg'].mean(),
            'proveedores_unicos': df['proveedor'].nunique(),
            'compras_count': len(df),
            'tiempo_conexion_promedio': df['tiempo_conexion'].mean()
        }
    except:
        return {}

def _group_by_month(df):
    """Agrupa datos por mes."""
    try:
        if 'mes' not in df.columns or df['mes'].isna().all():
            return {}
        
        monthly_data = {}
        
        for mes in df['mes'].dropna().unique():
            month_df = df[df['mes'] == mes]
            
            monthly_data[mes] = {
                'total_compras': month_df['total_factura'].sum(),
                'total_peso_kg': month_df['peso_kg'].sum(),
                'precio_promedio_kg': month_df['precio_kg'].mean(),
                'proveedores_activos': month_df['proveedor'].nunique(),
                'compras_count': len(month_df),
                'tiempo_conexion_promedio': month_df['tiempo_conexion'].mean(),
                'pedidos_entregados': len(month_df[month_df['estado_entrega'] == 'ENTREGADO']),
                'pedidos_embarcados': len(month_df[month_df['estado_entrega'] == 'EMBARCADO']),
                'pedidos_preparacion': len(month_df[month_df['estado_entrega'] == 'EN PREPARACION']),
                'proveedor_estrella': month_df.groupby('proveedor')['total_factura'].sum().idxmax() if not month_df.empty else None
            }
        
        return monthly_data
    except:
        return {}
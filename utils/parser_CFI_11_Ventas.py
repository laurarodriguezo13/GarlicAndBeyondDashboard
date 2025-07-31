"""
Parser CFI_11_Ventas - VERSIÓN CORREGIDA PARA ESTRUCTURA REAL
==============================================================
Parser optimizado para la estructura real del Excel "VENTAS Y PEDIDOS 2025".
Procesa las 3 hojas principales: Ventas 2025, Pedidos 2025, Contratos Abiertos 2025.

Estructura confirmada:
- Ventas 2025: Headers en fila 3, datos desde fila 4
- Pedidos 2025: Headers en fila 3, datos desde fila 4  
- Contratos Abiertos 2025: Headers en fila 3, datos desde fila 4

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 2.0 - Estructura Real Excel
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import Dict, Any, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

def parse_excel(raw_data) -> Dict[str, Any]:
    """
    Parser principal para datos de ventas CFI desde SharePoint.
    Procesa las 3 hojas principales según estructura real confirmada.
    """
    
    try:
        # ================================================================
        # VALIDACIÓN Y EXTRACCIÓN DE HOJAS
        # ================================================================
        
        if not isinstance(raw_data, dict):
            return {
                'status': 'error',
                'message': 'Formato de datos no válido - se esperaba diccionario con hojas',
                'data': None,
                'metadata': {
                    'error': 'Tipo de datos incorrecto',
                    'data_type': str(type(raw_data)),
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        # Buscar hojas principales
        ventas_sheet = None
        pedidos_sheet = None
        contratos_sheet = None
        
        for sheet_name, df in raw_data.items():
            sheet_lower = sheet_name.lower()
            if 'ventas 2025' in sheet_lower:
                ventas_sheet = df
            elif 'pedidos 2025' in sheet_lower:
                pedidos_sheet = df
            elif 'contratos abiertos 2025' in sheet_lower:
                contratos_sheet = df
        
        # Validar que encontramos las hojas necesarias
        missing_sheets = []
        if ventas_sheet is None:
            missing_sheets.append('Ventas 2025')
        if pedidos_sheet is None:
            missing_sheets.append('Pedidos 2025')
        if contratos_sheet is None:
            missing_sheets.append('Contratos Abiertos 2025')
        
        if missing_sheets:
            return {
                'status': 'error',
                'message': f'Hojas faltantes: {", ".join(missing_sheets)}',
                'data': None,
                'metadata': {
                    'error': 'Hojas requeridas no encontradas',
                    'missing_sheets': missing_sheets,
                    'available_sheets': list(raw_data.keys()),
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        # ================================================================
        # PROCESAMIENTO DE VENTAS 2025
        # ================================================================
        
        ventas_data = []
        ventas_errors = []
        
        try:
            # Headers en fila 3 (índice 2), datos desde fila 4 (índice 3)
            if len(ventas_sheet) > 3:
                
                # Mapeo de columnas para Ventas 2025 (confirmado por análisis)
                # A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8, J=9, K=10, L=11, M=12
                ventas_mapping = {
                    0: 'fecha_carga',    # A: FECHA CARGA
                    1: 'cliente',        # B: CLIENTE  
                    2: 'num_packing',    # C: Nº Packing COMAGRA
                    3: 'num_pedido',     # D: Nº PEDIDO CLIENTE
                    4: 'producto',       # E: PRODUCTO
                    5: 'facturado_por',  # F: FACTURADO POR
                    6: 'formato',        # G: FORMATO
                    7: 'incoterm',       # H: INCOTERM
                    8: 'pallets',        # I: PALLETS
                    9: 'kg',             # J: KG
                    10: 'precio',        # K: PRECIO
                    11: 'total'          # L: TOTAL
                }
                
                for idx in range(3, len(ventas_sheet)):  # Desde fila 4 (índice 3)
                    try:
                        row_data = {}
                        has_valid_data = False
                        
                        for col_idx, col_name in ventas_mapping.items():
                            if col_idx < len(ventas_sheet.columns):
                                value = ventas_sheet.iloc[idx, col_idx]
                                
                                if col_name == 'fecha_carga':
                                    if pd.notna(value):
                                        try:
                                            if isinstance(value, datetime):
                                                row_data[col_name] = value
                                            else:
                                                row_data[col_name] = pd.to_datetime(value)
                                            has_valid_data = True
                                        except:
                                            row_data[col_name] = None
                                    else:
                                        row_data[col_name] = None
                                
                                elif col_name in ['pallets', 'kg', 'precio', 'total']:
                                    if pd.notna(value) and value != '':
                                        try:
                                            numeric_val = float(str(value).replace(',', '.'))
                                            row_data[col_name] = numeric_val
                                            if numeric_val > 0:
                                                has_valid_data = True
                                        except:
                                            row_data[col_name] = 0.0
                                    else:
                                        row_data[col_name] = 0.0
                                
                                else:  # campos de texto
                                    if pd.notna(value) and str(value).strip() != '':
                                        row_data[col_name] = str(value).strip()
                                        if col_name in ['cliente', 'producto']:
                                            has_valid_data = True
                                    else:
                                        row_data[col_name] = ''
                        
                        # Solo agregar si tiene datos válidos
                        if has_valid_data and row_data.get('cliente', '').strip() != '':
                            # Agregar información de mes
                            fecha_obj = row_data.get('fecha_carga')
                            if isinstance(fecha_obj, datetime):
                                row_data['mes'] = f"{fecha_obj.month:02d}"
                                row_data['año'] = str(fecha_obj.year)
                                row_data['mes_nombre'] = get_month_name(fecha_obj.month)
                            else:
                                row_data['mes'] = '01'
                                row_data['año'] = '2025'
                                row_data['mes_nombre'] = 'enero'
                            
                            ventas_data.append(row_data)
                        
                    except Exception as e:
                        ventas_errors.append(f"Error fila {idx+1}: {str(e)}")
                        continue
                        
        except Exception as e:
            ventas_errors.append(f"Error procesando hoja Ventas 2025: {str(e)}")
        
        # ================================================================
        # PROCESAMIENTO DE PEDIDOS 2025
        # ================================================================
        
        pedidos_data = []
        pedidos_errors = []
        
        try:
            if len(pedidos_sheet) > 3:
                
                # Mapeo para Pedidos 2025 (estructura similar pero FECHA CARGA contiene meses)
                pedidos_mapping = {
                    0: 'fecha_carga',    # A: FECHA CARGA (contiene meses como "JULIO")
                    1: 'cliente',        # B: CLIENTE
                    2: 'num_packing',    # C: Nº Packing COMAGRA
                    3: 'num_pedido',     # D: Nº PEDIDO CLIENTE
                    4: 'producto',       # E: PRODUCTO
                    5: 'formato',        # F: FORMATO
                    6: 'incoterm',       # G: INCOTERM
                    7: 'pallets',        # H: PALLETS
                    8: 'kg',             # I: KG
                    9: 'precio',         # J: PRECIO
                    10: 'total'          # K: TOTAL
                }
                
                for idx in range(3, len(pedidos_sheet)):
                    try:
                        row_data = {}
                        has_valid_data = False
                        
                        for col_idx, col_name in pedidos_mapping.items():
                            if col_idx < len(pedidos_sheet.columns):
                                value = pedidos_sheet.iloc[idx, col_idx]
                                
                                if col_name == 'fecha_carga':
                                    # En Pedidos, fecha_carga contiene nombres de meses
                                    if pd.notna(value) and str(value).strip() != '':
                                        month_text = str(value).strip().upper()
                                        row_data[col_name] = month_text
                                        row_data['mes_nombre'] = month_text.lower()
                                        has_valid_data = True
                                    else:
                                        row_data[col_name] = ''
                                        row_data['mes_nombre'] = ''
                                
                                elif col_name in ['pallets', 'kg', 'precio', 'total']:
                                    if pd.notna(value) and value != '':
                                        try:
                                            numeric_val = float(str(value).replace(',', '.'))
                                            row_data[col_name] = numeric_val
                                            if numeric_val > 0:
                                                has_valid_data = True
                                        except:
                                            row_data[col_name] = 0.0
                                    else:
                                        row_data[col_name] = 0.0
                                
                                else:  # campos de texto
                                    if pd.notna(value) and str(value).strip() != '':
                                        row_data[col_name] = str(value).strip()
                                        if col_name in ['cliente', 'producto']:
                                            has_valid_data = True
                                    else:
                                        row_data[col_name] = ''
                        
                        if has_valid_data and row_data.get('cliente', '').strip() != '':
                            pedidos_data.append(row_data)
                        
                    except Exception as e:
                        pedidos_errors.append(f"Error fila {idx+1}: {str(e)}")
                        continue
                        
        except Exception as e:
            pedidos_errors.append(f"Error procesando hoja Pedidos 2025: {str(e)}")
        
        # ================================================================
        # PROCESAMIENTO DE CONTRATOS ABIERTOS 2025
        # ================================================================
        
        contratos_data = []
        contratos_errors = []
        
        try:
            if len(contratos_sheet) > 3:
                
                # Mapeo para Contratos Abiertos (estructura diferente)
                contratos_mapping = {
                    0: 'fecha',          # A: FECHA
                    1: 'estado',         # B: ESTADO
                    2: 'producto',       # C: PRODUCTO
                    3: 'medidas',        # D: MEDIDAS
                    4: 'incoterm',       # E: INCOTERM
                    5: 'kg',             # F: KG
                    6: 'precio',         # G: PRECIO
                    7: 'total'           # H: TOTAL
                }
                
                for idx in range(3, len(contratos_sheet)):
                    try:
                        row_data = {}
                        has_valid_data = False
                        
                        for col_idx, col_name in contratos_mapping.items():
                            if col_idx < len(contratos_sheet.columns):
                                value = contratos_sheet.iloc[idx, col_idx]
                                
                                if col_name in ['kg', 'precio', 'total']:
                                    if pd.notna(value) and value != '':
                                        try:
                                            numeric_val = float(str(value).replace(',', '.'))
                                            row_data[col_name] = numeric_val
                                            if numeric_val > 0:
                                                has_valid_data = True
                                        except:
                                            row_data[col_name] = 0.0
                                    else:
                                        row_data[col_name] = 0.0
                                
                                else:  # campos de texto
                                    if pd.notna(value) and str(value).strip() != '':
                                        row_data[col_name] = str(value).strip()
                                        if col_name in ['estado', 'producto']:
                                            has_valid_data = True
                                    else:
                                        row_data[col_name] = ''
                        
                        if has_valid_data:
                            contratos_data.append(row_data)
                        
                    except Exception as e:
                        contratos_errors.append(f"Error fila {idx+1}: {str(e)}")
                        continue
                        
        except Exception as e:
            contratos_errors.append(f"Error procesando hoja Contratos Abiertos: {str(e)}")
        
        # ================================================================
        # VALIDACIÓN FINAL Y CREACIÓN DE ESTRUCTURAS
        # ================================================================
        
        if not ventas_data:
            return {
                'status': 'error',
                'message': 'No se encontraron datos válidos en hoja Ventas 2025',
                'data': None,
                'metadata': {
                    'error': 'Sin datos de ventas válidos',
                    'ventas_errors': ventas_errors,
                    'pedidos_errors': pedidos_errors,
                    'contratos_errors': contratos_errors,
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        # Crear DataFrames
        ventas_df = pd.DataFrame(ventas_data)
        pedidos_df = pd.DataFrame(pedidos_data) if pedidos_data else pd.DataFrame()
        contratos_df = pd.DataFrame(contratos_data) if contratos_data else pd.DataFrame()
        
        # Generar resúmenes por mes
        monthly_summaries = generate_monthly_summaries(ventas_df)
        
        # Generar estadísticas generales
        general_stats = generate_general_stats(ventas_df)
        
        # ================================================================
        # RESULTADO EXITOSO
        # ================================================================
        
        return {
            'status': 'success',
            'message': f'Datos CFI procesados correctamente: {len(ventas_data)} ventas, {len(pedidos_data)} pedidos, {len(contratos_data)} contratos',
            'data': {
                'ventas': ventas_df,
                'pedidos': pedidos_df,
                'contratos_abiertos': contratos_df,
                'monthly_summaries': monthly_summaries,
                'general_stats': general_stats
            },
            'metadata': {
                'ventas_count': len(ventas_data),
                'pedidos_count': len(pedidos_data),
                'contratos_count': len(contratos_data),
                'months_with_data': list(monthly_summaries.keys()),
                'unique_months_found': len(monthly_summaries),
                'total_sales': float(ventas_df['total'].sum()) if not ventas_df.empty else 0,
                'total_kg': float(ventas_df['kg'].sum()) if not ventas_df.empty else 0,
                'unique_clients': int(ventas_df['cliente'].nunique()) if not ventas_df.empty else 0,
                'unique_products': int(ventas_df['producto'].nunique()) if not ventas_df.empty else 0,
                'processing_errors': {
                    'ventas': len(ventas_errors),
                    'pedidos': len(pedidos_errors),
                    'contratos': len(contratos_errors)
                },
                'timestamp': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error crítico procesando Excel CFI: {str(e)}',
            'data': None,
            'metadata': {
                'error': str(e),
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
        }

def get_month_name(month_num: int) -> str:
    """Convierte número de mes a nombre en español."""
    month_names = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    return month_names.get(month_num, f'mes_{month_num}')

def generate_monthly_summaries(ventas_df: pd.DataFrame) -> Dict[str, Dict]:
    """Genera resúmenes mensuales de ventas."""
    summaries = {}
    
    if ventas_df.empty:
        return summaries
    
    try:
        # Agrupar por mes_nombre
        for mes_nombre in ventas_df['mes_nombre'].unique():
            if pd.isna(mes_nombre) or mes_nombre == '':
                continue
                
            mes_data = ventas_df[ventas_df['mes_nombre'] == mes_nombre]
            
            if mes_data.empty:
                continue
            
            # Calcular métricas para KPIs
            summaries[mes_nombre] = {
                'ventas_totales': float(mes_data['total'].sum()),
                'kg_totales': float(mes_data['kg'].sum()),
                'pallets_totales': float(mes_data['pallets'].sum()),
                'clientes_activos': int(mes_data['cliente'].nunique()),
                'productos_vendidos': int(mes_data['producto'].nunique()),
                'precio_promedio': float(mes_data['precio'].mean()) if len(mes_data) > 0 else 0,
                'registros_totales': len(mes_data),
                
                # Cliente estrella
                'cliente_estrella': mes_data.groupby('cliente')['total'].sum().idxmax() if len(mes_data) > 0 else '',
                'cliente_estrella_ventas': float(mes_data.groupby('cliente')['total'].sum().max()) if len(mes_data) > 0 else 0,
                
                # Producto estrella
                'producto_estrella': mes_data.groupby('producto')['total'].sum().idxmax() if len(mes_data) > 0 else '',
                'producto_estrella_ventas': float(mes_data.groupby('producto')['total'].sum().max()) if len(mes_data) > 0 else 0,
            }
    
    except Exception as e:
        pass
    
    return summaries

def generate_general_stats(ventas_df: pd.DataFrame) -> Dict[str, Any]:
    """Genera estadísticas generales."""
    if ventas_df.empty:
        return {}
    
    try:
        return {
            'total_registros': len(ventas_df),
            'ventas_totales': float(ventas_df['total'].sum()),
            'kg_totales': float(ventas_df['kg'].sum()),
            'pallets_totales': float(ventas_df['pallets'].sum()),
            'clientes_unicos': int(ventas_df['cliente'].nunique()),
            'productos_unicos': int(ventas_df['producto'].nunique()),
            'precio_promedio_global': float(ventas_df['precio'].mean()),
            'venta_promedio': float(ventas_df['total'].mean()),
            'kg_promedio': float(ventas_df['kg'].mean()),
            
            # Top clientes
            'top_clientes': ventas_df.groupby('cliente')['total'].sum().nlargest(5).to_dict(),
            
            # Top productos  
            'top_productos': ventas_df.groupby('producto')['total'].sum().nlargest(5).to_dict(),
            
            # Distribución por facturado por
            'distribucion_facturado': ventas_df.groupby('facturado_por')['total'].sum().to_dict(),
        }
    
    except Exception as e:
        return {}

def validate_parsed_data(parsed_result: Dict[str, Any]) -> bool:
    """Valida que los datos parseados sean correctos."""
    try:
        if parsed_result.get('status') != 'success':
            return False
        
        data = parsed_result.get('data', {})
        
        # Verificar DataFrames principales
        if 'ventas' not in data or data['ventas'].empty:
            return False
        
        # Verificar columnas esenciales
        required_columns = ['fecha_carga', 'cliente', 'producto', 'total', 'kg', 'mes_nombre']
        ventas_df = data['ventas']
        
        for col in required_columns:
            if col not in ventas_df.columns:
                return False
        
        # Verificar que hay datos numéricos válidos
        if ventas_df['total'].sum() <= 0:
            return False
        
        return True
        
    except:
        return False
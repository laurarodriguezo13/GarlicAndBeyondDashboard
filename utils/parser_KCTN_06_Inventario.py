"""
KCTN_06_Inventario Parser - Sistema de Análisis de Inventario
============================================================
Parser específico para datos de inventario de KCTN.
Procesa la hoja "Inventario teorico" del Excel de entradas.

Estructura esperada:
- Fila 1: A1=Título, B1=Total Kg, C1=Total Euros
- Fila 2: Vacía
- Fila 3: A3=Proveedor, B3=Título Kgs, C3=Título Euros, D3=Título €/Kg
- Fila 4+: Datos de proveedores

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0 - Parser Inventario KCTN
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import warnings
from datetime import datetime
import re

warnings.filterwarnings('ignore')

class InventarioKCTNParser:
    """Parser especializado para datos de inventario KCTN."""
    
    def __init__(self, debug_mode: bool = False):
        """Inicializa el parser."""
        self.debug_mode = debug_mode
        self.processed_data = {}
        self.metadata = {
            'errors': [],
            'warnings': [],
            'processing_info': [],
            'sheet_analysis': []
        }
    
    def _log(self, message: str, level: str = 'info'):
        """Log interno para debugging."""
        if self.debug_mode:
            print(f"[{level.upper()}] {message}")
        
        if level == 'error':
            self.metadata['errors'].append(message)
        elif level == 'warning':
            self.metadata['warnings'].append(message)
        else:
            self.metadata['processing_info'].append(message)
    
    def _clean_numeric_value(self, value) -> float:
        """Limpia y convierte valores numéricos (formato europeo: 2.703.695 kg, 1,30 €)."""
        if pd.isna(value) or value == '' or value is None:
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remover caracteres no numéricos excepto punto, coma y signo menos
            cleaned = re.sub(r'[^\d.,\-]', '', str(value))
            
            # Formato europeo específico: 2.703.695,25 o 1,30
            if '.' in cleaned and ',' in cleaned:
                # Formato: 2.703.695,25 (punto=miles, coma=decimal)
                parts = cleaned.split(',')
                if len(parts) == 2:
                    # Remover puntos de la parte entera (separadores de miles)
                    integer_part = parts[0].replace('.', '')
                    decimal_part = parts[1]
                    cleaned = f"{integer_part}.{decimal_part}"
                else:
                    # Si hay problema, solo quitar puntos
                    cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned and '.' not in cleaned:
                # Solo coma: 1,30 (coma=decimal)
                cleaned = cleaned.replace(',', '.')
            elif '.' in cleaned and ',' not in cleaned:
                # Solo punto: verificar si es decimal o miles
                parts = cleaned.split('.')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Probablemente decimal: 1.30
                    cleaned = cleaned  # Mantener como está
                else:
                    # Probablemente miles: 2.703.695
                    cleaned = cleaned.replace('.', '')
            
            try:
                return float(cleaned) if cleaned else 0.0
            except ValueError:
                self._log(f"Error convirtiendo '{value}' -> '{cleaned}'", 'warning')
                return 0.0
        
        return 0.0
    
    def _analyze_sheet_structure(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Analiza la estructura de una hoja."""
        analysis = {
            'sheet_name': sheet_name,
            'shape': df.shape,
            'has_data': not df.empty,
            'first_5_rows': df.head().to_dict() if not df.empty else {},
            'column_count': len(df.columns),
            'row_count': len(df)
        }
        
        self.metadata['sheet_analysis'].append(analysis)
        return analysis
    
    def _extract_totals_from_row1(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extrae los totales de la fila 1 (B1 y C1)."""
        totals = {
            'total_kg': 0.0,
            'total_euros': 0.0
        }
        
        try:
            # B1 = Total Kg (índice 1)
            if len(df.columns) > 1 and len(df) > 0:
                total_kg_value = df.iloc[0, 1]  # Fila 0, Columna 1 (B1)
                totals['total_kg'] = self._clean_numeric_value(total_kg_value)
                self._log(f"Total Kg extraído: {totals['total_kg']}")
            
            # C1 = Total Euros (índice 2)
            if len(df.columns) > 2 and len(df) > 0:
                total_euros_value = df.iloc[0, 2]  # Fila 0, Columna 2 (C1)
                totals['total_euros'] = self._clean_numeric_value(total_euros_value)
                self._log(f"Total Euros extraído: {totals['total_euros']}")
                
        except Exception as e:
            self._log(f"Error extrayendo totales de fila 1: {e}", 'error')
        
        return totals
    
    def _extract_headers_from_row3(self, df: pd.DataFrame) -> List[str]:
        """Extrae los headers de la fila 3."""
        headers = []
        
        try:
            if len(df) > 2:  # Asegurar que existe fila 3 (índice 2)
                row3 = df.iloc[2]  # Fila 3 (índice 2)
                
                # Construir headers basándose en la estructura esperada
                headers = [
                    'Proveedor',    # A3
                    'Kg',           # B3
                    'Euros',        # C3
                    'Euros_por_Kg'  # D3
                ]
                
                # Verificar que los valores en row3 coincidan aproximadamente
                actual_headers = []
                for i, val in enumerate(row3[:4]):
                    if pd.notna(val) and str(val).strip():
                        actual_headers.append(str(val).strip())
                    else:
                        actual_headers.append(f"Col_{i+1}")
                
                self._log(f"Headers esperados: {headers}")
                self._log(f"Headers encontrados: {actual_headers}")
                
        except Exception as e:
            self._log(f"Error extrayendo headers de fila 3: {e}", 'error')
            # Headers por defecto
            headers = ['Proveedor', 'Kg', 'Euros', 'Euros_por_Kg']
        
        return headers
    
    def _extract_data_from_row4_onwards(self, df: pd.DataFrame, headers: List[str]) -> pd.DataFrame:
        """Extrae los datos desde la fila 4 en adelante."""
        data_rows = []
        
        try:
            if len(df) > 3:  # Debe haber al menos 4 filas (0,1,2,3)
                # Datos empiezan desde fila 4 (índice 3)
                data_df = df.iloc[3:].copy()
                
                # Asignar headers correctos
                data_df.columns = range(len(data_df.columns))  # Reset índices
                
                # Procesar cada fila de datos
                for idx, row in data_df.iterrows():
                    # Verificar que la fila no esté vacía
                    if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip():
                        
                        proveedor = str(row.iloc[0]).strip()
                        kg = self._clean_numeric_value(row.iloc[1] if len(row) > 1 else 0)
                        euros = self._clean_numeric_value(row.iloc[2] if len(row) > 2 else 0)
                        
                        # Calcular euros por kg
                        euros_por_kg = euros / kg if kg > 0 else 0
                        
                        # Si hay columna D3 con euros por kg, usar ese valor
                        if len(row) > 3:
                            euros_por_kg_orig = self._clean_numeric_value(row.iloc[3])
                            if euros_por_kg_orig > 0:
                                euros_por_kg = euros_por_kg_orig
                        
                        data_rows.append({
                            'Proveedor': proveedor,
                            'Kg': kg,
                            'Euros': euros,
                            'Euros_por_Kg': euros_por_kg
                        })
                
                self._log(f"Extraídas {len(data_rows)} filas de datos de proveedores")
                
        except Exception as e:
            self._log(f"Error extrayendo datos desde fila 4: {e}", 'error')
        
        # Crear DataFrame final
        if data_rows:
            result_df = pd.DataFrame(data_rows)
            
            # Filtrar filas con datos válidos
            result_df = result_df[
                (result_df['Kg'] > 0) | 
                (result_df['Euros'] > 0) | 
                (result_df['Proveedor'].str.len() > 0)
            ].copy()
            
            return result_df
        else:
            return pd.DataFrame(columns=['Proveedor', 'Kg', 'Euros', 'Euros_por_Kg'])
    
    def _find_inventario_sheet(self, excel_data: Dict[str, pd.DataFrame]) -> Optional[str]:
        """Encuentra la hoja de inventario teórico (específicamente hoja 4)."""
        # Nombres posibles basados en la estructura real vista
        possible_names = [
            'Inventario teorico',
            'Inventario teórico', 
            'Inventario Teorico',
            'Inventario Teórico',
            'inventario teorico',
            'inventario teórico',
            'Inventario',
            'inventario',
            'Hoja4',  # Por si viene como nombre genérico
            'Sheet4'
        ]
        
        # Buscar por nombre exacto primero
        for name in possible_names:
            if name in excel_data:
                self._log(f"Hoja de inventario encontrada: {name}")
                return name
        
        # Buscar por coincidencia parcial
        for sheet_name in excel_data.keys():
            sheet_lower = sheet_name.lower()
            if 'inventario' in sheet_lower and ('teorico' in sheet_lower or 'teórico' in sheet_lower):
                self._log(f"Hoja de inventario encontrada por coincidencia: {sheet_name}")
                return sheet_name
            elif 'inventario' in sheet_lower:
                self._log(f"Hoja con 'inventario' encontrada: {sheet_name}")
                return sheet_name
        
        # Si hay exactamente 4+ hojas, intentar la cuarta (índice 3)
        sheet_names = list(excel_data.keys())
        if len(sheet_names) >= 4:
            fourth_sheet = sheet_names[3]  # Hoja 4 (índice 3)
            self._log(f"Usando hoja 4 por posición: {fourth_sheet}")
            return fourth_sheet
        
        self._log("No se encontró hoja de inventario", 'error')
        self._log(f"Hojas disponibles: {list(excel_data.keys())}", 'error')
        return None
    
    def parse_inventario_data(self, excel_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Procesa los datos de inventario."""
        try:
            self._log("Iniciando procesamiento de datos de inventario")
            
            # Encontrar la hoja de inventario
            sheet_name = self._find_inventario_sheet(excel_data)
            if not sheet_name:
                available_sheets = list(excel_data.keys())
                self._log(f"Hojas disponibles: {available_sheets}", 'error')
                return {
                    'status': 'error',
                    'message': 'No se encontró la hoja de inventario teórico',
                    'data': {},
                    'metadata': self.metadata
                }
            
            df = excel_data[sheet_name]
            self._analyze_sheet_structure(df, sheet_name)
            
            if df.empty:
                self._log("La hoja de inventario está vacía", 'error')
                return {
                    'status': 'error',
                    'message': 'La hoja de inventario está vacía',
                    'data': {},
                    'metadata': self.metadata
                }
            
            # Extraer totales de la fila 1
            totals = self._extract_totals_from_row1(df)
            
            # Extraer headers de la fila 3
            headers = self._extract_headers_from_row3(df)
            
            # Extraer datos desde la fila 4
            inventario_df = self._extract_data_from_row4_onwards(df, headers)
            
            # Calcular estadísticas
            stats = self._calculate_inventario_stats(inventario_df, totals)
            
            # Preparar resultado
            result_data = {
                'inventario_dataframe': inventario_df,
                'totals': totals,
                'statistics': stats,
                'headers': headers,
                'processed_date': datetime.now().isoformat()
            }
            
            self._log(f"Procesamiento completado. {len(inventario_df)} proveedores procesados")
            
            return {
                'status': 'success',
                'message': f'Inventario procesado correctamente: {len(inventario_df)} proveedores',
                'data': result_data,
                'metadata': self.metadata
            }
            
        except Exception as e:
            self._log(f"Error crítico procesando inventario: {str(e)}", 'error')
            return {
                'status': 'error',
                'message': f'Error procesando inventario: {str(e)}',
                'data': {},
                'metadata': self.metadata
            }
    
    def _calculate_inventario_stats(self, df: pd.DataFrame, totals: Dict[str, float]) -> Dict[str, Any]:
        """Calcula estadísticas del inventario."""
        stats = {
            'total_proveedores': len(df),
            'total_kg_calculado': df['Kg'].sum() if not df.empty else 0,
            'total_euros_calculado': df['Euros'].sum() if not df.empty else 0,
            'total_kg_archivo': totals.get('total_kg', 0),
            'total_euros_archivo': totals.get('total_euros', 0),
            'precio_promedio_kg': 0,
            'proveedor_mayor_volumen': '',
            'proveedor_mayor_valor': '',
            'kg_promedio_por_proveedor': 0,
            'euros_promedio_por_proveedor': 0
        }
        
        try:
            if not df.empty and len(df) > 0:
                # Precio promedio por kg
                total_kg = stats['total_kg_calculado']
                total_euros = stats['total_euros_calculado']
                stats['precio_promedio_kg'] = total_euros / total_kg if total_kg > 0 else 0
                
                # Proveedor con mayor volumen (kg)
                max_kg_idx = df['Kg'].idxmax()
                stats['proveedor_mayor_volumen'] = df.loc[max_kg_idx, 'Proveedor']
                
                # Proveedor con mayor valor (euros)
                max_euros_idx = df['Euros'].idxmax()
                stats['proveedor_mayor_valor'] = df.loc[max_euros_idx, 'Proveedor']
                
                # Promedios
                stats['kg_promedio_por_proveedor'] = df['Kg'].mean()
                stats['euros_promedio_por_proveedor'] = df['Euros'].mean()
                
        except Exception as e:
            self._log(f"Error calculando estadísticas: {e}", 'warning')
        
        return stats


def parse_excel(excel_data: Dict[str, pd.DataFrame], debug_mode: bool = False) -> Dict[str, Any]:
    """
    Función principal para parsear datos de inventario KCTN.
    
    Args:
        excel_data: Diccionario con DataFrames de cada hoja
        debug_mode: Activar logging detallado
        
    Returns:
        Dict con resultado del procesamiento
    """
    try:
        parser = InventarioKCTNParser(debug_mode=debug_mode)
        return parser.parse_inventario_data(excel_data)
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error crítico en parser de inventario: {str(e)}',
            'data': {},
            'metadata': {'errors': [str(e)]}
        }


# Exportaciones
__all__ = [
    'InventarioKCTNParser',
    'parse_excel'
]
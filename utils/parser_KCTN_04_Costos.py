"""
Parser para KCTN_04_Costos - Control entrada M.P. Planta pelado
==============================================================
Procesa datos de Excel desde SharePoint para el módulo de Costos KCTN.

Estructura esperada del Excel:
- Hoja: "Desgrane Datos"
- Fila 1: Datos de totales/resumen
- Fila 2: Encabezados de columnas  
- Fila 3+: Datos reales

Autor: GANDB Dashboard Team
Fecha: 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
import warnings

warnings.filterwarnings('ignore')

# Meses en español
MESES_ESPANOL = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def parse_excel(raw_data: Union[pd.DataFrame, Dict[str, pd.DataFrame]]) -> Dict[str, Any]:
    """
    Función principal de parsing para KCTN_04_Costos.
    
    Args:
        raw_data: Datos del Excel desde SharePoint
        
    Returns:
        dict: Datos procesados con estructura estándar
    """
    try:
        # 1. Extraer DataFrame de los datos raw
        df = _extract_dataframe(raw_data)
        if df is None:
            return _create_error_response("No se pudo extraer DataFrame de los datos")
        
        # 2. Procesar datos
        processed_df = _process_data(df)
        if processed_df is None or processed_df.empty:
            return _create_error_response("Error procesando los datos del Excel")
        
        # 3. Validar datos
        validation_result = _validate_data(processed_df)
        if not validation_result['valid']:
            return _create_error_response(f"Datos inválidos: {validation_result['error']}")
        
        # 4. Calcular métricas
        metrics = _calculate_metrics(processed_df)
        
        # 5. Preparar respuesta exitosa
        return {
            'status': 'success',
            'data': processed_df,
            'metrics': metrics,
            'metadata': {
                'module_id': 'KCTN_04_Costos',
                'total_records': len(processed_df),
                'date_range': _get_date_range(processed_df),
                'providers': sorted(processed_df['proveedor'].unique().tolist()),
                'corredor_types': sorted(processed_df['corredor'].unique().tolist()),
                'processed_at': datetime.now().isoformat(),
                'columns': list(processed_df.columns),
                'months_with_data': sorted([MESES_ESPANOL[m] for m in processed_df['mes'].unique().tolist()]) if 'mes' in processed_df.columns else [],
                'months_with_data_nums': sorted(processed_df['mes'].unique().tolist()) if 'mes' in processed_df.columns else []
            }
        }
        
    except Exception as e:
        return _create_error_response(f"Error crítico en parsing: {str(e)}")

def _extract_dataframe(raw_data: Union[pd.DataFrame, Dict[str, pd.DataFrame]]) -> Optional[pd.DataFrame]:
    """Extrae el DataFrame desde los datos raw."""
    try:
        if isinstance(raw_data, pd.DataFrame):
            return raw_data
        elif isinstance(raw_data, dict):
            # Buscar la hoja "Desgrane Datos"
            if "Desgrane Datos" in raw_data:
                return raw_data["Desgrane Datos"]
            # Si no existe, usar la primera hoja disponible
            elif raw_data:
                first_key = list(raw_data.keys())[0]
                return raw_data[first_key]
        return None
    except Exception:
        return None

def _process_data(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Procesa y limpia el DataFrame."""
    try:
        # Verificar que el DataFrame tenga suficientes filas y columnas
        if df.shape[0] < 3 or df.shape[1] < 29:  # Mínimo 3 filas (header + 2 datos) y 29 columnas (A-AC)
            return None
        
        # Los encabezados están en la fila 2 (índice 1)
        headers = df.iloc[1].values.tolist()
        
        # Los datos empiezan desde la fila 3 (índice 2)
        data_df = df.iloc[2:].copy()
        data_df.columns = range(len(data_df.columns))  # Resetear índices de columnas
        
        # Mapear columnas según la estructura conocida
        column_mapping = {
            0: 'coste_kg_diente_cat1',     # A: € Kg diente Cat 1
            1: 'porcentaje_desg',          # B: % DESG
            2: 'porcentaje_cat1',          # C: % CAT I
            3: 'porcentaje_cat2',          # D: % CAT II
            4: 'porcentaje_dag',           # E: % DAG
            5: 'porcentaje_merma',         # F: % MERMA
            6: 'proveedor',                # G: Proveedor
            7: 'fecha_entrega',            # H: F. Entrega
            8: 'lote',                     # I: Lote
            9: 'albaran',                  # J: Albaran
            10: 'factura',                 # K: Factura
            11: 'entrada_en',              # L: Entrada en
            12: 'variedad',                # M: Variedad
            13: 'calibre',                 # N: Calibre
            14: 'kg_mp',                   # O: Kg. M.P.
            15: 'coste_kg_mp',             # P: € x Kg
            16: 'total_fra',               # Q: Total fra.
            17: 'corredor',                # R: Corredor
            18: 'coste_kg_corredor',       # S: coste por kg del corredor
            19: 'total_coste_corredor',    # T: Total coste del corredor
            20: 'porte',                   # U: Porte
            21: 'coste_kg_porte',          # V: €/Kg
            22: 'kg_desgranado',           # W: Kg. Desgrane
            23: 'kg_cat1_diente',          # X: Kg. Cat 1 diente
            24: 'kg_cat2_diente',          # Y: Kg. Cat 2 diente
            25: 'kg_dag',                  # Z: Kg. DAG
            26: 'porcentaje_estimado',     # AA: % Estimado
            27: 'diferencia',              # AB: Diferencia
            28: 'ubicacion'                # AC: Ubicacion
        }
        
        # Aplicar mapeo de columnas - solo mapear las que existen
        processed_df = pd.DataFrame()
        for col_idx, new_name in column_mapping.items():
            if col_idx < len(data_df.columns):
                processed_df[new_name] = data_df.iloc[:, col_idx]
            else:
                # Si no existe la columna, crear con valores por defecto
                if new_name in ['porcentaje_merma', 'ubicacion']:
                    processed_df[new_name] = np.nan if new_name == 'ubicacion' else 0.0
                else:
                    processed_df[new_name] = np.nan
        
        # Limpiar filas vacías (sin proveedor)
        processed_df = processed_df.dropna(subset=['proveedor'])
        processed_df = processed_df[processed_df['proveedor'].astype(str).str.strip() != '']
        
        if processed_df.empty:
            return None
        
        # Convertir tipos de datos
        processed_df = _convert_data_types(processed_df)
        
        # Limpiar y validar datos
        processed_df = _clean_data(processed_df)
        
        return processed_df
        
    except Exception as e:
        print(f"Error procesando datos: {e}")
        return None

def _convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte tipos de datos."""
    try:
        df = df.copy()
        
        # Columnas numéricas
        numeric_columns = [
            'coste_kg_diente_cat1', 'porcentaje_desg', 'porcentaje_cat1', 'porcentaje_cat2',
            'porcentaje_dag', 'porcentaje_merma', 'kg_mp', 'coste_kg_mp', 'total_fra',
            'coste_kg_corredor', 'total_coste_corredor', 'porte', 'coste_kg_porte',
            'kg_desgranado', 'kg_cat1_diente', 'kg_cat2_diente', 'kg_dag',
            'porcentaje_estimado', 'diferencia'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Columnas de texto
        text_columns = ['proveedor', 'lote', 'albaran', 'factura', 'entrada_en', 
                       'variedad', 'calibre', 'corredor', 'ubicacion']
        
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', '')
        
        # Conversión de fechas desde formato numérico de Excel
        if 'fecha_entrega' in df.columns:
            df['fecha_entrega'] = _convert_excel_dates(df['fecha_entrega'])
            df['mes'] = df['fecha_entrega'].dt.month
            df['año'] = df['fecha_entrega'].dt.year
            df['mes_nombre'] = df['mes'].map(MESES_ESPANOL)  # Nombres en español
        
        # Calcular porcentaje de merma si no existe o está vacío
        if 'porcentaje_merma' not in df.columns or df['porcentaje_merma'].isna().all():
            # Calcular merma como el restante después de otras categorías
            if all(col in df.columns for col in ['porcentaje_desg', 'porcentaje_cat1', 'porcentaje_cat2', 'porcentaje_dag']):
                df['porcentaje_merma'] = 1 - (df['porcentaje_desg'] + df['porcentaje_cat1'] + df['porcentaje_cat2'] + df['porcentaje_dag'])
                df['porcentaje_merma'] = df['porcentaje_merma'].clip(lower=0, upper=1)  # Entre 0 y 1
            else:
                df['porcentaje_merma'] = 0.0
        
        # Calcular kg de merma si no existe
        if 'kg_merma' not in df.columns and 'kg_mp' in df.columns:
            df['kg_merma'] = df['kg_mp'] * df['porcentaje_merma']
        
        return df
        
    except Exception as e:
        print(f"Error convirtiendo tipos: {e}")
        return df

def _convert_excel_dates(date_series: pd.Series) -> pd.Series:
    """Convierte fechas desde formato numérico de Excel."""
    try:
        # Excel fecha base: 1900-01-01, pero con ajuste por bug de Excel
        excel_base = datetime(1899, 12, 30)
        
        def convert_date(value):
            try:
                if pd.isna(value) or value == '':
                    return pd.NaT
                
                # Si ya es datetime, devolverlo
                if isinstance(value, datetime):
                    return value
                
                # Si es string que parece fecha, intentar parsear
                if isinstance(value, str):
                    try:
                        return pd.to_datetime(value)
                    except:
                        # Intentar convertir a número
                        value = float(value)
                
                # Si es número, convertir desde Excel
                if isinstance(value, (int, float)):
                    return excel_base + timedelta(days=float(value))
                
                return pd.NaT
                
            except:
                return pd.NaT
        
        return date_series.apply(convert_date)
        
    except Exception as e:
        print(f"Error convirtiendo fechas: {e}")
        return pd.to_datetime(date_series, errors='coerce')

def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y valida los datos."""
    try:
        df = df.copy()
        
        # Llenar valores faltantes numéricos con 0
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Verificar y corregir porcentajes (deben estar entre 0 y 1)
        percentage_columns = ['porcentaje_desg', 'porcentaje_cat1', 'porcentaje_cat2', 
                            'porcentaje_dag', 'porcentaje_merma', 'porcentaje_estimado']
        
        for col in percentage_columns:
            if col in df.columns:
                # Si los valores están entre 0-100, convertir a 0-1
                max_val = df[col].max()
                if pd.notna(max_val) and max_val > 1:
                    df[col] = df[col] / 100
                
                # Asegurar que están entre 0 y 1
                df[col] = df[col].clip(lower=0, upper=1)
        
        # Validar que los costes sean positivos
        cost_columns = ['coste_kg_diente_cat1', 'coste_kg_mp', 'total_fra', 
                       'coste_kg_corredor', 'total_coste_corredor', 'coste_kg_porte']
        
        for col in cost_columns:
            if col in df.columns:
                df[col] = df[col].abs()  # Asegurar valores positivos
        
        return df
        
    except Exception as e:
        print(f"Error limpiando datos: {e}")
        return df

def _validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Valida la integridad de los datos."""
    try:
        errors = []
        
        # Validar columnas requeridas
        required_columns = ['proveedor', 'fecha_entrega', 'kg_mp', 'total_fra']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Columnas faltantes: {missing_columns}")
        
        # Validar que hay datos
        if df.empty:
            errors.append("DataFrame vacío")
        
        # Validar fechas
        if 'fecha_entrega' in df.columns:
            invalid_dates = df['fecha_entrega'].isna().sum()
            if invalid_dates > len(df) * 0.5:  # Más del 50% de fechas inválidas
                errors.append(f"Demasiadas fechas inválidas: {invalid_dates}")
        
        # Validar datos numéricos básicos
        if 'kg_mp' in df.columns:
            if (df['kg_mp'] <= 0).all():
                errors.append("Todos los valores de kg_mp son <= 0")
        
        return {
            'valid': len(errors) == 0,
            'error': '; '.join(errors) if errors else None,
            'total_records': len(df),
            'validation_checks': len(errors) == 0
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"Error en validación: {str(e)}",
            'total_records': 0,
            'validation_checks': False
        }

def _calculate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula métricas agregadas para los KPIs."""
    try:
        metrics = {}
        
        # Totales
        metrics['total_kg_mp'] = float(df['kg_mp'].sum()) if 'kg_mp' in df.columns else 0
        metrics['total_kg_desgranado'] = float(df['kg_desgranado'].sum()) if 'kg_desgranado' in df.columns else 0
        metrics['total_kg_cat1'] = float(df['kg_cat1_diente'].sum()) if 'kg_cat1_diente' in df.columns else 0
        metrics['total_kg_cat2'] = float(df['kg_cat2_diente'].sum()) if 'kg_cat2_diente' in df.columns else 0
        metrics['total_kg_dag'] = float(df['kg_dag'].sum()) if 'kg_dag' in df.columns else 0
        metrics['total_fra'] = float(df['total_fra'].sum()) if 'total_fra' in df.columns else 0
        metrics['total_coste_corredor'] = float(df['total_coste_corredor'].sum()) if 'total_coste_corredor' in df.columns else 0
        metrics['total_porte'] = float(df['porte'].sum()) if 'porte' in df.columns else 0
        
        # Promedios ponderados
        if metrics['total_kg_mp'] > 0:
            metrics['promedio_porcentaje_desg'] = float(df['porcentaje_desg'].mean()) if 'porcentaje_desg' in df.columns else 0
            metrics['promedio_porcentaje_cat1'] = float(df['porcentaje_cat1'].mean()) if 'porcentaje_cat1' in df.columns else 0
            metrics['promedio_porcentaje_cat2'] = float(df['porcentaje_cat2'].mean()) if 'porcentaje_cat2' in df.columns else 0
            metrics['promedio_porcentaje_dag'] = float(df['porcentaje_dag'].mean()) if 'porcentaje_dag' in df.columns else 0
            metrics['promedio_porcentaje_merma'] = float(df['porcentaje_merma'].mean()) if 'porcentaje_merma' in df.columns else 0
            metrics['promedio_porcentaje_estimado'] = float(df['porcentaje_estimado'].mean()) if 'porcentaje_estimado' in df.columns else 0
            metrics['promedio_diferencia'] = float(df['diferencia'].mean()) if 'diferencia' in df.columns else 0
            
            # Costes promedios
            metrics['promedio_coste_kg_corredor'] = float(df['coste_kg_corredor'].mean()) if 'coste_kg_corredor' in df.columns else 0
            metrics['promedio_coste_kg_porte'] = float(df['coste_kg_porte'].mean()) if 'coste_kg_porte' in df.columns else 0
            metrics['promedio_coste_kg_diente_cat1'] = float(df['coste_kg_diente_cat1'].mean()) if 'coste_kg_diente_cat1' in df.columns else 0
            metrics['promedio_coste_kg_mp'] = float(df['coste_kg_mp'].mean()) if 'coste_kg_mp' in df.columns else 0
        else:
            metrics.update({
                'promedio_porcentaje_desg': 0,
                'promedio_porcentaje_cat1': 0,
                'promedio_porcentaje_cat2': 0,
                'promedio_porcentaje_dag': 0,
                'promedio_porcentaje_merma': 0,
                'promedio_porcentaje_estimado': 0,
                'promedio_diferencia': 0,
                'promedio_coste_kg_corredor': 0,
                'promedio_coste_kg_porte': 0,
                'promedio_coste_kg_diente_cat1': 0,
                'promedio_coste_kg_mp': 0
            })
        
        # Conteos
        metrics['total_proveedores'] = int(df['proveedor'].nunique()) if 'proveedor' in df.columns else 0
        metrics['total_corredores'] = int(df['corredor'].nunique()) if 'corredor' in df.columns else 0
        metrics['total_registros'] = len(df)
        
        return metrics
        
    except Exception as e:
        print(f"Error calculando métricas: {e}")
        return {}

def _get_date_range(df: pd.DataFrame) -> Dict[str, str]:
    """Obtiene el rango de fechas de los datos."""
    try:
        if 'fecha_entrega' not in df.columns:
            return {'min_date': None, 'max_date': None}
        
        dates = df['fecha_entrega'].dropna()
        if dates.empty:
            return {'min_date': None, 'max_date': None}
        
        return {
            'min_date': dates.min().strftime('%Y-%m-%d'),
            'max_date': dates.max().strftime('%Y-%m-%d')
        }
        
    except Exception:
        return {'min_date': None, 'max_date': None}

def _create_error_response(error_message: str) -> Dict[str, Any]:
    """Crea respuesta de error estándar."""
    return {
        'status': 'error',
        'data': pd.DataFrame(),
        'metrics': {},
        'metadata': {
            'module_id': 'KCTN_04_Costos',
            'error': error_message,
            'processed_at': datetime.now().isoformat(),
            'total_records': 0
        }
    }

# Función de testing para desarrollo
def test_parser():
    """Función de prueba para desarrollo local."""
    print("Parser KCTN_04_Costos - Test Mode")
    print("Función parse_excel() lista para recibir datos del excel_loader")
    return True

if __name__ == "__main__":
    test_parser()
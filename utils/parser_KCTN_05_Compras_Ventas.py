"""
parser_KCTN_05_Compras_Ventas.py - Parser VALIDADO para Módulo Compras y Ventas KCTN
====================================================================================
Parser especializado para procesar datos Excel de Compras y Ventas de KCTN
con mapeo EXACTO según especificaciones y validación rigurosa MEJORADA.

VALIDACIONES MEJORADAS:
✅ Verificación estricta de años múltiples (2020-2025)
✅ Validación de separación correcta por mes-año
✅ Control de calidad de datos mejorado
✅ Debug más detallado para identificar problemas
✅ Manejo robusto de datos multi-año

MAPEO VALIDADO:
COMPRAS (Página 4): C=F.Factura, D=Mes, E=Año, F=Numero Factura, G=Proveedor, 
                    H=Base Imponible, I=IVA, J=Total Factura, S=Departamento, T=Subdepartamento
VENTAS (Página 5):  A=Deudor, B=Año, C=Mes, D=Fecha, E=Factura, F=Cliente, G=Producto, 
                    H=Kgs, I=Euro/Kg, L=Total Factura

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 2.1 - VALIDADO y MEJORADO
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def parse_excel(excel_data):
    """
    Parser principal para datos de Compras y Ventas KCTN.
    VALIDADO para mapeo exacto según especificaciones con validación mejorada.
    
    Args:
        excel_data: Dict con DataFrames o un solo DataFrame
        
    Returns:
        dict: Estructura con datos parseados y metadata
    """
    
    try:
        print(f"🔍 DEBUG Parser v2.1: Iniciando parse_excel VALIDADO")
        
        # Validar entrada
        if excel_data is None:
            return {
                'status': 'error',
                'message': 'Datos Excel son None',
                'data': {},
                'metadata': {'error': 'No data provided'}
            }
        
        # Convertir a dict si es DataFrame único
        if isinstance(excel_data, pd.DataFrame):
            excel_data = {'Sheet1': excel_data}
        
        if not isinstance(excel_data, dict):
            return {
                'status': 'error', 
                'message': f'Tipo de datos no soportado: {type(excel_data)}',
                'data': {},
                'metadata': {'error': f'Unsupported data type: {type(excel_data)}'}
            }
        
        # Buscar hojas de Compras y Ventas
        compras_sheet = None
        ventas_sheet = None
        compras_sheet_name = None
        ventas_sheet_name = None
        
        print(f"🔍 DEBUG Parser v2.1: Hojas disponibles: {list(excel_data.keys())}")
        
        # Buscar hojas por nombre (flexibilidad en mayúsculas/minúsculas)
        for sheet_name, df in excel_data.items():
            sheet_lower = sheet_name.lower()
            print(f"🔍 DEBUG Parser v2.1: Evaluando hoja '{sheet_name}' (lowercase: '{sheet_lower}')")
            
            if 'compras' in sheet_lower and 'kctn' in sheet_lower:
                compras_sheet = df
                compras_sheet_name = sheet_name
                print(f"✅ DEBUG Parser v2.1: Hoja de compras encontrada: '{sheet_name}'")
            elif 'ventas' in sheet_lower and 'kctn' in sheet_lower:
                ventas_sheet = df
                ventas_sheet_name = sheet_name
                print(f"✅ DEBUG Parser v2.1: Hoja de ventas encontrada: '{sheet_name}'")
        
        # Si no se encuentran por nombre exacto, buscar por posición
        sheet_names = list(excel_data.keys())
        print(f"🔍 DEBUG Parser v2.1: Intentando búsqueda por posición. Total hojas: {len(sheet_names)}")
        
        if compras_sheet is None and len(sheet_names) >= 4:
            compras_sheet = excel_data[sheet_names[3]]  # Página 4 (índice 3)
            compras_sheet_name = sheet_names[3]
            print(f"🔍 DEBUG Parser v2.1: Usando hoja posición 4 para compras: '{compras_sheet_name}'")
        
        if ventas_sheet is None and len(sheet_names) >= 5:
            ventas_sheet = excel_data[sheet_names[4]]  # Página 5 (índice 4)
            ventas_sheet_name = sheet_names[4]
            print(f"🔍 DEBUG Parser v2.1: Usando hoja posición 5 para ventas: '{ventas_sheet_name}'")
        
        print(f"🔍 DEBUG Parser v2.1: Resultado búsqueda - Compras: {compras_sheet_name}, Ventas: {ventas_sheet_name}")
        
        # Procesar hojas encontradas
        parsed_data = {}
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'parser_version': '2.1_VALIDADO',
            'sheets_found': [],
            'sheets_processed': [],
            'errors': [],
            'warnings': [],
            'data_quality': {
                'total_compras_records': 0,
                'total_ventas_records': 0,
                'years_found': [],
                'months_found': [],
                'validation_passed': False
            },
            'debug_info': {
                'total_sheets': len(excel_data),
                'sheet_names': list(excel_data.keys()),
                'compras_sheet_found': compras_sheet_name,
                'ventas_sheet_found': ventas_sheet_name
            }
        }
        
        print(f"🔍 DEBUG Parser v2.1: Iniciando procesamiento de hojas")
        
        # Procesar Compras KCTN
        if compras_sheet is not None:
            metadata['sheets_found'].append(f'Compras: {compras_sheet_name}')
            print(f"🔍 DEBUG Parser v2.1: Procesando compras - Hoja: {compras_sheet_name}")
            
            try:
                compras_data = parse_compras_sheet_validated(compras_sheet)
                if compras_data is not None and not compras_data.empty:
                    parsed_data['compras'] = compras_data
                    metadata['sheets_processed'].append('compras')
                    metadata['data_quality']['total_compras_records'] = len(compras_data)
                    
                    # ✅ VALIDACIÓN MEJORADA: Verificar años y meses
                    if 'año' in compras_data.columns:
                        years_compras = sorted(compras_data['año'].unique())
                        metadata['data_quality']['years_found'].extend(years_compras)
                        print(f"✅ DEBUG Parser v2.1: Años en compras: {years_compras}")
                    
                    if 'mes' in compras_data.columns:
                        months_compras = sorted(compras_data['mes'].unique())
                        metadata['data_quality']['months_found'].extend(months_compras)
                        print(f"✅ DEBUG Parser v2.1: Meses en compras: {months_compras}")
                    
                    print(f"✅ DEBUG Parser v2.1: Compras procesadas exitosamente - {len(compras_data)} filas")
                    metadata['debug_info']['compras_final_shape'] = compras_data.shape
                    metadata['debug_info']['compras_columns'] = list(compras_data.columns)
                else:
                    error_msg = 'Hoja de compras procesada pero resultó vacía o None'
                    metadata['errors'].append(error_msg)
                    print(f"⚠️ DEBUG Parser v2.1: {error_msg}")
            except Exception as e:
                error_msg = f'Error procesando compras: {str(e)}'
                metadata['errors'].append(error_msg)
                print(f"❌ DEBUG Parser v2.1: {error_msg}")
                import traceback
                print(f"🔍 DEBUG Parser v2.1: Traceback compras: {traceback.format_exc()}")
        else:
            error_msg = 'Hoja de Compras KCTN no encontrada'
            metadata['errors'].append(error_msg)
            print(f"❌ DEBUG Parser v2.1: {error_msg}")
        
        # Procesar Ventas KCTN
        if ventas_sheet is not None:
            metadata['sheets_found'].append(f'Ventas: {ventas_sheet_name}')
            print(f"🔍 DEBUG Parser v2.1: Procesando ventas - Hoja: {ventas_sheet_name}")
            
            try:
                ventas_data = parse_ventas_sheet_validated(ventas_sheet)
                if ventas_data is not None and not ventas_data.empty:
                    parsed_data['ventas'] = ventas_data
                    metadata['sheets_processed'].append('ventas')
                    metadata['data_quality']['total_ventas_records'] = len(ventas_data)
                    
                    # ✅ VALIDACIÓN MEJORADA: Verificar años y meses
                    if 'año' in ventas_data.columns:
                        years_ventas = sorted(ventas_data['año'].unique())
                        metadata['data_quality']['years_found'].extend(years_ventas)
                        print(f"✅ DEBUG Parser v2.1: Años en ventas: {years_ventas}")
                    
                    if 'mes' in ventas_data.columns:
                        months_ventas = sorted(ventas_data['mes'].unique())
                        metadata['data_quality']['months_found'].extend(months_ventas)
                        print(f"✅ DEBUG Parser v2.1: Meses en ventas: {months_ventas}")
                    
                    print(f"✅ DEBUG Parser v2.1: Ventas procesadas exitosamente - {len(ventas_data)} filas")
                    metadata['debug_info']['ventas_final_shape'] = ventas_data.shape
                    metadata['debug_info']['ventas_columns'] = list(ventas_data.columns)
                else:
                    error_msg = 'Hoja de ventas procesada pero resultó vacía o None'
                    metadata['errors'].append(error_msg)
                    print(f"⚠️ DEBUG Parser v2.1: {error_msg}")
            except Exception as e:
                error_msg = f'Error procesando ventas: {str(e)}'
                metadata['errors'].append(error_msg)
                print(f"❌ DEBUG Parser v2.1: {error_msg}")
                import traceback
                print(f"🔍 DEBUG Parser v2.1: Traceback ventas: {traceback.format_exc()}")
        else:
            error_msg = 'Hoja de Ventas KCTN no encontrada'
            metadata['errors'].append(error_msg)
            print(f"❌ DEBUG Parser v2.1: {error_msg}")
        
        # ✅ VALIDACIÓN FINAL MEJORADA
        print(f"🔍 DEBUG Parser v2.1: Procesamiento completado")
        print(f"🔍 DEBUG Parser v2.1: Hojas procesadas exitosamente: {metadata['sheets_processed']}")
        print(f"🔍 DEBUG Parser v2.1: Errores encontrados: {len(metadata['errors'])}")
        
        # Consolidar años y meses únicos
        all_years = sorted(list(set(metadata['data_quality']['years_found'])))
        all_months = sorted(list(set(metadata['data_quality']['months_found'])))
        metadata['data_quality']['years_found'] = [int(y) for y in all_years if pd.notna(y) and y > 0]
        metadata['data_quality']['months_found'] = [int(m) for m in all_months if pd.notna(m) and 1 <= m <= 12]
        
        # ✅ VALIDACIÓN DE CALIDAD DE DATOS
        validation_checks = []
        
        # Check 1: Al menos una hoja procesada
        if len(parsed_data) > 0:
            validation_checks.append("✅ Al menos una hoja procesada")
        else:
            validation_checks.append("❌ Ninguna hoja procesada correctamente")
        
        # Check 2: Datos multi-año presentes
        if len(metadata['data_quality']['years_found']) > 1:
            validation_checks.append(f"✅ Datos multi-año encontrados: {metadata['data_quality']['years_found']}")
        elif len(metadata['data_quality']['years_found']) == 1:
            validation_checks.append(f"⚠️ Solo un año encontrado: {metadata['data_quality']['years_found']}")
        else:
            validation_checks.append("❌ No se encontraron años válidos")
        
        # Check 3: Meses válidos
        if len(metadata['data_quality']['months_found']) >= 1:
            validation_checks.append(f"✅ Meses válidos encontrados: {metadata['data_quality']['months_found']}")
        else:
            validation_checks.append("❌ No se encontraron meses válidos")
        
        # Check 4: Volumen de datos razonable
        total_records = metadata['data_quality']['total_compras_records'] + metadata['data_quality']['total_ventas_records']
        if total_records > 50:
            validation_checks.append(f"✅ Volumen de datos adecuado: {total_records} registros")
        elif total_records > 0:
            validation_checks.append(f"⚠️ Volumen de datos bajo: {total_records} registros")
        else:
            validation_checks.append("❌ Sin datos válidos")
        
        metadata['data_quality']['validation_checks'] = validation_checks
        metadata['data_quality']['validation_passed'] = all("✅" in check for check in validation_checks[:2])  # Al menos los 2 primeros deben pasar
        
        print(f"📊 DEBUG Parser v2.1: Validación de calidad:")
        for check in validation_checks:
            print(f"  {check}")
        
        # Determinar status final
        if len(parsed_data) == 0:
            print(f"❌ DEBUG Parser v2.1: Status FINAL = ERROR (sin datos)")
            return {
                'status': 'error',
                'message': 'No se pudieron procesar las hojas de Compras ni Ventas',
                'data': {},
                'metadata': metadata
            }
        elif len(metadata['errors']) > 0:
            print(f"⚠️ DEBUG Parser v2.1: Status FINAL = PARTIAL_SUCCESS ({len(parsed_data)} hojas de 2)")
            return {
                'status': 'partial_success',
                'message': f'Procesado parcialmente: {len(parsed_data)} hojas de 2',
                'data': parsed_data,
                'metadata': metadata
            }
        else:
            print(f"✅ DEBUG Parser v2.1: Status FINAL = SUCCESS ({len(parsed_data)} hojas)")
            print(f"📅 DEBUG Parser v2.1: Años encontrados: {metadata['data_quality']['years_found']}")
            print(f"📅 DEBUG Parser v2.1: Meses encontrados: {metadata['data_quality']['months_found']}")
            
            return {
                'status': 'success',
                'message': f'Procesadas correctamente {len(parsed_data)} hojas con validación exitosa',
                'data': parsed_data,
                'metadata': metadata
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error crítico en parser: {str(e)}',
            'data': {},
            'metadata': {'error': str(e), 'timestamp': datetime.now().isoformat()}
        }

def parse_compras_sheet_validated(df):
    """
    Procesa la hoja de Compras KCTN con validación MEJORADA.
    
    MAPEO VALIDADO:
    C=F.Factura, D=Mes, E=Año, F=Numero Factura, G=Proveedor, 
    H=Base Imponible, I=IVA, J=Total Factura, S=Departamento, T=Subdepartamento
    
    Estructura esperada:
    - Fila 1: Totales
    - Fila 2: Headers
    - Fila 3+: Datos
    """
    
    try:
        print(f"🔍 DEBUG parse_compras_sheet_validated: Iniciando procesamiento MEJORADO")
        
        if df is None or df.empty:
            print(f"❌ DEBUG parse_compras_sheet_validated: DataFrame inválido")
            return None
        
        print(f"🔍 DEBUG parse_compras_sheet_validated: Shape inicial: {df.shape}")
        
        # Crear copia y limpiar
        df_work = df.copy()
        df_work = df_work.dropna(how='all').dropna(axis=1, how='all')
        print(f"🔍 DEBUG parse_compras_sheet_validated: Shape después de limpiar: {df_work.shape}")
        
        if df_work.empty or len(df_work) < 3:
            print(f"❌ DEBUG parse_compras_sheet_validated: Datos insuficientes después de limpiar")
            return None
        
        # ✅ VALIDACIÓN MEJORADA: Verificar que tenemos suficientes columnas
        if len(df_work.columns) < 20:  # Necesitamos al menos hasta la columna T (19)
            print(f"⚠️ DEBUG parse_compras_sheet_validated: Pocas columnas encontradas: {len(df_work.columns)}")
        
        # MAPEO EXACTO SEGÚN ESPECIFICACIONES
        if len(df_work) > 1:
            headers = df_work.iloc[1].fillna('').astype(str).tolist()
            print(f"🔍 DEBUG parse_compras_sheet_validated: Headers encontrados: {headers[:20]}...")
            
            # MAPEO EXACTO DE COLUMNAS SEGÚN ESPECIFICACIONES
            new_columns = []
            for i in range(len(df_work.columns)):
                col_letter = chr(65 + i)  # A, B, C, D...
                
                # MAPEO EXACTO SEGÚN ESPECIFICACIONES
                if i == 2:  # C = F.Factura
                    new_columns.append('fecha_factura')
                    print(f"✅ Columna C ({i}) → fecha_factura")
                elif i == 3:  # D = Mes  
                    new_columns.append('mes')
                    print(f"✅ Columna D ({i}) → mes")
                elif i == 4:  # E = Año
                    new_columns.append('año')
                    print(f"✅ Columna E ({i}) → año")
                elif i == 5:  # F = Numero Factura  
                    new_columns.append('numero_factura')
                    print(f"✅ Columna F ({i}) → numero_factura")
                elif i == 6:  # G = Proveedor
                    new_columns.append('proveedor')
                    print(f"✅ Columna G ({i}) → proveedor")
                elif i == 7:  # H = Base Imponible
                    new_columns.append('base_imponible')
                    print(f"✅ Columna H ({i}) → base_imponible")
                elif i == 8:  # I = IVA
                    new_columns.append('iva')
                    print(f"✅ Columna I ({i}) → iva")
                elif i == 9:  # J = Total Factura
                    new_columns.append('total_factura')
                    print(f"✅ Columna J ({i}) → total_factura")
                elif i == 13:  # N = Fecha pago
                    new_columns.append('fecha_pago')
                    print(f"✅ Columna N ({i}) → fecha_pago")
                elif i == 14:  # O = Pagador
                    new_columns.append('pagador')
                    print(f"✅ Columna O ({i}) → pagador")
                elif i == 15:  # P = Pagado
                    new_columns.append('pagado')
                    print(f"✅ Columna P ({i}) → pagado")
                elif i == 17:  # R = Forma pago
                    new_columns.append('forma_pago')
                    print(f"✅ Columna R ({i}) → forma_pago")
                elif i == 18:  # S = Departamento
                    new_columns.append('departamento')
                    print(f"✅ Columna S ({i}) → departamento")
                elif i == 19:  # T = Subdepartamento
                    new_columns.append('subdepartamento')
                    print(f"✅ Columna T ({i}) → subdepartamento")
                else:
                    new_columns.append(f'col_{col_letter}')
            
            # Renombrar columnas
            df_work.columns = new_columns
            print(f"🔍 DEBUG parse_compras_sheet_validated: Columnas finales: {new_columns}")
        
        # Tomar datos desde fila 3 (índice 2)
        data_df = df_work.iloc[2:].copy()
        print(f"🔍 DEBUG parse_compras_sheet_validated: Shape datos iniciales: {data_df.shape}")
        
        # Limpiar filas vacías
        data_df = data_df.dropna(how='all')
        print(f"🔍 DEBUG parse_compras_sheet_validated: Shape después de eliminar filas vacías: {data_df.shape}")
        
        if data_df.empty:
            print(f"❌ DEBUG parse_compras_sheet_validated: No hay datos después de limpiar")
            return None
        
        # VALIDACIÓN CRÍTICA: Verificar columnas esenciales
        required_columns = ['mes', 'año', 'total_factura', 'proveedor', 'departamento', 'subdepartamento']
        missing_columns = [col for col in required_columns if col not in data_df.columns]
        if missing_columns:
            print(f"❌ DEBUG parse_compras_sheet_validated: Columnas críticas faltantes: {missing_columns}")
            return None
        
        # Convertir tipos de datos CORRECTAMENTE
        # Columnas numéricas
        numeric_columns = ['base_imponible', 'iva', 'total_factura', 'pagado']
        for col in numeric_columns:
            if col in data_df.columns:
                print(f"🔍 DEBUG parse_compras_sheet_validated: Convirtiendo columna numérica: {col}")
                data_df[col] = pd.to_numeric(data_df[col], errors='coerce').fillna(0)
        
        # Limpiar campos de texto CORRECTAMENTE
        text_columns = ['proveedor', 'departamento', 'subdepartamento', 'forma_pago', 'pagador']
        for col in text_columns:
            if col in data_df.columns:
                data_df[col] = data_df[col].astype(str).str.strip().replace('nan', '').replace('NaN', '')
        
        # ✅ VALIDACIÓN MEJORADA: Convertir mes y año con validación estricta
        if 'mes' in data_df.columns:
            print(f"🔍 DEBUG parse_compras_sheet_validated: Convirtiendo columna mes con validación")
            data_df['mes'] = pd.to_numeric(data_df['mes'], errors='coerce').fillna(0).astype(int)
            sample_mes = data_df['mes'].dropna().head(10).tolist()
            print(f"🔍 DEBUG parse_compras_sheet_validated: Muestra valores MES: {sample_mes}")
            
            # Validar rango de meses
            invalid_months = data_df[(data_df['mes'] < 1) | (data_df['mes'] > 12)]['mes'].unique()
            if len(invalid_months) > 0:
                print(f"⚠️ DEBUG parse_compras_sheet_validated: Meses inválidos encontrados: {invalid_months}")
            
        if 'año' in data_df.columns:
            print(f"🔍 DEBUG parse_compras_sheet_validated: Convirtiendo columna año con validación")
            data_df['año'] = pd.to_numeric(data_df['año'], errors='coerce').fillna(0).astype(int)
            sample_año = data_df['año'].dropna().head(10).tolist()
            print(f"🔍 DEBUG parse_compras_sheet_validated: Muestra valores AÑO: {sample_año}")
            
            # ✅ VALIDACIÓN MEJORADA: Verificar rango de años
            years_unique = data_df['año'].unique()
            valid_years = [y for y in years_unique if 2020 <= y <= 2025]
            invalid_years = [y for y in years_unique if y < 2020 or y > 2025]
            print(f"✅ DEBUG parse_compras_sheet_validated: Años válidos: {valid_years}")
            if invalid_years:
                print(f"⚠️ DEBUG parse_compras_sheet_validated: Años inválidos: {invalid_years}")
        
        # ✅ FILTRADO MEJORADO: Filtrar filas con datos válidos
        valid_rows = (
            (data_df['proveedor'] != '') & 
            (data_df['proveedor'] != 'nan') &
            (data_df['total_factura'] > 0) &
            (data_df['mes'] >= 1) & (data_df['mes'] <= 12) &
            (data_df['año'] >= 2020) & (data_df['año'] <= 2025)  # Rango más estricto
        )
        
        print(f"🔍 DEBUG parse_compras_sheet_validated: Filas válidas antes de filtrar: {len(data_df)}")
        data_df = data_df[valid_rows]
        print(f"🔍 DEBUG parse_compras_sheet_validated: Filas válidas después de filtrar: {len(data_df)}")
        
        # Reset índice
        data_df = data_df.reset_index(drop=True)
        
        # ✅ VALIDACIÓN FINAL MEJORADA
        if data_df.empty:
            print(f"❌ DEBUG parse_compras_sheet_validated: No hay datos válidos después del filtrado")
            return None
        
        # ✅ VALIDACIONES ADICIONALES DE CALIDAD
        print(f"✅ DEBUG parse_compras_sheet_validated: Procesamiento exitoso - Shape final: {data_df.shape}")
        print(f"✅ DEBUG parse_compras_sheet_validated: Columnas finales: {list(data_df.columns)}")
        
        # Validar datos de materia prima
        if 'departamento' in data_df.columns and 'subdepartamento' in data_df.columns:
            unique_deptos = data_df['departamento'].unique()
            unique_subdeptos = data_df['subdepartamento'].unique()
            print(f"✅ DEBUG parse_compras_sheet_validated: Departamentos únicos: {unique_deptos}")
            print(f"✅ DEBUG parse_compras_sheet_validated: Subdepartamentos únicos: {unique_subdeptos}")
            
            # Verificar si hay materia prima
            materia_prima_count = len(data_df[
                data_df['departamento'].str.contains('produccion', case=False, na=False) &
                data_df['subdepartamento'].str.contains('materia prima', case=False, na=False)
            ])
            print(f"✅ DEBUG parse_compras_sheet_validated: Registros de materia prima: {materia_prima_count}")
        
        # Validar distribución por años
        if 'año' in data_df.columns:
            year_distribution = data_df['año'].value_counts().sort_index()
            print(f"✅ DEBUG parse_compras_sheet_validated: Distribución por años: {dict(year_distribution)}")
        
        return data_df
        
    except Exception as e:
        print(f"❌ DEBUG parse_compras_sheet_validated: Error procesando: {e}")
        import traceback
        print(f"🔍 DEBUG parse_compras_sheet_validated: Traceback: {traceback.format_exc()}")
        return None

def parse_ventas_sheet_validated(df):
    """
    Procesa la hoja de Ventas KCTN con validación MEJORADA.
    
    MAPEO VALIDADO:
    A=Deudor, B=Año, C=Mes, D=Fecha, E=Factura, F=Cliente, G=Producto, 
    H=Kgs, I=Euro/Kg, J=Base imponible, K=IVA, L=Total Factura, M=Fecha cobro, N=Pagador, O=Cobrado
    
    Estructura esperada:
    - Fila 1: Totales
    - Fila 2: Headers  
    - Fila 3+: Datos
    """
    
    try:
        print(f"🔍 DEBUG parse_ventas_sheet_validated: Iniciando procesamiento MEJORADO")
        
        if df is None or df.empty:
            print(f"❌ DEBUG parse_ventas_sheet_validated: DataFrame inválido")
            return None
        
        print(f"🔍 DEBUG parse_ventas_sheet_validated: Shape inicial: {df.shape}")
        
        # Crear copia y limpiar
        df_work = df.copy()
        df_work = df_work.dropna(how='all').dropna(axis=1, how='all')
        print(f"🔍 DEBUG parse_ventas_sheet_validated: Shape después de limpiar: {df_work.shape}")
        
        if df_work.empty or len(df_work) < 3:
            print(f"❌ DEBUG parse_ventas_sheet_validated: Datos insuficientes después de limpiar")
            return None
        
        # ✅ VALIDACIÓN MEJORADA: Verificar que tenemos suficientes columnas
        if len(df_work.columns) < 15:  # Necesitamos al menos hasta la columna O (14)
            print(f"⚠️ DEBUG parse_ventas_sheet_validated: Pocas columnas encontradas: {len(df_work.columns)}")
        
        # MAPEO EXACTO SEGÚN ESPECIFICACIONES
        if len(df_work) > 1:
            headers = df_work.iloc[1].fillna('').astype(str).tolist()
            print(f"🔍 DEBUG parse_ventas_sheet_validated: Headers encontrados: {headers[:15]}...")
            
            # MAPEO EXACTO DE COLUMNAS SEGÚN ESPECIFICACIONES
            new_columns = []
            for i in range(len(df_work.columns)):
                col_letter = chr(65 + i)  # A, B, C, D...
                
                # MAPEO EXACTO SEGÚN ESPECIFICACIONES
                if i == 0:  # A = Deudor
                    new_columns.append('deudor')
                    print(f"✅ Columna A ({i}) → deudor")
                elif i == 1:  # B = Año
                    new_columns.append('año')
                    print(f"✅ Columna B ({i}) → año")
                elif i == 2:  # C = Mes
                    new_columns.append('mes')
                    print(f"✅ Columna C ({i}) → mes")
                elif i == 3:  # D = Fecha
                    new_columns.append('fecha')
                    print(f"✅ Columna D ({i}) → fecha")
                elif i == 4:  # E = Factura
                    new_columns.append('factura')
                    print(f"✅ Columna E ({i}) → factura")
                elif i == 5:  # F = Cliente
                    new_columns.append('cliente')
                    print(f"✅ Columna F ({i}) → cliente")
                elif i == 6:  # G = Producto
                    new_columns.append('producto')
                    print(f"✅ Columna G ({i}) → producto")
                elif i == 7:  # H = Kgs
                    new_columns.append('kgs')
                    print(f"✅ Columna H ({i}) → kgs")
                elif i == 8:  # I = Euro/Kg
                    new_columns.append('euro_kg')
                    print(f"✅ Columna I ({i}) → euro_kg")
                elif i == 9:  # J = Base imponible
                    new_columns.append('base_imponible')
                    print(f"✅ Columna J ({i}) → base_imponible")
                elif i == 10:  # K = IVA
                    new_columns.append('iva')
                    print(f"✅ Columna K ({i}) → iva")
                elif i == 11:  # L = Total Factura
                    new_columns.append('total_factura')
                    print(f"✅ Columna L ({i}) → total_factura")
                elif i == 12:  # M = Fecha cobro
                    new_columns.append('fecha_cobro')
                    print(f"✅ Columna M ({i}) → fecha_cobro")
                elif i == 13:  # N = Pagador
                    new_columns.append('pagador')
                    print(f"✅ Columna N ({i}) → pagador")
                elif i == 14:  # O = Cobrado
                    new_columns.append('cobrado')
                    print(f"✅ Columna O ({i}) → cobrado")
                else:
                    new_columns.append(f'col_{col_letter}')
            
            # Renombrar columnas
            df_work.columns = new_columns
            print(f"🔍 DEBUG parse_ventas_sheet_validated: Columnas finales: {new_columns}")
        
        # Tomar datos desde fila 3 (índice 2)
        data_df = df_work.iloc[2:].copy()
        print(f"🔍 DEBUG parse_ventas_sheet_validated: Shape datos iniciales: {data_df.shape}")
        
        # Limpiar filas vacías
        data_df = data_df.dropna(how='all')
        print(f"🔍 DEBUG parse_ventas_sheet_validated: Shape después de eliminar filas vacías: {data_df.shape}")
        
        if data_df.empty:
            print(f"❌ DEBUG parse_ventas_sheet_validated: No hay datos después de limpiar")
            return None
        
        # VALIDACIÓN CRÍTICA: Verificar columnas esenciales
        required_columns = ['mes', 'año', 'total_factura', 'cliente', 'producto']
        missing_columns = [col for col in required_columns if col not in data_df.columns]
        if missing_columns:
            print(f"❌ DEBUG parse_ventas_sheet_validated: Columnas críticas faltantes: {missing_columns}")
            return None
        
        # Convertir tipos de datos CORRECTAMENTE
        # Columnas numéricas
        numeric_columns = ['kgs', 'euro_kg', 'base_imponible', 'iva', 'total_factura', 'cobrado']
        for col in numeric_columns:
            if col in data_df.columns:
                print(f"🔍 DEBUG parse_ventas_sheet_validated: Convirtiendo columna numérica: {col}")
                data_df[col] = pd.to_numeric(data_df[col], errors='coerce').fillna(0)
        
        # Limpiar campos de texto CORRECTAMENTE
        text_columns = ['deudor', 'cliente', 'producto', 'pagador']
        for col in text_columns:
            if col in data_df.columns:
                data_df[col] = data_df[col].astype(str).str.strip().replace('nan', '').replace('NaN', '')
        
        # ✅ VALIDACIÓN MEJORADA: Convertir mes y año con validación estricta
        if 'mes' in data_df.columns:
            print(f"🔍 DEBUG parse_ventas_sheet_validated: Convirtiendo columna mes con validación")
            data_df['mes'] = pd.to_numeric(data_df['mes'], errors='coerce').fillna(0).astype(int)
            sample_mes = data_df['mes'].dropna().head(10).tolist()
            print(f"🔍 DEBUG parse_ventas_sheet_validated: Muestra valores MES: {sample_mes}")
            
            # Validar rango de meses
            invalid_months = data_df[(data_df['mes'] < 1) | (data_df['mes'] > 12)]['mes'].unique()
            if len(invalid_months) > 0:
                print(f"⚠️ DEBUG parse_ventas_sheet_validated: Meses inválidos encontrados: {invalid_months}")
            
        if 'año' in data_df.columns:
            print(f"🔍 DEBUG parse_ventas_sheet_validated: Convirtiendo columna año con validación")
            data_df['año'] = pd.to_numeric(data_df['año'], errors='coerce').fillna(0).astype(int)
            sample_año = data_df['año'].dropna().head(10).tolist()
            print(f"🔍 DEBUG parse_ventas_sheet_validated: Muestra valores AÑO: {sample_año}")
            
            # ✅ VALIDACIÓN MEJORADA: Verificar rango de años
            years_unique = data_df['año'].unique()
            valid_years = [y for y in years_unique if 2020 <= y <= 2025]
            invalid_years = [y for y in years_unique if y < 2020 or y > 2025]
            print(f"✅ DEBUG parse_ventas_sheet_validated: Años válidos: {valid_years}")
            if invalid_years:
                print(f"⚠️ DEBUG parse_ventas_sheet_validated: Años inválidos: {invalid_years}")
        
        # ✅ FILTRADO MEJORADO: Filtrar filas con datos válidos
        valid_rows = (
            (data_df['cliente'] != '') & 
            (data_df['cliente'] != 'nan') &
            (data_df['total_factura'] > 0) &
            (data_df['mes'] >= 1) & (data_df['mes'] <= 12) &
            (data_df['año'] >= 2020) & (data_df['año'] <= 2025)  # Rango más estricto
        )
        
        print(f"🔍 DEBUG parse_ventas_sheet_validated: Filas válidas antes de filtrar: {len(data_df)}")
        data_df = data_df[valid_rows]
        print(f"🔍 DEBUG parse_ventas_sheet_validated: Filas válidas después de filtrar: {len(data_df)}")
        
        # Reset índice
        data_df = data_df.reset_index(drop=True)
        
        # ✅ VALIDACIÓN FINAL MEJORADA
        if data_df.empty:
            print(f"❌ DEBUG parse_ventas_sheet_validated: No hay datos válidos después del filtrado")
            return None
        
        # ✅ VALIDACIONES ADICIONALES DE CALIDAD
        print(f"✅ DEBUG parse_ventas_sheet_validated: Procesamiento exitoso - Shape final: {data_df.shape}")
        print(f"✅ DEBUG parse_ventas_sheet_validated: Columnas finales: {list(data_df.columns)}")
        
        # Validar diversidad de productos y clientes
        if 'cliente' in data_df.columns:
            unique_clientes = data_df['cliente'].unique()
            print(f"✅ DEBUG parse_ventas_sheet_validated: Clientes únicos (muestra): {unique_clientes[:10]}")
            print(f"✅ DEBUG parse_ventas_sheet_validated: Total clientes únicos: {len(unique_clientes)}")
        
        if 'producto' in data_df.columns:
            unique_productos = data_df['producto'].unique()
            print(f"✅ DEBUG parse_ventas_sheet_validated: Productos únicos: {unique_productos}")
            print(f"✅ DEBUG parse_ventas_sheet_validated: Total productos únicos: {len(unique_productos)}")
        
        # Validar valores monetarios y kg
        if 'total_factura' in data_df.columns:
            sample_totals = data_df['total_factura'].dropna().head(10).tolist()
            total_sum = data_df['total_factura'].sum()
            print(f"✅ DEBUG parse_ventas_sheet_validated: Muestra total_factura: {sample_totals}")
            print(f"✅ DEBUG parse_ventas_sheet_validated: Suma total de facturación: {total_sum}")
        
        if 'kgs' in data_df.columns:
            sample_kgs = data_df['kgs'].dropna().head(10).tolist()
            total_kgs = data_df['kgs'].sum()
            print(f"✅ DEBUG parse_ventas_sheet_validated: Muestra kgs: {sample_kgs}")
            print(f"✅ DEBUG parse_ventas_sheet_validated: Suma total de kgs: {total_kgs}")
        
        # Validar distribución por años
        if 'año' in data_df.columns:
            year_distribution = data_df['año'].value_counts().sort_index()
            print(f"✅ DEBUG parse_ventas_sheet_validated: Distribución por años: {dict(year_distribution)}")
        
        return data_df
        
    except Exception as e:
        print(f"❌ DEBUG parse_ventas_sheet_validated: Error procesando: {e}")
        import traceback
        print(f"🔍 DEBUG parse_ventas_sheet_validated: Traceback: {traceback.format_exc()}")
        return None

def get_available_months(compras_df=None, ventas_df=None):
    """
    Obtiene lista de meses con años disponibles en los datos.
    ✅ VALIDADO para formato mes-año correcto.
    """
    month_year_combinations = set()
    
    month_names = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    if compras_df is not None and 'mes' in compras_df.columns and 'año' in compras_df.columns:
        compras_combinations = compras_df[['mes', 'año']].drop_duplicates()
        for _, row in compras_combinations.iterrows():
            if 1 <= row['mes'] <= 12 and 2020 <= row['año'] <= 2025:
                month_year_key = f"{month_names[row['mes']]} {row['año']}"
                month_year_combinations.add(month_year_key)
    
    if ventas_df is not None and 'mes' in ventas_df.columns and 'año' in ventas_df.columns:
        ventas_combinations = ventas_df[['mes', 'año']].drop_duplicates()
        for _, row in ventas_combinations.iterrows():
            if 1 <= row['mes'] <= 12 and 2020 <= row['año'] <= 2025:
                month_year_key = f"{month_names[row['mes']]} {row['año']}"
                month_year_combinations.add(month_year_key)
    
    # Ordenar cronológicamente
    def sort_key(month_year_str):
        try:
            parts = month_year_str.split()
            if len(parts) == 2:
                month_name, year_str = parts
                month_num = {v: k for k, v in month_names.items()}.get(month_name, 0)
                year_num = int(year_str)
                return (year_num, month_num)
        except:
            pass
        return (0, 0)
    
    available = sorted(list(month_year_combinations), key=sort_key)
    return available

# Función de utilidad para testing MEJORADA
def validate_parsed_data_enhanced(parsed_result):
    """Valida que los datos parseados tengan la estructura correcta con validaciones MEJORADAS."""
    
    if not isinstance(parsed_result, dict):
        return False, "Resultado no es un diccionario"
    
    required_keys = ['status', 'message', 'data', 'metadata']
    for key in required_keys:
        if key not in parsed_result:
            return False, f"Clave requerida '{key}' no encontrada"
    
    if parsed_result['status'] not in ['success', 'partial_success', 'error']:
        return False, f"Status inválido: {parsed_result['status']}"
    
    # ✅ VALIDACIONES MEJORADAS
    metadata = parsed_result.get('metadata', {})
    data_quality = metadata.get('data_quality', {})
    
    # Validar que hay datos multi-año si el status es success
    if parsed_result['status'] == 'success':
        years_found = data_quality.get('years_found', [])
        if len(years_found) == 0:
            return False, "Success status pero no se encontraron años válidos"
        
        months_found = data_quality.get('months_found', [])
        if len(months_found) == 0:
            return False, "Success status pero no se encontraron meses válidos"
        
        total_records = data_quality.get('total_compras_records', 0) + data_quality.get('total_ventas_records', 0)
        if total_records == 0:
            return False, "Success status pero no hay registros de datos"
    
    return True, "Estructura válida con validaciones mejoradas"
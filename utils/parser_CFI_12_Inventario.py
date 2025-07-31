"""
parser_CFI_12_Inventario.py - Parser para Inventario CFI
=======================================================
Parser específico para procesar datos de inventario de CFI (Comagra Food Ingredients).
Procesa archivos Excel con hojas mensuales de existencias de productos.

Estructura esperada del Excel:
- Hojas: Enero, Febrero, Marzo, ..., Diciembre (2025)
- Columnas: A(Código), B(Tipo), C(Nombre), D(Kilos), E(Precio), F(Valor)

Funcionalidades:
- Procesamiento de todas las hojas mensuales
- Validación de estructura de datos
- Limpieza y normalización de tipos de productos
- Cálculos de agregaciones por tipo
- Manejo de productos "ajo" vs "no ajo"

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
import re
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

def parse_excel(excel_data: Union[Dict[str, pd.DataFrame], pd.DataFrame]) -> Dict[str, Any]:
    """
    Parser principal para datos de inventario CFI.
    
    Args:
        excel_data: Diccionario con hojas del Excel o DataFrame único
        
    Returns:
        Dict con estructura:
        {
            'status': 'success' | 'error',
            'message': str,
            'data': Dict[mes: DataFrame],
            'metadata': Dict con información adicional
        }
    """
    
    try:
        # Validar entrada
        if excel_data is None:
            return {
                'status': 'error',
                'message': 'No se proporcionaron datos de Excel',
                'data': {},
                'metadata': {'errors': ['Datos Excel vacíos']}
            }
        
        # Si es DataFrame único, convertir a diccionario
        if isinstance(excel_data, pd.DataFrame):
            excel_data = {'Hoja1': excel_data}
        
        # Verificar que es diccionario
        if not isinstance(excel_data, dict):
            return {
                'status': 'error',
                'message': 'Formato de datos Excel inválido',
                'data': {},
                'metadata': {'errors': ['Formato de datos incorrecto']}
            }
        
        # Meses esperados
        meses_esperados = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        
        # Diccionario para almacenar datos parseados
        data_parseada = {}
        errores = []
        meses_procesados = []
        meses_vacios = []
        total_productos = 0
        tipos_productos_unicos = set()
        
        # Procesar cada hoja del Excel
        for hoja_nombre, df in excel_data.items():
            try:
                # Normalizar nombre de hoja (remover espacios)
                mes_normalizado = hoja_nombre.strip()
                
                # Verificar si es un mes válido
                if mes_normalizado not in meses_esperados:
                    # Buscar mes similar (por si hay espacios extra)
                    mes_encontrado = None
                    for mes in meses_esperados:
                        if mes.lower() in mes_normalizado.lower():
                            mes_encontrado = mes
                            break
                    
                    if mes_encontrado:
                        mes_normalizado = mes_encontrado
                    else:
                        errores.append(f"Hoja '{hoja_nombre}' no es un mes válido")
                        continue
                
                # Procesar datos del mes
                datos_mes = procesar_mes(df, mes_normalizado)
                
                if datos_mes is not None and not datos_mes.empty:
                    data_parseada[mes_normalizado] = datos_mes
                    meses_procesados.append(mes_normalizado)
                    total_productos += len(datos_mes)
                    
                    # Recopilar tipos únicos
                    tipos_productos_unicos.update(datos_mes['tipo'].unique())
                else:
                    meses_vacios.append(mes_normalizado)
                    
            except Exception as e:
                errores.append(f"Error procesando hoja '{hoja_nombre}': {str(e)}")
                continue
        
        # Verificar si se procesaron datos
        if not data_parseada:
            return {
                'status': 'error',
                'message': 'No se pudieron procesar datos de ningún mes',
                'data': {},
                'metadata': {
                    'errors': errores,
                    'meses_intentados': list(excel_data.keys())
                }
            }
        
        # Crear metadata
        metadata = {
            'meses_procesados': meses_procesados,
            'meses_vacios': meses_vacios,
            'total_productos': total_productos,
            'tipos_productos_count': len(tipos_productos_unicos),
            'tipos_productos': sorted(list(tipos_productos_unicos)),
            'meses_con_datos': len(meses_procesados),
            'errors': errores,
            'processed_at': datetime.now().isoformat(),
            'source': 'CFI_12_Inventario'
        }
        
        # Análisis adicional de tipos de productos
        productos_ajo = [tipo for tipo in tipos_productos_unicos if tipo != 'no ajo']
        productos_no_ajo = ['no ajo'] if 'no ajo' in tipos_productos_unicos else []
        
        metadata.update({
            'productos_ajo_tipos': len(productos_ajo),
            'productos_ajo_lista': sorted(productos_ajo),
            'tiene_productos_no_ajo': len(productos_no_ajo) > 0
        })
        
        return {
            'status': 'success',
            'message': f'Inventario CFI parseado exitosamente: {len(meses_procesados)} meses',
            'data': data_parseada,
            'metadata': metadata
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error crítico parseando inventario CFI: {str(e)}',
            'data': {},
            'metadata': {'errors': [f'Error crítico: {str(e)}']}
        }

def procesar_mes(df: pd.DataFrame, mes: str) -> Optional[pd.DataFrame]:
    """
    Procesa datos de un mes específico.
    
    Args:
        df: DataFrame con datos del mes
        mes: Nombre del mes
        
    Returns:
        DataFrame procesado o None si hay error
    """
    
    try:
        # Verificar que el DataFrame no esté vacío
        if df is None or df.empty:
            return None
        
        # Copiar DataFrame para no modificar original
        datos = df.copy()
        
        # Si el DataFrame tiene menos de 6 columnas, es inválido
        if len(datos.columns) < 6:
            return None
        
        # Renombrar columnas esperadas
        if len(datos.columns) >= 6:
            datos.columns = ['codigo', 'tipo', 'nombre', 'kilos', 'precio', 'valor'] + list(datos.columns[6:])
        else:
            return None
        
        # Filtrar filas válidas
        # 1. Eliminar filas con valores nulos en columnas críticas
        datos = datos.dropna(subset=['codigo', 'tipo', 'nombre'])
        
        # 2. Eliminar filas de encabezado
        datos = datos[
            (datos['codigo'] != 'CODIGO') & 
            (datos['tipo'] != 'tipo') &
            (datos['codigo'].astype(str).str.len() > 5)  # Los códigos reales son largos
        ]
        
        # 3. Filtrar filas con códigos válidos
        datos = datos[datos['codigo'].astype(str).str.contains(r'^[A-Z0-9]', na=False)]
        
        # Si no quedan datos válidos
        if datos.empty:
            return None
        
        # Limpiar y convertir tipos de datos
        datos = limpiar_datos(datos)
        
        # Agregar columna de mes
        datos['mes'] = mes
        
        # Agregar análisis de productos ajo vs no ajo
        datos['es_ajo'] = datos['tipo'] != 'no ajo'
        
        # Validar datos numéricos
        datos = validar_datos_numericos(datos)
        
        return datos
        
    except Exception as e:
        print(f"Error procesando mes {mes}: {str(e)}")
        return None

def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y normaliza los datos del DataFrame.
    
    Args:
        df: DataFrame a limpiar
        
    Returns:
        DataFrame limpio
    """
    
    # Copiar DataFrame
    datos = df.copy()
    
    # Limpiar strings
    columnas_string = ['codigo', 'tipo', 'nombre']
    for col in columnas_string:
        if col in datos.columns:
            datos[col] = datos[col].astype(str).str.strip()
            datos[col] = datos[col].replace('nan', '')
    
    # Limpiar tipos de producto
    if 'tipo' in datos.columns:
        datos['tipo'] = datos['tipo'].str.lower().str.strip()
        
        # Normalizar tipos conocidos
        normalizaciones = {
            'no ajo': 'no ajo',
            'ajo dado conv.': 'ajo dado conv.',
            'ajo diente entero': 'ajo diente entero',
            'ajo dado eco': 'ajo dado eco',
            'ajo pellet natural': 'ajo pellet natural',
            'rechazo ajo diente': 'rechazo ajo diente',
            'ajo diente asado': 'ajo diente asado',
            'ajo diente conv.': 'ajo diente conv.',
            'ajo diente': 'ajo diente',
            'ajo pellet asado': 'ajo pellet asado',
        }
        
        for tipo_original, tipo_normalizado in normalizaciones.items():
            datos.loc[datos['tipo'].str.contains(tipo_original, na=False), 'tipo'] = tipo_normalizado
    
    return datos

def validar_datos_numericos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida y convierte datos numéricos.
    
    Args:
        df: DataFrame a validar
        
    Returns:
        DataFrame con datos numéricos validados
    """
    
    datos = df.copy()
    
    # Columnas numéricas esperadas
    columnas_numericas = ['kilos', 'precio', 'valor']
    
    for col in columnas_numericas:
        if col in datos.columns:
            # Convertir a numérico, convirtiendo errores en NaN
            datos[col] = pd.to_numeric(datos[col], errors='coerce')
            
            # Rellenar NaN con 0 para cálculos
            datos[col] = datos[col].fillna(0)
            
            # Asegurar que no hay valores negativos (excepto en casos específicos)
            if col in ['kilos', 'valor']:
                datos[col] = datos[col].abs()  # Convertir negativos a positivos
    
    # Verificar consistencia: valor debería ser aprox. kilos * precio
    if all(col in datos.columns for col in ['kilos', 'precio', 'valor']):
        # Calcular valor esperado
        datos['valor_calculado'] = datos['kilos'] * datos['precio']
        
        # Si el valor está muy alejado del calculado y el calculado > 0, usar el calculado
        diferencia_umbral = 0.1  # 10% de diferencia
        mask_corregir = (
            (datos['valor'] == 0) & (datos['valor_calculado'] > 0)
        ) | (
            (datos['valor'] > 0) & (datos['valor_calculado'] > 0) &
            (abs(datos['valor'] - datos['valor_calculado']) / datos['valor'] > diferencia_umbral)
        )
        
        # Solo corregir si hay pocos casos (no cambiar toda la estructura)
        if mask_corregir.sum() < len(datos) * 0.1:  # Menos del 10% de los datos
            datos.loc[mask_corregir, 'valor'] = datos.loc[mask_corregir, 'valor_calculado']
        
        # Eliminar columna temporal
        datos = datos.drop('valor_calculado', axis=1)
    
    return datos

def calcular_kpis_mes(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula KPIs para un mes específico.
    
    Args:
        df: DataFrame con datos del mes
        
    Returns:
        Dict con KPIs calculados
    """
    
    if df is None or df.empty:
        return {
            'total_productos': 0,
            'total_kilos': 0,
            'total_valor': 0,
            'precio_promedio': 0,
            'tipos_productos': [],
            'productos_ajo': 0,
            'productos_no_ajo': 0
        }
    
    # KPIs básicos
    kpis = {
        'total_productos': len(df),
        'total_kilos': df['kilos'].sum(),
        'total_valor': df['valor'].sum(),
        'precio_promedio': df['precio'].mean() if len(df) > 0 else 0,
        'tipos_productos': df['tipo'].unique().tolist(),
        'cantidad_tipos': df['tipo'].nunique()
    }
    
    # Análisis ajo vs no ajo
    productos_ajo = df[df['tipo'] != 'no ajo']
    productos_no_ajo = df[df['tipo'] == 'no ajo']
    
    kpis.update({
        'productos_ajo': len(productos_ajo),
        'productos_no_ajo': len(productos_no_ajo),
        'kilos_ajo': productos_ajo['kilos'].sum(),
        'kilos_no_ajo': productos_no_ajo['kilos'].sum(),
        'valor_ajo': productos_ajo['valor'].sum(),
        'valor_no_ajo': productos_no_ajo['valor'].sum()
    })
    
    # Agregación por tipo
    agregacion_tipos = df.groupby('tipo').agg({
        'kilos': 'sum',
        'precio': 'mean',
        'valor': 'sum',
        'codigo': 'count'
    }).rename(columns={'codigo': 'cantidad_productos'})
    
    kpis['agregacion_tipos'] = agregacion_tipos.to_dict('index')
    
    # Producto estrella (mayor valor)
    if not df.empty:
        idx_estrella = df['valor'].idxmax()
        producto_estrella = df.loc[idx_estrella]
        kpis['producto_estrella'] = {
            'codigo': producto_estrella['codigo'],
            'nombre': producto_estrella['nombre'],
            'tipo': producto_estrella['tipo'],
            'valor': producto_estrella['valor'],
            'kilos': producto_estrella['kilos']
        }
    
    return kpis

# Funciones auxiliares para el controller
def get_available_months(data: Dict[str, pd.DataFrame]) -> List[str]:
    """Obtiene lista de meses disponibles."""
    meses_orden = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    return [mes for mes in meses_orden if mes in data and not data[mes].empty]

def get_available_tipos(data: Dict[str, pd.DataFrame], mes: Optional[str] = None) -> List[str]:
    """Obtiene lista de tipos de productos disponibles."""
    tipos = set()
    
    if mes and mes in data:
        tipos.update(data[mes]['tipo'].unique())
    else:
        for df in data.values():
            if not df.empty:
                tipos.update(df['tipo'].unique())
    
    return sorted(list(tipos))

# Exportaciones
__all__ = [
    'parse_excel',
    'procesar_mes',
    'limpiar_datos',
    'validar_datos_numericos',
    'calcular_kpis_mes',
    'get_available_months',
    'get_available_tipos'
]
"""
controller_KCTN_05_Compras_Ventas.py - Controller CORREGIDO para Módulo Compras y Ventas KCTN
===========================================================================================
Controller especializado para manejar toda la lógica de negocio, KPIs y visualizaciones
del módulo de Compras y Ventas con FILTROS MES-AÑO CORREGIDOS.

CORRECCIONES CRÍTICAS APLICADAS:
✅ Filtros unificados mes-año para Compras Y Ventas
✅ Función get_ventas_kpis() corregida para recibir month_year_str
✅ Todos los gráficos de ventas corregidos para usar mes-año
✅ Validación de datos multi-año implementada
✅ Consistencia total entre Compras y Ventas

Autor: GANDB Dashboard Team
Fecha: 2025
Versión: 2.0 - CORREGIDO
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class GarlicComprasVentasController:
    """Controller principal para el módulo de Compras y Ventas KCTN - CORREGIDO."""
    
    def __init__(self):
        """Inicializa el controller."""
        self.compras_data = None
        self.ventas_data = None
        self.is_initialized = False
        self.metadata = {}
        
        # Mapeo de números de mes a nombres
        self.month_names = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        
        # Mapeo inverso para parsing
        self.name_to_month = {v: k for k, v in self.month_names.items()}
    
    def _create_month_year_key(self, month_num, year_num):
        """Crea una clave única mes-año."""
        if 1 <= month_num <= 12 and year_num > 0:
            return f"{self.month_names[month_num]} {year_num}"
        return None
    
    def _parse_month_year_key(self, month_year_str):
        """Parsea una clave mes-año para obtener números."""
        try:
            parts = month_year_str.strip().split()
            if len(parts) == 2:
                month_name, year_str = parts
                month_num = self.name_to_month.get(month_name, 0)
                year_num = int(year_str)
                return month_num, year_num
        except:
            pass
        return 0, 0
    
    def initialize_with_data(self, parsed_data):
        """
        Inicializa el controller con datos parseados.
        
        Args:
            parsed_data: Dict con datos parseados del parser
            
        Returns:
            bool: True si inicialización exitosa
        """
        try:
            print("🔍 DEBUG: Iniciando initialize_with_data")
            
            if not isinstance(parsed_data, dict):
                print(f"❌ ERROR: parsed_data no es dict, es {type(parsed_data)}")
                return False
            
            if parsed_data.get('status') not in ['success', 'partial_success']:
                print(f"❌ ERROR: status inválido: {parsed_data.get('status')}")
                return False
            
            data = parsed_data.get('data', {})
            
            # Reset datos previos
            self.compras_data = None
            self.ventas_data = None
            
            # Cargar datos de compras
            if 'compras' in data and isinstance(data['compras'], pd.DataFrame):
                if not data['compras'].empty:
                    self.compras_data = data['compras']
                    print(f"✅ Compras cargadas: {len(self.compras_data)} filas")
            
            # Cargar datos de ventas
            if 'ventas' in data and isinstance(data['ventas'], pd.DataFrame):
                if not data['ventas'].empty:
                    self.ventas_data = data['ventas']
                    print(f"✅ Ventas cargadas: {len(self.ventas_data)} filas")
            
            # Guardar metadata
            self.metadata = parsed_data.get('metadata', {})
            
            # Marcar como inicializado si hay al menos un dataset válido
            compras_valid = self.compras_data is not None and isinstance(self.compras_data, pd.DataFrame) and not self.compras_data.empty
            ventas_valid = self.ventas_data is not None and isinstance(self.ventas_data, pd.DataFrame) and not self.ventas_data.empty
            
            self.is_initialized = compras_valid or ventas_valid
            
            print(f"🔍 DEBUG: Controller inicializado: {self.is_initialized}")
            return self.is_initialized
            
        except Exception as e:
            print(f"❌ EXCEPCIÓN inicializando controller: {e}")
            return False
    
    def get_status(self):
        """Obtiene el status actual del controller."""
        
        compras_valid = self.compras_data is not None and isinstance(self.compras_data, pd.DataFrame)
        ventas_valid = self.ventas_data is not None and isinstance(self.ventas_data, pd.DataFrame)
        
        status = {
            'initialized': self.is_initialized,
            'has_compras': compras_valid,
            'has_ventas': ventas_valid,
            'compras_records': len(self.compras_data) if compras_valid else 0,
            'ventas_records': len(self.ventas_data) if ventas_valid else 0,
            'available_months': self.get_available_months(),
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        return status
    
    def get_available_months(self):
        """Obtiene lista de meses con año disponibles en los datos."""
        month_year_combinations = set()
        
        # Meses de compras
        if self.compras_data is not None and isinstance(self.compras_data, pd.DataFrame):
            if 'mes' in self.compras_data.columns and 'año' in self.compras_data.columns:
                compras_combinations = self.compras_data[['mes', 'año']].drop_duplicates()
                for _, row in compras_combinations.iterrows():
                    month_key = self._create_month_year_key(row['mes'], row['año'])
                    if month_key:
                        month_year_combinations.add(month_key)
        
        # Meses de ventas
        if self.ventas_data is not None and isinstance(self.ventas_data, pd.DataFrame):
            if 'mes' in self.ventas_data.columns and 'año' in self.ventas_data.columns:
                ventas_combinations = self.ventas_data[['mes', 'año']].drop_duplicates()
                for _, row in ventas_combinations.iterrows():
                    month_key = self._create_month_year_key(row['mes'], row['año'])
                    if month_key:
                        month_year_combinations.add(month_key)
        
        # Ordenar cronológicamente
        def sort_key(month_year_str):
            try:
                parts = month_year_str.split()
                if len(parts) == 2:
                    month_name, year_str = parts
                    month_num = self.name_to_month.get(month_name, 0)
                    year_num = int(year_str)
                    return (year_num, month_num)
            except:
                pass
            return (0, 0)
        
        sorted_months = sorted(list(month_year_combinations), key=sort_key)
        return sorted_months
    
    def get_months_with_data(self, data_type='both'):
        """
        Obtiene meses con año que tienen datos válidos.
        
        Args:
            data_type: 'compras', 'ventas', o 'both'
        """
        month_year_combinations = set()
        
        if data_type in ['compras', 'both'] and self.compras_data is not None:
            if 'mes' in self.compras_data.columns and 'año' in self.compras_data.columns and 'total_factura' in self.compras_data.columns:
                valid_data = self.compras_data[self.compras_data['total_factura'] > 0]
                compras_combinations = valid_data[['mes', 'año']].drop_duplicates()
                for _, row in compras_combinations.iterrows():
                    month_key = self._create_month_year_key(row['mes'], row['año'])
                    if month_key:
                        month_year_combinations.add(month_key)
        
        if data_type in ['ventas', 'both'] and self.ventas_data is not None:
            if 'mes' in self.ventas_data.columns and 'año' in self.ventas_data.columns and 'total_factura' in self.ventas_data.columns:
                valid_data = self.ventas_data[self.ventas_data['total_factura'] > 0]
                ventas_combinations = valid_data[['mes', 'año']].drop_duplicates()
                for _, row in ventas_combinations.iterrows():
                    month_key = self._create_month_year_key(row['mes'], row['año'])
                    if month_key:
                        month_year_combinations.add(month_key)
        
        # Ordenar cronológicamente
        def sort_key(month_year_str):
            try:
                parts = month_year_str.split()
                if len(parts) == 2:
                    month_name, year_str = parts
                    month_num = self.name_to_month.get(month_name, 0)
                    year_num = int(year_str)
                    return (year_num, month_num)
            except:
                pass
            return (0, 0)
        
        sorted_months = sorted(list(month_year_combinations), key=sort_key)
        return sorted_months
    
    # ================================================================
    # COMPRAS - KPIs INDIVIDUALES (YA ESTABAN CORRECTOS)
    # ================================================================
    
    def get_compras_kpis(self, month_year_str):
        """Obtiene KPIs de compras para un mes-año específico."""
        
        if not self.is_initialized or self.compras_data is None:
            return self._empty_compras_kpis()
        
        month_number, year_number = self._parse_month_year_key(month_year_str)
        if month_number == 0 or year_number == 0:
            return self._empty_compras_kpis()
        
        required_columns = ['mes', 'año', 'total_factura']
        for col in required_columns:
            if col not in self.compras_data.columns:
                return self._empty_compras_kpis()
        
        # Filtrar datos del mes y año específicos
        month_data = self.compras_data[
            (self.compras_data['mes'] == month_number) & 
            (self.compras_data['año'] == year_number)
        ].copy()
        
        if month_data.empty:
            return self._empty_compras_kpis()
        
        try:
            # KPI 1: Total valor de compras
            total_compras = month_data['total_factura'].sum()
            
            # KPI 2: Total valor por departamento
            compras_por_depto = {}
            if 'departamento' in month_data.columns:
                compras_por_depto = month_data.groupby('departamento')['total_factura'].sum().to_dict()
            
            # KPI 3: Proveedores activos
            proveedores_activos = 0
            if 'proveedor' in month_data.columns:
                proveedores_activos = month_data[month_data['total_factura'] > 0]['proveedor'].nunique()
            
            # KPI 4: Proveedores de Materia Prima
            proveedores_materia_prima = {}
            if 'departamento' in month_data.columns and 'subdepartamento' in month_data.columns:
                materia_prima_data = month_data[
                    (month_data['departamento'].str.contains('produccion', case=False, na=False)) &
                    (month_data['subdepartamento'].str.contains('materia prima', case=False, na=False))
                ]
                
                if not materia_prima_data.empty and 'proveedor' in materia_prima_data.columns:
                    proveedores_materia_prima = materia_prima_data.groupby('proveedor')['total_factura'].sum().to_dict()
            
            return {
                'has_data': True,
                'month': month_year_str,
                'total_compras': total_compras,
                'compras_por_departamento': compras_por_depto,
                'proveedores_activos_count': proveedores_activos,
                'proveedores_materia_prima': proveedores_materia_prima,
                'proveedores_materia_prima_count': len(proveedores_materia_prima),
                'total_materia_prima': sum(proveedores_materia_prima.values()) if proveedores_materia_prima else 0
            }
            
        except Exception as e:
            print(f"Error calculando KPIs compras: {e}")
            return self._empty_compras_kpis()
    
    def _empty_compras_kpis(self):
        """Retorna KPIs vacíos para compras."""
        return {
            'has_data': False,
            'month': '',
            'total_compras': 0,
            'compras_por_departamento': {},
            'proveedores_activos_count': 0,
            'proveedores_materia_prima': {},
            'proveedores_materia_prima_count': 0,
            'total_materia_prima': 0
        }
    
    # ================================================================
    # VENTAS - KPIs INDIVIDUALES ✅ CORREGIDOS
    # ================================================================
    
    def get_ventas_kpis(self, month_year_str):
        """
        ✅ CORREGIDO: Obtiene KPIs de ventas para un mes-año específico.
        
        Args:
            month_year_str: Mes con año (ej: 'Enero 2024')
            
        Returns:
            dict: KPIs de ventas
        """
        
        if not self.is_initialized or self.ventas_data is None:
            return self._empty_ventas_kpis()
        
        # ✅ CORRECCIÓN: Parsear mes Y año
        month_number, year_number = self._parse_month_year_key(month_year_str)
        if month_number == 0 or year_number == 0:
            return self._empty_ventas_kpis()
        
        required_columns = ['mes', 'año', 'total_factura']
        for col in required_columns:
            if col not in self.ventas_data.columns:
                return self._empty_ventas_kpis()
        
        # ✅ CORRECCIÓN: Filtrar por mes Y año
        month_data = self.ventas_data[
            (self.ventas_data['mes'] == month_number) & 
            (self.ventas_data['año'] == year_number)
        ].copy()
        
        if month_data.empty:
            return self._empty_ventas_kpis()
        
        try:
            # KPI 1: Total Ventas Mensuales
            total_ventas = month_data['total_factura'].sum()
            
            # KPI 2: Total Kg Mensuales
            total_kgs = 0
            if 'kgs' in month_data.columns:
                total_kgs = month_data['kgs'].sum()
            
            # KPI 3: Categorías Vendidas (por producto)
            categorias_vendidas = {}
            if 'producto' in month_data.columns:
                productos_data = month_data.groupby('producto').agg({
                    'kgs': 'sum' if 'kgs' in month_data.columns else lambda x: 0,
                    'total_factura': 'sum'
                }).to_dict('index')
                
                for producto, data in productos_data.items():
                    categorias_vendidas[producto] = {
                        'kgs': data.get('kgs', 0),
                        'total_factura': data.get('total_factura', 0)
                    }
            
            # KPI 4: Clientes
            clientes_activos_count = 0
            clientes_lista = []
            if 'cliente' in month_data.columns:
                clientes_activos_count = month_data[month_data['total_factura'] > 0]['cliente'].nunique()
                clientes_lista = month_data[month_data['total_factura'] > 0]['cliente'].unique().tolist()
            
            return {
                'has_data': True,
                'month': month_year_str,
                'total_ventas': total_ventas,
                'total_kgs': total_kgs,
                'categorias_vendidas': categorias_vendidas,
                'clientes_activos_count': clientes_activos_count,
                'clientes_lista': clientes_lista
            }
            
        except Exception as e:
            print(f"Error calculando KPIs ventas: {e}")
            return self._empty_ventas_kpis()
    
    def _empty_ventas_kpis(self):
        """Retorna KPIs vacíos para ventas."""
        return {
            'has_data': False,
            'month': '',
            'total_ventas': 0,
            'total_kgs': 0,
            'categorias_vendidas': {},
            'clientes_activos_count': 0,
            'clientes_lista': []
        }
    
    # ================================================================
    # GRÁFICOS COMPRAS (YA ESTABAN CORRECTOS)
    # ================================================================
    
    def create_compras_barras_departamento(self, month_year_str):
        """Gráfico de barras por departamento con stack por subdepartamento."""
        
        if not self.is_initialized or self.compras_data is None:
            return self._empty_chart("No hay datos de compras disponibles")
        
        month_number, year_number = self._parse_month_year_key(month_year_str)
        if month_number == 0 or year_number == 0:
            return self._empty_chart("Mes-año no válido")
        
        required_columns = ['mes', 'año', 'departamento', 'subdepartamento', 'total_factura']
        missing_columns = [col for col in required_columns if col not in self.compras_data.columns]
        if missing_columns:
            return self._empty_chart(f"Columnas faltantes: {', '.join(missing_columns)}")
        
        month_data = self.compras_data[
            (self.compras_data['mes'] == month_number) & 
            (self.compras_data['año'] == year_number)
        ]
        
        if month_data.empty:
            return self._empty_chart(f"No hay datos de compras para {month_year_str}")
        
        try:
            grouped_data = month_data.groupby(['departamento', 'subdepartamento'])['total_factura'].sum().reset_index()
            
            fig = px.bar(
                grouped_data,
                x='departamento',
                y='total_factura',
                color='subdepartamento',
                title=f'Compras por Departamento y Subdepartamento - {month_year_str}',
                labels={
                    'total_factura': 'Total Facturas (€)',
                    'departamento': 'Departamento',
                    'subdepartamento': 'Subdepartamento'
                },
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                showlegend=True,
                height=500,
                xaxis_tickangle=-45,
                yaxis_tickformat=',.0f'
            )
            
            return fig
            
        except Exception as e:
            return self._empty_chart(f"Error creando gráfico: {str(e)}")
    
    def create_compras_pie_materia_prima(self, month_year_str):
        """Pie chart de compras de materia prima por proveedor."""
        
        if not self.is_initialized or self.compras_data is None:
            return self._empty_chart("No hay datos de compras disponibles")
        
        month_number, year_number = self._parse_month_year_key(month_year_str)
        if month_number == 0 or year_number == 0:
            return self._empty_chart("Mes-año no válido")
        
        month_data = self.compras_data[
            (self.compras_data['mes'] == month_number) & 
            (self.compras_data['año'] == year_number)
        ]
        
        if month_data.empty:
            return self._empty_chart(f"No hay datos de compras para {month_year_str}")
        
        try:
            if 'departamento' in month_data.columns and 'subdepartamento' in month_data.columns:
                materia_prima_data = month_data[
                    (month_data['departamento'].str.contains('produccion', case=False, na=False)) &
                    (month_data['subdepartamento'].str.contains('materia prima', case=False, na=False))
                ]
            else:
                return self._empty_chart("Columnas de departamento/subdepartamento no encontradas")
            
            if materia_prima_data.empty:
                return self._empty_chart("No hay compras de materia prima en este período")
            
            proveedores_data = materia_prima_data.groupby('proveedor')['total_factura'].sum().reset_index()
            
            fig = px.pie(
                proveedores_data,
                values='total_factura',
                names='proveedor',
                title=f'Compras Materia Prima por Proveedor - {month_year_str}',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=True, height=500)
            
            return fig
            
        except Exception as e:
            return self._empty_chart(f"Error creando pie chart: {str(e)}")
    
    # ================================================================
    # GRÁFICOS VENTAS ✅ CORREGIDOS
    # ================================================================
    
    def create_ventas_tendencia_facturado(self, month_year_str):
        """
        ✅ CORREGIDO: Gráfico de tendencia de total facturado por fecha.
        """
        
        if not self.is_initialized or self.ventas_data is None:
            return self._empty_chart("No hay datos de ventas disponibles")
        
        # ✅ CORRECCIÓN: Parsear mes Y año
        month_number, year_number = self._parse_month_year_key(month_year_str)
        if month_number == 0 or year_number == 0:
            return self._empty_chart("Mes-año no válido")
        
        required_columns = ['mes', 'año', 'total_factura']
        missing_columns = [col for col in required_columns if col not in self.ventas_data.columns]
        if missing_columns:
            return self._empty_chart(f"Columnas faltantes: {', '.join(missing_columns)}")
        
        # ✅ CORRECCIÓN: Filtrar por mes Y año
        month_data = self.ventas_data[
            (self.ventas_data['mes'] == month_number) & 
            (self.ventas_data['año'] == year_number)
        ]
        
        if month_data.empty:
            return self._empty_chart(f"No hay datos de ventas para {month_year_str}")
        
        try:
            valid_data = month_data[month_data['total_factura'] > 0].copy()
            
            if valid_data.empty:
                return self._empty_chart("No hay ventas facturadas en este mes-año")
            
            # Agrupar por fecha si existe, sino por día del mes
            if 'fecha_cobro' in valid_data.columns:
                daily_data = valid_data.groupby('fecha_cobro')['total_factura'].sum().reset_index()
                x_col = 'fecha_cobro'
                x_label = 'Fecha de Cobro'
            else:
                valid_data['dia'] = range(1, len(valid_data) + 1)
                daily_data = valid_data.groupby('dia')['total_factura'].sum().reset_index()
                x_col = 'dia'
                x_label = 'Día del Mes'
            
            fig = px.line(
                daily_data,
                x=x_col,
                y='total_factura',
                title=f'Tendencia de Facturación - {month_year_str}',
                labels={
                    'total_factura': 'Total Facturado (€)',
                    x_col: x_label
                },
                markers=True
            )
            
            fig.update_layout(
                showlegend=False,
                height=400,
                yaxis_tickformat=',.0f'
            )
            
            return fig
            
        except Exception as e:
            return self._empty_chart(f"Error creando tendencia: {str(e)}")
    
    def create_ventas_barras_cliente(self, month_year_str):
        """
        ✅ CORREGIDO: Gráfico de barras por cliente.
        """
        
        if not self.is_initialized or self.ventas_data is None:
            return self._empty_chart("No hay datos de ventas disponibles")
        
        # ✅ CORRECCIÓN: Parsear mes Y año
        month_number, year_number = self._parse_month_year_key(month_year_str)
        if month_number == 0 or year_number == 0:
            return self._empty_chart("Mes-año no válido")
        
        required_columns = ['mes', 'año', 'cliente', 'total_factura']
        missing_columns = [col for col in required_columns if col not in self.ventas_data.columns]
        if missing_columns:
            return self._empty_chart(f"Columnas faltantes: {', '.join(missing_columns)}")
        
        # ✅ CORRECCIÓN: Filtrar por mes Y año
        month_data = self.ventas_data[
            (self.ventas_data['mes'] == month_number) & 
            (self.ventas_data['año'] == year_number)
        ]
        
        if month_data.empty:
            return self._empty_chart(f"No hay datos de ventas para {month_year_str}")
        
        try:
            cliente_data = month_data.groupby('cliente')['total_factura'].sum().reset_index()
            cliente_data = cliente_data.sort_values('total_factura', ascending=False)
            
            fig = px.bar(
                cliente_data,
                x='cliente',
                y='total_factura',
                title=f'Ventas por Cliente - {month_year_str}',
                labels={
                    'total_factura': 'Total Facturado (€)',
                    'cliente': 'Cliente'
                },
                color='total_factura',
                color_continuous_scale='Greens'
            )
            
            fig.update_layout(
                showlegend=False,
                height=500,
                xaxis_tickangle=-45,
                yaxis_tickformat=',.0f'
            )
            
            return fig
            
        except Exception as e:
            return self._empty_chart(f"Error creando gráfico de clientes: {str(e)}")
    
    def create_ventas_pie_productos(self, month_year_str):
        """
        ✅ CORREGIDO: Pie chart de ventas por producto.
        """
        
        if not self.is_initialized or self.ventas_data is None:
            return self._empty_chart("No hay datos de ventas disponibles")
        
        # ✅ CORRECCIÓN: Parsear mes Y año
        month_number, year_number = self._parse_month_year_key(month_year_str)
        if month_number == 0 or year_number == 0:
            return self._empty_chart("Mes-año no válido")
        
        required_columns = ['mes', 'año', 'producto', 'total_factura']
        missing_columns = [col for col in required_columns if col not in self.ventas_data.columns]
        if missing_columns:
            return self._empty_chart(f"Columnas faltantes: {', '.join(missing_columns)}")
        
        # ✅ CORRECCIÓN: Filtrar por mes Y año
        month_data = self.ventas_data[
            (self.ventas_data['mes'] == month_number) & 
            (self.ventas_data['año'] == year_number)
        ]
        
        if month_data.empty:
            return self._empty_chart(f"No hay datos de ventas para {month_year_str}")
        
        try:
            producto_data = month_data.groupby('producto').agg({
                'kgs': 'sum' if 'kgs' in month_data.columns else lambda x: 0,
                'total_factura': 'sum'
            }).reset_index()
            
            # Verificar si hay datos de kg
            has_kgs = 'kgs' in month_data.columns and month_data['kgs'].sum() > 0
            
            if has_kgs:
                # Crear subplots para mostrar tanto Kg como facturación
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=['Ventas por Producto (Kg)', 'Ventas por Producto (€)'],
                    specs=[[{"type": "pie"}, {"type": "pie"}]]
                )
                
                # Pie chart de Kg
                fig.add_trace(
                    go.Pie(
                        labels=producto_data['producto'],
                        values=producto_data['kgs'],
                        name="Kg",
                        textposition='inside',
                        textinfo='percent+label'
                    ),
                    row=1, col=1
                )
                
                # Pie chart de facturación
                fig.add_trace(
                    go.Pie(
                        labels=producto_data['producto'],
                        values=producto_data['total_factura'],
                        name="Euros",
                        textposition='inside',
                        textinfo='percent+label'
                    ),
                    row=1, col=2
                )
                
                fig.update_layout(
                    title_text=f'Distribución de Ventas por Producto - {month_year_str}',
                    height=500,
                    showlegend=True
                )
            else:
                # Solo pie chart de facturación
                fig = px.pie(
                    producto_data,
                    values='total_factura',
                    names='producto',
                    title=f'Distribución de Ventas por Producto (€) - {month_year_str}',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=True, height=500)
            
            return fig
            
        except Exception as e:
            return self._empty_chart(f"Error creando pie chart productos: {str(e)}")
    
    # ================================================================
    # COMPARACIÓN MULTI-MES ✅ CORREGIDOS
    # ================================================================
    
    def create_compras_kpi_table(self, selected_month_years):
        """Tabla comparativa de KPIs de compras."""
        
        if not selected_month_years:
            return pd.DataFrame()
        
        try:
            table_data = []
            
            for month_year in selected_month_years:
                kpis = self.get_compras_kpis(month_year)
                
                if kpis['has_data']:
                    row = {
                        'Período': month_year,
                        'Total Compras (€)': f"€{kpis['total_compras']:,.0f}",
                        'Proveedores Activos': kpis['proveedores_activos_count'],
                        'Proveedores Mat. Prima': kpis['proveedores_materia_prima_count'],
                        'Total Mat. Prima (€)': f"€{kpis['total_materia_prima']:,.0f}"
                    }
                    
                    # Agregar top 3 departamentos
                    if kpis['compras_por_departamento']:
                        sorted_deptos = sorted(kpis['compras_por_departamento'].items(), 
                                             key=lambda x: x[1], reverse=True)
                        for i, (depto, valor) in enumerate(sorted_deptos[:3]):
                            row[f'Depto #{i+1}'] = f"{depto}: €{valor:,.0f}"
                    
                    table_data.append(row)
            
            return pd.DataFrame(table_data)
            
        except Exception as e:
            print(f"Error creando tabla compras: {e}")
            return pd.DataFrame()
    
    def create_ventas_kpi_table(self, selected_month_years):
        """
        ✅ CORREGIDO: Tabla comparativa de KPIs de ventas.
        """
        
        if not selected_month_years:
            return pd.DataFrame()
        
        try:
            table_data = []
            
            for month_year in selected_month_years:
                # ✅ CORRECCIÓN: Usar month_year_str en lugar de month_name
                kpis = self.get_ventas_kpis(month_year)
                
                if kpis['has_data']:
                    row = {
                        'Período': month_year,
                        'Total Ventas (€)': f"€{kpis['total_ventas']:,.0f}",
                        'Total Kg': f"{kpis['total_kgs']:,.0f}",
                        'Clientes Activos': kpis['clientes_activos_count'],
                        'Productos Vendidos': len(kpis['categorias_vendidas'])
                    }
                    
                    # Agregar top 3 productos
                    if kpis['categorias_vendidas']:
                        sorted_productos = sorted(kpis['categorias_vendidas'].items(), 
                                                key=lambda x: x[1]['total_factura'], reverse=True)
                        for i, (producto, data) in enumerate(sorted_productos[:3]):
                            row[f'Producto #{i+1}'] = f"{producto}: €{data['total_factura']:,.0f}"
                    
                    table_data.append(row)
            
            return pd.DataFrame(table_data)
            
        except Exception as e:
            print(f"Error creando tabla ventas: {e}")
            return pd.DataFrame()
    
    def create_ventas_evolucion_chart(self, selected_month_years):
        """
        ✅ CORREGIDO: Gráfico de evolución de ventas totales.
        """
        
        if not self.is_initialized or self.ventas_data is None or not selected_month_years:
            return self._empty_chart("No hay datos suficientes")
        
        required_columns = ['mes', 'año', 'total_factura']
        missing_columns = [col for col in required_columns if col not in self.ventas_data.columns]
        if missing_columns:
            return self._empty_chart(f"Columnas faltantes: {', '.join(missing_columns)}")
        
        try:
            # ✅ CORRECCIÓN: Usar selected_month_years en lugar de selected_months
            monthly_totals = []
            
            for month_year in selected_month_years:
                month_number, year_number = self._parse_month_year_key(month_year)
                if month_number > 0 and year_number > 0:
                    month_data = self.ventas_data[
                        (self.ventas_data['mes'] == month_number) & 
                        (self.ventas_data['año'] == year_number)
                    ]
                    total = month_data['total_factura'].sum()
                    monthly_totals.append({
                        'periodo': month_year,
                        'total_factura': total,
                        'orden': (year_number, month_number)
                    })
            
            if not monthly_totals:
                return self._empty_chart("No hay datos para los períodos seleccionados")
            
            # Ordenar por año y mes
            monthly_totals.sort(key=lambda x: x['orden'])
            
            df_totals = pd.DataFrame(monthly_totals)
            
            fig = px.line(
                df_totals,
                x='periodo',
                y='total_factura',
                title='Evolución de Ventas Totales',
                labels={
                    'total_factura': 'Total Ventas (€)',
                    'periodo': 'Período'
                },
                markers=True
            )
            
            fig.update_layout(
                height=400,
                yaxis_tickformat=',.0f',
                xaxis_tickangle=-45
            )
            
            return fig
            
        except Exception as e:
            return self._empty_chart(f"Error creando evolución ventas: {str(e)}")
    
    # ================================================================
    # UTILIDADES Y DEBUG
    # ================================================================
    
    def get_debug_info(self):
        """Obtiene información de debug del controller."""
        debug_info = {
            'controller_initialized': self.is_initialized,
            'compras_data_info': {
                'exists': self.compras_data is not None,
                'type': type(self.compras_data).__name__ if self.compras_data is not None else 'None',
                'is_dataframe': isinstance(self.compras_data, pd.DataFrame),
                'shape': self.compras_data.shape if isinstance(self.compras_data, pd.DataFrame) else 'N/A',
                'columns': list(self.compras_data.columns) if isinstance(self.compras_data, pd.DataFrame) else []
            },
            'ventas_data_info': {
                'exists': self.ventas_data is not None,
                'type': type(self.ventas_data).__name__ if self.ventas_data is not None else 'None',
                'is_dataframe': isinstance(self.ventas_data, pd.DataFrame),
                'shape': self.ventas_data.shape if isinstance(self.ventas_data, pd.DataFrame) else 'N/A',
                'columns': list(self.ventas_data.columns) if isinstance(self.ventas_data, pd.DataFrame) else []
            },
            'available_periods': self.get_available_months(),
            'periods_with_data': self.get_months_with_data(),
            'metadata': self.metadata
        }
        
        # Agregar información de validación de columnas
        if isinstance(self.compras_data, pd.DataFrame):
            debug_info['compras_column_validation'] = self._validate_compras_columns()
        
        if isinstance(self.ventas_data, pd.DataFrame):
            debug_info['ventas_column_validation'] = self._validate_ventas_columns()
        
        return debug_info
    
    def _validate_compras_columns(self):
        """Valida que las columnas de compras coincidan con las especificaciones."""
        if not isinstance(self.compras_data, pd.DataFrame):
            return {'valid': False, 'reason': 'No es DataFrame'}
        
        validation_result = {
            'valid': True,
            'columns_found': list(self.compras_data.columns),
            'missing_columns': [],
            'column_mapping_check': {}
        }
        
        # Verificar columnas críticas
        critical_columns = ['mes', 'año', 'total_factura', 'proveedor', 'departamento']
        for col in critical_columns:
            if col in self.compras_data.columns:
                validation_result['column_mapping_check'][col] = 'Found'
            else:
                validation_result['missing_columns'].append(col)
                validation_result['valid'] = False
        
        # Verificar tipos de datos en columnas críticas
        if 'mes' in self.compras_data.columns:
            sample_mes = self.compras_data['mes'].dropna().head(5).tolist()
            validation_result['column_mapping_check']['mes_sample'] = sample_mes
        
        if 'año' in self.compras_data.columns:
            sample_año = self.compras_data['año'].dropna().head(5).tolist()
            validation_result['column_mapping_check']['año_sample'] = sample_año
        
        return validation_result
    
    def _validate_ventas_columns(self):
        """Valida que las columnas de ventas coincidan con las especificaciones."""
        if not isinstance(self.ventas_data, pd.DataFrame):
            return {'valid': False, 'reason': 'No es DataFrame'}
        
        validation_result = {
            'valid': True,
            'columns_found': list(self.ventas_data.columns),
            'missing_columns': [],
            'column_mapping_check': {}
        }
        
        # Verificar columnas críticas
        critical_columns = ['mes', 'año', 'total_factura', 'cliente', 'producto']
        for col in critical_columns:
            if col in self.ventas_data.columns:
                validation_result['column_mapping_check'][col] = 'Found'
            else:
                validation_result['missing_columns'].append(col)
                validation_result['valid'] = False
        
        # Verificar tipos de datos en columnas críticas
        if 'mes' in self.ventas_data.columns:
            sample_mes = self.ventas_data['mes'].dropna().head(5).tolist()
            validation_result['column_mapping_check']['mes_sample'] = sample_mes
        
        if 'año' in self.ventas_data.columns:
            sample_año = self.ventas_data['año'].dropna().head(5).tolist()
            validation_result['column_mapping_check']['año_sample'] = sample_año
        
        return validation_result
    
    def _empty_chart(self, message="No hay datos disponibles"):
        """Retorna un gráfico vacío con mensaje."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            xanchor='center',
            yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=400,
            plot_bgcolor='white'
        )
        return fig
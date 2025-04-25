import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
import datetime
from typing import List, Dict, Optional, Tuple
import os
import pickle
from PIL import Image, ImageTk  

# Configuración de colores
COLORES = {
    "fondo": "#f8f4e9",  # Beige claro
    "primario": "#a68a64",  # Café claro
    "secundario": "#d4b483",  # Café muy claro
    "acento": "#e8d9c5",  # Beige
    "texto": "#5a4a3a",  # Café oscuro para texto
    "exito": "#7cb342",  # Verde claro
    "error": "#e53935",  # Rojo
    "advertencia": "#ffb74d",  # Naranja claro
    "info": "#64b5f6"  # Azul claro
}

# Opciones adicionales para productos
TIPOS_LECHE = ["Entera", "Deslactosada", "Almendras", "Soya", "Sin leche"]
NIVELES_AZUCAR = ["Sin azúcar", "Poco", "Normal", "Mucho"]

class ProductoConExtras:
    """Clase que representa un producto con sus opciones personalizadas"""
    def __init__(self, producto: 'Producto', cantidad: int = 1, tipo_leche: str = None, 
                 azucar: str = None, notas: str = ""):
        self.producto = producto
        self.cantidad = cantidad
        self.tipo_leche = tipo_leche
        self.azucar = azucar
        self.notas = notas
    
    @property
    def precio_total(self) -> float:
        """Calcula el precio total considerando la cantidad"""
        return self.producto.precio * self.cantidad
    
    def __str__(self) -> str:
        """Formatea la información del producto con extras para mostrar"""
        detalles = []
        if self.tipo_leche:
            detalles.append(f"Leche: {self.tipo_leche}")
        if self.azucar:
            detalles.append(f"Azúcar: {self.azucar}")
        if self.notas:
            detalles.append(f"Notas: {self.notas}")
        
        detalles_str = " - " + ", ".join(detalles) if detalles else ""
        return f"{self.cantidad}x {self.producto.nombre}{detalles_str} - ${self.precio_total:.2f}"

class Persona:
    """Clase base para personas"""
    def __init__(self, nombre: str, telefono: str):
        self.nombre = nombre
        self.telefono = telefono
    
    def contactar(self) -> str:
        """Método para contactar a la persona"""
        return f"Contactando a {self.nombre} en {self.telefono}"

class Cliente(Persona):
    """Clase que representa a un cliente"""
    def __init__(self, nombre: str, telefono: str, identificacion: str):
        super().__init__(nombre, telefono)
        self.identificacion = identificacion
        self.historial_pedidos: List["Pedido"] = []
    
    def realizar_pedido(self, productos: List[ProductoConExtras]) -> "Pedido":
        """Crea un nuevo pedido para el cliente"""
        nuevo_pedido = Pedido(self, productos)
        self.historial_pedidos.append(nuevo_pedido)
        return nuevo_pedido

class Empleado(Persona):
    """Clase que representa a un empleado"""
    def __init__(self, nombre: str, telefono: str, puesto: str, usuario: str, contrasena: str):
        super().__init__(nombre, telefono)
        self.puesto = puesto
        self.usuario = usuario
        self.contrasena = contrasena
    
    def procesar_pedido(self, pedido: "Pedido") -> None:
        """Cambia el estado del pedido a 'En preparación'"""
        pedido.estado = "En preparación"
    
    def entregar_pedido(self, pedido: "Pedido") -> None:
        """Cambia el estado del pedido a 'Entregado'"""
        pedido.estado = "Entregado"
    
    def actualizar_inventario(self, producto: "Producto", cantidad: int) -> None:
        """Actualiza el stock de un producto"""
        producto.stock += cantidad

class ProductoBase:
    """Clase base para productos"""
    def __init__(self, codigo: str, nombre: str, precio: float, stock: int = 0):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
    
    def obtener_precio(self) -> float:
        """Devuelve el precio del producto"""
        return self.precio
    
    def actualizar_stock(self, cantidad: int) -> None:
        """Actualiza el stock del producto"""
        self.stock += cantidad
        if self.stock < 0:
            self.stock = 0

class Producto(ProductoBase):
    """Clase para productos generales"""
    def __init__(self, codigo: str, nombre: str, precio: float, stock: int = 0, descripcion: str = "", imagen: str = None):
        super().__init__(codigo, nombre, precio, stock)
        self.descripcion = descripcion
        self.imagen = imagen
    
    def __str__(self) -> str:
        """Representación en string del producto"""
        return f"{self.nombre} - ${self.precio:.2f} ({self.stock} disponibles)"

class Bebida(Producto):
    """Clase para bebidas"""
    def __init__(self, codigo: str, nombre: str, precio: float, stock: int = 0, tamano: str = "Mediano", imagen: str = None):
        super().__init__(codigo, nombre, precio, stock, "", imagen)
        self.tamano = tamano
    
    def cambiar_tamano(self, nuevo_tamano: str) -> None:
        """Cambia el tamaño de la bebida"""
        self.tamano = nuevo_tamano

class Postre(Producto):
    """Clase para postres"""
    def __init__(self, codigo: str, nombre: str, precio: float, stock: int = 0, ingredientes: List[str] = None, imagen: str = None):
        super().__init__(codigo, nombre, precio, stock, "", imagen)
        self.ingredientes = ingredientes if ingredientes else []
    
    def mostrar_ingredientes(self) -> str:
        """Devuelve los ingredientes como string"""
        return ", ".join(self.ingredientes)

class Pedido:
    """Clase que representa un pedido"""
    contador_pedidos = 0
    
    def __init__(self, cliente: Cliente, productos: List[ProductoConExtras]):
        Pedido.contador_pedidos += 1
        self.numero = Pedido.contador_pedidos
        self.cliente = cliente
        self.productos = productos.copy()
        self.fecha = datetime.datetime.now()
        self.estado = "Nuevo"
        self.total = self.calcular_total()
    
    def calcular_total(self) -> float:
        """Calcula el total del pedido"""
        return sum(item.precio_total for item in self.productos)
    
    def agregar_producto(self, producto: ProductoConExtras) -> None:
        """Agrega un producto al pedido"""
        self.productos.append(producto)
        self.total = self.calcular_total()
    
    def eliminar_producto(self, producto: ProductoConExtras) -> bool:
        """Elimina un producto del pedido"""
        if producto in self.productos:
            self.productos.remove(producto)
            self.total = self.calcular_total()
            return True
        return False
    
    def actualizar_estado(self, nuevo_estado: str) -> None:
        """Actualiza el estado del pedido"""
        self.estado = nuevo_estado

class ProcesoBase:
    """Clase base para procesos"""
    def __init__(self, fecha: datetime.datetime):
        self.fecha = fecha
    
    def obtener_fecha(self) -> datetime.datetime:
        """Devuelve la fecha del proceso"""
        return self.fecha

class ProcesoPedido(ProcesoBase):
    """Clase para el proceso de preparación de pedidos"""
    def __init__(self, pedido: Pedido, empleado: Empleado):
        super().__init__(datetime.datetime.now())
        self.pedido = pedido
        self.empleado = empleado
    
    def iniciar_proceso(self) -> None:
        """Inicia el proceso de preparación"""
        self.pedido.actualizar_estado("En preparación")
    
    def finalizar_proceso(self) -> None:
        """Finaliza el proceso de preparación"""
        self.pedido.actualizar_estado("Listo para entrega")

class ProcesoEntrega(ProcesoBase):
    """Clase para el proceso de entrega de pedidos"""
    def __init__(self, pedido: Pedido, empleado: Empleado):
        super().__init__(datetime.datetime.now())
        self.pedido = pedido
        self.empleado = empleado
    
    def entregar(self) -> None:
        """Marca el pedido como entregado"""
        self.pedido.actualizar_estado("Entregado")
    
    def obtener_detalle(self) -> str:
        """Devuelve el detalle de la entrega"""
        return f"Pedido #{self.pedido.numero} entregado por {self.empleado.nombre} en {self.fecha}"

class Inventario:
    """Clase para gestionar el inventario de productos"""
    def __init__(self):
        self.productos: Dict[str, Producto] = {}
    
    def agregar_producto(self, producto: Producto) -> None:
        """Agrega un producto al inventario"""
        self.productos[producto.codigo] = producto
    
    def actualizar_stock(self, codigo: str, cantidad: int) -> bool:
        """Actualiza el stock de un producto"""
        if codigo in self.productos:
            self.productos[codigo].actualizar_stock(cantidad)
            return True
        return False
    
    def obtener_producto(self, codigo: str) -> Optional[Producto]:
        """Obtiene un producto por su código"""
        return self.productos.get(codigo)
    
    def listar_productos(self) -> List[Producto]:
        """Lista todos los productos"""
        return list(self.productos.values())
    
    def listar_bebidas(self) -> List[Bebida]:
        """Lista todas las bebidas"""
        return [p for p in self.productos.values() if isinstance(p, Bebida)]
    
    def listar_postres(self) -> List[Postre]:
        """Lista todos los postres"""
        return [p for p in self.productos.values() if isinstance(p, Postre)]

class SistemaPedidos:
    """Clase principal del sistema de pedidos"""
    DATA_FILE = "cafeteria_data.pkl"
    
    def __init__(self):
        self.inventario = Inventario()
        self.pedidos: List[Pedido] = []
        self.clientes: Dict[str, Cliente] = {}
        self.empleados: Dict[str, Empleado] = {}
        self.cargar_datos()
    
    def inicializar_datos_demo(self) -> None:
        """Inicializa datos de demostración"""
        # Bebidas
        bebidas = [
            Bebida("B001", "Café Americano", 2.50, 50, "Mediano", "☕"),
            Bebida("B002", "Cappuccino", 3.50, 30, "Mediano", "☕"),
            Bebida("B003", "Chocolate Caliente", 3.00, 25, "Mediano", "☕"),
            Bebida("B004", "Té Verde", 2.00, 40, "Mediano", "🍵"),
            Bebida("B005", "Smoothie de Frutas", 4.00, 20, "Grande", "🥤"),
            Bebida("B006", "Mocha", 3.75, 35, "Mediano", "☕"),
            Bebida("B007", "Latte", 3.25, 30, "Grande", "☕"),
            Bebida("B008", "Té de Manzanilla", 2.25, 25, "Mediano", "🍵"),
            Bebida("B009", "Jugo Natural", 3.50, 20, "Grande", "🧃"),
            Bebida("B010", "Frappé de Vainilla", 4.50, 15, "Grande", "🥤")
        ]
        
        # Postres
        postres = [
            Postre("P001", "Croissant", 2.00, 20, ["Harina", "Mantequilla", "Azúcar"], "🥐"),
            Postre("P002", "Donut", 1.50, 15, ["Harina", "Azúcar", "Chocolate"], "🍩"),
            Postre("P003", "Cheesecake", 3.50, 10, ["Queso crema", "Galleta", "Azúcar"], "🍰"),
            Postre("P004", "Brownie", 2.50, 12, ["Chocolate", "Nueces", "Harina"], "🍫"),
            Postre("P005", "Muffin de Arándanos", 2.75, 18, ["Harina", "Arándanos", "Azúcar"], "🧁"),
            Postre("P006", "Tarta de Manzana", 4.00, 8, ["Manzana", "Masa", "Canela"], "🍎"),
            Postre("P007", "Galletas de Chocolate", 1.75, 25, ["Harina", "Chocolate", "Mantequilla"], "🍪"),
            Postre("P008", "Flan", 3.00, 12, ["Huevo", "Leche", "Azúcar"], "🍮"),
            Postre("P009", "Tiramisú", 4.50, 10, ["Café", "Queso mascarpone", "Bizcochos"], "🍰"),
            Postre("P010", "Profiteroles", 3.75, 8, ["Crema", "Masa", "Chocolate"], "🧁")
        ]
        
        # Agregar productos al inventario
        for bebida in bebidas:
            self.inventario.agregar_producto(bebida)
        
        for postre in postres:
            self.inventario.agregar_producto(postre)
        
        # Agregar empleados
        empleados = [
            Empleado("Amanda Sanchez", "555-1234", "Barista", "amanda", "amanda"),
            Empleado("Carlos Castillo", "555-5678", "Cajero", "carlos", "carlos"),
            Empleado("Guadalupe Mino", "555-0000", "Administrador", "admin", "admin")
        ]
        
        for empleado in empleados:
            self.empleados[empleado.usuario] = empleado
    
    def guardar_datos(self) -> None:
        """Guarda los datos en un archivo"""
        with open(self.DATA_FILE, 'wb') as f:
            pickle.dump((self.inventario, self.pedidos, self.clientes, self.empleados), f)
    
    def cargar_datos(self) -> bool:
        """Carga los datos desde un archivo"""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'rb') as f:
                    self.inventario, self.pedidos, self.clientes, self.empleados = pickle.load(f)
                return True
            except:
                self.inicializar_datos_demo()
                return False
        else:
            self.inicializar_datos_demo()
            return False
    
    def validar_empleado(self, usuario: str, contrasena: str) -> Optional[Empleado]:
        """Valida las credenciales de un empleado"""
        if usuario in self.empleados and self.empleados[usuario].contrasena == contrasena:
            return self.empleados[usuario]
        return None
    
    def registrar_cliente(self, nombre: str, telefono: str, identificacion: str) -> Cliente:
        """Registra un nuevo cliente"""
        nuevo_cliente = Cliente(nombre, telefono, identificacion)
        self.clientes[identificacion] = nuevo_cliente
        self.guardar_datos()
        return nuevo_cliente
    
    def buscar_cliente(self, identificacion: str) -> Optional[Cliente]:
        """Busca un cliente por su identificación"""
        return self.clientes.get(identificacion)
    
    def crear_pedido(self, cliente_id: str, productos: List[ProductoConExtras]) -> Optional[Pedido]:
        """Crea un nuevo pedido"""
        cliente = self.buscar_cliente(cliente_id)
        if not cliente:
            return None
        
        # Verificar stock antes de crear el pedido
        for item in productos:
            producto = self.inventario.obtener_producto(item.producto.codigo)
            if not producto or producto.stock < item.cantidad:
                messagebox.showwarning("Error", f"No hay suficiente stock de {item.producto.nombre}")
                return None
        
        # Descontar el stock
        for item in productos:
            producto = self.inventario.obtener_producto(item.producto.codigo)
            producto.actualizar_stock(-item.cantidad)
        
        pedido = cliente.realizar_pedido(productos)
        self.pedidos.append(pedido)
        self.guardar_datos()
        return pedido
    
    def listar_pedidos(self, estado: Optional[str] = None) -> List[Pedido]:
        """Lista los pedidos según su estado"""
        if estado:
            return [p for p in self.pedidos if p.estado == estado]
        return self.pedidos
    
    def modificar_pedido(self, numero_pedido: int, accion: str, producto: ProductoConExtras = None) -> bool:
        """Modifica un pedido existente"""
        for pedido in self.pedidos:
            if pedido.numero == numero_pedido and pedido.estado == "Nuevo":
                if accion == "agregar":
                    prod_base = self.inventario.obtener_producto(producto.producto.codigo)
                    if prod_base and prod_base.stock >= producto.cantidad:
                        pedido.agregar_producto(producto)
                        prod_base.actualizar_stock(-producto.cantidad)
                        self.guardar_datos()
                        return True
                elif accion == "eliminar":
                    for p in pedido.productos:
                        if p.producto.codigo == producto.producto.codigo:
                            if pedido.eliminar_producto(p):
                                prod_base = self.inventario.obtener_producto(p.producto.codigo)
                                prod_base.actualizar_stock(p.cantidad)
                                self.guardar_datos()
                                return True
        return False
    
    def procesar_pedido(self, numero_pedido: int, empleado_usuario: str) -> bool:
        """Cambia el estado del pedido a 'En preparación'"""
        empleado = self.empleados.get(empleado_usuario)
        if not empleado:
            return False
        
        for pedido in self.pedidos:
            if pedido.numero == numero_pedido and pedido.estado == "Nuevo":
                proceso = ProcesoPedido(pedido, empleado)
                proceso.iniciar_proceso()
                self.guardar_datos()
                return True
        return False
    
    def entregar_pedido(self, numero_pedido: int, empleado_usuario: str) -> bool:
        """Marca el pedido como entregado"""
        empleado = self.empleados.get(empleado_usuario)
        if not empleado:
            return False
        
        for pedido in self.pedidos:
            if pedido.numero == numero_pedido and pedido.estado == "En preparación":
                proceso = ProcesoEntrega(pedido, empleado)
                proceso.entregar()
                self.guardar_datos()
                return True
        return False
    
    def listar_productos_disponibles(self) -> List[Producto]:
        """Lista los productos con stock disponible"""
        return [p for p in self.inventario.listar_productos() if p.stock > 0]
    
    def generar_reporte_ventas(self) -> Dict:
        """Genera un reporte de ventas"""
        total_ventas = sum(p.total for p in self.pedidos if p.estado == "Entregado")
        productos_vendidos = {}
        for pedido in self.pedidos:
            if pedido.estado == "Entregado":
                for item in pedido.productos:
                    if item.producto.codigo in productos_vendidos:
                        productos_vendidos[item.producto.codigo] += item.cantidad
                    else:
                        productos_vendidos[item.producto.codigo] = item.cantidad
        
        return {
            "total_ventas": total_ventas,
            "productos_vendidos": productos_vendidos,
            "pedidos_completados": len([p for p in self.pedidos if p.estado == "Entregado"])
        }
    
    def agregar_empleado(self, nombre: str, telefono: str, puesto: str, usuario: str, contrasena: str) -> bool:
        """Agrega un nuevo empleado"""
        if usuario in self.empleados:
            return False
        
        nuevo_empleado = Empleado(nombre, telefono, puesto, usuario, contrasena)
        self.empleados[usuario] = nuevo_empleado
        self.guardar_datos()
        return True
    
    def exportar_clientes_excel(self, filename: str = "clientes_cafeteria.xlsx") -> bool:
        """Exporta la lista de clientes a un archivo Excel"""
        try:
            import openpyxl
            from openpyxl.styles import Font
            
            # Crear un nuevo libro de Excel
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Clientes"
            
            # Escribir los encabezados
            headers = ["Identificación", "Nombre", "Teléfono", "Total Pedidos", "Total Gastado"]
            ws.append(headers)
            
            # Estilo para los encabezados
            for cell in ws[1]:
                cell.font = Font(bold=True)
            
            # Escribir los datos de cada cliente
            for cliente in self.clientes.values():
                total_pedidos = len(cliente.historial_pedidos)
                total_gastado = sum(p.total for p in cliente.historial_pedidos)
                
                ws.append([
                    cliente.identificacion,
                    cliente.nombre,
                    cliente.telefono,
                    total_pedidos,
                    total_gastado
                ])
            
            # Ajustar el ancho de las columnas
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2
                ws.column_dimensions[column].width = adjusted_width
            
            # Guardar el archivo
            wb.save(filename)
            return True
            
        except Exception as e:
            print(f"Error al exportar a Excel: {e}")
            return False

class InterfazCafeteria:
    """Clase para la interfaz gráfica de la cafetería"""
    def __init__(self, root):
        self.root = root
        self.sistema = SistemaPedidos()
        self.carrito: List[ProductoConExtras] = []
        self.cliente_actual = None
        self.empleado_actual = None

        # Configuración de la ventana principal
        self.root.title("☕ Sistema de Gestión de Pedidos - Cafetería Dulce Aroma")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        
        try:
            # Usar PIL para redimensionar la imagen al tamaño de la ventana
            original_img = Image.open("E://Programación avanzada//fondo_inicio.jpg")  # Cambia por tu ruta
            resized_img = original_img.resize((1000, 700), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized_img)
        except Exception as e:
            print(f"Error cargando el fondo: {e}. Usando color sólido.")
            self.bg_image = None

        self.configurar_estilos()
        self.mostrar_pantalla_inicio()
    
    def configurar_estilos(self):
        """Configura los estilos visuales de la aplicación"""
        style = ttk.Style()
        
        # Configurar tema general
        style.theme_use('clam')
        
        # Configurar colores y fuentes
        style.configure('.', background=COLORES["fondo"], foreground=COLORES["texto"])
        style.configure('TFrame', background=COLORES["fondo"])
        style.configure('TLabel', background=COLORES["fondo"], foreground=COLORES["texto"], font=('Helvetica', 10))
        style.configure('TButton', background=COLORES["primario"], foreground='white', 
                       font=('Helvetica', 10, 'bold'), padding=10, borderwidth=0)
        style.configure('TEntry', fieldbackground='white', foreground=COLORES["texto"])
        style.configure('TNotebook', background=COLORES["fondo"])
        style.configure('TNotebook.Tab', background=COLORES["secundario"], foreground='white', 
                       padding=[10, 5], font=('Helvetica', 10, 'bold'))
        
        # Estilos personalizados
        style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'), foreground=COLORES["primario"])
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'), foreground=COLORES["primario"])
        style.configure('Success.TLabel', foreground=COLORES["exito"])
        style.configure('Error.TLabel', foreground=COLORES["error"])
        
        # Estilo para botones importantes
        style.map('Primary.TButton',
                 background=[('active', COLORES["secundario"]), ('!disabled', COLORES["primario"])],
                 foreground=[('!disabled', 'white')])
        
        # Estilo para botones secundarios
        style.map('Secondary.TButton',
                 background=[('active', COLORES["acento"]), ('!disabled', COLORES["secundario"])],
                 foreground=[('!disabled', 'white')])
        
        # Configurar el Listbox
        self.root.option_add('*Listbox*Background', 'white')
        self.root.option_add('*Listbox*Foreground', COLORES["texto"])
        self.root.option_add('*Listbox*selectBackground', COLORES["primario"])
        self.root.option_add('*Listbox*selectForeground', 'white')

    def limpiar_pantalla(self):
        """Elimina todos los widgets de la pantalla"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_pantalla_inicio(self):
        self.limpiar_pantalla()

        # Crear un Canvas como contenedor principal (para el fondo)
        canvas = tk.Canvas(self.root, highlightthickness=0)
        canvas.pack(expand=True, fill=tk.BOTH)

        # Mostrar la imagen de fondo si existe
        if self.bg_image:
            canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # Frame principal para los widgets (con fondo semitransparente)
        main_frame = ttk.Frame(canvas, style='TFrame')
        main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Centrado

        # Logo y título
        logo_frame = ttk.Frame(main_frame)
        logo_frame.pack(pady=(20, 10))

        ttk.Label(logo_frame, text="☕", font=('Helvetica', 60), foreground=COLORES["primario"]).pack()
        ttk.Label(logo_frame, text="Cafetería Dulce Aroma", style="Title.TLabel").pack(pady=10)

        # Botones principales
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30, fill=tk.X, padx=50)

        ttk.Button(btn_frame, text="Realizar Pedido", command=self.mostrar_identificacion_cliente, 
              style="Primary.TButton").pack(fill=tk.X, pady=10, ipady=10)
        ttk.Button(btn_frame, text="Ver Pedidos", command=self.mostrar_lista_pedidos, 
              style="Primary.TButton").pack(fill=tk.X, pady=10, ipady=10)
        ttk.Button(btn_frame, text="Soy Empleado", command=self.mostrar_login_empleado, 
              style="Primary.TButton").pack(fill=tk.X, pady=10, ipady=10)
        ttk.Button(btn_frame, text="Salir", command=self.root.quit, 
              style="Secondary.TButton").pack(fill=tk.X, pady=10, ipady=10)

        # Pie de página
        footer = ttk.Frame(main_frame)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        ttk.Label(footer, text="© 2025 Cafetería Dulce Aroma", anchor=tk.CENTER).pack()

    def mostrar_lista_pedidos(self):
        """Muestra la lista de pedidos del cliente actual"""
        if not self.cliente_actual:
            messagebox.showwarning("Error", "Debe identificarse como cliente primero", parent=self.root)
            self.mostrar_identificacion_cliente()
            return
        
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título
        ttk.Label(
            main_frame, 
            text=f"📋 Mis Pedidos - {self.cliente_actual.nombre}", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Frame contenedor con scroll
        container = ttk.Frame(main_frame)
        container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(container, bg=COLORES["fondo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mostrar pedidos
        if not self.cliente_actual.historial_pedidos:
            ttk.Label(
                scrollable_frame, 
                text="No hay pedidos registrados", 
                font=('Helvetica', 12)
            ).pack(pady=20)
        else:
            for pedido in sorted(self.cliente_actual.historial_pedidos, key=lambda p: p.fecha, reverse=True):
                self.mostrar_resumen_pedido(scrollable_frame, pedido)
        
        # Botón volver
        ttk.Button(
            main_frame, 
            text="Volver", 
            command=self.mostrar_pantalla_inicio,
            style="Secondary.TButton"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def mostrar_resumen_pedido(self, parent, pedido: Pedido):
        """Muestra un resumen del pedido en un frame con opciones adicionales"""
        pedido_frame = ttk.Frame(
            parent, 
            borderwidth=2, 
            relief="groove", 
            padding=10
        )
        pedido_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Encabezado del pedido
        estado_color = {
            "Nuevo": COLORES["info"],
            "En preparación": COLORES["advertencia"],
            "Entregado": COLORES["exito"]
        }.get(pedido.estado, COLORES["texto"])
        
        header_frame = ttk.Frame(pedido_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            header_frame, 
            text=f"Pedido #{pedido.numero} - {pedido.fecha.strftime('%d/%m/%Y %H:%M')}", 
            font=('Helvetica', 12, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame, 
            text=pedido.estado, 
            font=('Helvetica', 12, 'bold'),
            foreground=estado_color
        ).pack(side=tk.RIGHT)
        
        # Productos del pedido
        productos_frame = ttk.Frame(pedido_frame)
        productos_frame.pack(fill=tk.X, padx=10)
        
        for item in pedido.productos:
            ttk.Label(
                productos_frame, 
                text=f"• {item}", 
                font=('Helvetica', 10)
            ).pack(anchor=tk.W, pady=2)
        
        # Total del pedido
        ttk.Label(
            pedido_frame, 
            text=f"Total: ${pedido.total:.2f}", 
            font=('Helvetica', 11, 'bold')
        ).pack(anchor=tk.E, pady=(5, 0))
        
        # Frame para botones de acción
        btn_frame = ttk.Frame(pedido_frame)
        btn_frame.pack(pady=(5, 0))
        
        # Botón para ver detalles (siempre visible)
        ttk.Button(
            btn_frame, 
            text="Ver Detalles", 
            command=lambda p=pedido: self.mostrar_detalle_pedido(p),
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        # Botón "Ya lo recibí" solo para pedidos entregados
        if pedido.estado == "Entregado":
            ttk.Button(
                btn_frame, 
                text="✅ Ya lo recibí", 
                command=lambda p=pedido: self.confirmar_recepcion(p),
                style="Success.TButton"
            ).pack(side=tk.LEFT, padx=5)
        
        # Botón para eliminar pedido (visible para todos los estados)
        ttk.Button(
            btn_frame, 
            text="🗑️ Eliminar", 
            command=lambda p=pedido: self.eliminar_pedido(p),
            style="Error.TButton"
        ).pack(side=tk.LEFT, padx=5)

    def confirmar_recepcion(self, pedido: Pedido):
        """Confirma la recepción de un pedido entregado"""
        if messagebox.askyesno(
            "Confirmar recepción", 
            f"¿Confirmas que has recibido el pedido #{pedido.numero}?", 
            parent=self.root
        ):
            # En un sistema real, aquí podríamos marcar el pedido como recibido
            # Por ahora simplemente lo eliminaremos
            self.eliminar_pedido(pedido)
            messagebox.showinfo(
                "Confirmado", 
                f"Pedido #{pedido.numero} marcado como recibido", 
                parent=self.root
            )

    def eliminar_pedido(self, pedido: Pedido):
        """Elimina un pedido del historial del cliente"""
        if messagebox.askyesno(
            "Eliminar pedido", 
            f"¿Estás seguro de eliminar el pedido #{pedido.numero}?\nEsta acción no se puede deshacer.", 
            parent=self.root
        ):
            # Eliminar el pedido del sistema
            if pedido in self.sistema.pedidos:
                self.sistema.pedidos.remove(pedido)
            
            # Eliminar el pedido del historial del cliente
            if self.cliente_actual and pedido in self.cliente_actual.historial_pedidos:
                self.cliente_actual.historial_pedidos.remove(pedido)
            
            self.sistema.guardar_datos()
            messagebox.showinfo(
                "Éxito", 
                f"Pedido #{pedido.numero} eliminado correctamente", 
                parent=self.root
            )
            
            # Actualizar la vista
            self.mostrar_lista_pedidos()

    def mostrar_detalle_pedido(self, pedido: Pedido):
        """Muestra el detalle completo de un pedido"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título
        ttk.Label(
            main_frame, 
            text=f"📝 Detalle del Pedido #{pedido.numero}", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Frame de detalles
        detalles_frame = ttk.Frame(
            main_frame, 
            padding=15, 
            relief=tk.RAISED, 
            borderwidth=2
        )
        detalles_frame.pack(pady=10, fill=tk.X)
        
        # Información del pedido
        ttk.Label(
            detalles_frame, 
            text=f"👤 Cliente: {pedido.cliente.nombre}", 
            font=('Helvetica', 12)
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Label(
            detalles_frame, 
            text=f"📅 Fecha: {pedido.fecha.strftime('%Y-%m-%d %H:%M:%S')}", 
            font=('Helvetica', 12)
        ).pack(anchor=tk.W, pady=5)
        
        estado_color = {
            "Nuevo": COLORES["info"],
            "En preparación": COLORES["advertencia"],
            "Entregado": COLORES["exito"]
        }.get(pedido.estado, COLORES["texto"])
        
        estado_label = ttk.Label(
            detalles_frame, 
            text=f"🔄 Estado: {pedido.estado}", 
            font=('Helvetica', 12, 'bold'),
            foreground=estado_color
        )
        estado_label.pack(anchor=tk.W, pady=5)
        
        # Lista de productos
        productos_frame = ttk.LabelFrame(
            main_frame, 
            text="🍽️ Productos en el Pedido",
            padding=10
        )
        productos_frame.pack(fill=tk.BOTH, pady=10)
        
        for item in pedido.productos:
            producto_frame = ttk.Frame(productos_frame)
            producto_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                producto_frame, 
                text=f"• {item.cantidad}x {item.producto.nombre} - ${item.producto.precio:.2f} c/u", 
                font=('Helvetica', 10, 'bold')
            ).pack(anchor=tk.W)
            
            # Mostrar opciones personalizadas si existen
            if item.tipo_leche or item.azucar or item.notas:
                opciones_frame = ttk.Frame(producto_frame, padding=(10, 0))
                opciones_frame.pack(anchor=tk.W)
                
                if item.tipo_leche:
                    ttk.Label(
                        opciones_frame, 
                        text=f"Leche: {item.tipo_leche}", 
                        font=('Helvetica', 9)
                    ).pack(side=tk.LEFT, padx=5)
                
                if item.azucar:
                    ttk.Label(
                        opciones_frame, 
                        text=f"Azúcar: {item.azucar}", 
                        font=('Helvetica', 9)
                    ).pack(side=tk.LEFT, padx=5)
                
                if item.notas:
                    ttk.Label(
                        opciones_frame, 
                        text=f"Notas: {item.notas}", 
                        font=('Helvetica', 9)
                    ).pack(side=tk.LEFT, padx=5)
        
        # Total del pedido
        ttk.Label(
            main_frame, 
            text=f"💰 Total: ${pedido.total:.2f}", 
            style="Header.TLabel",
            font=('Helvetica', 14, 'bold')
        ).pack(anchor=tk.E, pady=10, padx=20)
        
        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="🔄 Volver al Menú", 
            command=self.mostrar_menu_productos,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="🏠 Volver al Inicio", 
            command=self.mostrar_pantalla_inicio,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=5)
    
    def mostrar_identificacion_cliente(self):
        """Muestra la pantalla para identificar al cliente"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título
        ttk.Label(main_frame, text="Identificación del Cliente", style="Title.TLabel").pack(pady=10)
        
        # Frame del formulario
        form_frame = ttk.Frame(main_frame, padding=20, relief=tk.RAISED, borderwidth=2)
        form_frame.pack(pady=20, ipadx=20, ipady=20)
        
        # Etiqueta y campo de entrada
        ttk.Label(form_frame, text="Identificación:", font=('Helvetica', 12)).grid(row=0, column=0, pady=10, sticky=tk.W)
        id_entry = ttk.Entry(form_frame, font=('Helvetica', 12), width=30)
        id_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Buscar", command=lambda: self.buscar_cliente(id_entry.get()), 
                  style="Primary.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Nuevo Cliente", command=self.mostrar_registro_cliente, 
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=10)
        
        # Botón volver
        ttk.Button(main_frame, text="Volver", command=self.mostrar_pantalla_inicio, 
                  style="Secondary.TButton").pack(side=tk.BOTTOM, pady=10)
    
    def buscar_cliente(self, id_cliente):
        """Busca un cliente en el sistema"""
        if not id_cliente:
            messagebox.showwarning("Error", "Por favor ingrese una identificación", parent=self.root)
            return
        
        cliente = self.sistema.buscar_cliente(id_cliente)
        if cliente:
            self.cliente_actual = cliente
            messagebox.showinfo("Bienvenido", f"¡Bienvenido/a {cliente.nombre}!", parent=self.root)
            self.mostrar_menu_productos()
        else:
            if messagebox.askyesno("Cliente No Encontrado", 
                                  "No se encontró el cliente. ¿Desea registrarse?", 
                                  parent=self.root):
                self.mostrar_registro_cliente()
    
    def mostrar_registro_cliente(self):
        """Muestra el formulario de registro de cliente"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="Registro de Cliente", style="Title.TLabel").pack(pady=10)
        
        # Frame del formulario
        form_frame = ttk.Frame(main_frame, padding=20, relief=tk.RAISED, borderwidth=2)
        form_frame.pack(pady=20, ipadx=20, ipady=20)
        
        # Campos del formulario
        ttk.Label(form_frame, text="Identificación:", font=('Helvetica', 12)).grid(row=0, column=0, pady=10, sticky=tk.W)
        id_entry = ttk.Entry(form_frame, font=('Helvetica', 12), width=30)
        id_entry.grid(row=0, column=1, pady=10, padx=10)
        
        ttk.Label(form_frame, text="Nombre:", font=('Helvetica', 12)).grid(row=1, column=0, pady=10, sticky=tk.W)
        nombre_entry = ttk.Entry(form_frame, font=('Helvetica', 12), width=30)
        nombre_entry.grid(row=1, column=1, pady=10, padx=10)
        
        ttk.Label(form_frame, text="Teléfono:", font=('Helvetica', 12)).grid(row=2, column=0, pady=10, sticky=tk.W)
        telefono_entry = ttk.Entry(form_frame, font=('Helvetica', 12), width=30)
        telefono_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Botón registrar
        ttk.Button(form_frame, text="Registrar", 
                  command=lambda: self.registrar_cliente(
                      id_entry.get(), nombre_entry.get(), telefono_entry.get()
                  ), style="Primary.TButton"
                  ).grid(row=3, column=0, columnspan=2, pady=20, sticky=tk.EW)
        
        # Botón volver
        ttk.Button(main_frame, text="Volver", command=self.mostrar_identificacion_cliente, 
                  style="Secondary.TButton").pack(side=tk.BOTTOM, pady=10)
    
    def registrar_cliente(self, id_cliente, nombre, telefono):
        """Registra un nuevo cliente en el sistema"""
        if not id_cliente or not nombre or not telefono:
            messagebox.showwarning("Error", "Todos los campos son obligatorios", parent=self.root)
            return
        
        if self.sistema.buscar_cliente(id_cliente):
            messagebox.showwarning("Error", "Ya existe un cliente con esa identificación", parent=self.root)
            return
        
        cliente = self.sistema.registrar_cliente(nombre, telefono, id_cliente)
        self.cliente_actual = cliente
        messagebox.showinfo("Éxito", "Cliente registrado correctamente", parent=self.root)
        self.mostrar_menu_productos()
    
    def mostrar_menu_productos(self):
        """Muestra el menú de productos disponibles"""
        self.limpiar_pantalla()
        self.carrito = []
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título y info del cliente
        ttk.Label(main_frame, text="Menú de Productos", style="Title.TLabel").pack(pady=5)
        ttk.Label(main_frame, text=f"Cliente: {self.cliente_actual.nombre}", style="Header.TLabel").pack()
        
        # Notebook para pestañas de productos
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill=tk.BOTH, pady=10)
        
        # Pestaña Bebidas
        bebidas_tab = ttk.Frame(notebook)
        notebook.add(bebidas_tab, text="☕ Bebidas")
        self.crear_productos_tab(bebidas_tab, self.sistema.inventario.listar_bebidas())
        
        # Pestaña Postres
        postres_tab = ttk.Frame(notebook)
        notebook.add(postres_tab, text="🍰 Postres")
        self.crear_productos_tab(postres_tab, self.sistema.inventario.listar_postres())
        
        # Frame para carrito
        carrito_frame = ttk.LabelFrame(main_frame, text="🛒 Carrito de Compras", padding=10)
        carrito_frame.pack(fill=tk.X, pady=10)
        
        # Listbox para el carrito con scrollbar
        self.carrito_listbox = tk.Listbox(
            carrito_frame, 
            height=5, 
            font=('Helvetica', 10),
            selectbackground=COLORES["primario"],
            selectforeground='white'
        )
        self.carrito_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(carrito_frame, orient=tk.VERTICAL, command=self.carrito_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.carrito_listbox.config(yscrollcommand=scrollbar.set)
        
        # Label para el total
        self.total_label = ttk.Label(
            main_frame, 
            text="Total: $0.00", 
            style="Header.TLabel",
            font=('Helvetica', 12, 'bold')
        )
        self.total_label.pack(anchor=tk.E, padx=20)
        
        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10, fill=tk.X, padx=20)
        
        ttk.Button(
            btn_frame, 
            text="❌ Eliminar Seleccionado", 
            command=self.eliminar_del_carrito,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="✅ Realizar Pedido", 
            command=self.finalizar_pedido,
            style="Primary.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="↩️ Volver", 
            command=self.mostrar_pantalla_inicio,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=5)
    
    def crear_productos_tab(self, tab, productos):
        """Crea una pestaña con los productos disponibles"""
        # Frame contenedor con scroll
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(container, bg=COLORES["fondo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Crear grid de productos
        row, col = 0, 0
        max_cols = 3
        
        for producto in productos:
            if producto.stock > 0:
                producto_frame = ttk.Frame(
                    scrollable_frame, 
                    borderwidth=2, 
                    relief="solid", 
                    padding=10,
                    style='TFrame'
                )
                
                # Nombre y precio
                ttk.Label(
                    producto_frame, 
                    text=producto.nombre, 
                    style="Header.TLabel",
                    font=('Helvetica', 12, 'bold')
                ).pack()
                
                # "Imagen" (emoji)
                img_label = ttk.Label(
                    producto_frame, 
                    text=producto.imagen if hasattr(producto, 'imagen') and producto.imagen else "☕" if isinstance(producto, Bebida) else "🍰",
                    font=('Helvetica', 36),
                    foreground=COLORES["primario"]
                )
                img_label.pack(pady=5)
                
                # Detalles específicos
                detalles_frame = ttk.Frame(producto_frame)
                detalles_frame.pack(fill=tk.X, pady=5)
                
                if isinstance(producto, Bebida):
                    ttk.Label(detalles_frame, text=f"Tamaño: {producto.tamano}").pack(anchor=tk.W)
                elif isinstance(producto, Postre):
                    ttk.Label(detalles_frame, text=f"Ingredientes: {producto.mostrar_ingredientes()}").pack(anchor=tk.W)
                
                ttk.Label(detalles_frame, text=f"💲 Precio: ${producto.precio:.2f}", font=('Helvetica', 11, 'bold')).pack(anchor=tk.W)
                ttk.Label(detalles_frame, text=f"📦 Disponible: {producto.stock}", 
                         foreground=COLORES["exito"] if producto.stock > 5 else COLORES["advertencia"] if producto.stock > 0 else COLORES["error"],
                         font=('Helvetica', 10)).pack(anchor=tk.W)
                
                # Botón agregar con opciones
                self.crear_boton_agregar(producto_frame, producto)
                
                # Posicionamiento en el grid
                producto_frame.grid(
                    row=row, 
                    column=col, 
                    padx=10, 
                    pady=10, 
                    sticky="nsew"
                )
                
                # Configurar columnas para expansión
                scrollable_frame.columnconfigure(col, weight=1)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        # Configurar filas para expansión
        for r in range(row + 1):
            scrollable_frame.rowconfigure(r, weight=1)
    
    def crear_boton_agregar(self, parent, producto):
        """Crea el botón de agregar con opciones para el producto"""
        def mostrar_opciones():
            opciones_window = tk.Toplevel(self.root)
            opciones_window.title(f"Opciones para {producto.nombre}")
            opciones_window.geometry("400x300")
            opciones_window.resizable(False, False)
            
            # Variables para las opciones
            cantidad = tk.IntVar(value=1)
            tipo_leche = tk.StringVar(value=TIPOS_LECHE[0] if isinstance(producto, Bebida) else "")
            nivel_azucar = tk.StringVar(value=NIVELES_AZUCAR[2] if isinstance(producto, Bebida) else "")
            notas = tk.StringVar()
            
            # Frame principal
            main_frame = ttk.Frame(opciones_window, padding=10)
            main_frame.pack(expand=True, fill=tk.BOTH)
            
            # Cantidad
            ttk.Label(main_frame, text="Cantidad:").grid(row=0, column=0, sticky=tk.W, pady=5)
            ttk.Spinbox(main_frame, from_=1, to=10, textvariable=cantidad, width=5).grid(row=0, column=1, sticky=tk.W, pady=5)
            
            # Opciones específicas para bebidas
            if isinstance(producto, Bebida):
                # Tipo de leche
                ttk.Label(main_frame, text="Tipo de leche:").grid(row=1, column=0, sticky=tk.W, pady=5)
                ttk.Combobox(
                    main_frame, 
                    textvariable=tipo_leche, 
                    values=TIPOS_LECHE,
                    state="readonly"
                ).grid(row=1, column=1, sticky=tk.W, pady=5)
                
                # Nivel de azúcar
                ttk.Label(main_frame, text="Nivel de azúcar:").grid(row=2, column=0, sticky=tk.W, pady=5)
                ttk.Combobox(
                    main_frame, 
                    textvariable=nivel_azucar, 
                    values=NIVELES_AZUCAR,
                    state="readonly"
                ).grid(row=2, column=1, sticky=tk.W, pady=5)
            
            # Notas adicionales
            ttk.Label(main_frame, text="Notas adicionales:").grid(row=3, column=0, sticky=tk.W, pady=5)
            ttk.Entry(main_frame, textvariable=notas).grid(row=3, column=1, sticky=tk.W, pady=5)
            
            # Botones
            btn_frame = ttk.Frame(main_frame)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
            
            ttk.Button(
                btn_frame, 
                text="Agregar al Carrito", 
                command=lambda: self.agregar_con_opciones(
                    producto, 
                    cantidad.get(),
                    tipo_leche.get() if isinstance(producto, Bebida) else None,
                    nivel_azucar.get() if isinstance(producto, Bebida) else None,
                    notas.get(),
                    opciones_window
                ),
                style="Primary.TButton"
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                btn_frame, 
                text="Cancelar", 
                command=opciones_window.destroy,
                style="Secondary.TButton"
            ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            parent, 
            text="➕ Agregar al Carrito", 
            command=mostrar_opciones,
            style="Primary.TButton"
        ).pack(fill=tk.X, pady=5, ipady=5)
    
    def agregar_con_opciones(self, producto, cantidad, tipo_leche, azucar, notas, ventana):
        """Agrega un producto al carrito con las opciones seleccionadas"""
        if cantidad < 1:
            messagebox.showwarning("Error", "La cantidad debe ser al menos 1", parent=ventana)
            return
        
        if producto.stock >= cantidad:
            item = ProductoConExtras(
                producto=producto,
                cantidad=cantidad,
                tipo_leche=tipo_leche,
                azucar=azucar,
                notas=notas
            )
            self.carrito.append(item)
            self.actualizar_carrito()
            ventana.destroy()
            messagebox.showinfo("Éxito", f"{cantidad}x {producto.nombre} agregado al carrito", parent=self.root)
        else:
            messagebox.showwarning("Error", "No hay suficiente stock", parent=ventana)
    
    def eliminar_del_carrito(self):
        """Elimina un producto seleccionado del carrito"""
        try:
            seleccion = self.carrito_listbox.curselection()[0]
            item = self.carrito.pop(seleccion)
            self.actualizar_carrito()
        except IndexError:
            messagebox.showwarning("Error", "Seleccione un producto para eliminar", parent=self.root)
    
    def actualizar_carrito(self):
        """Actualiza la visualización del carrito y el total"""
        self.carrito_listbox.delete(0, tk.END)
        total = 0.0
        
        for item in self.carrito:
            self.carrito_listbox.insert(tk.END, str(item))
            total += item.precio_total
        
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def finalizar_pedido(self):
        """Finaliza el pedido y lo registra en el sistema"""
        if not self.carrito:
            messagebox.showwarning("Error", "El carrito está vacío", parent=self.root)
            return
        
        # Crear pedido
        pedido = self.sistema.crear_pedido(self.cliente_actual.identificacion, self.carrito)
        
        if pedido:
            messagebox.showinfo(
                "Éxito", 
                f"Pedido #{pedido.numero} creado con éxito.\nTotal: ${pedido.total:.2f}", 
                parent=self.root
            )
            self.carrito = []
            self.actualizar_carrito()
            self.mostrar_detalle_pedido(pedido)
        else:
            messagebox.showerror("Error", "No se pudo crear el pedido", parent=self.root)
    
    def mostrar_login_empleado(self):
        """Muestra el formulario de inicio de sesión para empleados"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(
            main_frame, 
            text="🔐 Inicio de Sesión para Empleados", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Frame del formulario
        form_frame = ttk.Frame(
            main_frame, 
            padding=20, 
            relief=tk.RAISED, 
            borderwidth=2
        )
        form_frame.pack(pady=20, ipadx=20, ipady=20)
        
        # Campos del formulario
        ttk.Label(
            form_frame, 
            text="👤 Usuario:", 
            font=('Helvetica', 12)
        ).grid(row=0, column=0, pady=10, sticky=tk.W)
        
        self.usuario_entry = ttk.Entry(
            form_frame, 
            font=('Helvetica', 12), 
            width=30
        )
        self.usuario_entry.grid(row=0, column=1, pady=10, padx=10)
        
        ttk.Label(
            form_frame, 
            text="🔒 Contraseña:", 
            font=('Helvetica', 12)
        ).grid(row=1, column=0, pady=10, sticky=tk.W)
        
        self.contrasena_entry = ttk.Entry(
            form_frame, 
            font=('Helvetica', 12), 
            width=30, 
            show="*"
        )
        self.contrasena_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            btn_frame, 
            text="Iniciar Sesión", 
            command=self.validar_empleado,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame, 
            text="Volver", 
            command=self.mostrar_pantalla_inicio,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=10)
    
    def validar_empleado(self):
        """Valida las credenciales del empleado"""
        usuario = self.usuario_entry.get()
        contrasena = self.contrasena_entry.get()
        
        empleado = self.sistema.validar_empleado(usuario, contrasena)
        if empleado:
            self.empleado_actual = empleado
            messagebox.showinfo(
                "Bienvenido", 
                f"Bienvenido/a {empleado.nombre} ({empleado.puesto})", 
                parent=self.root
            )
            self.mostrar_panel_empleado()
        else:
            messagebox.showerror(
                "Error", 
                "Usuario o contraseña incorrectos", 
                parent=self.root
            )
    
    def mostrar_panel_empleado(self):
        """Muestra el panel de control para empleados"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título
        ttk.Label(
            main_frame, 
            text=f"👨‍💼 Panel de Empleado - {self.empleado_actual.nombre}", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Información del empleado
        info_frame = ttk.Frame(main_frame, padding=10, relief=tk.RAISED, borderwidth=1)
        info_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(
            info_frame, 
            text=f"Puesto: {self.empleado_actual.puesto}", 
            font=('Helvetica', 12)
        ).pack(anchor=tk.W)
        
        ttk.Label(
            info_frame, 
            text=f"Teléfono: {self.empleado_actual.telefono}", 
            font=('Helvetica', 12)
        ).pack(anchor=tk.W)
        
        # Botones de acciones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame, 
            text="➕ Agregar Producto", 
            command=self.mostrar_agregar_producto,
            style="Primary.TButton"
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(
            btn_frame, 
            text="📦 Actualizar Stock", 
            command=self.mostrar_actualizar_stock,
            style="Primary.TButton"
        ).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(
            btn_frame, 
            text="📋 Ver Inventario", 
            command=self.mostrar_inventario,
            style="Primary.TButton"
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(
            btn_frame, 
            text="📊 Reporte de Ventas", 
            command=self.mostrar_reporte_ventas,
            style="Primary.TButton"
        ).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(
            btn_frame, 
            text="📝 Gestionar Pedidos", 
            command=self.mostrar_gestion_pedidos,
            style="Primary.TButton"
        ).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        # Botón para exportar clientes a Excel
        ttk.Button(
            btn_frame,
            text="Exportar Clientes a Excel",
            command=self.exportar_clientes_excel,
            style="Primary.TButton"
            ).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        # Botón cerrar sesión
        ttk.Button(
            main_frame, 
            text="🚪 Cerrar Sesión", 
            command=self.cerrar_sesion_empleado,
            style="Secondary.TButton"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def mostrar_gestion_pedidos(self):
        """Muestra la interfaz para gestionar pedidos (empleados)"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título
        ttk.Label(
            main_frame, 
            text="📝 Gestión de Pedidos", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Notebook para pestañas de estados
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill=tk.BOTH, pady=10)
        
        # Pestaña de pedidos nuevos
        nuevos_tab = ttk.Frame(notebook)
        notebook.add(nuevos_tab, text="🆕 Nuevos")
        self.crear_lista_pedidos_empleado(nuevos_tab, "Nuevo")
        
        # Pestaña de pedidos en preparación
        preparacion_tab = ttk.Frame(notebook)
        notebook.add(preparacion_tab, text="👨‍🍳 En Preparación")
        self.crear_lista_pedidos_empleado(preparacion_tab, "En preparación")
        
        # Pestaña de pedidos entregados
        entregados_tab = ttk.Frame(notebook)
        notebook.add(entregados_tab, text="✅ Entregados")
        self.crear_lista_pedidos_empleado(entregados_tab, "Entregado")
        
        # Botón volver
        ttk.Button(
            main_frame, 
            text="Volver", 
            command=self.mostrar_panel_empleado,
            style="Secondary.TButton"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def crear_lista_pedidos_empleado(self, parent, estado: str):
        """Crea una lista de pedidos para el panel de empleados"""
        # Frame contenedor con scroll
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(container, bg=COLORES["fondo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Obtener pedidos según estado
        pedidos = self.sistema.listar_pedidos(estado)
        
        if not pedidos:
            ttk.Label(
                scrollable_frame, 
                text=f"No hay pedidos {estado.lower()}", 
                font=('Helvetica', 12)
            ).pack(pady=20)
        else:
            for pedido in pedidos:
                self.mostrar_pedido_empleado(scrollable_frame, pedido)
    
    def mostrar_pedido_empleado(self, parent, pedido: Pedido):
        """Muestra un pedido en el panel de empleados"""
        pedido_frame = ttk.Frame(
            parent, 
            borderwidth=2, 
            relief="groove", 
            padding=10
        )
        pedido_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Encabezado del pedido
        header_frame = ttk.Frame(pedido_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            header_frame, 
            text=f"Pedido #{pedido.numero} - Cliente: {pedido.cliente.nombre}", 
            font=('Helvetica', 12, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame, 
            text=f"Fecha: {pedido.fecha.strftime('%d/%m/%Y %H:%M')}", 
            font=('Helvetica', 10)
        ).pack(side=tk.RIGHT)
        
        # Productos del pedido
        productos_frame = ttk.Frame(pedido_frame)
        productos_frame.pack(fill=tk.X, padx=10)
        
        for item in pedido.productos:
            ttk.Label(
                productos_frame, 
                text=f"• {item}", 
                font=('Helvetica', 10)
            ).pack(anchor=tk.W, pady=2)
        
        # Total del pedido
        ttk.Label(
            pedido_frame, 
            text=f"Total: ${pedido.total:.2f}", 
            font=('Helvetica', 11, 'bold')
        ).pack(anchor=tk.E, pady=(5, 0))
        
        # Botones de acción según estado
        btn_frame = ttk.Frame(pedido_frame)
        btn_frame.pack(pady=(5, 0))
        
        if pedido.estado == "Nuevo":
            ttk.Button(
                btn_frame, 
                text="Iniciar Preparación", 
                command=lambda p=pedido: self.procesar_pedido(p),
                style="Primary.TButton"
            ).pack(side=tk.LEFT, padx=5)
        
        elif pedido.estado == "En preparación":
            ttk.Button(
                btn_frame, 
                text="Marcar como Entregado", 
                command=lambda p=pedido: self.entregar_pedido(p),
                style="Primary.TButton"
            ).pack(side=tk.LEFT, padx=5)
    
    def procesar_pedido(self, pedido: Pedido):
        """Cambia el estado del pedido a 'En preparación'"""
        if self.sistema.procesar_pedido(pedido.numero, self.empleado_actual.usuario):
            messagebox.showinfo(
                "Éxito", 
                f"Pedido #{pedido.numero} en preparación", 
                parent=self.root
            )
            self.mostrar_gestion_pedidos()
        else:
            messagebox.showerror(
                "Error", 
                "No se pudo procesar el pedido", 
                parent=self.root
            )
    
    def entregar_pedido(self, pedido: Pedido):
        """Marca el pedido como entregado"""
        if self.sistema.entregar_pedido(pedido.numero, self.empleado_actual.usuario):
            messagebox.showinfo(
                "Éxito", 
                f"Pedido #{pedido.numero} marcado como entregado", 
                parent=self.root
            )
            self.mostrar_gestion_pedidos()
        else:
            messagebox.showerror(
                "Error", 
                "No se pudo marcar el pedido como entregado", 
                parent=self.root
            )
    
    def mostrar_agregar_producto(self):
        """Muestra el formulario para agregar un nuevo producto"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(
            main_frame, 
            text="➕ Agregar Producto", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Frame del formulario
        form_frame = ttk.Frame(
            main_frame, 
            padding=20, 
            relief=tk.RAISED, 
            borderwidth=2
        )
        form_frame.pack(pady=20, ipadx=20, ipady=20)
        
        # Campos del formulario
        ttk.Label(
            form_frame, 
            text="🆔 Código:", 
            font=('Helvetica', 12)
        ).grid(row=0, column=0, pady=10, sticky=tk.W)
        
        codigo_entry = ttk.Entry(
            form_frame, 
            font=('Helvetica', 12), 
            width=30
        )
        codigo_entry.grid(row=0, column=1, pady=10, padx=10)
        
        ttk.Label(
            form_frame, 
            text="📛 Nombre:", 
            font=('Helvetica', 12)
        ).grid(row=1, column=0, pady=10, sticky=tk.W)
        
        nombre_entry = ttk.Entry(
            form_frame, 
            font=('Helvetica', 12), 
            width=30
        )
        nombre_entry.grid(row=1, column=1, pady=10, padx=10)
        
        ttk.Label(
            form_frame, 
            text="💲 Precio:", 
            font=('Helvetica', 12)
        ).grid(row=2, column=0, pady=10, sticky=tk.W)
        
        precio_entry = ttk.Entry(
            form_frame, 
            font=('Helvetica', 12), 
            width=30
        )
        precio_entry.grid(row=2, column=1, pady=10, padx=10)
        
        ttk.Label(
            form_frame, 
            text="📦 Stock:", 
            font=('Helvetica', 12)
        ).grid(row=3, column=0, pady=10, sticky=tk.W)
        
        stock_entry = ttk.Entry(
            form_frame, 
            font=('Helvetica', 12), 
            width=30
        )
        stock_entry.grid(row=3, column=1, pady=10, padx=10)
        
        ttk.Label(
            form_frame, 
            text="📌 Tipo:", 
            font=('Helvetica', 12)
        ).grid(row=4, column=0, pady=10, sticky=tk.W)
        
        tipo_var = tk.StringVar(value="Bebida")
        
        ttk.Radiobutton(
            form_frame, 
            text="☕ Bebida", 
            variable=tipo_var, 
            value="Bebida",
            style='TRadiobutton'
        ).grid(row=4, column=1, pady=5, sticky=tk.W)
        
        ttk.Radiobutton(
            form_frame, 
            text="🍰 Postre", 
            variable=tipo_var, 
            value="Postre",
            style='TRadiobutton'
        ).grid(row=5, column=1, pady=5, sticky=tk.W)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            btn_frame, 
            text="Agregar", 
            command=lambda: self.agregar_producto(
                codigo_entry.get(), 
                nombre_entry.get(), 
                precio_entry.get(), 
                stock_entry.get(), 
                tipo_var.get()
            ),
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame, 
            text="Volver", 
            command=self.mostrar_panel_empleado,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=10)
    
    def agregar_producto(self, codigo, nombre, precio, stock, tipo):
        """Agrega un nuevo producto al inventario"""
        if not codigo or not nombre or not precio or not stock:
            messagebox.showwarning("Error", "Todos los campos son obligatorios", parent=self.root)
            return
        
        try:
            precio = float(precio)
            stock = int(stock)
            if precio <= 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Precio y stock deben ser números válidos", parent=self.root)
            return
        
        if tipo == "Bebida":
            producto = Bebida(codigo, nombre, precio, stock)
        elif tipo == "Postre":
            producto = Postre(codigo, nombre, precio, stock)
        
        self.sistema.inventario.agregar_producto(producto)
        self.sistema.guardar_datos()
        messagebox.showinfo("Éxito", "Producto agregado correctamente", parent=self.root)
        self.mostrar_panel_empleado()
    
    def mostrar_actualizar_stock(self):
        """Muestra la lista de productos para actualizar stock"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(
            main_frame, 
            text="📦 Actualizar Stock", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Frame contenedor con scroll
        container = ttk.Frame(main_frame)
        container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(container, bg=COLORES["fondo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Lista de productos
        for producto in self.sistema.inventario.listar_productos():
            producto_frame = ttk.Frame(
                scrollable_frame, 
                borderwidth=1, 
                relief="solid", 
                padding=10
            )
            producto_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Información del producto
            ttk.Label(
                producto_frame, 
                text=f"{producto.nombre} (Código: {producto.codigo})", 
                font=('Helvetica', 11, 'bold')
            ).pack(anchor=tk.W)
            
            ttk.Label(
                producto_frame, 
                text=f"Stock actual: {producto.stock}", 
                font=('Helvetica', 10)
            ).pack(anchor=tk.W)
            
            # Botón actualizar
            ttk.Button(
                producto_frame, 
                text="Actualizar Stock", 
                command=lambda p=producto: self.actualizar_stock_producto(p),
                style="Primary.TButton"
            ).pack(side=tk.RIGHT, padx=5)
        
        # Botón volver
        ttk.Button(
            main_frame, 
            text="Volver", 
            command=self.mostrar_panel_empleado,
            style="Secondary.TButton"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def actualizar_stock_producto(self, producto):
        """Actualiza el stock de un producto específico"""
        nuevo_stock = simpledialog.askinteger(
            "Actualizar Stock", 
            f"Ingrese el nuevo stock para {producto.nombre}:", 
            parent=self.root,
            minvalue=0
        )
        
        if nuevo_stock is not None:
            producto.actualizar_stock(nuevo_stock - producto.stock)
            self.sistema.guardar_datos()
            messagebox.showinfo("Éxito", "Stock actualizado correctamente", parent=self.root)
            self.mostrar_actualizar_stock()
    
    def mostrar_inventario(self):
        """Muestra el inventario completo"""
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(
            main_frame, 
            text="📋 Inventario Completo", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Frame contenedor con scroll
        container = ttk.Frame(main_frame)
        container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(container, bg=COLORES["fondo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Lista de productos
        for producto in self.sistema.inventario.listar_productos():
            producto_frame = ttk.Frame(
                scrollable_frame, 
                borderwidth=1, 
                relief="solid", 
                padding=10
            )
            producto_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Tipo de producto (icono)
            tipo_icono = "☕" if isinstance(producto, Bebida) else "🍰"
            ttk.Label(
                producto_frame, 
                text=tipo_icono, 
                font=('Helvetica', 14)
            ).pack(side=tk.LEFT, padx=5)
            
            # Información del producto
            info_frame = ttk.Frame(producto_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            ttk.Label(
                info_frame, 
                text=f"{producto.nombre} (Código: {producto.codigo})", 
                font=('Helvetica', 11, 'bold')
            ).pack(anchor=tk.W)
            
            ttk.Label(
                info_frame, 
                text=f"Precio: ${producto.precio:.2f} | Stock: {producto.stock}", 
                font=('Helvetica', 10)
            ).pack(anchor=tk.W)
            
            # Detalles específicos
            if isinstance(producto, Bebida):
                ttk.Label(
                    info_frame, 
                    text=f"Tamaño: {producto.tamano}", 
                    font=('Helvetica', 10)
                ).pack(anchor=tk.W)
            elif isinstance(producto, Postre):
                ttk.Label(
                    info_frame, 
                    text=f"Ingredientes: {producto.mostrar_ingredientes()}", 
                    font=('Helvetica', 10)
                ).pack(anchor=tk.W)
        
        # Botón volver
        ttk.Button(
            main_frame, 
            text="Volver", 
            command=self.mostrar_panel_empleado,
            style="Secondary.TButton"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def mostrar_reporte_ventas(self):
        """Muestra un reporte de ventas"""
        reporte = self.sistema.generar_reporte_ventas()
        
        self.limpiar_pantalla()
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(
            main_frame, 
            text="📊 Reporte de Ventas", 
            style="Title.TLabel"
        ).pack(pady=10)
        
        # Frame de información
        info_frame = ttk.Frame(
            main_frame, 
            padding=15, 
            relief=tk.RAISED, 
            borderwidth=2
        )
        info_frame.pack(pady=10, fill=tk.X)
        
        # Total de ventas
        ttk.Label(
            info_frame, 
            text=f"💰 Total de ventas: ${reporte['total_ventas']:.2f}", 
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Label(
            info_frame, 
            text=f"📦 Pedidos completados: {reporte['pedidos_completados']}", 
            font=('Helvetica', 12)
        ).pack(anchor=tk.W, pady=5)
        
        # Productos más vendidos
        productos_vendidos = sorted(
            reporte['productos_vendidos'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]  # Top 5
        
        ttk.Label(
            info_frame, 
            text="🏆 Productos más vendidos:", 
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W, pady=(15, 5))
        
        for codigo, cantidad in productos_vendidos:
            producto = self.sistema.inventario.obtener_producto(codigo)
            if producto:
                ttk.Label(
                    info_frame, 
                    text=f"• {producto.nombre}: {cantidad} unidades", 
                    font=('Helvetica', 11)
                ).pack(anchor=tk.W, padx=20)
        
        # Botón volver
        ttk.Button(
            main_frame, 
            text="Volver", 
            command=self.mostrar_panel_empleado,
            style="Secondary.TButton"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def cerrar_sesion_empleado(self):
        """Cierra la sesión del empleado"""
        self.empleado_actual = None
        self.mostrar_pantalla_inicio()
    
    def exportar_clientes_excel(self):
        """Exporta los datos de clientes a un archivo Excel"""
        if self.sistema.exportar_clientes_excel():
            messagebox.showinfo(
                "Éxito",
                "Datos de clientes exportados correctamente a 'clientes_cafeteria.xlsx'",
                parent=self.root
            )
        else:
            messagebox.showerror(
                "Error",
                "No se pudo exportar los datos. Asegúrate de tener instalado openpyxl (pip install openpyxl)",
                parent=self.root
            )

    def cerrar_sesion_empleado(self):
        """Cierra la sesión del empleado"""
        self.empleado_actual = None
        self.mostrar_pantalla_inicio()
# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazCafeteria(root)
    root.mainloop()
-- ============================================================
-- SCRIPT SQL - Sistema de Inventario y Ventas
-- Base de datos: bd_inventario
-- ============================================================

-- Crear la base de datos (ejecutar como superusuario si no existe)
-- CREATE DATABASE bd_inventario;

-- Conectarse a la base de datos: \c bd_inventario

-- ============================================================
-- 1. TABLA: categoria
--    Categorías de los productos (ej: Electrónica, Ropa, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS categoria (
    id_categoria SERIAL PRIMARY KEY,
    descripcion  VARCHAR(100) NOT NULL,
    activo       BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 2. TABLA: proveedor
--    Proveedores que suministran los productos
-- ============================================================
CREATE TABLE IF NOT EXISTS proveedor (
    id_proveedor SERIAL PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL,
    contacto     VARCHAR(100),
    telefono     VARCHAR(20),
    email        VARCHAR(100),
    direccion    VARCHAR(200),
    activo       BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 3. TABLA: producto
--    Catálogo de productos con precios de compra/venta y stock
-- ============================================================
CREATE TABLE IF NOT EXISTS producto (
    id_producto   SERIAL PRIMARY KEY,
    id_categoria  INT           NOT NULL REFERENCES categoria(id_categoria),
    id_proveedor  INT           NOT NULL REFERENCES proveedor(id_proveedor),
    codigo        VARCHAR(50)   UNIQUE NOT NULL,
    descripcion   VARCHAR(200)  NOT NULL,
    precio_compra NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    precio_venta  NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    stock         INT           NOT NULL DEFAULT 0,
    stock_minimo  INT           NOT NULL DEFAULT 0,
    unidad        VARCHAR(30)   NOT NULL DEFAULT 'unidad',
    activo        BOOLEAN       NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 4. TABLA: cliente
--    Clientes que realizan compras / ventas
-- ============================================================
CREATE TABLE IF NOT EXISTS cliente (
    id_cliente SERIAL PRIMARY KEY,
    ci         VARCHAR(20)  UNIQUE NOT NULL,
    nombre     VARCHAR(100) NOT NULL,
    paterno    VARCHAR(100),
    materno    VARCHAR(100),
    telefono   VARCHAR(20),
    email      VARCHAR(100),
    direccion  VARCHAR(200),
    activo     BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 5. TABLA: venta
--    Cabecera de cada venta realizada
-- ============================================================
CREATE TABLE IF NOT EXISTS venta (
    id_venta    SERIAL PRIMARY KEY,
    id_cliente  INT           NOT NULL REFERENCES cliente(id_cliente),
    fecha_venta DATE          NOT NULL DEFAULT CURRENT_DATE,
    total       NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    descuento   NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    estado      VARCHAR(20)   NOT NULL DEFAULT 'pendiente'
                              CHECK (estado IN ('pendiente','completada','anulada')),
    observacion TEXT
);

-- ============================================================
-- 6. TABLA: detalle_venta
--    Detalle de los productos incluidos en cada venta
-- ============================================================
CREATE TABLE IF NOT EXISTS detalle_venta (
    id_detalle      SERIAL PRIMARY KEY,
    id_venta        INT           NOT NULL REFERENCES venta(id_venta) ON DELETE CASCADE,
    id_producto     INT           NOT NULL REFERENCES producto(id_producto),
    cantidad        INT           NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL,
    descuento       NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    subtotal        NUMERIC(10,2) NOT NULL
);

-- ============================================================
-- DATOS DE EJEMPLO (opcional - borrar si no se necesita)
-- ============================================================

INSERT INTO categoria (descripcion, activo) VALUES
    ('Electrónica', true),
    ('Ropa y Calzado', true),
    ('Alimentos', true),
    ('Hogar y Decoración', true);

INSERT INTO proveedor (nombre, contacto, telefono, email, direccion, activo) VALUES
    ('Distribuidora Tech SRL', 'Juan Pérez', '70012345', 'jperez@tech.com', 'Av. Camacho 123', true),
    ('Textiles Bolivia', 'Ana López', '71198765', 'alopez@textiles.com', 'Calle Murillo 456', true);

INSERT INTO producto (id_categoria, id_proveedor, codigo, descripcion, precio_compra, precio_venta, stock, stock_minimo, unidad, activo) VALUES
    (1, 1, 'EL-001', 'Cable USB-C 1m', 15.00, 25.00, 100, 10, 'unidad', true),
    (1, 1, 'EL-002', 'Cargador 20W', 50.00, 85.00, 50,  5,  'unidad', true),
    (2, 2, 'RO-001', 'Camiseta Algodón M', 30.00, 55.00, 80,  10, 'unidad', true),
    (3, 1, 'AL-001', 'Arroz 1kg',  5.00, 9.00, 200, 20, 'kg',     true);

INSERT INTO cliente (ci, nombre, paterno, materno, telefono, email, direccion, activo) VALUES
    ('12345678', 'María', 'Flores', 'Quispe', '76543210', 'mflores@email.com', 'Av. Villazon 789', true),
    ('87654321', 'Carlos', 'Mamani', 'Huanca', '79876543', 'cmamani@email.com', 'Calle Potosí 321', true);

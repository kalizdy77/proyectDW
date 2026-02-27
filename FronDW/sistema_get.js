const BASE_URL = 'http://127.0.0.1:8000';
let currentTab = 'categoria';
let currentData = [];
let editingId = null;

// Catalogs for Venta
let cachedClientes = [];
let cachedProductos = [];

// Configuration for each entity
const CONFIG = {
    categoria: {
        title: 'Categorías',
        endpoint: '/categoria',
        idField: 'id_categoria',
        fields: [
            { name: 'descripcion', label: 'Descripción', type: 'text', required: true },
            { name: 'activo', label: 'Activo', type: 'checkbox' }
        ],
        columns: ['ID', 'Descripción', 'Estado', 'Acciones']
    },
    producto: {
        title: 'Productos',
        endpoint: '/producto',
        idField: 'id_producto',
        fields: [
            { name: 'id_categoria', label: 'ID Categoría', type: 'number', required: true },
            { name: 'id_proveedor', label: 'ID Proveedor', type: 'number', required: true },
            { name: 'codigo', label: 'Código', type: 'text', required: true },
            { name: 'descripcion', label: 'Descripción', type: 'text', required: true },
            { name: 'precio_compra', label: 'Precio Compra', type: 'number', step: '0.01', required: true },
            { name: 'precio_venta', label: 'Precio Venta', type: 'number', step: '0.01', required: true },
            { name: 'stock', label: 'Stock', type: 'number', required: true },
            { name: 'stock_minimo', label: 'Stock Mínimo', type: 'number', required: true },
            { name: 'unidad', label: 'Unidad', type: 'text', required: true },
            { name: 'activo', label: 'Activo', type: 'checkbox' }
        ],
        columns: ['ID', 'Código', 'Descripción', 'Stock', 'P. Venta', 'Estado', 'Acciones']
    },
    cliente: {
        title: 'Clientes',
        endpoint: '/cliente',
        idField: 'id_cliente',
        fields: [
            { name: 'ci', label: 'CI', type: 'text', required: true },
            { name: 'nombre', label: 'Nombre', type: 'text', required: true },
            { name: 'paterno', label: 'A. Paterno', type: 'text', required: true },
            { name: 'materno', label: 'A. Materno', type: 'text' },
            { name: 'telefono', label: 'Teléfono', type: 'text' },
            { name: 'email', label: 'Email', type: 'email' },
            { name: 'direccion', label: 'Dirección', type: 'text' },
            { name: 'activo', label: 'Activo', type: 'checkbox' }
        ],
        columns: ['ID', 'CI', 'Nombre Completo', 'Teléfono', 'Estado', 'Acciones']
    },
    proveedor: {
        title: 'Proveedores',
        endpoint: '/proveedor',
        idField: 'id_proveedor',
        fields: [
            { name: 'nombre', label: 'Nombre', type: 'text', required: true },
            { name: 'contacto', label: 'Contacto', type: 'text' },
            { name: 'telefono', label: 'Teléfono', type: 'text' },
            { name: 'email', label: 'Email', type: 'email' },
            { name: 'direccion', label: 'Dirección', type: 'text' },
            { name: 'activo', label: 'Activo', type: 'checkbox' }
        ],
        columns: ['ID', 'Nombre', 'Contacto', 'Teléfono', 'Estado', 'Acciones']
    },
    venta: {
        title: 'Ventas',
        endpoint: '/venta',
        idField: 'id_venta',
        fields: [
            { name: 'id_cliente', label: 'Cliente', type: 'select', required: true },
            { name: 'fecha_venta', label: 'Fecha (YYYY-MM-DD)', type: 'date', required: true },
            { name: 'total', label: 'Total', type: 'number', step: '0.01', readOnly: true },
            { name: 'descuento', label: 'Descuento', type: 'number', step: '0.01' },
            { name: 'estado', label: 'Estado', type: 'select', options: ['pendiente', 'completada', 'anulada'], required: true },
            { name: 'observacion', label: 'Observación', type: 'textarea' }
        ],
        columns: ['ID', 'Cliente', 'Fecha', 'Total', 'Estado', 'Acciones']
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    switchTab('categoria');

    document.getElementById('main-form').addEventListener('submit', (e) => {
        e.preventDefault();
        handleSubmit();
    });
});

// Tab Switching
async function switchTab(tab) {
    currentTab = tab;

    // Update active nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.id === `nav-${tab}`);
    });
    document.getElementById('current-title').textContent = CONFIG[tab].title;

    if (tab === 'venta') {
        await preloadCatalogs();
    }

    // Refresh Data
    loadData();
}

async function preloadCatalogs() {
    try {
        const [resCli, resProd] = await Promise.all([
            fetch(`${BASE_URL}/cliente/`),
            fetch(`${BASE_URL}/producto/`)
        ]);
        cachedClientes = await resCli.json();
        cachedProductos = await resProd.json();
    } catch (error) {
        console.error('Error precargando catálogos:', error);
    }
}

// Load Data from Backend
async function loadData() {
    try {
        const response = await fetch(`${BASE_URL}${CONFIG[currentTab].endpoint}/`);
        if (!response.ok) throw new Error('Error al cargar datos');
        currentData = await response.json();
        renderTable();
    } catch (error) {
        showToast(error.message, 'danger');
    }
}

// Render Table based on current entity
function renderTable() {
    const head = document.getElementById('table-head');
    const body = document.getElementById('table-body');
    const config = CONFIG[currentTab];

    // Render Head
    head.innerHTML = `<tr>${config.columns.map(col => `<th>${col}</th>`).join('')}</tr>`;

    // Render Body
    body.innerHTML = currentData.map(row => {
        let cells = '';
        if (currentTab === 'categoria') {
            cells = `
                <td>${row.id_categoria}</td>
                <td>${row.descripcion}</td>
                <td>${row.activo ? '<span class="badge badge-success">Activo</span>' : '<span class="badge badge-danger">Inactivo</span>'}</td>
            `;
        } else if (currentTab === 'producto') {
            cells = `
                <td>${row.id_producto}</td>
                <td>${row.codigo}</td>
                <td>${row.descripcion}</td>
                <td>${row.stock} ${row.unidad}</td>
                <td>$${row.precio_venta}</td>
                <td>${row.activo ? '<span class="badge badge-success">Activo</span>' : '<span class="badge badge-danger">Inactivo</span>'}</td>
            `;
        } else if (currentTab === 'cliente') {
            cells = `
                <td>${row.id_cliente}</td>
                <td>${row.ci}</td>
                <td>${row.nombre} ${row.paterno}</td>
                <td>${row.telefono}</td>
                <td>${row.activo ? '<span class="badge badge-success">Activo</span>' : '<span class="badge badge-danger">Inactivo</span>'}</td>
            `;
        } else if (currentTab === 'proveedor') {
            cells = `
                <td>${row.id_proveedor}</td>
                <td>${row.nombre}</td>
                <td>${row.contacto}</td>
                <td>${row.telefono}</td>
                <td>${row.activo ? '<span class="badge badge-success">Activo</span>' : '<span class="badge badge-danger">Inactivo</span>'}</td>
            `;
        } else if (currentTab === 'venta') {
            cells = `
                <td>${row.id_venta}</td>
                <td>${row.cliente || row.id_cliente}</td>
                <td>${row.fecha_venta}</td>
                <td><span class="badge ${row.estado === 'completada' ? 'badge-success' : 'badge-danger'}">${row.estado}</span></td>
            `;
        }

        const id = row[config.idField];
        return `
            <tr>
                ${cells}
                <td class="action-btns">
                    ${currentTab === 'venta' ? `
                        <button class="action-btn" onclick="viewSaleDetails(${id})" title="Ver Productos">👁️</button>
                    ` : ''}
                    <button class="action-btn" onclick="editRecord(${id})" title="Editar">✏️</button>
                    <button class="action-btn delete" onclick="deleteRecord(${id})" title="Eliminar">🗑️</button>
                </td>
            </tr>
        `;
    }).join('');
}

// Modal Actions
function openModal(isEdit = false) {
    const modal = document.getElementById('modal');
    const title = document.getElementById('modal-title');
    const fieldsContainer = document.getElementById('form-fields');
    const config = CONFIG[currentTab];

    title.textContent = isEdit ? `Editar ${config.title.slice(0, -1)}` : `Nueva ${config.title.slice(0, -1)}`;

    // Generate Fields
    fieldsContainer.innerHTML = config.fields.map(field => {
        let input = '';
        if (field.type === 'select') {
            let options = '';
            if (field.name === 'id_cliente') {
                options = `<option value="">Seleccione un cliente...</option>` +
                    cachedClientes.map(c => `<option value="${c.id_cliente}">${c.nombre} ${c.paterno}</option>`).join('');
            } else if (field.options) {
                options = field.options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
            }
            input = `
                <select id="field-${field.name}" ${field.required ? 'required' : ''}>
                    ${options}
                </select>
            `;
        } else if (field.type === 'textarea') {
            input = `<textarea id="field-${field.name}" rows="3"></textarea>`;
        } else if (field.type === 'checkbox') {
            input = `<input type="checkbox" id="field-${field.name}" style="width: auto;">`;
        } else {
            input = `
                <input type="${field.type}" id="field-${field.name}" 
                ${field.step ? `step="${field.step}"` : ''} 
                ${field.required ? 'required' : ''} 
                ${field.readOnly ? 'readonly style="background:#f1f5f9; cursor:not-allowed;"' : ''}>
            `;
        }

        return `
            <div class="form-group">
                <label for="field-${field.name}">${field.label}</label>
                ${input}
            </div>
        `;
    }).join('');

    // Handle Sale Items
    const itemsContainer = document.getElementById('venta-items-container');
    if (currentTab === 'venta' && !isEdit) {
        itemsContainer.style.display = 'block';
        document.getElementById('items-list').innerHTML = '';
        addProductLine();
    } else {
        itemsContainer.style.display = 'none';
    }

    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
    document.getElementById('main-form').reset();
    editingId = null;
}

// CRUD Operations
async function handleSubmit() {
    const config = CONFIG[currentTab];
    const data = {};
    let hasError = false;

    config.fields.forEach(field => {
        const el = document.getElementById(`field-${field.name}`);
        if (field.type === 'checkbox') {
            data[field.name] = el.checked;
        } else if (field.type === 'number') {
            const val = parseFloat(el.value);
            if (isNaN(val) && field.required) {
                showToast(`El campo ${field.label} debe ser un número válido`, 'danger');
                hasError = true;
            }
            data[field.name] = isNaN(val) ? 0 : val;
        } else {
            if (!el.value && field.required) {
                showToast(`El campo ${field.label} es obligatorio`, 'danger');
                hasError = true;
            }
            data[field.name] = el.value;
        }
    });

    if (hasError) return;

    // Handle Sale items if creating a sale
    if (currentTab === 'venta' && !editingId) {
        data.items = [];
        const itemRows = document.querySelectorAll('.item-row');
        itemRows.forEach(row => {
            const idProd = parseInt(row.querySelector('.item-prod').value);
            const cant = parseInt(row.querySelector('.item-cant').value);
            const price = parseFloat(row.querySelector('.item-price').value);

            if (idProd && cant > 0) {
                data.items.push({
                    id_producto: idProd,
                    cantidad: cant,
                    precio_unitario: price,
                    descuento: 0,
                    subtotal: cant * price
                });
            }
        });

        if (data.items.length === 0) {
            showToast('Debe agregar al menos un producto a la venta', 'danger');
            return;
        }
    }

    try {
        const url = editingId ? `${BASE_URL}${config.endpoint}/${editingId}` : `${BASE_URL}${config.endpoint}/`;
        const method = editingId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            // Manejar errores detallados de FastAPI
            const errorMsg = result.detail ?
                (typeof result.detail === 'string' ? result.detail : JSON.stringify(result.detail)) :
                'Error al guardar el registro';
            throw new Error(errorMsg);
        }

        showToast(editingId ? 'Registro actualizado' : 'Registro creado', 'success');
        closeModal();
        loadData();
    } catch (error) {
        showToast(error.message, 'danger');
        console.error('Error en submit:', error);
    }
}

async function editRecord(id) {
    editingId = id;
    const record = currentData.find(r => r[CONFIG[currentTab].idField] === id);

    openModal(true);

    // Fill data
    CONFIG[currentTab].fields.forEach(field => {
        const el = document.getElementById(`field-${field.name}`);
        if (field.type === 'checkbox') {
            el.checked = record[field.name];
        } else {
            el.value = record[field.name] || '';
        }
    });
}

async function deleteRecord(id) {
    if (!confirm('¿Está seguro de eliminar este registro?')) return;

    try {
        const response = await fetch(`${BASE_URL}${CONFIG[currentTab].endpoint}/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Error al eliminar');

        showToast('Registro eliminado', 'success');
        loadData();
    } catch (error) {
        showToast(error.message, 'danger');
    }
}

// Sale Details specialized logic
async function viewSaleDetails(id) {
    document.getElementById('det-nro-venta').textContent = id;
    const body = document.getElementById('det-table-body');
    body.innerHTML = '<tr><td colspan="5">Cargando detalles...</td></tr>';
    document.getElementById('modal-detalle').style.display = 'flex';

    try {
        const response = await fetch(`${BASE_URL}/detalle-venta/por-venta/${id}`);
        if (!response.ok) throw new Error('No se pudieron cargar los detalles');
        const detalles = await response.json();

        if (detalles.length === 0) {
            body.innerHTML = '<tr><td colspan="5">No hay productos registrados en esta venta.</td></tr>';
        } else {
            body.innerHTML = detalles.map(det => `
                <tr>
                    <td>${det.producto}</td>
                    <td>${det.cantidad}</td>
                    <td>$${det.precio_unitario}</td>
                    <td>$${det.descuento}</td>
                    <td>$${det.subtotal}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        showToast(error.message, 'danger');
        closeDetalleModal();
    }
}

function closeDetalleModal() {
    document.getElementById('modal-detalle').style.display = 'none';
}

// Sale Items logic
function addProductLine() {
    const list = document.getElementById('items-list');
    const div = document.createElement('div');
    div.className = 'item-row';
    div.style = 'display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 8px; margin-bottom: 8px;';

    const prodOptions = `<option value="">Producto...</option>` +
        cachedProductos.map(p => `<option value="${p.id_producto}" data-price="${p.precio_venta}">${p.descripcion}</option>`).join('');

    div.innerHTML = `
        <select class="item-prod" onchange="updateItemPrice(this)" required>
            ${prodOptions}
        </select>
        <input type="number" class="item-cant" placeholder="Cant." value="1" oninput="calculateVentaTotal()" required>
        <input type="number" class="item-price" placeholder="Precio" step="0.01" oninput="calculateVentaTotal()" required>
        <button type="button" class="btn delete" style="padding: 5px 10px;" onclick="this.parentElement.remove(); calculateVentaTotal();">×</button>
    `;
    list.appendChild(div);
}

function updateItemPrice(select) {
    const priceInput = select.parentElement.querySelector('.item-price');
    const selectedOption = select.options[select.selectedIndex];
    const price = selectedOption.getAttribute('data-price');
    if (price) {
        priceInput.value = price;
    }
    calculateVentaTotal();
}

function calculateVentaTotal() {
    let total = 0;
    document.querySelectorAll('.item-row').forEach(row => {
        const cant = parseFloat(row.querySelector('.item-cant').value) || 0;
        const price = parseFloat(row.querySelector('.item-price').value) || 0;
        total += cant * price;
    });
    const totalField = document.getElementById('field-total');
    if (totalField) totalField.value = total.toFixed(2);
}

// UI Helpers
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.style.backgroundColor = type === 'danger' ? '#ef4444' : '#1e293b';
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

let isEditMode = false;
let originalData = {};

document.addEventListener('DOMContentLoaded', () => {
    const photoInput = document.getElementById('companyPhotoInput');
    const logo = document.getElementById('companyLogo');

    if (photoInput && logo) {
        photoInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Validar que sea una imagen
            if (!file.type.startsWith('image/')) {
                alert('Por favor selecciona un archivo de imagen válido');
                return;
            }

            // Validar tamaño (máximo 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('La imagen es demasiado grande. Máximo 5MB');
                return;
            }

            // Crear FormData para enviar el archivo
            const formData = new FormData();
            formData.append('photo', file);

            try {
                const response = await fetch('/upload_company_photo', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    // Actualizar logo con la nueva imagen
                    logo.style.backgroundImage = `url('${data.photo_url}')`;
                    logo.style.backgroundSize = 'cover';
                    logo.style.backgroundPosition = 'center';
                    logo.style.fontSize = '0';
                    logo.textContent = '';

                    showSuccessMessage('Logo actualizado exitosamente');
                } else {
                    alert('Error al subir el logo: ' + data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al subir el logo');
            }
        });
    }
});

function toggleEditMode() {
    isEditMode = !isEditMode;
    const card = document.querySelector('.company-card');
    const editBtn = document.querySelector('.btn-edit');

    if (isEditMode) {
        // Guardar datos originales
        saveOriginalData();

        // Activar modo edición
        card.classList.add('edit-mode');

        // Cambiar botón
        editBtn.innerHTML = '💾 Guardar Cambios';
        editBtn.classList.add('btn-save');
        editBtn.onclick = saveChanges;

        // Agregar botón cancelar
        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn-edit btn-cancel';
        cancelBtn.innerHTML = '✖️ Cancelar';
        cancelBtn.onclick = cancelEdit;
        editBtn.parentElement.appendChild(cancelBtn);

        // Hacer editables los campos
        document.querySelectorAll('.info-value').forEach(el => {
            if (!el.querySelector('a')) { // No hacer editable si contiene un link
                el.contentEditable = true;
                el.classList.add('editable-field');
            }
        });
    }
}

function saveOriginalData() {
    const fields = document.querySelectorAll('.info-value');
    originalData = {};

    fields.forEach(field => {
        const label = field.closest('.info-row').querySelector('.info-label').textContent;
        originalData[label] = field.textContent.trim();
    });
}

function saveChanges() {
    const companyData = {
        nombre: getFieldValue('Nombre:'),
        descripcion: getFieldValue('Descripción:'),
        industria: getFieldValue('Industria:'),
        direccion: getFieldValue('Dirección:'),
        ciudad: getFieldValue('Ciudad:'),
        pais: getFieldValue('País:'),
        sitio: getFieldValue('Sitio Web:')
    };

    // Enviar al servidor
    fetch('/update_company', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(companyData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                exitEditMode();
                showSuccessMessage('Empresa actualizada exitosamente');

                // Actualizar el título si cambió el nombre
                if (companyData.nombre) {
                    document.querySelector('.company-header h1').textContent = companyData.nombre;
                }
            } else {
                alert('Error al guardar: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al guardar los cambios');
        });
}

function getFieldValue(label) {
    const rows = document.querySelectorAll('.info-row');
    for (let row of rows) {
        const labelEl = row.querySelector('.info-label');
        if (labelEl && labelEl.textContent.includes(label)) {
            const value = row.querySelector('.info-value');
            if (value) {
                // Si es un link, extraer solo el texto
                const link = value.querySelector('a');
                if (link) {
                    return link.textContent.trim();
                }
                return value.textContent.trim();
            }
        }
    }
    return '';
}

function cancelEdit() {
    // Restaurar datos originales
    Object.keys(originalData).forEach(label => {
        const rows = document.querySelectorAll('.info-row');
        for (let row of rows) {
            const labelEl = row.querySelector('.info-label');
            if (labelEl && labelEl.textContent.includes(label)) {
                const valueEl = row.querySelector('.info-value');
                if (valueEl) {
                    valueEl.textContent = originalData[label];
                }
            }
        }
    });

    exitEditMode();
}

function exitEditMode() {
    isEditMode = false;
    const card = document.querySelector('.company-card');
    const editBtn = document.querySelector('.btn-edit');

    // Desactivar modo edición
    card.classList.remove('edit-mode');

    // Restaurar botón
    editBtn.innerHTML = '✏️ Editar Empresa';
    editBtn.classList.remove('btn-save');
    editBtn.onclick = toggleEditMode;

    // Remover botón cancelar
    const cancelBtn = document.querySelector('.btn-cancel');
    if (cancelBtn) {
        cancelBtn.remove();
    }

    // Deshabilitar edición
    document.querySelectorAll('.info-value').forEach(el => {
        el.contentEditable = false;
        el.classList.remove('editable-field');
    });
}

function showSuccessMessage(message) {
    // Crear o usar mensaje existente
    let messageEl = document.getElementById('successMessage');
    if (!messageEl) {
        messageEl = document.createElement('div');
        messageEl.id = 'successMessage';
        messageEl.className = 'success-message';
        document.body.appendChild(messageEl);
    }

    messageEl.textContent = '✓ ' + message;
    messageEl.classList.add('show');

    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 3000);
}
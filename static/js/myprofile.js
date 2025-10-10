
let isEditMode = false;
let originalData = {};

function toggleEditMode() {
    isEditMode = !isEditMode;
    const card = document.querySelector('.profile-card');
    const toggleBtn = document.getElementById('toggleBtn');
    const modeBadge = document.getElementById('modeBadge');

    if (isEditMode) {
        // Guardar datos originales
        saveOriginalData();

        // Activar modo edición
        card.classList.add('edit-mode');
        modeBadge.style.display = 'block';
        toggleBtn.innerHTML = '💾 Guardar Cambios';
        toggleBtn.classList.add('save');
        toggleBtn.insertAdjacentHTML('afterend', '<button class="toggle-btn cancel" onclick="cancelEdit()">✖️ Cancelar</button>');

        // Hacer editables los campos
        document.querySelectorAll('[contenteditable="false"]').forEach(el => {
            el.contentEditable = true;
        });
        document.querySelectorAll('input[readonly], select[disabled], textarea[readonly]').forEach(el => {
            el.readOnly = false;
            el.disabled = false;
        });
    } else {
        saveChanges();
    }
}

function saveOriginalData() {
    originalData = {
        name: document.getElementById('name').textContent,
        profession: document.getElementById('profession').textContent,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        email: document.getElementById('email').textContent,
        phone: document.getElementById('phone').textContent,
        location: document.getElementById('location').textContent,
        address: document.getElementById('address').textContent,
        experience: document.getElementById('experience').value,
        company: document.getElementById('company').textContent,
        skills: document.getElementById('skills').value,
        bio: document.getElementById('bio').value,
    };
}

function saveChanges() {
    const card = document.querySelector('.profile-card');
    const toggleBtn = document.getElementById('toggleBtn');
    const modeBadge = document.getElementById('modeBadge');

    // Recopilar todos los datos
    const profileData = {
        name: document.getElementById('name').textContent,
        profession: document.getElementById('profession').textContent,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        email: document.getElementById('email').textContent,
        phone: document.getElementById('phone').textContent,
        location: document.getElementById('location').textContent,
        address: document.getElementById('address').textContent,
        experience: document.getElementById('experience').value,
        company: document.getElementById('company').textContent,
        skills: document.getElementById('skills').value,
        bio: document.getElementById('bio').value,
        certifications: getCertifications(),
        projects: document.getElementById('statProjects').textContent,
        clients: document.getElementById('statClients').textContent,
        rating: document.getElementById('statRating').textContent
    };

    // Enviar al servidor
    fetch('/update_profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Desactivar modo edición
                card.classList.remove('edit-mode');
                modeBadge.style.display = 'none';
                toggleBtn.innerHTML = '✏️ Editar Perfil';
                toggleBtn.classList.remove('save');
                document.querySelector('.cancel')?.remove();

                // Deshabilitar edición
                document.querySelectorAll('[contenteditable="true"]').forEach(el => {
                    el.contentEditable = false;
                });
                document.querySelectorAll('input:not([readonly]), select:not([disabled]), textarea:not([readonly])').forEach(el => {
                    el.readOnly = true;
                    el.disabled = true;
                });

                // Actualizar el encabezado
                const name = document.getElementById('name').textContent;
                const profession = document.getElementById('profession').textContent;
                document.getElementById('profileName').textContent = name;
                document.getElementById('profileTitle').textContent = profession;

                // Actualizar avatar
                const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                document.getElementById('avatar').textContent = initials;

                showSuccessMessage();
            } else {
                alert('Error al guardar: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al guardar los cambios');
        });
}

function getCertifications() {
    const badges = document.querySelectorAll('.cert-badge');
    const certs = [];
    badges.forEach(badge => {
        const text = badge.textContent.replace('×', '').trim();
        if (text) certs.push(text);
    });
    return certs.join(',');
}


function cancelEdit() {
    // Restaurar datos originales
    document.getElementById('name').textContent = originalData.name;
    document.getElementById('profession').textContent = originalData.profession;
    document.getElementById('age').value = originalData.age;
    document.getElementById('gender').value = originalData.gender;
    document.getElementById('email').textContent = originalData.email;
    document.getElementById('phone').textContent = originalData.phone;
    document.getElementById('location').textContent = originalData.location;
    document.getElementById('address').textContent = originalData.address;
    document.getElementById('experience').value = originalData.experience;
    document.getElementById('company').textContent = originalData.company;
    document.getElementById('skills').value = originalData.skills;
    document.getElementById('bio').value = originalData.bio;

    isEditMode = true; // Para que toggleEditMode lo desactive
    toggleEditMode();
}

function addCert() {
    const input = document.getElementById('newCert');
    const value = input.value.trim();

    if (value) {
        const container = document.getElementById('certificationsContainer');
        const badge = document.createElement('div');
        badge.className = 'cert-badge';
        badge.innerHTML = `
                    ${value}
                    <button class="remove-cert" onclick="removeCert(this)">×</button>
                `;
        container.appendChild(badge);
        input.value = '';
    }
}

function removeCert(btn) {
    btn.parentElement.remove();
}

function showSuccessMessage() {
    const message = document.getElementById('successMessage');
    message.classList.add('show');
    setTimeout(() => {
        message.classList.remove('show');
    }, 3000);
}

// Permitir agregar certificación con Enter
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('newCert').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addCert();
        }
    });
});

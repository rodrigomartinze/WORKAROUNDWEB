// ==================== FUNCIONES PARA GESTIÓN DE CANDIDATOS ====================

// Cargar vacantes en el select de candidatos
async function cargarVacantesParaCandidatos() {
    try {
        const response = await fetch('/get_vacantes_empresa');
        const data = await response.json();

        const select = document.getElementById('vacanteSelectCandidatos');

        if (data.success && data.vacantes.length > 0) {
            select.innerHTML = '<option value="">-- Selecciona una vacante --</option>' +
                data.vacantes.map(v => `
                    <option value="${v.Id}">${v.Titulo} (${v.Activa ? 'Activa' : 'Inactiva'})</option>
                `).join('');
        } else {
            select.innerHTML = '<option value="">No tienes vacantes publicadas</option>';
        }
    } catch (error) {
        console.error('Error al cargar vacantes:', error);
    }
}

// Cargar candidatos de una vacante
async function cargarCandidatos() {
    const vacanteId = document.getElementById('vacanteSelectCandidatos').value;
    const candidatosList = document.getElementById('candidatosList');
    const noCandidatos = document.getElementById('noCandidatos');
    const seleccionaVacante = document.getElementById('seleccionaVacante');

    if (!vacanteId) {
        candidatosList.style.display = 'none';
        noCandidatos.style.display = 'none';
        seleccionaVacante.style.display = 'block';
        return;
    }

    try {
        const response = await fetch(`/get_candidatos_vacante/${vacanteId}`);
        const data = await response.json();

        if (data.success) {
            seleccionaVacante.style.display = 'none';

            // Actualizar título de la vacante
            document.getElementById('vacanteTituloSeleccionada').textContent = data.vacante.Titulo;

            if (data.candidatos.length > 0) {
                noCandidatos.style.display = 'none';
                candidatosList.style.display = 'block';

                // Actualizar contador
                const pendientes = data.candidatos.filter(c => c.Estado === 'en_espera').length;
                const aceptados = data.candidatos.filter(c => c.Estado === 'aceptado').length;
                const rechazados = data.candidatos.filter(c => c.Estado === 'rechazado').length;

                document.getElementById('totalCandidatos').textContent =
                    `Total: ${data.candidatos.length} | ⏱ Pendientes: ${pendientes} | ✓ Aceptados: ${aceptados} | ✕ Rechazados: ${rechazados}`;

                // Renderizar candidatos
                const grid = document.getElementById('candidatosGrid');
                grid.innerHTML = data.candidatos.map(c => {
                    const estadoInfo = getEstadoInfo(c.Estado);
                    const initials = c.NombreCompleto ? c.NombreCompleto.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'U';

                    return `
                        <div class="vacante-item">
                            <div class="vacante-item-header">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div style="width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 1.2rem; flex-shrink: 0; ${c.FotoPerfil ? `background-image: url('${c.FotoPerfil}'); background-size: cover; background-position: center; font-size: 0;` : ''}">
                                        ${!c.FotoPerfil ? initials : ''}
                                    </div>
                                    <div style="flex: 1;">
                                        <div class="vacante-item-title">${c.NombreCompleto || 'Sin nombre'}</div>
                                        <div class="vacante-item-meta">
                                            <span>💼 ${c.Profesion || 'Sin especificar'}</span>
                                            <span>📧 ${c.Email}</span>
                                            <span>📅 ${c.FechaAplicacion}</span>
                                        </div>
                                        ${c.AniosExperiencia ? `<div style="color: #00FFEF; font-weight: 600; margin-top: 0.5rem;">🎯 ${c.AniosExperiencia} años de experiencia</div>` : ''}
                                    </div>
                                </div>
                                <div class="vacante-actions">
                                    <button class="btn-icon" style="background: ${estadoInfo.bg}; color: ${estadoInfo.color}; width: auto; padding: 0.5rem 1rem; font-size: 0.9rem;" title="${estadoInfo.texto}">
                                        ${estadoInfo.icon} ${estadoInfo.texto}
                                    </button>
                                </div>
                            </div>
                            ${c.Habilidades ? `
                                <div style="color: #6c757d; margin-top: 0.5rem;">
                                    <strong>Habilidades:</strong> ${c.Habilidades.substring(0, 100)}${c.Habilidades.length > 100 ? '...' : ''}
                                </div>
                            ` : ''}
                            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                                <button class="btn-create-vacante" style="flex: 1; padding: 0.75rem;" onclick="verPerfilCandidato(${c.UsuarioId}, ${c.AplicacionId})">
                                    👁️ Ver Perfil Completo
                                </button>
                                ${c.Estado === 'en_espera' ? `
                                    <button class="btn-create-vacante" style="flex: 1; padding: 0.75rem; background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);" onclick="cambiarEstadoCandidato(${c.AplicacionId}, 'aceptado')">
                                        ✓ Aceptar
                                    </button>
                                    <button class="btn-create-vacante" style="flex: 1; padding: 0.75rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);" onclick="cambiarEstadoCandidato(${c.AplicacionId}, 'rechazado')">
                                        ✕ Rechazar
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    `;
                }).join('');
            } else {
                noCandidatos.style.display = 'block';
                candidatosList.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error al cargar candidatos:', error);
        alert('Error al cargar candidatos');
    }
}

// Obtener información del estado
function getEstadoInfo(estado) {
    const estados = {
        'en_espera': { icon: '⏱', texto: 'En Espera', color: '#fbbf24', bg: 'rgba(251, 191, 36, 0.2)' },
        'aceptado': { icon: '✓', texto: 'Aceptado', color: '#22c55e', bg: 'rgba(34, 197, 94, 0.2)' },
        'rechazado': { icon: '✕', texto: 'Rechazado', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.2)' }
    };
    return estados[estado] || estados['en_espera'];
}

// Ver perfil completo del candidato
async function verPerfilCandidato(usuarioId, aplicacionId) {
    try {
        const response = await fetch(`/get_candidato_detalle/${usuarioId}`);
        const data = await response.json();

        if (data.success) {
            const perfil = data.perfil;
            const certificaciones = data.certificaciones || [];
            const experiencias = data.experiencias || [];
            const initials = perfil.NombreCompleto ? perfil.NombreCompleto.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'U';

            const content = document.getElementById('candidatoDetalleContent');
            content.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 2rem;">
                    <!-- Cabecera con foto y nombre -->
                    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
                        <div style="width: 120px; height: 120px; border-radius: 50%; background: rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 3rem; font-weight: 700; border: 4px solid white; ${perfil.FotoPerfil ? `background-image: url('${perfil.FotoPerfil}'); background-size: cover; background-position: center; font-size: 0;` : ''}">
                            ${!perfil.FotoPerfil ? initials : ''}
                        </div>
                        <h2 style="margin-bottom: 0.5rem;">${perfil.NombreCompleto || 'Sin nombre'}</h2>
                        <p style="opacity: 0.9;">${perfil.Profesion || 'Sin profesión especificada'}</p>
                    </div>

                    <!-- Información Personal -->
                    <div>
                        <h3 style="margin-bottom: 1rem; color: #2d3748;">👤 Información Personal</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                            <div class="info-row">
                                <strong>Edad:</strong> ${perfil.Edad || 'No especificada'}
                            </div>
                            <div class="info-row">
                                <strong>Género:</strong> ${perfil.Genero || 'No especificado'}
                            </div>
                            <div class="info-row">
                                <strong>Email:</strong> ${perfil.Email}
                            </div>
                            <div class="info-row">
                                <strong>Teléfono:</strong> ${perfil.Telefono || 'No especificado'}
                            </div>
                            <div class="info-row">
                                <strong>Localidad:</strong> ${perfil.Localidad || 'No especificada'}
                            </div>
                            <div class="info-row">
                                <strong>Dirección:</strong> ${perfil.Direccion || 'No especificada'}
                            </div>
                        </div>
                    </div>

                    <!-- Experiencia Profesional -->
                    <div>
                        <h3 style="margin-bottom: 1rem; color: #2d3748;">💼 Experiencia Profesional</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                            <div class="info-row">
                                <strong>Años de Experiencia:</strong> ${perfil.AniosExperiencia || '0'}
                            </div>
                            <div class="info-row">
                                <strong>Empresa Actual:</strong> ${perfil.EmpresaActual || 'No especificada'}
                            </div>
                        </div>
                        ${perfil.Habilidades ? `
                            <div class="info-row" style="margin-top: 1rem;">
                                <strong>Habilidades:</strong>
                                <div style="margin-top: 0.5rem; padding: 1rem; background: #f7fafc; border-radius: 8px;">
                                    ${perfil.Habilidades}
                                </div>
                            </div>
                        ` : ''}
                        ${perfil.DescripcionProfesional ? `
                            <div class="info-row" style="margin-top: 1rem;">
                                <strong>Descripción Profesional:</strong>
                                <div style="margin-top: 0.5rem; padding: 1rem; background: #f7fafc; border-radius: 8px;">
                                    ${perfil.DescripcionProfesional}
                                </div>
                            </div>
                        ` : ''}
                    </div>

                    <!-- Experiencias -->
                    ${experiencias.length > 0 ? `
                        <div>
                            <h3 style="margin-bottom: 1rem; color: #2d3748;">💼 Experiencias Profesionales</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">
                                ${experiencias.map(exp => `
                                    <div style="padding: 1rem; background: #f7fafc; border-radius: 8px; border-left: 4px solid #667eea;">
                                        <div style="font-weight: 700; color: #2d3748; margin-bottom: 0.5rem;">${exp.TipoExperiencia}</div>
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                                            <span style="background: #e0e7ff; color: #4338ca; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">
                                                ${exp.Categoria}
                                            </span>
                                            <span style="color: #00FFEF; font-weight: 700; font-size: 1.1rem;">
                                                ${exp.AniosExperiencia} años
                                            </span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}

                    <!-- Certificaciones -->
                    ${certificaciones.length > 0 ? `
                        <div>
                            <h3 style="margin-bottom: 1rem; color: #2d3748;">🎓 Certificaciones</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">
                                ${certificaciones.map(cert => `
                                    <div style="padding: 1rem; background: #f7fafc; border-radius: 8px; border-left: 4px solid #764ba2;">
                                        <div style="font-weight: 700; color: #2d3748; margin-bottom: 0.5rem;">${cert.Nombre}</div>
                                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
                                            <span style="background: #fce7f3; color: #be185d; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">
                                                ${cert.Categoria}
                                            </span>
                                            ${cert.InstitucionEmisora ? `
                                                <span style="background: #e0e7ff; color: #4338ca; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem;">
                                                    📍 ${cert.InstitucionEmisora}
                                                </span>
                                            ` : ''}
                                        </div>
                                        ${cert.FechaObtencion ? `
                                            <div style="color: #6c757d; font-size: 0.85rem; margin-top: 0.5rem;">
                                                📅 Obtenida: ${cert.FechaObtencion}
                                                ${cert.FechaVencimiento ? `<br>⏰ Vence: ${cert.FechaVencimiento}` : ''}
                                            </div>
                                        ` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}

                    <!-- Estadísticas -->
                    <div>
                        <h3 style="margin-bottom: 1rem; color: #2d3748;">📊 Estadísticas</h3>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                            <div style="text-align: center; padding: 1.5rem; background: #f7fafc; border-radius: 10px;">
                                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">${perfil.ProyectosCompletados || 0}</div>
                                <div style="font-size: 0.9rem; color: #6c757d; margin-top: 0.5rem;">Proyectos Completados</div>
                            </div>
                            <div style="text-align: center; padding: 1.5rem; background: #f7fafc; border-radius: 10px;">
                                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">${perfil.ClientesSatisfechos || 0}</div>
                                <div style="font-size: 0.9rem; color: #6c757d; margin-top: 0.5rem;">Clientes Satisfechos</div>
                            </div>
                            <div style="text-align: center; padding: 1.5rem; background: #f7fafc; border-radius: 10px;">
                                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">${perfil.CalificacionPromedio || '0.0'}</div>
                                <div style="font-size: 0.9rem; color: #6c757d; margin-top: 0.5rem;">Calificación Promedio</div>
                            </div>
                        </div>
                    </div>

                    <!-- Botones de Acción -->
                    <div style="display: flex; gap: 1rem; padding-top: 1rem; border-top: 2px solid #e2e8f0;">
                        <button class="btn-create-vacante" style="flex: 1;" onclick="cambiarEstadoCandidato(${aplicacionId}, 'aceptado'); cerrarModalCandidato();">
                            ✓ Aceptar Candidato
                        </button>
                        <button class="btn-create-vacante" style="flex: 1; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);" onclick="cambiarEstadoCandidato(${aplicacionId}, 'rechazado'); cerrarModalCandidato();">
                            ✕ Rechazar Candidato
                        </button>
                    </div>
                </div>
            `;

            document.getElementById('modalCandidato').classList.add('active');
        }
    } catch (error) {
        console.error('Error al cargar perfil:', error);
        alert('Error al cargar el perfil del candidato');
    }
}

// Cerrar modal de candidato
function cerrarModalCandidato() {
    document.getElementById('modalCandidato').classList.remove('active');
}

// Cambiar estado del candidato (aceptar/rechazar)
async function cambiarEstadoCandidato(aplicacionId, nuevoEstado) {
    const mensajes = {
        'aceptado': '¿Estás seguro de aceptar a este candidato?',
        'rechazado': '¿Estás seguro de rechazar a este candidato?'
    };

    if (!confirm(mensajes[nuevoEstado])) return;

    try {
        const response = await fetch('/actualizar_estado_aplicacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                aplicacionId: aplicacionId,
                estado: nuevoEstado
            })
        });

        const result = await response.json();

        if (result.success) {
            // Recargar candidatos
            cargarCandidatos();

            // Mostrar mensaje de éxito
            if (typeof showSuccessMessage === 'function') {
                showSuccessMessage(result.message);
            } else {
                alert(result.message);
            }
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar el estado del candidato');
    }
}

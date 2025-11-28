-- Crear tabla de catálogo de experiencias y tabla relacional para usuarios

-- Tabla catálogo de tipos de experiencia
CREATE TABLE IF NOT EXISTS catalogo_experiencias (
    Id INT(11) NOT NULL AUTO_INCREMENT,
    TipoExperiencia VARCHAR(150) NOT NULL,
    Categoria VARCHAR(50) NOT NULL,
    Descripcion TEXT DEFAULT NULL,
    Activa TINYINT(1) DEFAULT 1,
    PRIMARY KEY (Id),
    UNIQUE KEY tipo_experiencia_unico (TipoExperiencia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla relacional entre usuarios y experiencias (con años de experiencia)
CREATE TABLE IF NOT EXISTS usuario_experiencias (
    Id INT(11) NOT NULL AUTO_INCREMENT,
    UsuarioId INT(11) NOT NULL,
    ExperienciaId INT(11) NOT NULL,
    AniosExperiencia INT(11) NOT NULL,
    FechaAgregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (Id),
    UNIQUE KEY usuario_experiencia_unico (UsuarioId, ExperienciaId),
    FOREIGN KEY (UsuarioId) REFERENCES usuarios(Id) ON DELETE CASCADE,
    FOREIGN KEY (ExperienciaId) REFERENCES catalogo_experiencias(Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insertar tipos de experiencia comunes
INSERT INTO catalogo_experiencias (TipoExperiencia, Categoria, Descripcion) VALUES
-- Cuidado y atención
('Cuidado de niños', 'Cuidado y Atención', 'Experiencia en el cuidado y atención de niños'),
('Cuidado de adultos mayores', 'Cuidado y Atención', 'Experiencia en el cuidado de personas de la tercera edad'),
('Cuidado de mascotas', 'Cuidado y Atención', 'Experiencia en el cuidado de animales domésticos'),
('Enfermería', 'Cuidado y Atención', 'Experiencia en enfermería y cuidados médicos'),

-- Servicios del hogar
('Limpieza del hogar', 'Servicios del Hogar', 'Experiencia en limpieza y mantenimiento doméstico'),
('Lavandería y planchado', 'Servicios del Hogar', 'Experiencia en lavado y planchado de ropa'),
('Jardinería', 'Servicios del Hogar', 'Experiencia en cuidado de jardines y plantas'),
('Mantenimiento general', 'Servicios del Hogar', 'Experiencia en reparaciones y mantenimiento del hogar'),

-- Cocina y alimentos
('Cocina general', 'Cocina y Alimentos', 'Experiencia en preparación de comidas'),
('Repostería', 'Cocina y Alimentos', 'Experiencia en preparación de postres y pasteles'),
('Cocina vegetariana/vegana', 'Cocina y Alimentos', 'Experiencia en cocina basada en plantas'),
('Chef profesional', 'Cocina y Alimentos', 'Experiencia profesional en gastronomía'),

-- Educación y tutoría
('Tutoría escolar', 'Educación', 'Experiencia enseñando a estudiantes escolares'),
('Clases de idiomas', 'Educación', 'Experiencia enseñando idiomas'),
('Clases de música', 'Educación', 'Experiencia enseñando música'),
('Clases de arte', 'Educación', 'Experiencia enseñando artes plásticas'),

-- Oficios y construcción
('Plomería', 'Oficios', 'Experiencia en instalaciones y reparaciones de plomería'),
('Electricidad', 'Oficios', 'Experiencia en instalaciones y reparaciones eléctricas'),
('Carpintería', 'Oficios', 'Experiencia en trabajo con madera'),
('Pintura', 'Oficios', 'Experiencia en pintura de interiores y exteriores'),
('Albañilería', 'Oficios', 'Experiencia en construcción y obra'),

-- Belleza y estética
('Peluquería', 'Belleza y Estética', 'Experiencia en corte y peinado'),
('Manicure y pedicure', 'Belleza y Estética', 'Experiencia en cuidado de uñas'),
('Maquillaje', 'Belleza y Estética', 'Experiencia en maquillaje profesional'),
('Masajes', 'Belleza y Estética', 'Experiencia en masoterapia'),

-- Transporte y logística
('Conductor particular', 'Transporte', 'Experiencia como chofer privado'),
('Mensajería', 'Transporte', 'Experiencia en servicio de mensajería'),
('Mudanzas', 'Transporte', 'Experiencia en servicios de mudanza'),

-- Tecnología y digital
('Soporte técnico', 'Tecnología', 'Experiencia en soporte técnico de computadoras'),
('Diseño gráfico', 'Tecnología', 'Experiencia en diseño digital'),
('Fotografía', 'Tecnología', 'Experiencia en fotografía profesional'),
('Edición de video', 'Tecnología', 'Experiencia en edición audiovisual'),

-- Eventos y entretenimiento
('Organización de eventos', 'Eventos', 'Experiencia organizando eventos'),
('Catering', 'Eventos', 'Experiencia en servicio de catering'),
('Animación infantil', 'Eventos', 'Experiencia en entretenimiento para niños'),
('DJ/Música en vivo', 'Eventos', 'Experiencia en música para eventos'),

-- Servicios administrativos
('Asistencia administrativa', 'Administración', 'Experiencia en tareas administrativas'),
('Contabilidad', 'Administración', 'Experiencia en contabilidad y finanzas'),
('Atención al cliente', 'Administración', 'Experiencia en servicio al cliente'),

-- Deportes y fitness
('Entrenamiento personal', 'Deportes y Fitness', 'Experiencia como entrenador personal'),
('Clases de yoga', 'Deportes y Fitness', 'Experiencia enseñando yoga'),
('Instructor de deportes', 'Deportes y Fitness', 'Experiencia enseñando deportes');

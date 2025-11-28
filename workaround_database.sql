-- ====================================================================
-- SCRIPT SQL PARA WORKAROUND DATABASE
-- Base de datos para plataforma de empleos WorkAround
-- Compatible con MySQL/MariaDB para PythonAnywhere
-- ====================================================================

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS workarounddb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE workarounddb;

-- ====================================================================
-- TABLA: usuarios
-- Almacena información básica de todos los usuarios del sistema
-- ====================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    NombreCompleto VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    TipoUsuario ENUM('Candidato', 'Empleador') DEFAULT 'Candidato',
    Telefono VARCHAR(20),
    FotoPerfil VARCHAR(500),
    Documento VARCHAR(50),
    Activo TINYINT(1) DEFAULT 1,
    rol ENUM('usuario', 'admin') DEFAULT 'usuario',
    FechaRegistro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (Email),
    INDEX idx_tipo_usuario (TipoUsuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- TABLA: perfiles_usuarios
-- Información detallada del perfil profesional de cada usuario
-- ====================================================================
CREATE TABLE IF NOT EXISTS perfiles_usuarios (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    UsuarioId INT NOT NULL,
    NombreCompleto VARCHAR(255),
    Profesion VARCHAR(255),
    Edad INT,
    Genero ENUM('Masculino', 'Femenino', 'Otro', 'Prefiero no decir'),
    Email VARCHAR(255),
    Telefono VARCHAR(20),
    Localidad VARCHAR(255),
    Direccion VARCHAR(500),
    AniosExperiencia VARCHAR(50),
    EmpresaActual VARCHAR(255),
    Habilidades TEXT,
    DescripcionProfesional TEXT,
    ProyectosCompletados INT DEFAULT 0,
    ClientesSatisfechos INT DEFAULT 0,
    CalificacionPromedio DECIMAL(3,2) DEFAULT 0.00,
    FotoPerfil VARCHAR(500),
    FechaActualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (UsuarioId) REFERENCES usuarios(Id) ON DELETE CASCADE,
    INDEX idx_usuario (UsuarioId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- TABLA: empresas
-- Información de las empresas registradas en la plataforma
-- ====================================================================
CREATE TABLE IF NOT EXISTS empresas (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    UsuarioId INT NOT NULL,
    NombreEmpresa VARCHAR(255) NOT NULL,
    Descripcion TEXT,
    Industria VARCHAR(255),
    Sitio VARCHAR(500),
    LogoEmpresa VARCHAR(500),
    Direccion VARCHAR(500),
    Ciudad VARCHAR(255),
    Pais VARCHAR(100) DEFAULT 'México',
    FechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Verificada TINYINT(1) DEFAULT 0,
    FOREIGN KEY (UsuarioId) REFERENCES usuarios(Id) ON DELETE CASCADE,
    INDEX idx_usuario (UsuarioId),
    INDEX idx_ciudad (Ciudad)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- TABLA: vacantes
-- Publicaciones de trabajo disponibles
-- ====================================================================
CREATE TABLE IF NOT EXISTS vacantes (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    EmpresaId INT NOT NULL,
    Titulo VARCHAR(255) NOT NULL,
    Descripcion TEXT,
    Requisitos TEXT,
    Responsabilidades TEXT,
    SalarioMin DECIMAL(10,2),
    SalarioMax DECIMAL(10,2),
    Ubicacion VARCHAR(255),
    TipoTrabajo ENUM('Remoto', 'Presencial', 'Hibrido') DEFAULT 'Presencial',
    TipoContrato ENUM('Tiempo Completo', 'Medio Tiempo', 'Temporal', 'Freelance') DEFAULT 'Tiempo Completo',
    Experiencia VARCHAR(100),
    FechaPublicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FechaCierre DATETIME,
    Activa TINYINT(1) DEFAULT 1,
    Vistas INT DEFAULT 0,
    FOREIGN KEY (EmpresaId) REFERENCES empresas(Id) ON DELETE CASCADE,
    INDEX idx_empresa (EmpresaId),
    INDEX idx_activa (Activa),
    INDEX idx_ubicacion (Ubicacion),
    INDEX idx_tipo_trabajo (TipoTrabajo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- TABLA: aplicaciones
-- Registro de postulaciones de usuarios a vacantes
-- ====================================================================
CREATE TABLE IF NOT EXISTS aplicaciones (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    VacanteId INT NOT NULL,
    UsuarioId INT NOT NULL,
    FechaSolicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Estado ENUM('Pendiente', 'En Revision', 'Entrevista', 'Aceptada', 'Rechazada') DEFAULT 'Pendiente',
    FOREIGN KEY (VacanteId) REFERENCES vacantes(Id) ON DELETE CASCADE,
    FOREIGN KEY (UsuarioId) REFERENCES usuarios(Id) ON DELETE CASCADE,
    UNIQUE KEY unique_aplicacion (VacanteId, UsuarioId),
    INDEX idx_vacante (VacanteId),
    INDEX idx_usuario (UsuarioId),
    INDEX idx_estado (Estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- TABLA: catalogo_certificaciones
-- Catálogo de certificaciones disponibles para los usuarios
-- ====================================================================
CREATE TABLE IF NOT EXISTS catalogo_certificaciones (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    Categoria VARCHAR(100) NOT NULL,
    Descripcion TEXT,
    Activa TINYINT(1) DEFAULT 1,
    FechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_categoria (Categoria),
    INDEX idx_activa (Activa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- TABLA: catalogo_experiencias
-- Catálogo de tipos de experiencia profesional
-- ====================================================================
CREATE TABLE IF NOT EXISTS catalogo_experiencias (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    TipoExperiencia VARCHAR(255) NOT NULL,
    Categoria VARCHAR(100) NOT NULL,
    Descripcion TEXT,
    Activa TINYINT(1) DEFAULT 1,
    FechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_categoria (Categoria),
    INDEX idx_activa (Activa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- TABLA: usuario_experiencias
-- Relación entre usuarios y sus experiencias profesionales
-- ====================================================================
CREATE TABLE IF NOT EXISTS usuario_experiencias (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    UsuarioId INT NOT NULL,
    ExperienciaId INT NOT NULL,
    AniosExperiencia INT NOT NULL DEFAULT 0,
    FechaAgregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UsuarioId) REFERENCES usuarios(Id) ON DELETE CASCADE,
    FOREIGN KEY (ExperienciaId) REFERENCES catalogo_experiencias(Id) ON DELETE CASCADE,
    UNIQUE KEY unique_usuario_experiencia (UsuarioId, ExperienciaId),
    INDEX idx_usuario (UsuarioId),
    INDEX idx_experiencia (ExperienciaId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- TABLA: usuario_certificaciones
-- Relación entre usuarios y sus certificaciones obtenidas
-- ====================================================================
CREATE TABLE IF NOT EXISTS usuario_certificaciones (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    UsuarioId INT NOT NULL,
    CertificacionId INT NOT NULL,
    FechaObtencion DATE,
    FechaVencimiento DATE,
    InstitucionEmisora VARCHAR(255),
    FechaAgregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UsuarioId) REFERENCES usuarios(Id) ON DELETE CASCADE,
    FOREIGN KEY (CertificacionId) REFERENCES catalogo_certificaciones(Id) ON DELETE CASCADE,
    UNIQUE KEY unique_usuario_certificacion (UsuarioId, CertificacionId),
    INDEX idx_usuario (UsuarioId),
    INDEX idx_certificacion (CertificacionId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- DATOS INICIALES: Usuario Administrador
-- ====================================================================
INSERT INTO usuarios (NombreCompleto, Email, Password, TipoUsuario, rol, Activo)
VALUES ('Admin', 'admin@workaround.com', 'admin', 'Empleador', 'admin', 1)
ON DUPLICATE KEY UPDATE Email=Email;

-- ====================================================================
-- DATOS DE EJEMPLO: Catálogo de Certificaciones
-- ====================================================================
INSERT INTO catalogo_certificaciones (Nombre, Categoria, Descripcion, Activa) VALUES
('Certificación AWS Cloud Practitioner', 'Tecnología', 'Certificación básica de Amazon Web Services', 1),
('Google Analytics Certified', 'Marketing Digital', 'Certificación en herramientas de análisis de Google', 1),
('PMP - Project Management Professional', 'Gestión de Proyectos', 'Certificación profesional en gestión de proyectos', 1),
('TOEFL', 'Idiomas', 'Test de inglés como lengua extranjera', 1),
('Scrum Master Certified', 'Metodologías Ágiles', 'Certificación en metodología Scrum', 1),
('CompTIA Security+', 'Seguridad Informática', 'Certificación en seguridad de la información', 1),
('Microsoft Excel Expert', 'Ofimática', 'Certificación avanzada en Microsoft Excel', 1),
('Adobe Certified Professional', 'Diseño Gráfico', 'Certificación profesional en suite Adobe', 1)
ON DUPLICATE KEY UPDATE Nombre=Nombre;

-- ====================================================================
-- DATOS DE EJEMPLO: Catálogo de Experiencias
-- ====================================================================
INSERT INTO catalogo_experiencias (TipoExperiencia, Categoria, Descripcion, Activa) VALUES
('Desarrollo Web Frontend', 'Programación', 'Experiencia en desarrollo de interfaces web con HTML, CSS, JavaScript', 1),
('Desarrollo Web Backend', 'Programación', 'Experiencia en desarrollo de servidores y APIs', 1),
('Diseño UX/UI', 'Diseño', 'Experiencia en diseño de experiencia e interfaces de usuario', 1),
('Marketing Digital', 'Marketing', 'Experiencia en campañas digitales y redes sociales', 1),
('Gestión de Proyectos', 'Administración', 'Experiencia coordinando equipos y proyectos', 1),
('Análisis de Datos', 'Análisis', 'Experiencia en análisis de datos y business intelligence', 1),
('Atención al Cliente', 'Servicio', 'Experiencia en soporte y atención a clientes', 1),
('Desarrollo Mobile', 'Programación', 'Experiencia en desarrollo de aplicaciones móviles', 1),
('DevOps', 'Tecnología', 'Experiencia en integración y despliegue continuo', 1),
('Ciberseguridad', 'Seguridad', 'Experiencia en seguridad informática y protección de datos', 1)
ON DUPLICATE KEY UPDATE TipoExperiencia=TipoExperiencia;

-- ====================================================================
-- VERIFICACIÓN DE TABLAS CREADAS
-- ====================================================================
SHOW TABLES;

-- ====================================================================
-- FIN DEL SCRIPT
-- ====================================================================

-- ====================================================================
-- SCRIPT DE MIGRACIÓN: Eliminar columna Certificaciones de perfiles_usuarios
-- ====================================================================
-- IMPORTANTE: Este script elimina la columna Certificaciones de la tabla
-- perfiles_usuarios ya que ahora se usa la tabla usuario_certificaciones
-- ====================================================================

USE workarounddb;

-- Verificar que la tabla usuario_certificaciones existe
-- Si no existe, crearla primero
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

-- OPCIONAL: Migrar datos existentes de la columna Certificaciones
-- Este código intenta convertir las certificaciones separadas por comas
-- en registros de la tabla usuario_certificaciones
-- NOTA: Solo funcionará si los nombres coinciden exactamente con el catálogo

-- Descomentar las siguientes líneas si quieres migrar datos existentes:
/*
INSERT INTO usuario_certificaciones (UsuarioId, CertificacionId)
SELECT
    pu.UsuarioId,
    cc.Id
FROM perfiles_usuarios pu
CROSS JOIN catalogo_certificaciones cc
WHERE
    pu.Certificaciones IS NOT NULL
    AND pu.Certificaciones != ''
    AND FIND_IN_SET(TRIM(cc.Nombre), REPLACE(pu.Certificaciones, ',', ',')) > 0
ON DUPLICATE KEY UPDATE UsuarioId = UsuarioId;
*/

-- Eliminar la columna Certificaciones de perfiles_usuarios
ALTER TABLE perfiles_usuarios DROP COLUMN Certificaciones;

-- Verificar que se eliminó correctamente
SHOW COLUMNS FROM perfiles_usuarios;

-- ====================================================================
-- FIN DEL SCRIPT DE MIGRACIÓN
-- ====================================================================

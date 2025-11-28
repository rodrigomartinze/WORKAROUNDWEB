– Clean SQL for PythonAnywhere (No procedures, no definers)

DROP VIEW IF EXISTS vistavacantescompleta; DROP TABLE IF EXISTS
aplicaciones; DROP TABLE IF EXISTS empresas; DROP TABLE IF EXISTS
perfiles_usuarios; DROP TABLE IF EXISTS usuarios; DROP TABLE IF EXISTS
vacantes;

CREATE TABLE aplicaciones ( Id int(11) NOT NULL AUTO_INCREMENT,
VacanteId int(11) NOT NULL, UsuarioId int(11) NOT NULL, FechaSolicitud
datetime DEFAULT current_timestamp(), Estado enum(‘Pendiente’,‘En
Revision’,‘Entrevista’,‘Rechazada’,‘Aceptada’) DEFAULT ‘Pendiente’,
PRIMARY KEY (Id), UNIQUE KEY VacanteId (VacanteId, UsuarioId), KEY
UsuarioId (UsuarioId) );

CREATE TABLE empresas ( Id int(11) NOT NULL AUTO_INCREMENT, UsuarioId
int(11) NOT NULL, NombreEmpresa varchar(200) NOT NULL, Descripcion text
DEFAULT NULL, Industria varchar(100) DEFAULT NULL, Sitio varchar(200)
DEFAULT NULL, LogoEmpresa varchar(255) DEFAULT NULL, Direccion
varchar(300) DEFAULT NULL, Ciudad varchar(100) DEFAULT NULL, Pais
varchar(100) DEFAULT NULL, FechaCreacion datetime DEFAULT
current_timestamp(), Verificada tinyint(1) DEFAULT 0, PRIMARY KEY (Id),
KEY IX_Empresas_UsuarioId (UsuarioId) );

CREATE TABLE perfiles_usuarios ( Id int(11) NOT NULL AUTO_INCREMENT,
UsuarioId int(11) NOT NULL, NombreCompleto varchar(100) DEFAULT NULL,
Profesion varchar(100) DEFAULT NULL, Edad int(11) DEFAULT NULL, Genero
varchar(50) DEFAULT NULL, Email varchar(100) DEFAULT NULL, Telefono
varchar(20) DEFAULT NULL, Localidad varchar(100) DEFAULT NULL, Direccion
varchar(200) DEFAULT NULL, AniosExperiencia varchar(50) DEFAULT NULL,
EmpresaActual varchar(100) DEFAULT NULL, Habilidades text DEFAULT NULL,
DescripcionProfesional text DEFAULT NULL, Certificaciones text DEFAULT
NULL, ProyectosCompletados int(11) DEFAULT 0, ClientesSatisfechos
int(11) DEFAULT 0, CalificacionPromedio decimal(3,2) DEFAULT 0.00,
FotoPerfil varchar(255) DEFAULT NULL, FechaActualizacion timestamp NOT
NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(), PRIMARY
KEY (Id), UNIQUE KEY UsuarioId (UsuarioId) );

CREATE TABLE usuarios ( Id int(11) NOT NULL AUTO_INCREMENT, Email
varchar(100) NOT NULL, Password varchar(255) NOT NULL, NombreCompleto
varchar(200) NOT NULL, TipoUsuario enum(‘Candidato’,‘Empleador’) NOT
NULL, Telefono varchar(20) DEFAULT NULL, FotoPerfil varchar(500) DEFAULT
NULL, Documento varchar(500) DEFAULT NULL, FechaRegistro datetime
DEFAULT current_timestamp(), rol varchar(10) DEFAULT ‘usuario’, Activo
tinyint(1) DEFAULT 1, PRIMARY KEY (Id), UNIQUE KEY Email (Email), KEY
IX_Usuarios_Email (Email) );

CREATE TABLE vacantes ( Id int(11) NOT NULL AUTO_INCREMENT, EmpresaId
int(11) NOT NULL, Titulo varchar(200) NOT NULL, Descripcion text NOT
NULL, Requisitos text DEFAULT NULL, Responsabilidades text DEFAULT NULL,
SalarioMin decimal(10,2) DEFAULT NULL, SalarioMax decimal(10,2) DEFAULT
NULL, Ubicacion varchar(100) NOT NULL, TipoTrabajo
enum(‘Remoto’,‘Presencial’,‘Hibrido’) DEFAULT NULL, TipoContrato
enum(‘Tiempo Completo’,‘Medio Tiempo’,‘Temporal’,‘Freelance’) DEFAULT
NULL, Experiencia varchar(50) DEFAULT NULL, FechaPublicacion datetime
DEFAULT current_timestamp(), FechaCierre datetime DEFAULT NULL, Activa
tinyint(1) DEFAULT 1, Vistas int(11) DEFAULT 0, PRIMARY KEY (Id), KEY
EmpresaId (EmpresaId), KEY IX_Vacantes_Activa (Activa) );

ALTER TABLE aplicaciones ADD CONSTRAINT aplicaciones_ibfk_1 FOREIGN KEY
(VacanteId) REFERENCES vacantes(Id), ADD CONSTRAINT aplicaciones_ibfk_2
FOREIGN KEY (UsuarioId) REFERENCES usuarios(Id);

ALTER TABLE empresas ADD CONSTRAINT empresas_ibfk_1 FOREIGN KEY
(UsuarioId) REFERENCES usuarios(Id);

ALTER TABLE perfiles_usuarios ADD CONSTRAINT perfiles_usuarios_ibfk_1
FOREIGN KEY (UsuarioId) REFERENCES usuarios(Id) ON DELETE CASCADE;

ALTER TABLE vacantes ADD CONSTRAINT vacantes_ibfk_1 FOREIGN KEY
(EmpresaId) REFERENCES empresas(Id);

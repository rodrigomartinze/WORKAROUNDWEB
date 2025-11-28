-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-11-2025 a las 03:55:32
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `workarounddb`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `aplicaciones`
--

CREATE TABLE `aplicaciones` (
  `Id` int(11) NOT NULL,
  `VacanteId` int(11) NOT NULL,
  `UsuarioId` int(11) NOT NULL,
  `FechaSolicitud` datetime DEFAULT current_timestamp(),
  `Estado` enum('Pendiente','En Revision','Entrevista','Rechazada','Aceptada') DEFAULT 'Pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `aplicaciones`
--

INSERT INTO `aplicaciones` (`Id`, `VacanteId`, `UsuarioId`, `FechaSolicitud`, `Estado`) VALUES
(18, 11, 27, '2025-11-10 07:33:32', 'Aceptada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `catalogo_certificaciones`
--

CREATE TABLE `catalogo_certificaciones` (
  `Id` int(11) NOT NULL,
  `Nombre` varchar(150) NOT NULL,
  `Categoria` varchar(50) NOT NULL,
  `Emisor` varchar(100) DEFAULT NULL,
  `Descripcion` text DEFAULT NULL,
  `Activa` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `catalogo_certificaciones`
--

INSERT INTO `catalogo_certificaciones` (`Id`, `Nombre`, `Categoria`, `Emisor`, `Descripcion`, `Activa`) VALUES
(1, 'python', 'sistemas computacionales', 'Harvard', NULL, 1),
(2, 'AWS Certified Solutions Architect', 'Cloud Computing', 'Amazon Web Services', 'Certificación para arquitectos de soluciones en AWS', 1),
(3, 'Microsoft Azure Fundamentals', 'Cloud Computing', 'Microsoft', 'Certificación básica de Azure', 1),
(4, 'Google Cloud Professional', 'Cloud Computing', 'Google', 'Certificación profesional de Google Cloud', 1),
(5, 'Certified Kubernetes Administrator', 'DevOps', 'Cloud Native Computing Foundation', 'Administración de Kubernetes', 1),
(6, 'Docker Certified Associate', 'DevOps', 'Docker Inc', 'Certificación de Docker', 1),
(7, 'PMP - Project Management Professional', 'Gestión de Proyectos', 'PMI', 'Gestión profesional de proyectos', 1),
(8, 'Scrum Master Certification', 'Metodologías Ágiles', 'Scrum Alliance', 'Certificación Scrum Master', 1),
(9, 'Certified Ethical Hacker', 'Seguridad', 'EC-Council', 'Hacking ético certificado', 1),
(10, 'CISSP', 'Seguridad', 'ISC2', 'Profesional certificado en seguridad de sistemas de información', 1),
(11, 'CompTIA Security+', 'Seguridad', 'CompTIA', 'Certificación de seguridad CompTIA', 1),
(12, 'Oracle Certified Professional', 'Bases de Datos', 'Oracle', 'Certificación profesional de Oracle', 1),
(13, 'MongoDB Certified Developer', 'Bases de Datos', 'MongoDB Inc', 'Desarrollador certificado MongoDB', 1),
(14, 'Python Institute PCEP', 'Programación', 'Python Institute', 'Programador Python certificado nivel básico', 1),
(15, 'Java SE Programmer', 'Programación', 'Oracle', 'Programador Java SE', 1),
(16, 'Microsoft Certified: Azure Developer', 'Desarrollo', 'Microsoft', 'Desarrollador Azure certificado', 1),
(17, 'Salesforce Certified Administrator', 'CRM', 'Salesforce', 'Administrador Salesforce certificado', 1),
(18, 'Tableau Desktop Specialist', 'Análisis de Datos', 'Tableau', 'Especialista en Tableau Desktop', 1),
(19, 'Google Analytics Individual Qualification', 'Marketing Digital', 'Google', 'Certificación de Google Analytics', 1),
(20, 'HubSpot Inbound Marketing', 'Marketing Digital', 'HubSpot', 'Marketing de entrada HubSpot', 1),
(21, 'Red Hat Certified System Administrator', 'Sistemas Operativos', 'Red Hat', 'Administrador de sistemas Red Hat', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `catalogo_experiencias`
--

CREATE TABLE `catalogo_experiencias` (
  `Id` int(11) NOT NULL,
  `TipoExperiencia` varchar(150) NOT NULL,
  `Categoria` varchar(50) NOT NULL,
  `Descripcion` text DEFAULT NULL,
  `Activa` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `catalogo_experiencias`
--

INSERT INTO `catalogo_experiencias` (`Id`, `TipoExperiencia`, `Categoria`, `Descripcion`, `Activa`) VALUES
(1, 'Cuidado de niños', 'Cuidado y Atención', 'Experiencia en el cuidado y atención de niños', 1),
(2, 'Cuidado de adultos mayores', 'Cuidado y Atención', 'Experiencia en el cuidado de personas de la tercera edad', 1),
(3, 'Cuidado de mascotas', 'Cuidado y Atención', 'Experiencia en el cuidado de animales domésticos', 1),
(4, 'Enfermería', 'Cuidado y Atención', 'Experiencia en enfermería y cuidados médicos', 1),
(5, 'Limpieza del hogar', 'Servicios del Hogar', 'Experiencia en limpieza y mantenimiento doméstico', 1),
(6, 'Lavandería y planchado', 'Servicios del Hogar', 'Experiencia en lavado y planchado de ropa', 1),
(7, 'Jardinería', 'Servicios del Hogar', 'Experiencia en cuidado de jardines y plantas', 1),
(8, 'Mantenimiento general', 'Servicios del Hogar', 'Experiencia en reparaciones y mantenimiento del hogar', 1),
(9, 'Cocina general', 'Cocina y Alimentos', 'Experiencia en preparación de comidas', 1),
(10, 'Repostería', 'Cocina y Alimentos', 'Experiencia en preparación de postres y pasteles', 1),
(11, 'Cocina vegetariana/vegana', 'Cocina y Alimentos', 'Experiencia en cocina basada en plantas', 1),
(12, 'Chef profesional', 'Cocina y Alimentos', 'Experiencia profesional en gastronomía', 1),
(13, 'Tutoría escolar', 'Educación', 'Experiencia enseñando a estudiantes escolares', 1),
(14, 'Clases de idiomas', 'Educación', 'Experiencia enseñando idiomas', 1),
(15, 'Clases de música', 'Educación', 'Experiencia enseñando música', 1),
(16, 'Clases de arte', 'Educación', 'Experiencia enseñando artes plásticas', 1),
(17, 'Plomería', 'Oficios', 'Experiencia en instalaciones y reparaciones de plomería', 1),
(18, 'Electricidad', 'Oficios', 'Experiencia en instalaciones y reparaciones eléctricas', 1),
(19, 'Carpintería', 'Oficios', 'Experiencia en trabajo con madera', 1),
(20, 'Pintura', 'Oficios', 'Experiencia en pintura de interiores y exteriores', 1),
(21, 'Albañilería', 'Oficios', 'Experiencia en construcción y obra', 1),
(22, 'Peluquería', 'Belleza y Estética', 'Experiencia en corte y peinado', 1),
(23, 'Manicure y pedicure', 'Belleza y Estética', 'Experiencia en cuidado de uñas', 1),
(24, 'Maquillaje', 'Belleza y Estética', 'Experiencia en maquillaje profesional', 1),
(25, 'Masajes', 'Belleza y Estética', 'Experiencia en masoterapia', 1),
(26, 'Conductor particular', 'Transporte', 'Experiencia como chofer privado', 1),
(27, 'Mensajería', 'Transporte', 'Experiencia en servicio de mensajería', 1),
(28, 'Mudanzas', 'Transporte', 'Experiencia en servicios de mudanza', 1),
(29, 'Soporte técnico', 'Tecnología', 'Experiencia en soporte técnico de computadoras', 1),
(30, 'Diseño gráfico', 'Tecnología', 'Experiencia en diseño digital', 1),
(31, 'Fotografía', 'Tecnología', 'Experiencia en fotografía profesional', 1),
(32, 'Edición de video', 'Tecnología', 'Experiencia en edición audiovisual', 1),
(33, 'Organización de eventos', 'Eventos', 'Experiencia organizando eventos', 1),
(34, 'Catering', 'Eventos', 'Experiencia en servicio de catering', 1),
(35, 'Animación infantil', 'Eventos', 'Experiencia en entretenimiento para niños', 1),
(36, 'DJ/Música en vivo', 'Eventos', 'Experiencia en música para eventos', 1),
(37, 'Asistencia administrativa', 'Administración', 'Experiencia en tareas administrativas', 1),
(38, 'Contabilidad', 'Administración', 'Experiencia en contabilidad y finanzas', 1),
(39, 'Atención al cliente', 'Administración', 'Experiencia en servicio al cliente', 1),
(40, 'Entrenamiento personal', 'Deportes y Fitness', 'Experiencia como entrenador personal', 1),
(41, 'Clases de yoga', 'Deportes y Fitness', 'Experiencia enseñando yoga', 1),
(42, 'Instructor de deportes', 'Deportes y Fitness', 'Experiencia enseñando deportes', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresas`
--

CREATE TABLE `empresas` (
  `Id` int(11) NOT NULL,
  `UsuarioId` int(11) NOT NULL,
  `NombreEmpresa` varchar(200) NOT NULL,
  `Descripcion` text DEFAULT NULL,
  `Industria` varchar(100) DEFAULT NULL,
  `Sitio` varchar(200) DEFAULT NULL,
  `LogoEmpresa` varchar(255) DEFAULT NULL,
  `Direccion` varchar(300) DEFAULT NULL,
  `Ciudad` varchar(100) DEFAULT NULL,
  `Pais` varchar(100) DEFAULT NULL,
  `FechaCreacion` datetime DEFAULT current_timestamp(),
  `Verificada` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empresas`
--

INSERT INTO `empresas` (`Id`, `UsuarioId`, `NombreEmpresa`, `Descripcion`, `Industria`, `Sitio`, `LogoEmpresa`, `Direccion`, `Ciudad`, `Pais`, `FechaCreacion`, `Verificada`) VALUES
(9, 27, 'Asadero Angus Beef INEGI 3', 'Come RibEye se feliz muy feliz', 'Servicios', 'No especificado', NULL, 'AV Heroe de Nacozaria #2513', 'Aguascalientes, Ags', 'Mexico', '2025-11-10 07:30:40', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `perfiles_usuarios`
--

CREATE TABLE `perfiles_usuarios` (
  `Id` int(11) NOT NULL,
  `UsuarioId` int(11) NOT NULL,
  `NombreCompleto` varchar(100) DEFAULT NULL,
  `Profesion` varchar(100) DEFAULT NULL,
  `Edad` int(11) DEFAULT NULL,
  `Genero` varchar(50) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Telefono` varchar(20) DEFAULT NULL,
  `Localidad` varchar(100) DEFAULT NULL,
  `Direccion` varchar(200) DEFAULT NULL,
  `AniosExperiencia` varchar(50) DEFAULT NULL,
  `EmpresaActual` varchar(100) DEFAULT NULL,
  `Habilidades` text DEFAULT NULL,
  `DescripcionProfesional` text DEFAULT NULL,
  `Certificaciones` text DEFAULT NULL,
  `ProyectosCompletados` int(11) DEFAULT 0,
  `ClientesSatisfechos` int(11) DEFAULT 0,
  `CalificacionPromedio` decimal(3,2) DEFAULT 0.00,
  `FotoPerfil` varchar(255) DEFAULT NULL,
  `FechaActualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `perfiles_usuarios`
--

INSERT INTO `perfiles_usuarios` (`Id`, `UsuarioId`, `NombreCompleto`, `Profesion`, `Edad`, `Genero`, `Email`, `Telefono`, `Localidad`, `Direccion`, `AniosExperiencia`, `EmpresaActual`, `Habilidades`, `DescripcionProfesional`, `Certificaciones`, `ProyectosCompletados`, `ClientesSatisfechos`, `CalificacionPromedio`, `FotoPerfil`, `FechaActualizacion`) VALUES
(31, 27, 'Rodrigo Perez', 'Coloca tu profesion', 34, 'Masculino', 'rodrixraton@gmail.com', '4492107183', 'Coloca tu localidad', 'Coloca tu direccion', '12', 'CETIS 155', 'platillof fdf', 'Coloca tu descripcion profesional', '', 0, 0, 0.00, '/static/uploads/profile_photos/27_1763693491_sobre.png', '2025-11-21 02:51:57'),
(32, 13, 'Admin', NULL, NULL, NULL, 'wrkaaraund25@gmail.com', '', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0.00, NULL, '2025-11-07 18:56:33'),
(34, 32, 'Rodrigo Martin Alvarez', NULL, NULL, NULL, 'rodrigomartinze@gmail.com', '4492107183', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0.00, NULL, '2025-11-11 23:41:37'),
(35, 35, 'William Efren', NULL, 18, NULL, 'william@gmail.com', '4492107181', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0.00, '/static/uploads/profile_photos/35_1763648764_perfil.jpg', '2025-11-20 14:26:04');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `Id` int(11) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `NombreCompleto` varchar(200) NOT NULL,
  `edad` int(11) NOT NULL,
  `TipoUsuario` enum('Candidato','Empleador') NOT NULL,
  `Telefono` varchar(20) DEFAULT NULL,
  `FotoPerfil` varchar(500) DEFAULT NULL,
  `Documento` varchar(500) DEFAULT NULL,
  `FechaRegistro` datetime DEFAULT current_timestamp(),
  `rol` varchar(10) DEFAULT 'usuario',
  `Activo` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`Id`, `Email`, `Password`, `NombreCompleto`, `edad`, `TipoUsuario`, `Telefono`, `FotoPerfil`, `Documento`, `FechaRegistro`, `rol`, `Activo`) VALUES
(13, 'wrkaaraund25@gmail.com', 'admin', 'Admin', 0, 'Empleador', NULL, NULL, NULL, '2025-10-14 08:06:02', 'admin', 1),
(27, 'rodrixraton@gmail.com', '123', 'Rodrigo Perez', 0, 'Empleador', '4492107183', 'None', 'None', '2025-10-27 07:39:47', 'usuario', 1),
(32, 'rodrigomartinze@gmail.com', 'R0dr1g0_123', 'Rodrigo Martin Alvarez', 0, 'Candidato', '4492107183', NULL, NULL, '2025-11-11 17:41:22', 'usuario', 1),
(33, 'pepito@gmail.com', 'PepechuyCUM123_', 'Rodrigo Martin Alvarez1', 0, 'Candidato', '4492107183', NULL, NULL, '2025-11-14 08:33:21', 'usuario', 1),
(34, '123@gmail.com', '123', '123', 0, 'Empleador', '123', NULL, NULL, '2025-11-18 07:29:11', 'usuario', 1),
(35, 'william@gmail.com', 'W1ll14m123_', 'William Efren', 0, 'Candidato', '4492107181', NULL, NULL, '2025-11-20 08:23:46', 'usuario', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_experiencias`
--

CREATE TABLE `usuario_experiencias` (
  `Id` int(11) NOT NULL,
  `UsuarioId` int(11) NOT NULL,
  `ExperienciaId` int(11) NOT NULL,
  `AniosExperiencia` int(11) NOT NULL,
  `FechaAgregado` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario_experiencias`
--

INSERT INTO `usuario_experiencias` (`Id`, `UsuarioId`, `ExperienciaId`, `AniosExperiencia`, `FechaAgregado`) VALUES
(4, 27, 2, 2, '2025-11-20 20:51:52');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vacantes`
--

CREATE TABLE `vacantes` (
  `Id` int(11) NOT NULL,
  `EmpresaId` int(11) NOT NULL,
  `Titulo` varchar(200) NOT NULL,
  `Descripcion` text NOT NULL,
  `Requisitos` text DEFAULT NULL,
  `Responsabilidades` text DEFAULT NULL,
  `SalarioMin` decimal(10,2) DEFAULT NULL,
  `SalarioMax` decimal(10,2) DEFAULT NULL,
  `Ubicacion` varchar(100) NOT NULL,
  `TipoTrabajo` enum('Remoto','Presencial','Hibrido') DEFAULT NULL,
  `TipoContrato` enum('Tiempo Completo','Medio Tiempo','Temporal','Freelance') DEFAULT NULL,
  `Experiencia` varchar(50) DEFAULT NULL,
  `FechaPublicacion` datetime DEFAULT current_timestamp(),
  `FechaCierre` datetime DEFAULT NULL,
  `Activa` tinyint(1) DEFAULT 1,
  `Vistas` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `vacantes`
--

INSERT INTO `vacantes` (`Id`, `EmpresaId`, `Titulo`, `Descripcion`, `Requisitos`, `Responsabilidades`, `SalarioMin`, `SalarioMax`, `Ubicacion`, `TipoTrabajo`, `TipoContrato`, `Experiencia`, `FechaPublicacion`, `FechaCierre`, `Activa`, `Vistas`) VALUES
(11, 9, 'Parrillero', 'Parrillero para un restaurante de cortes de carne de gran calidad', 'Conocer los terminos de la carne y elaboracion de otros platillos con facilidad.', '', 15000.00, 20000.00, 'Mexico', 'Presencial', 'Tiempo Completo', '1-3 años', '2025-11-10 07:33:14', NULL, 1, 0);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vistavacantescompleta`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vistavacantescompleta` (
);

-- --------------------------------------------------------

--
-- Estructura para la vista `vistavacantescompleta`
--
DROP TABLE IF EXISTS `vistavacantescompleta`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vistavacantescompleta`  AS SELECT `v`.`Id` AS `Id`, `v`.`Titulo` AS `Titulo`, `v`.`Descripcion` AS `Descripcion`, `v`.`SalarioMin` AS `SalarioMin`, `v`.`SalarioMax` AS `SalarioMax`, `v`.`Ubicacion` AS `Ubicacion`, `v`.`TipoTrabajo` AS `TipoTrabajo`, `v`.`TipoContrato` AS `TipoContrato`, `v`.`Experiencia` AS `Experiencia`, `v`.`FechaPublicacion` AS `FechaPublicacion`, `e`.`NombreEmpresa` AS `NombreEmpresa`, `e`.`Logo` AS `EmpresaLogo`, `e`.`Industria` AS `Industria`, `e`.`Verificada` AS `EmpresaVerificada`, (select count(0) from `aplicaciones` `a` where `a`.`VacanteId` = `v`.`Id`) AS `NumeroAplicaciones` FROM (`vacantes` `v` join `empresas` `e` on(`v`.`EmpresaId` = `e`.`Id`)) ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `aplicaciones`
--
ALTER TABLE `aplicaciones`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `VacanteId` (`VacanteId`,`UsuarioId`),
  ADD KEY `UsuarioId` (`UsuarioId`);

--
-- Indices de la tabla `catalogo_certificaciones`
--
ALTER TABLE `catalogo_certificaciones`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `nombre_unico` (`Nombre`);

--
-- Indices de la tabla `catalogo_experiencias`
--
ALTER TABLE `catalogo_experiencias`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `tipo_experiencia_unico` (`TipoExperiencia`);

--
-- Indices de la tabla `empresas`
--
ALTER TABLE `empresas`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `IX_Empresas_UsuarioId` (`UsuarioId`);

--
-- Indices de la tabla `perfiles_usuarios`
--
ALTER TABLE `perfiles_usuarios`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `UsuarioId` (`UsuarioId`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `Email` (`Email`),
  ADD KEY `IX_Usuarios_Email` (`Email`);

--
-- Indices de la tabla `usuario_experiencias`
--
ALTER TABLE `usuario_experiencias`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `usuario_experiencia_unico` (`UsuarioId`,`ExperienciaId`),
  ADD KEY `ExperienciaId` (`ExperienciaId`);

--
-- Indices de la tabla `vacantes`
--
ALTER TABLE `vacantes`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `EmpresaId` (`EmpresaId`),
  ADD KEY `IX_Vacantes_Activa` (`Activa`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `aplicaciones`
--
ALTER TABLE `aplicaciones`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `catalogo_certificaciones`
--
ALTER TABLE `catalogo_certificaciones`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT de la tabla `catalogo_experiencias`
--
ALTER TABLE `catalogo_experiencias`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT de la tabla `empresas`
--
ALTER TABLE `empresas`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT de la tabla `perfiles_usuarios`
--
ALTER TABLE `perfiles_usuarios`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT de la tabla `usuario_experiencias`
--
ALTER TABLE `usuario_experiencias`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `vacantes`
--
ALTER TABLE `vacantes`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `aplicaciones`
--
ALTER TABLE `aplicaciones`
  ADD CONSTRAINT `aplicaciones_ibfk_1` FOREIGN KEY (`VacanteId`) REFERENCES `vacantes` (`Id`),
  ADD CONSTRAINT `aplicaciones_ibfk_2` FOREIGN KEY (`UsuarioId`) REFERENCES `usuarios` (`Id`);

--
-- Filtros para la tabla `empresas`
--
ALTER TABLE `empresas`
  ADD CONSTRAINT `empresas_ibfk_1` FOREIGN KEY (`UsuarioId`) REFERENCES `usuarios` (`Id`);

--
-- Filtros para la tabla `perfiles_usuarios`
--
ALTER TABLE `perfiles_usuarios`
  ADD CONSTRAINT `perfiles_usuarios_ibfk_1` FOREIGN KEY (`UsuarioId`) REFERENCES `usuarios` (`Id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `usuario_experiencias`
--
ALTER TABLE `usuario_experiencias`
  ADD CONSTRAINT `usuario_experiencias_ibfk_1` FOREIGN KEY (`UsuarioId`) REFERENCES `usuarios` (`Id`) ON DELETE CASCADE,
  ADD CONSTRAINT `usuario_experiencias_ibfk_2` FOREIGN KEY (`ExperienciaId`) REFERENCES `catalogo_experiencias` (`Id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `vacantes`
--
ALTER TABLE `vacantes`
  ADD CONSTRAINT `vacantes_ibfk_1` FOREIGN KEY (`EmpresaId`) REFERENCES `empresas` (`Id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

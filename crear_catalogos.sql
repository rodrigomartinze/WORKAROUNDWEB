-- Crear tablas de catálogo para certificaciones y habilidades

CREATE TABLE IF NOT EXISTS catalogo_habilidades (
    Id INT(11) NOT NULL AUTO_INCREMENT,
    Nombre VARCHAR(100) NOT NULL,
    Categoria VARCHAR(50) NOT NULL,
    Descripcion TEXT DEFAULT NULL,
    Activa TINYINT(1) DEFAULT 1,
    PRIMARY KEY (Id),
    UNIQUE KEY nombre_unico (Nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS catalogo_certificaciones (
    Id INT(11) NOT NULL AUTO_INCREMENT,
    Nombre VARCHAR(150) NOT NULL,
    Categoria VARCHAR(50) NOT NULL,
    Emisor VARCHAR(100) DEFAULT NULL,
    Descripcion TEXT DEFAULT NULL,
    Activa TINYINT(1) DEFAULT 1,
    PRIMARY KEY (Id),
    UNIQUE KEY nombre_unico (Nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insertar datos de ejemplo para certificaciones
INSERT INTO catalogo_certificaciones (Nombre, Categoria, Emisor, Descripcion) VALUES
('AWS Certified Solutions Architect', 'Cloud Computing', 'Amazon Web Services', 'Certificación para arquitectos de soluciones en AWS'),
('Microsoft Azure Fundamentals', 'Cloud Computing', 'Microsoft', 'Certificación básica de Azure'),
('Google Cloud Professional', 'Cloud Computing', 'Google', 'Certificación profesional de Google Cloud'),
('Certified Kubernetes Administrator', 'DevOps', 'Cloud Native Computing Foundation', 'Administración de Kubernetes'),
('Docker Certified Associate', 'DevOps', 'Docker Inc', 'Certificación de Docker'),
('PMP - Project Management Professional', 'Gestión de Proyectos', 'PMI', 'Gestión profesional de proyectos'),
('Scrum Master Certification', 'Metodologías Ágiles', 'Scrum Alliance', 'Certificación Scrum Master'),
('Certified Ethical Hacker', 'Seguridad', 'EC-Council', 'Hacking ético certificado'),
('CISSP', 'Seguridad', 'ISC2', 'Profesional certificado en seguridad de sistemas de información'),
('CompTIA Security+', 'Seguridad', 'CompTIA', 'Certificación de seguridad CompTIA'),
('Oracle Certified Professional', 'Bases de Datos', 'Oracle', 'Certificación profesional de Oracle'),
('MongoDB Certified Developer', 'Bases de Datos', 'MongoDB Inc', 'Desarrollador certificado MongoDB'),
('Python Institute PCEP', 'Programación', 'Python Institute', 'Programador Python certificado nivel básico'),
('Java SE Programmer', 'Programación', 'Oracle', 'Programador Java SE'),
('Microsoft Certified: Azure Developer', 'Desarrollo', 'Microsoft', 'Desarrollador Azure certificado'),
('Salesforce Certified Administrator', 'CRM', 'Salesforce', 'Administrador Salesforce certificado'),
('Tableau Desktop Specialist', 'Análisis de Datos', 'Tableau', 'Especialista en Tableau Desktop'),
('Google Analytics Individual Qualification', 'Marketing Digital', 'Google', 'Certificación de Google Analytics'),
('HubSpot Inbound Marketing', 'Marketing Digital', 'HubSpot', 'Marketing de entrada HubSpot'),
('Red Hat Certified System Administrator', 'Sistemas Operativos', 'Red Hat', 'Administrador de sistemas Red Hat');

-- Insertar datos de ejemplo para habilidades
INSERT INTO catalogo_habilidades (Nombre, Categoria, Descripcion) VALUES
('JavaScript', 'Lenguajes de Programación', 'Lenguaje de programación para desarrollo web'),
('Python', 'Lenguajes de Programación', 'Lenguaje de programación versátil'),
('Java', 'Lenguajes de Programación', 'Lenguaje de programación orientado a objetos'),
('C#', 'Lenguajes de Programación', 'Lenguaje de programación de Microsoft'),
('PHP', 'Lenguajes de Programación', 'Lenguaje para desarrollo web del lado del servidor'),
('React', 'Frameworks Frontend', 'Biblioteca de JavaScript para interfaces de usuario'),
('Angular', 'Frameworks Frontend', 'Framework de JavaScript para aplicaciones web'),
('Vue.js', 'Frameworks Frontend', 'Framework progresivo de JavaScript'),
('Node.js', 'Frameworks Backend', 'Entorno de ejecución de JavaScript del lado del servidor'),
('Django', 'Frameworks Backend', 'Framework web de Python'),
('Spring Boot', 'Frameworks Backend', 'Framework de Java para aplicaciones empresariales'),
('Express.js', 'Frameworks Backend', 'Framework minimalista para Node.js'),
('MySQL', 'Bases de Datos', 'Sistema de gestión de bases de datos relacionales'),
('PostgreSQL', 'Bases de Datos', 'Base de datos relacional avanzada'),
('MongoDB', 'Bases de Datos', 'Base de datos NoSQL orientada a documentos'),
('Redis', 'Bases de Datos', 'Base de datos en memoria'),
('Docker', 'DevOps', 'Plataforma de contenedores'),
('Kubernetes', 'DevOps', 'Orquestación de contenedores'),
('Git', 'Control de Versiones', 'Sistema de control de versiones distribuido'),
('AWS', 'Cloud Computing', 'Amazon Web Services'),
('Azure', 'Cloud Computing', 'Plataforma cloud de Microsoft'),
('Google Cloud', 'Cloud Computing', 'Plataforma cloud de Google'),
('Machine Learning', 'Inteligencia Artificial', 'Aprendizaje automático'),
('Deep Learning', 'Inteligencia Artificial', 'Aprendizaje profundo'),
('Data Analysis', 'Análisis de Datos', 'Análisis de datos'),
('Power BI', 'Análisis de Datos', 'Herramienta de visualización de datos'),
('Tableau', 'Análisis de Datos', 'Software de visualización de datos'),
('Scrum', 'Metodologías Ágiles', 'Marco de trabajo ágil'),
('Agile', 'Metodologías Ágiles', 'Metodología de desarrollo ágil'),
('UI/UX Design', 'Diseño', 'Diseño de interfaces y experiencia de usuario');

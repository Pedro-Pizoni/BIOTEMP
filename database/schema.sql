SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS biotemp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'biotemp'@'localhost' IDENTIFIED BY 'biotemp123';
CREATE USER IF NOT EXISTS 'biotemp'@'%' IDENTIFIED BY 'biotemp123';
GRANT ALL PRIVILEGES ON biotemp.* TO 'biotemp'@'localhost';
GRANT ALL PRIVILEGES ON biotemp.* TO 'biotemp'@'%';
FLUSH PRIVILEGES;

USE biotemp;

CREATE TABLE IF NOT EXISTS equipamentos (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    localizacao  VARCHAR(100),
    temp_min     DOUBLE  NOT NULL DEFAULT 2,
    temp_max     DOUBLE  NOT NULL DEFAULT 8,
    ativo        BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS medicoes (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    equipamento_id  INT      NOT NULL,
    temperatura     DOUBLE   NOT NULL,
    umidade         DOUBLE,
    data_hora       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id)
);

CREATE TABLE IF NOT EXISTS alertas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    equipamento_id  INT          NOT NULL,
    tipo            VARCHAR(30)  NOT NULL,
    mensagem        VARCHAR(200) NOT NULL,
    valor           DOUBLE,
    data_hora       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id)
);

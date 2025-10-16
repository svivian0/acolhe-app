create database acolheapp;
use acolheapp;
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE, 
    senha VARCHAR(255) NOT NULL,
    tipo_usuario ENUM('pessoal', 'empresarial') NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE perfis_pessoais (
    id_perfil_pessoal INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE, 
    neurodivergencia VARCHAR(255),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);


CREATE TABLE estabelecimentos (
    id_estabelecimento INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE, 
    razao_social VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    endereco TEXT NOT NULL,
    telefone VARCHAR(20),
    descricao TEXT,
    media_avaliacao DECIMAL(2,1) DEFAULT 0.0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);


CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome_categoria VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE estabelecimento_categoria (
    id_estabelecimento_categoria INT AUTO_INCREMENT PRIMARY KEY,
    id_estabelecimento INT NOT NULL,
    id_categoria INT NOT NULL,
    FOREIGN KEY (id_estabelecimento) REFERENCES estabelecimentos(id_estabelecimento),
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    UNIQUE (id_estabelecimento, id_categoria) 
);


CREATE TABLE acessibilidade (
    id_acessibilidade INT AUTO_INCREMENT PRIMARY KEY,
    item_acessibilidade VARCHAR(255) NOT NULL UNIQUE
);


CREATE TABLE estabelecimento_acessibilidade (
    id_estabelecimento_acessibilidade INT AUTO_INCREMENT PRIMARY KEY,
    id_estabelecimento INT NOT NULL,
    id_acessibilidade INT NOT NULL,
    FOREIGN KEY (id_estabelecimento) REFERENCES estabelecimentos(id_estabelecimento),
    FOREIGN KEY (id_acessibilidade) REFERENCES acessibilidade(id_acessibilidade),
    UNIQUE (id_estabelecimento, id_acessibilidade) 
);


CREATE TABLE avaliacoes (
    id_avaliacao INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_estabelecimento INT NOT NULL,
    nota_geral DECIMAL(2,1) NOT NULL CHECK (nota_geral BETWEEN 1.0 AND 5.0),
    comentario TEXT,
    data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_estabelecimento) REFERENCES estabelecimentos(id_estabelecimento),
    UNIQUE (id_usuario, id_estabelecimento) 
);
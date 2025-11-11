-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema pedido
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema pedido
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `pedido` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `pedido` ;

-- -----------------------------------------------------
-- Table `pedido`.`clientes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido`.`clientes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(255) NOT NULL,
  `telefone` VARCHAR(20) NULL DEFAULT NULL,
  `email` VARCHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `nome` (`nome` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `pedido`.`estoque`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido`.`estoque` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Nome` VARCHAR(255) NOT NULL,
  `Quantidade` DECIMAL(10,2) NOT NULL DEFAULT '0.00',
  `DataCadastro` DATE NULL DEFAULT curdate(),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `Nome` (`Nome` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `pedido`.`fornecedores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido`.`fornecedores` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(255) NOT NULL,
  `contato` VARCHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `nome` (`nome` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `pedido`.`consignado`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido`.`consignado` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `estoque_id` INT NOT NULL,
  `fornecedor_id` INT NOT NULL,
  `Quantidade` DECIMAL(10,2) NOT NULL,
  `Valor` DECIMAL(10,2) NOT NULL,
  `DataChegada` DATE NULL DEFAULT curdate(),
  `DataColeta` DATE NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `estoque_id` (`estoque_id` ASC) VISIBLE,
  INDEX `fornecedor_id` (`fornecedor_id` ASC) VISIBLE,
  CONSTRAINT `consignado_ibfk_1`
    FOREIGN KEY (`estoque_id`)
    REFERENCES `pedido`.`estoque` (`id`),
  CONSTRAINT `consignado_ibfk_2`
    FOREIGN KEY (`fornecedor_id`)
    REFERENCES `pedido`.`fornecedores` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `pedido`.`usuarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido`.`usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `nivel` VARCHAR(20) NULL DEFAULT 'vendedor',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username` (`username` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `pedido`.`consignado_usos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido`.`consignado_usos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `estoque_id` INT NOT NULL,
  `fornecedor_id` INT NOT NULL,
  `usuario_id` INT NOT NULL,
  `QuantidadeUsada` DECIMAL(10,2) NOT NULL,
  `ValorUnitario` DECIMAL(10,2) NOT NULL,
  `DataUso` DATE NULL DEFAULT curdate(),
  PRIMARY KEY (`id`),
  INDEX `estoque_id` (`estoque_id` ASC) VISIBLE,
  INDEX `fornecedor_id` (`fornecedor_id` ASC) VISIBLE,
  INDEX `usuario_id` (`usuario_id` ASC) VISIBLE,
  CONSTRAINT `consignado_usos_ibfk_1`
    FOREIGN KEY (`estoque_id`)
    REFERENCES `pedido`.`estoque` (`id`),
  CONSTRAINT `consignado_usos_ibfk_2`
    FOREIGN KEY (`fornecedor_id`)
    REFERENCES `pedido`.`fornecedores` (`id`),
  CONSTRAINT `consignado_usos_ibfk_3`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `pedido`.`usuarios` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `pedido`.`entradas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido`.`entradas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `estoque_id` INT NOT NULL,
  `fornecedor_id` INT NULL DEFAULT NULL,
  `usuario_id` INT NOT NULL,
  `Quantidade` DECIMAL(10,2) NOT NULL,
  `DataEntrada` DATE NULL DEFAULT curdate(),
  PRIMARY KEY (`id`),
  INDEX `estoque_id` (`estoque_id` ASC) VISIBLE,
  INDEX `fornecedor_id` (`fornecedor_id` ASC) VISIBLE,
  INDEX `usuario_id` (`usuario_id` ASC) VISIBLE,
  CONSTRAINT `entradas_ibfk_1`
    FOREIGN KEY (`estoque_id`)
    REFERENCES `pedido`.`estoque` (`id`),
  CONSTRAINT `entradas_ibfk_2`
    FOREIGN KEY (`fornecedor_id`)
    REFERENCES `pedido`.`fornecedores` (`id`),
  CONSTRAINT `entradas_ibfk_3`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `pedido`.`usuarios` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `pedido`.`saidas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido`.`saidas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `estoque_id` INT NOT NULL,
  `cliente_id` INT NOT NULL,
  `usuario_id` INT NOT NULL,
  `Quantidade` DECIMAL(10,2) NOT NULL,
  `DataSaida` DATE NULL DEFAULT curdate(),
  PRIMARY KEY (`id`),
  INDEX `estoque_id` (`estoque_id` ASC) VISIBLE,
  INDEX `cliente_id` (`cliente_id` ASC) VISIBLE,
  INDEX `usuario_id` (`usuario_id` ASC) VISIBLE,
  CONSTRAINT `saidas_ibfk_1`
    FOREIGN KEY (`estoque_id`)
    REFERENCES `pedido`.`estoque` (`id`),
  CONSTRAINT `saidas_ibfk_2`
    FOREIGN KEY (`cliente_id`)
    REFERENCES `pedido`.`clientes` (`id`),
  CONSTRAINT `saidas_ibfk_3`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `pedido`.`usuarios` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

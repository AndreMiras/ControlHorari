CREATE SCHEMA Corbera21;
USE Corbera21;

CREATE TABLE `Corbera21`.`Professor` (
  `idProfessor` INT NOT NULL AUTO_INCREMENT,
  `Dni` VARCHAR(10) NOT NULL,
  `Nom` VARCHAR(45) NOT NULL,
  `Cognom` VARCHAR(45) NOT NULL,
  `CodiHorari` INT NOT NULL,
  `CodiBarres` VARCHAR(12) NOT NULL,
  `Departament` VARCHAR(45) NULL,
  `Actiu` INT NOT NULL,
  `Substitut` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`idProfessor`),
  UNIQUE INDEX `DNI_UNIQUE` (`Dni` ASC),
  UNIQUE INDEX `CodiBarres_UNIQUE` (`CodiBarres` ASC));

CREATE TABLE `Corbera21`.`Horari` (
  `idHorari` INT NOT NULL AUTO_INCREMENT,
  `Dia` INT NOT NULL,
  `Hora` INT NOT NULL,
  `Assignatura` VARCHAR(20) NOT NULL,
  `CodiHorari` INT NOT NULL,
  `Aula` VARCHAR(10) NULL,
  `Grup` VARCHAR(20) NULL,
  PRIMARY KEY (`idHorari`));

CREATE TABLE `Corbera21`.`Registre` (
  `idRegistre` INT NOT NULL AUTO_INCREMENT,
  `Dni` VARCHAR(10) NOT NULL,
  `CodiHorari` INT NOT NULL,
  `Data` DATE NOT NULL,
  `HoraEntrada` TIME NOT NULL,
  `HoraSortida` TIME NULL,
  PRIMARY KEY (`idRegistre`));


SET GLOBAL event_scheduler = ON;
CREATE EVENT sortida_profes
  ON SCHEDULE
    EVERY 1 DAY
    STARTS '2021-09-01 20:30:00'
  DO
    UPDATE Registre SET HoraSortida = '14:45:00' WHERE HoraSortida IS NULL;

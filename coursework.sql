DROP DATABASE IF EXISTS `music_archive`;
CREATE DATABASE `music_archive`
	DEFAULT CHARACTER SET utf8
    COLLATE utf8_unicode_ci;
USE `music_archive`;

CREATE TABLE `roles`(
id TINYINT UNSIGNED NOT NULL,
name VARCHAR (255)  NOT NULL,
PRIMARY KEY(id)
);
INSERT INTO `roles` VALUES(1, 'user');
INSERT INTO `roles` VALUES(2, 'composer');
INSERT INTO `roles` VALUES(3, 'admin');

CREATE TABLE `users`( 
	id INT UNSIGNED AUTO_INCREMENT NOT NULL,
    login VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(255) UNIQUE NOT NULL,
    `date` TIMESTAMP,
    `status` BOOLEAN,
    role_id TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(role_id) REFERENCES music_archive.`roles`(id)
);

DROP TRIGGER IF EXISTS registr_date;
CREATE TRIGGER registr_date BEFORE INSERT ON users
FOR EACH ROW 
	SET new.`date` = CURRENT_TIMESTAMP();

DELIMITER //
CREATE PROCEDURE update_status (IN user_id INT UNSIGNED, user_status BOOLEAN)
BEGIN
UPDATE `users`
SET `status` = user_status WHERE id = user_id;
END //
DELIMITER ;
INSERT INTO `users` VALUES (1234, 'olya', 'qnfk1e', 'oll', '0955039387', null, true, 1);
INSERT INTO `users` VALUES (1236, 'kate', 'qn689e', 'kat', '045739387', null, true, 1);
CALL update_status(1234, false);

DELIMITER //
CREATE PROCEDURE delete_user (IN user_id INT UNSIGNED)
BEGIN
DELETE FROM `users` WHERE id = user_id;
END//
DELIMITER ;
-- CALL delete_user(1234);

CREATE TABLE `composers`(
	id INT UNSIGNED UNIQUE NOT NULL,
    bio VARCHAR(255),
    `c_name` VARCHAR(255) UNIQUE NOT NULL,
    -- comp_amount INT UNSIGNED,
    FOREIGN KEY (id) REFERENCES users(id)
)ENGINE=INNODB;

DELIMITER //
CREATE PROCEDURE ins_comp (IN comp_bio VARCHAR(255), comp_name VARCHAR(255))
BEGIN
	INSERT INTO `composers`(bio, `c_name`) VALUES (comp_bio, comp_name);
END //
DELIMITER ;
CALL ins_comp('Born in 1995, California', 'Tom');
CALL ins_comp('Born in 1990, award-winning composer','Ted');

CREATE TABLE instruments (
id INT UNSIGNED AUTO_INCREMENT NOT NULL,
`name` VARCHAR(50),
PRIMARY KEY(id)
);
DELIMITER //
CREATE PROCEDURE ins_instr(IN `name` VARCHAR(50))
    BEGIN
    INSERT INTO instruments(`name`) VALUES(`name`);
    END //
DELIMITER ;

CREATE TABLE `compositions`(
	id INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    composer_name VARCHAR(255) NOT NULL,
    composer_id INT UNSIGNED NOT NULL,
    price DECIMAL(5,2),
    rating SMALLINT UNSIGNED,
    PRIMARY KEY(id),
    FOREIGN KEY(composer_name) REFERENCES music_archive.`composers`(`c_name`),
    FOREIGN KEY(composer_id) REFERENCES music_archive.`composers`(id)
);
CREATE TABLE `purchases`(
	id INT UNSIGNED AUTO_INCREMENT UNIQUE NOT NULL,
    composition_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(composition_id) REFERENCES `compositions`(id),
    FOREIGN KEY(user_id) REFERENCES `users`(id),
    `date` DATE
);
CREATE TRIGGER purchase_date BEFORE INSERT ON `purchases`
FOR EACH ROW 
	SET new.`date` = CURRENT_TIMESTAMP();

CREATE TABLE instr_composition (
instrument_id INT UNSIGNED NOT NULL,
composition_id INT UNSIGNED NOT NULL,
CONSTRAINT pk_instr_composition PRIMARY KEY(instrument_id, composition_id),
FOREIGN KEY (instrument_id) REFERENCES `instruments`(id),
FOREIGN KEY (composition_id) REFERENCES `compositions`(id)
);

DELIMITER //
CREATE FUNCTION max_price()
RETURNS INT
READS SQL DATA
BEGIN 
	DECLARE maxprice DECIMAL(5,2) DEFAULT NULL;
	SELECT MAX(`compositions`.price) FROM `compositions` INTO maxprice;
	RETURN maxprice;
END //
DELIMITER ;
SELECT max_price();
SELECT * FROM composers;
SELECT * FROM compositions;






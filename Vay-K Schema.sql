
-- ------------------------------------------------------
-- CREATE TABLE
-- ------------------------------------------------------
DROP DATABASE IF EXISTS VayK;
CREATE DATABASE IF NOT EXISTS VayK;
USE VayK;


-- Table structure for table user
DROP TABLE IF EXISTS user;
CREATE TABLE user (
	email varchar(50) not null,
    password varchar(50) not null,
    firstName varchar(50) not null,
    lastName varchar(50) not null,
    primary key(email)
)ENGINE=InnoDB;


-- Table structure for table trip
DROP TABLE IF EXISTS trip;
CREATE TABLE trip (
	id int NOT NULL AUTO_INCREMENT,
	title varchar(50) not null,
	ownerEmail varchar(50) not null,
    startDate date,
    endDate date,
    primary key(id),
	CONSTRAINT fk1 FOREIGN KEY (ownerEmail) REFERENCES user (email)
)ENGINE=InnoDB;

-- Table structure for table us_destination
DROP TABLE IF EXISTS us_location;
CREATE TABLE us_location (
	tripID int not null,
	city varchar(50) not null,
	state varchar(50) not null,
	country varchar(50) not null,
	primary key(tripID, city, state, country),
	CONSTRAINT fk2 FOREIGN KEY (tripID) REFERENCES trip (id)
)ENGINE=InnoDB;

-- Table structure for table non_us_destination
DROP TABLE IF EXISTS non_us_location;
CREATE TABLE non_us_location (
	tripID int not null,
	city varchar(50) not null,
	country varchar(50) not null,
	primary key(tripID, city, country),
	CONSTRAINT fk3 FOREIGN KEY (tripID) REFERENCES trip (id)
)ENGINE=InnoDB;

-- Table structure for table stops
DROP TABLE IF EXISTS stops;
CREATE TABLE stops (
	tripID int not null,
	day tinyint not null,
	eventNo tinyint not null,
	stopName varchar(50) not null,
	street varchar (50) not null,
	city varchar(50) not null,
	postalCode varchar(7) default null,
	stateRegion varchar(15) default null,
	country varchar(20) not null,
	type varchar(10) default "Attraction",
	time varchar(5) default null,
	confirmationNo varchar(50) default null,
	flightNo varchar(20) default null,
	notes text default null,
	primary key(tripID, day, eventNo),
	CONSTRAINT fk4 FOREIGN KEY (tripID) REFERENCES trip (id)
)ENGINE=InnoDB;

-- Table structure for table transportation
DROP TABLE IF EXISTS transportation;
CREATE TABLE transportation (
	tripID int not null,
	day tinyint not null,
	transNo tinyint not null,
	mode varChar(10) not null,
	hour int default 0,
	minutes int default 0,
	primary key(tripID, day, transNo),
	CONSTRAINT fk5 FOREIGN KEY (tripID) REFERENCES trip (id)
)ENGINE=InnoDB;


-- Table structure for table extension_info
DROP TABLE IF EXISTS extension_info;
CREATE TABLE extension_info (
	tripID int not null,
	id int NOT NULL AUTO_INCREMENT,
	title varchar(50) not null,
	website varchar(50) not null,
	description text default null,
	isSaved boolean default false,
	day tinyint default null,
	eventNo tinyint default null,
	primary key(id),
	CONSTRAINT fk7 FOREIGN KEY (tripID) REFERENCES trip (id),
	CONSTRAINT fk8 FOREIGN KEY (tripID, day, eventNo) REFERENCES stops (tripID, day, eventNo)
)ENGINE=InnoDB;







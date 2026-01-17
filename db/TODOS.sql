CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);

CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content VARCHAR(100),
    due DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    name VARCHAR(100) NOT NULL,
    type ENUM('savings', 'checking', 'private', 'youth'),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE kategorien (
    kategorie_id int AUTO_INCREMENT primary key,
    name varchar(50) not null
);

CREATE TABLE transfer (
    transfer_id INT AUTO_INCREMENT primary key,
    account_from INT not null,
    account_to int not null, 
    betrag decimal(10, 2) not null,
    datum datetime not null,
    foreign key(account_from) references accounts(account_id),
    foreign key (account_to) references accounts(account_id)  
);

CREATE TABLE ausgaben (
    ausgabe_id int AUTO_INCREMENT primary key,
    account_id int not null,
    kategorie_id int not null,
    datum datetime not null,
    betrag decimal(10, 2) not null,
    foreign key(account_id) references accounts(account_id),
    foreign key(kategorie_id) references kategorien(kategorie_id)

);

CREATE TABLE income (
    income_id int AUTO_INCREMENT primary key,
    user_id int not null,
    betrag decimal(10, 2) not null,
    datum datetime not null,
    foreign key(user_id) references users(id)
);

CREATE TABLE budget (
    budget_id int AUTO_INCREMENT primary key,
    user_id int not null,
    kategorie_id int not null,
    income_id int,
    limit_budget decimal(10, 2) not null,
    foreign key(user_id) references users(id),
    foreign key (kategorie_id) references kategorien(kategorie_id),
    foreign key (income_id) references income(income_id)
);


insert into users(username, password) values
('tibolb' 'tobi');

insert into accounts(user_id, name, type) values
('1' 'Main account' 'private'),
('1' 'Savings account' 'savings'),
('1' 'Youth Account' 'youth'),
('1' 'Checkings account' 'checkings');

insert into kategorien(name) values
('Essen'),
('Abo'),
('Miete'),
('Unterhaltung'),
('Kleider');
('Saving')

insert into transfer(account_from, account_to, betrag, datum) values
(1, 2, 100, '2026-01-15 10:00:00'),
(2, 1, 100, '2026-01-16 10:00:00');

insert into ausgaben(account_id, kategorie_id, datum, betrag) values
(1, 1, '2026-01-14 16:00:00', 25),
(1, 3, '2026-01-01' 1600);

insert into income(user_id, betrag, datum) values
(1, 4500, '2026-01-01 10:00:00'),
(1, 4500, '2026-02-01 10:00:00');

insert into budget(user_id, kategorie_id, income_id, limit_budget) values
(1, 1, 1, 400),
(1, 2, 1 100),
(1, 3, 1 1500),
(1, 4, 1, 700),
(1, 5, 1, 300),
(1, 6, 2, 1500),
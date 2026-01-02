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

CREATE TABLE account (
    acount_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL
    name VARCHAR(100) NOT NULL 
    type ENUM('savings' 'checking' 'private' 'youth')
    FOREIGN KEY user_id REFERENCES users(id)
)

CREATE TABLE transfer (
    transfer_id INT AUTO_INCREMENT primary key,
    account_from INT not null,
    account_to int not null, 
    betrag decimal(10, 2) not null,
    datum datetime not null,
    foreign key(account_from) references accounts(account_id),
    foreign key (account_to) references accounts(account_id)  
)

CREATE TABLE ausgabe (
    ausgabe_id int AUTO_INCREMENT primary key,
    account_id int not null,
    kategorie_id int not null,
    datum datetime not null,
    betrag deciman(10, 2) not null,
    foreign key(account_id) references accounts(account_id)
    foreign key(kategorie_id) references kategorien(kategorie_id)

)

CREATE TABLE reminder (
    reminder_id int AUTO_INCREMENT primary key,
    ausgabe_id int not null,
    betrag decimal(10, 2) not null,
    fällig_bis date not null
    fällig_von date not null,
    foreign key(ausgabe_id) references ausgaben(ausgabe_id)
)

CREATE TABLE kategorie (
    kategorie_id int AUTO_INCREMENT primary key,
    name varchar(50) not null
)

CREATE TABLE budget (
    budget_id int AUTO_INCREMENT primary key,
    user_id int not null,
    kategorie_id int not null,
    income_id int,
    limit_budget decimal(10, 2) not null,
    foreign key(user_id) references users(id),
    foreign key (kategorie_id) references kategorien(kategorie_id),
    foreign key (income_id) references income(income_id)
)

CREATE TABLE income (
    income_id int AUTO_INCREMENT primary key,
    user_id int not null,
    betrag decimal(10, 2) not null,
    datum datetime not null,
    foreign key(user_id) references users(id)
);
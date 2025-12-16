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
    transfer_id INT 
)

CREATE TABLE ausgabe (
    ausgabe_id
)

CREATE TABLE reminder (
    reminder_id
)

CREATE TABLE kategorie (
    kategorie_id
)

CREATE TABLE budget (
    budget_id
)

CREATE TABLE income (
    income_id
)
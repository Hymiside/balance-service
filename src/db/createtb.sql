CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE cash_accounts (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    balance INTEGER DEFAULT 0
);

CREATE TABLE type_transactions (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    type INTEGER REFERENCES type_transactions(id) NOT NULL,
    amount_money INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    user_id_from INTEGER REFERENCES users(id),
    user_id_to INTEGER REFERENCES users(id)
);
CREATE USER repl_shumkin WITH PASSWORD '123' REPLICATION;

CREATE TABLE IF NOT EXISTS hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 scram-sha-256');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();

CREATE TABLE IF NOT EXISTS emails  (
    emailid SERIAL PRIMARY KEY,
    email VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS phones  (
    phoneid SERIAL PRIMARY KEY,
    phone_number VARCHAR(256)
);

\connect postgres

SET client_min_messages TO WARNING;
DROP DATABASE IF EXISTS baxdb;
DROP ROLE IF EXISTS baxdb_owner;

CREATE ROLE baxdb_owner WITH
    LOGIN
    CREATEROLE
    ENCRYPTED PASSWORD 'password'
    ;
CREATE DATABASE baxdb
    WITH OWNER = baxdb_owner
    ENCODING = 'UTF-8'
    ;
-- Create the database user
CREATE USER sadie WITH PASSWORD 'sadie_dev';

-- Create the database
CREATE DATABASE sadie_dev WITH OWNER = sadie;

-- Connect to the database
\c sadie_dev

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sadie_dev TO sadie; 
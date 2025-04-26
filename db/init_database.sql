-- ===============================
-- Pinboard Project - Database Setup
-- Master Script: Creates tables + procedures
-- ===============================

-- Step 0: Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Step 1: Create tables (schema only)
\i db/tables/init_schema.sql

-- Step 2: Create stored procedures (functions)
\i db/functions/create_function_signup_user.sql
\i db/functions/create_function_signin_user.sql
-- NOTE TO COLLABORATORS: Add more functions here as you create them


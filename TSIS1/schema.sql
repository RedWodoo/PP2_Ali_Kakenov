-- ============================================================
-- TSIS 1 — Extended PhoneBook Schema
-- Creates: groups table, extends contacts, creates phones table
-- ============================================================

-- Group/category table
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default groups
INSERT INTO groups(name) VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- Extend the phonebook table with new fields
-- (safe to run multiple times thanks to IF NOT EXISTS logic)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='phonebook' AND column_name='email') THEN
        ALTER TABLE phonebook ADD COLUMN email VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='phonebook' AND column_name='birthday') THEN
        ALTER TABLE phonebook ADD COLUMN birthday DATE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='phonebook' AND column_name='group_id') THEN
        ALTER TABLE phonebook ADD COLUMN group_id INTEGER REFERENCES groups(id);
    END IF;
END $$;

-- Phones table: multiple phone numbers per contact (1-to-many)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES phonebook(contact_id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);

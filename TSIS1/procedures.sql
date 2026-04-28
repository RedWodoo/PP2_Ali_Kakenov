-- ============================================================
-- TSIS 1 — Stored Procedures (extends Practice 8)
-- Carries forward: upsert_contact, insert_many_contacts, delete_contact
-- NEW: add_phone, move_to_group
-- ============================================================

-- [Practice 8] Upsert: insert or update by name
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_name) THEN
        UPDATE phonebook SET phone_number = p_phone WHERE first_name = p_name;
    ELSE
        INSERT INTO phonebook(first_name, phone_number) VALUES(p_name, p_phone);
    END IF;
END;
$$;

-- [Practice 8] Bulk insert with validation
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names TEXT[], p_phones TEXT[],
    OUT bad_names TEXT[], OUT bad_phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE i INT;
BEGIN
    bad_names := ARRAY[]::TEXT[];
    bad_phones := ARRAY[]::TEXT[];
    IF p_names IS NOT NULL AND array_length(p_names, 1) > 0 THEN
        FOR i IN 1 .. array_length(p_names, 1) LOOP
            IF p_phones[i] ~ '^\+?[0-9]{10,15}$' THEN
                IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_names[i]) THEN
                    UPDATE phonebook SET phone_number = p_phones[i] WHERE first_name = p_names[i];
                ELSE
                    INSERT INTO phonebook(first_name, phone_number) VALUES (p_names[i], p_phones[i])
                    ON CONFLICT (phone_number) DO NOTHING;
                END IF;
            ELSE
                bad_names := array_append(bad_names, p_names[i]);
                bad_phones := array_append(bad_phones, p_phones[i]);
            END IF;
        END LOOP;
    END IF;
END;
$$;

-- [Practice 8] Delete by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(identifier VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook WHERE first_name = identifier OR phone_number = identifier;
END;
$$;

-- ============================================================
-- NEW PROCEDURES FOR TSIS 1
-- ============================================================

-- Add a phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT contact_id INTO v_contact_id FROM phonebook WHERE first_name = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    INSERT INTO phones(contact_id, phone, type) VALUES (v_contact_id, p_phone, p_type);
END;
$$;

-- Move a contact to a group (create group if it doesn't exist)
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR, p_group_name VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    -- Create group if missing
    INSERT INTO groups(name) VALUES (p_group_name) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    -- Update contact
    UPDATE phonebook SET group_id = v_group_id WHERE first_name = p_contact_name;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
END;
$$;

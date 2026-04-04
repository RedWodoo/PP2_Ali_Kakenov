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

CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names TEXT[],
    p_phones TEXT[],
    OUT bad_names TEXT[],
    OUT bad_phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    bad_names := ARRAY[]::TEXT[];
    bad_phones := ARRAY[]::TEXT[];

    IF p_names IS NOT NULL AND array_length(p_names, 1) > 0 THEN
        FOR i IN 1 .. array_length(p_names, 1) LOOP
            IF p_phones[i] ~ '^\+?[0-9]{10,15}$' THEN
                IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_names[i]) THEN
                    UPDATE phonebook SET phone_number = p_phones[i] WHERE first_name = p_names[i];
                ELSE
                    INSERT INTO phonebook(first_name, phone_number) 
                    VALUES (p_names[i], p_phones[i])
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

CREATE OR REPLACE PROCEDURE delete_contact(identifier VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook 
    WHERE first_name = identifier OR phone_number = identifier;
END;
$$;
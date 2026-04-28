-- ============================================================
-- TSIS 1 — Functions (extends Practice 8)
-- Updated search_contacts to also match email and phones table
-- ============================================================

-- Drop old functions first (signature changed from Practice 8)
DROP FUNCTION IF EXISTS search_contacts(VARCHAR);
DROP FUNCTION IF EXISTS get_contacts_paginated(INT, INT);

-- Extended search: matches name, phone_number, email, AND phones table
CREATE OR REPLACE FUNCTION search_contacts(pattern VARCHAR)
RETURNS TABLE(contact_id INT, first_name VARCHAR, phone_number VARCHAR,
              email VARCHAR, birthday DATE, group_name VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT p.contact_id, p.first_name, p.phone_number,
           p.email, p.birthday, g.name
    FROM phonebook p
    LEFT JOIN groups g ON p.group_id = g.id
    LEFT JOIN phones ph ON p.contact_id = ph.contact_id
    WHERE p.first_name ILIKE '%' || pattern || '%'
       OR p.phone_number LIKE '%' || pattern || '%'
       OR p.email ILIKE '%' || pattern || '%'
       OR ph.phone LIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- Paginated query (carried forward from Practice 8, extended with new fields)
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(contact_id INT, first_name VARCHAR, phone_number VARCHAR,
              email VARCHAR, birthday DATE, group_name VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT p.contact_id, p.first_name, p.phone_number,
           p.email, p.birthday, g.name
    FROM phonebook p
    LEFT JOIN groups g ON p.group_id = g.id
    ORDER BY p.contact_id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION search_contacts(pattern VARCHAR)
RETURNS TABLE(contact_id INT, first_name VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.contact_id, p.first_name, p.phone_number 
    FROM phonebook p
    WHERE p.first_name ILIKE '%' || pattern || '%'
       OR p.phone_number LIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(contact_id INT, first_name VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.contact_id, p.first_name, p.phone_number 
    FROM phonebook p
    ORDER BY p.contact_id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
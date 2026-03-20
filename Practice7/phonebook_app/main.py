from database import create_table
import phonebook_ops as ops

def main():
    create_table()
    
    while True:
        print("\n--- PhoneBook Console App ---")
        print("1. Add contact (Console)")
        print("2. Upload from CSV")
        print("3. Update contact")
        print("4. Search (Query)")
        print("5. Delete contact")
        print("0. Exit")
        
        cmd = input("\nEnter choice: ")
        
        if cmd == '1':
            n, p = input("Name: "), input("Phone: ")
            ops.insert_contact(n, p)
        elif cmd == '2':
            ops.upload_csv('data.csv')
            print("CSV Imported.")
        elif cmd == '4':
            term = input("Search name or phone: ")
            for row in ops.query_contacts(term): print(row)
        elif cmd == '5':
            val = input("Name or Phone to delete: ")
            ops.delete_contact(val)
        elif cmd == '0':
            break

if __name__ == "__main__":
    main()
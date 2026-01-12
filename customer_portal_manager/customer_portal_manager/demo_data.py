import frappe
from frappe.utils import nowdate, add_days

def execute():
    """Generate demo data for Customer Portal Manager."""
    frappe.db.commit()  # Commit any pending changes
    
    # Demo Companies
    demo_companies = [
        {
            "company_name": "Tech Corp International",
            "email": "admin@techcorp.com",
            "tax_id": "TAX-12345",
            "commercial_number": "CR-98765",
            "logo_url": "https://via.placeholder.com/150/4B7BEC/FFFFFF?text=TC"
        },
        {
            "company_name": "Global Solutions Ltd",
            "email": "manager@globalsolutions.com",
            "tax_id": "TAX-67890",
            "commercial_number": "CR-54321",
            "logo_url": "https://via.placeholder.com/150/26C6DA/FFFFFF?text=GS"
        },
        {
            "company_name": "Sunrise Trading Co",
            "email": "info@sunrisetrading.com",
            "tax_id": "TAX-11223",
            "commercial_number": "CR-33445",
            "logo_url": "https://via.placeholder.com/150/FFA726/FFFFFF?text=ST"
        }
    ]

    print("Creating Demo Data...")

    for company in demo_companies:
        # 1. Create Customer
        customer_name = company["company_name"]
        if not frappe.db.exists("Customer", customer_name):
            customer = frappe.new_doc("Customer")
            customer.customer_name = customer_name
            customer.customer_type = "Company"
            customer.customer_group = "All Customer Groups"
            customer.territory = "All Territories"
            customer.save(ignore_permissions=True)
            print(f"Created Customer: {customer_name}")
        else:
            print(f"Customer exists: {customer_name}")

        # 2. Create User
        user_email = company["email"]
        if not frappe.db.exists("User", user_email):
            user = frappe.new_doc("User")
            user.email = user_email
            user.first_name = customer_name.split()[0]
            user.last_name = "Admin"
            user.send_welcome_email = 0
            user.save(ignore_permissions=True)
            print(f"Created User: {user_email}")
        else:
            print(f"User exists: {user_email}")

        # 3. Create Portal Profile
        if not frappe.db.exists("Customer Portal Profile", {"customer": customer_name}):
            profile = frappe.new_doc("Customer Portal Profile")
            profile.customer = customer_name
            profile.company_name = company["company_name"]
            profile.commercial_number = company["commercial_number"]
            profile.tax_id = company["tax_id"]
            # To set an image URL directly, usually we need an existing file or upload it.
            # For simplicity in demo, we might skip the image or assume it's set manually later.
            # But we can try to set the field if it allows URL (unlikely for Attach Image).
            # profile.company_logo = company["logo_url"] 
            profile.save(ignore_permissions=True)
            print(f"Created Profile for: {customer_name}")
        else:
            print(f"Profile exists for: {customer_name}")
        
        # 4. Create Portal User linking them
        full_user_name = f"{customer_name}-{user_email}"
        if not frappe.db.exists("Customer Portal User", {"user": user_email}):
            portal_user = frappe.new_doc("Customer Portal User")
            portal_user.customer = customer_name
            portal_user.user = user_email
            portal_user.start_date = nowdate()
            portal_user.enabled = 1
            
            # Assign some modules
            modules = [
                {"module_name": "Invoices", "module_key": "invoices", "enabled": 1},
                {"module_name": "Orders", "module_key": "orders", "enabled": 1},
                {"module_name": "Support", "module_key": "support", "enabled": 0}
            ]
            for mod in modules:
                portal_user.append("modules", mod)
            
            portal_user.save(ignore_permissions=True)
            print(f"Created Portal User linkage for: {user_email}")
        else:
            print(f"Portal User linkage exists for: {user_email}")

    frappe.db.commit()
    print("Demo Data Creation Completed!")

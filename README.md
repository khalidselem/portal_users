# Customer Portal Manager

A Frappe v15+ application that provides a single-screen management portal for customer users, including company branding and commercial/legal information.

## Features

- **Customer Portal Profiles**: Manage company branding, logos, commercial registration, and tax IDs
- **User Management**: Assign users to customers with specific roles and modules
- **Single-Screen Dashboard**: Card-based responsive layout for managing all customers
- **Role-Based Access**: Customer Portal Admin and Customer Portal User roles
- **Module Management**: Assign specific modules to each portal user

## Installation

```bash
# Get the app
bench get-app customer_portal_manager /path/to/customer_portal_manager

# Install on your site
bench --site your-site.local install-app customer_portal_manager
```

## DocTypes

### Customer Portal Profile
Stores company branding and commercial information:
- Customer link (unique)
- Company name
- Company logo
- Commercial registration number
- Tax ID / VAT number
- Enabled status

### Customer Portal User
Manages individual users under a customer:
- Customer link
- Portal profile link
- User link
- Role assignment
- Start date
- Enabled status
- Assigned modules

### Customer Portal Module (Child Table)
Defines modules available to each user:
- Module name
- Module key
- Enabled status

## Roles

### Customer Portal Admin
- Full access to manage portal profiles
- Can create, edit, and delete users
- Can enable/disable users and profiles
- Access to the management dashboard

### Customer Portal User
- Read-only access to their own customer data
- Can view company branding and information
- Limited to their assigned modules

## API Endpoints

All endpoints are whitelisted and require appropriate permissions:

- `get_portal_profiles()` - Fetch all customer profiles with users
- `get_profile_users(customer)` - Get users for a specific customer
- `toggle_user_status(user_id, enabled)` - Enable/disable a portal user
- `validate_customer_access(customer)` - Validate user access rights

## License

MIT License

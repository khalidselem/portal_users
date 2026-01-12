"""
Portal API - Whitelisted API methods for Customer Portal Manager.

This module provides API endpoints for:
- Fetching customer portal profiles with users and modules
- Enabling/disabling users
- Validating user access permissions
- Role-based and customer-based data filtering
"""

import frappe
from frappe import _


# =============================================================================
# Permission Query Conditions (for hooks.py)
# =============================================================================

def get_profile_permission_query_conditions(user):
    """
    Permission query conditions for Customer Portal Profile.
    Admins see all, portal users see only their customer's profile.
    
    Args:
        user: Current user
        
    Returns:
        SQL condition string or empty string
    """
    if not user:
        user = frappe.session.user
    
    # Admins can see all
    if is_portal_admin(user):
        return ""
    
    # Portal users can only see their customer's profile
    customer = get_user_customer(user)
    if customer:
        return f"`tabCustomer Portal Profile`.customer = '{customer}'"
    
    # No access if not linked to any customer
    return "1=0"


def get_user_permission_query_conditions(user):
    """
    Permission query conditions for Customer Portal User.
    Admins see all, portal users see only their own record.
    
    Args:
        user: Current user
        
    Returns:
        SQL condition string or empty string
    """
    if not user:
        user = frappe.session.user
    
    # Admins can see all
    if is_portal_admin(user):
        return ""
    
    # Portal users can only see their own record
    return f"`tabCustomer Portal User`.user = '{user}'"


def has_profile_permission(doc, user=None, permission_type=None):
    """
    Custom permission check for Customer Portal Profile.
    
    Args:
        doc: Document to check
        user: User to check permission for
        permission_type: Type of permission (read, write, etc.)
        
    Returns:
        Boolean indicating if user has permission
    """
    if not user:
        user = frappe.session.user
    
    # Admins have full access
    if is_portal_admin(user):
        return True
    
    # Portal users can only read their own customer's profile
    if permission_type == "read":
        customer = get_user_customer(user)
        return doc.customer == customer
    
    # No write access for non-admins
    return False


def has_user_permission(doc, user=None, permission_type=None):
    """
    Custom permission check for Customer Portal User.
    
    Args:
        doc: Document to check
        user: User to check permission for
        permission_type: Type of permission (read, write, etc.)
        
    Returns:
        Boolean indicating if user has permission
    """
    if not user:
        user = frappe.session.user
    
    # Admins have full access
    if is_portal_admin(user):
        return True
    
    # Portal users can only read their own record
    if permission_type == "read":
        return doc.user == user
    
    # No write access for non-admins
    return False


# =============================================================================
# Helper Functions
# =============================================================================

def is_portal_admin(user=None):
    """
    Check if user has Customer Portal Admin role.
    
    Args:
        user: User to check (defaults to current user)
        
    Returns:
        Boolean
    """
    if not user:
        user = frappe.session.user
    
    if user == "Administrator":
        return True
    
    roles = frappe.get_roles(user)
    return "Customer Portal Admin" in roles


def is_portal_user(user=None):
    """
    Check if user has Customer Portal User role.
    
    Args:
        user: User to check (defaults to current user)
        
    Returns:
        Boolean
    """
    if not user:
        user = frappe.session.user
    
    roles = frappe.get_roles(user)
    return "Customer Portal User" in roles


def get_user_customer(user=None):
    """
    Get the customer linked to a portal user.
    
    Args:
        user: User to check (defaults to current user)
        
    Returns:
        Customer name or None
    """
    if not user:
        user = frappe.session.user
    
    return frappe.db.get_value(
        "Customer Portal User",
        {"user": user, "enabled": 1},
        "customer"
    )


def validate_customer_access(customer, user=None):
    """
    Validate that a user has access to a specific customer.
    
    Args:
        customer: Customer name to check access for
        user: User to check (defaults to current user)
        
    Returns:
        Boolean indicating if user has access
        
    Raises:
        frappe.PermissionError if access denied
    """
    if not user:
        user = frappe.session.user
    
    # Admins have access to all customers
    if is_portal_admin(user):
        return True
    
    # Portal users can only access their own customer
    user_customer = get_user_customer(user)
    if user_customer != customer:
        frappe.throw(
            _("You do not have permission to access this customer's data"),
            frappe.PermissionError
        )
    
    return True


# =============================================================================
# Whitelisted API Methods
# =============================================================================

@frappe.whitelist()
def get_portal_profiles(filters=None):
    """
    Fetch all customer portal profiles with their users and modules.
    Respects role-based permissions.
    
    Args:
        filters: Optional dict of filters
        
    Returns:
        List of profiles with nested users and modules
    """
    user = frappe.session.user
    
    # Build base query
    profile_filters = {}
    
    # Apply permission filtering
    if not is_portal_admin(user):
        customer = get_user_customer(user)
        if not customer:
            return []
        profile_filters["customer"] = customer
    
    # Apply additional filters if provided
    if filters:
        if isinstance(filters, str):
            filters = frappe.parse_json(filters)
        profile_filters.update(filters)
    
    # Fetch profiles
    profiles = frappe.get_all(
        "Customer Portal Profile",
        filters=profile_filters,
        fields=[
            "name", "customer", "company_name", "company_logo",
            "commercial_number", "tax_id", "enabled"
        ],
        order_by="company_name asc"
    )
    
    # Enrich with user counts and user details
    for profile in profiles:
        # Get user count
        profile["user_count"] = frappe.db.count(
            "Customer Portal User",
            {"portal_profile": profile["name"]}
        )
        profile["active_user_count"] = frappe.db.count(
            "Customer Portal User",
            {"portal_profile": profile["name"], "enabled": 1}
        )
        
        # Get users for this profile
        profile["users"] = get_profile_users(profile["customer"])
    
    return profiles


@frappe.whitelist()
def get_profile_users(customer):
    """
    Get all users for a specific customer.
    
    Args:
        customer: Customer name
        
    Returns:
        List of user dictionaries with modules
    """
    # Validate access
    validate_customer_access(customer)
    
    # Fetch users
    users = frappe.get_all(
        "Customer Portal User",
        filters={"customer": customer},
        fields=[
            "name", "user", "portal_profile", "role",
            "start_date", "enabled"
        ],
        order_by="enabled desc, user asc"
    )
    
    # Enrich with user details and modules
    for user_record in users:
        # Get user full name and email
        user_doc = frappe.get_doc("User", user_record["user"])
        user_record["full_name"] = user_doc.full_name
        user_record["user_email"] = user_doc.email
        user_record["user_image"] = user_doc.user_image
        
        # Get role name
        if user_record["role"]:
            user_record["role_name"] = user_record["role"]
        else:
            user_record["role_name"] = ""
        
        # Get modules
        user_record["modules"] = get_user_modules(user_record["name"])
    
    return users


@frappe.whitelist()
def get_user_modules(portal_user_name):
    """
    Get modules assigned to a specific portal user.
    
    Args:
        portal_user_name: Name of Customer Portal User document
        
    Returns:
        List of module dictionaries
    """
    # Get the portal user document
    portal_user = frappe.get_doc("Customer Portal User", portal_user_name)
    
    # Validate access (user can only see their own modules)
    if not is_portal_admin():
        if portal_user.user != frappe.session.user:
            frappe.throw(
                _("You do not have permission to view this user's modules"),
                frappe.PermissionError
            )
    
    return [
        {
            "module_name": m.module_name,
            "module_key": m.module_key,
            "enabled": m.enabled
        }
        for m in portal_user.modules
    ]


@frappe.whitelist()
def toggle_user_status(portal_user_name, enabled):
    """
    Enable or disable a portal user.
    
    Args:
        portal_user_name: Name of Customer Portal User document
        enabled: Boolean or 1/0 for enabled status
        
    Returns:
        Dict with success status and updated document
    """
    # Only admins can toggle user status
    if not is_portal_admin():
        frappe.throw(
            _("Only Customer Portal Admins can enable/disable users"),
            frappe.PermissionError
        )
    
    # Convert to int if string
    if isinstance(enabled, str):
        enabled = int(enabled)
    
    # Update the user
    doc = frappe.get_doc("Customer Portal User", portal_user_name)
    doc.enabled = enabled
    doc.save()
    
    return {
        "success": True,
        "message": _("User {0} has been {1}").format(
            doc.user,
            _("enabled") if enabled else _("disabled")
        ),
        "user": doc.as_dict()
    }


@frappe.whitelist()
def toggle_profile_status(profile_name, enabled):
    """
    Enable or disable a customer portal profile.
    
    Args:
        profile_name: Name of Customer Portal Profile document
        enabled: Boolean or 1/0 for enabled status
        
    Returns:
        Dict with success status and updated document
    """
    # Only admins can toggle profile status
    if not is_portal_admin():
        frappe.throw(
            _("Only Customer Portal Admins can enable/disable profiles"),
            frappe.PermissionError
        )
    
    # Convert to int if string
    if isinstance(enabled, str):
        enabled = int(enabled)
    
    # Update the profile
    doc = frappe.get_doc("Customer Portal Profile", profile_name)
    doc.enabled = enabled
    doc.save()
    
    return {
        "success": True,
        "message": _("Profile {0} has been {1}").format(
            doc.company_name,
            _("enabled") if enabled else _("disabled")
        ),
        "profile": doc.as_dict()
    }


@frappe.whitelist()
def create_portal_user(customer, user, role=None, modules=None):
    """
    Create a new portal user for a customer.
    
    Args:
        customer: Customer name
        user: User email/name
        role: Optional role name
        modules: Optional list of module dicts
        
    Returns:
        Dict with success status and created document
    """
    # Only admins can create users
    if not is_portal_admin():
        frappe.throw(
            _("Only Customer Portal Admins can create users"),
            frappe.PermissionError
        )
    
    # Check if profile exists for customer
    profile = frappe.db.get_value(
        "Customer Portal Profile",
        {"customer": customer},
        "name"
    )
    
    # Create the portal user
    doc = frappe.new_doc("Customer Portal User")
    doc.customer = customer
    doc.portal_profile = profile
    doc.user = user
    doc.role = role
    doc.enabled = 1
    
    # Add modules if provided
    if modules:
        if isinstance(modules, str):
            modules = frappe.parse_json(modules)
        for module in modules:
            doc.append("modules", module)
    
    doc.insert()
    
    return {
        "success": True,
        "message": _("Portal user created successfully"),
        "user": doc.as_dict()
    }


@frappe.whitelist()
def update_portal_user(portal_user_name, updates):
    """
    Update a portal user.
    
    Args:
        portal_user_name: Name of Customer Portal User document
        updates: Dict of field updates
        
    Returns:
        Dict with success status and updated document
    """
    # Only admins can update users
    if not is_portal_admin():
        frappe.throw(
            _("Only Customer Portal Admins can update users"),
            frappe.PermissionError
        )
    
    if isinstance(updates, str):
        updates = frappe.parse_json(updates)
    
    doc = frappe.get_doc("Customer Portal User", portal_user_name)
    
    # Update fields
    for field, value in updates.items():
        if field == "modules":
            # Handle modules separately
            doc.modules = []
            for module in value:
                doc.append("modules", module)
        elif hasattr(doc, field):
            setattr(doc, field, value)
    
    doc.save()
    
    return {
        "success": True,
        "message": _("Portal user updated successfully"),
        "user": doc.as_dict()
    }


@frappe.whitelist()
def get_available_modules():
    """
    Get list of available modules that can be assigned to users.
    This returns a predefined list of modules - customize as needed.
    
    Returns:
        List of module dictionaries
    """
    # Define available modules - customize this list
    return [
        {"module_name": "Dashboard", "module_key": "dashboard"},
        {"module_name": "Orders", "module_key": "orders"},
        {"module_name": "Invoices", "module_key": "invoices"},
        {"module_name": "Payments", "module_key": "payments"},
        {"module_name": "Products", "module_key": "products"},
        {"module_name": "Reports", "module_key": "reports"},
        {"module_name": "Support", "module_key": "support"},
        {"module_name": "Settings", "module_key": "settings"},
    ]


@frappe.whitelist()
def get_dashboard_stats():
    """
    Get dashboard statistics for the portal management page.
    
    Returns:
        Dict with various counts and statistics
    """
    if not is_portal_admin():
        # Return limited stats for non-admins
        customer = get_user_customer()
        if customer:
            return {
                "total_profiles": 1,
                "active_profiles": frappe.db.count(
                    "Customer Portal Profile",
                    {"customer": customer, "enabled": 1}
                ),
                "total_users": frappe.db.count(
                    "Customer Portal User",
                    {"customer": customer}
                ),
                "active_users": frappe.db.count(
                    "Customer Portal User",
                    {"customer": customer, "enabled": 1}
                )
            }
        return {}
    
    # Full stats for admins
    return {
        "total_profiles": frappe.db.count("Customer Portal Profile"),
        "active_profiles": frappe.db.count(
            "Customer Portal Profile",
            {"enabled": 1}
        ),
        "disabled_profiles": frappe.db.count(
            "Customer Portal Profile",
            {"enabled": 0}
        ),
        "total_users": frappe.db.count("Customer Portal User"),
        "active_users": frappe.db.count(
            "Customer Portal User",
            {"enabled": 1}
        ),
        "disabled_users": frappe.db.count(
            "Customer Portal User",
            {"enabled": 0}
        )
    }

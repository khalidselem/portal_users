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
from customer_portal_manager.customer_portal_manager.demo_data import execute as generate_demo_data_script

# ... existing code ...

@frappe.whitelist()
def generate_demo_data():
    """Generate demo data for the app."""
    if not is_portal_admin():
        frappe.throw(_("Only Admins can generate demo data"), frappe.PermissionError)
    
    generate_demo_data_script()
    return {"message": _("Demo data generated successfully")}

# =============================================================================
# Permission Query Conditions (for hooks.py)
# =============================================================================

def get_profile_permission_query_conditions(user):
    """
    Permission query conditions for Customer Portal Profile.
    Admins see all, portal users see only their customer's profile.
    """
    if not user:
        user = frappe.session.user
    
    if is_portal_admin(user):
        return ""
    
    customer = get_user_customer(user)
    if customer:
        return f"`tabCustomer Portal Profile`.customer = '{customer}'"
    
    return "1=0"


def get_user_permission_query_conditions(user):
    """
    Permission query conditions for Customer Portal User.
    Admins see all, portal users see only their own record.
    """
    if not user:
        user = frappe.session.user
    
    if is_portal_admin(user):
        return ""
    
    return f"`tabCustomer Portal User`.user = '{user}'"


def has_profile_permission(doc, user=None, permission_type=None):
    """Custom permission check for Customer Portal Profile."""
    if not user:
        user = frappe.session.user
    
    if is_portal_admin(user):
        return True
    
    if permission_type == "read":
        customer = get_user_customer(user)
        return doc.customer == customer
    
    return False


def has_user_permission(doc, user=None, permission_type=None):
    """Custom permission check for Customer Portal User."""
    if not user:
        user = frappe.session.user
    
    if is_portal_admin(user):
        return True
    
    if permission_type == "read":
        return doc.user == user
    
    return False


# =============================================================================
# Helper Functions
# =============================================================================

def is_portal_admin(user=None):
    """Check if user has Customer Portal Admin role."""
    if not user:
        user = frappe.session.user
    
    if user == "Administrator":
        return True
    
    roles = frappe.get_roles(user)
    return "Customer Portal Admin" in roles


def is_portal_user(user=None):
    """Check if user has Customer Portal User role."""
    if not user:
        user = frappe.session.user
    
    roles = frappe.get_roles(user)
    return "Customer Portal User" in roles


def get_user_customer(user=None):
    """Get the customer linked to a portal user."""
    if not user:
        user = frappe.session.user
    
    return frappe.db.get_value(
        "Customer Portal User",
        {"user": user, "enabled": 1},
        "customer"
    )


def validate_customer_access(customer, user=None):
    """Validate that a user has access to a specific customer."""
    if not user:
        user = frappe.session.user
    
    if is_portal_admin(user):
        return True
    
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
    """Fetch all customer portal profiles with their users and modules."""
    user = frappe.session.user
    
    profile_filters = {}
    
    if not is_portal_admin(user):
        customer = get_user_customer(user)
        if not customer:
            return []
        profile_filters["customer"] = customer
    
    if filters:
        if isinstance(filters, str):
            filters = frappe.parse_json(filters)
        profile_filters.update(filters)
    
    profiles = frappe.get_all(
        "Customer Portal Profile",
        filters=profile_filters,
        fields=[
            "name", "customer", "company_name", "company_logo",
            "commercial_number", "tax_id", "enabled"
        ],
        order_by="company_name asc"
    )
    
    for profile in profiles:
        profile["user_count"] = frappe.db.count(
            "Customer Portal User",
            {"portal_profile": profile["name"]}
        )
        profile["active_user_count"] = frappe.db.count(
            "Customer Portal User",
            {"portal_profile": profile["name"], "enabled": 1}
        )
        profile["users"] = get_profile_users(profile["customer"])
    
    return profiles


@frappe.whitelist()
def get_profile_users(customer):
    """Get all users for a specific customer."""
    validate_customer_access(customer)
    
    users = frappe.get_all(
        "Customer Portal User",
        filters={"customer": customer},
        fields=[
            "name", "user", "portal_profile", "role",
            "start_date", "enabled"
        ],
        order_by="enabled desc, user asc"
    )
    
    for user_record in users:
        user_doc = frappe.get_doc("User", user_record["user"])
        user_record["full_name"] = user_doc.full_name
        user_record["user_email"] = user_doc.email
        user_record["user_image"] = user_doc.user_image
        user_record["role_name"] = user_record["role"] or ""
        user_record["modules"] = get_user_modules(user_record["name"])
    
    return users


@frappe.whitelist()
def get_user_modules(portal_user_name):
    """Get modules assigned to a specific portal user."""
    portal_user = frappe.get_doc("Customer Portal User", portal_user_name)
    
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
    """Enable or disable a portal user."""
    if not is_portal_admin():
        frappe.throw(
            _("Only Customer Portal Admins can enable/disable users"),
            frappe.PermissionError
        )
    
    if isinstance(enabled, str):
        enabled = int(enabled)
    
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
    """Enable or disable a customer portal profile."""
    if not is_portal_admin():
        frappe.throw(
            _("Only Customer Portal Admins can enable/disable profiles"),
            frappe.PermissionError
        )
    
    if isinstance(enabled, str):
        enabled = int(enabled)
    
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
    """Create a new portal user for a customer."""
    if not is_portal_admin():
        frappe.throw(
            _("Only Customer Portal Admins can create users"),
            frappe.PermissionError
        )
    
    profile = frappe.db.get_value(
        "Customer Portal Profile",
        {"customer": customer},
        "name"
    )
    
    doc = frappe.new_doc("Customer Portal User")
    doc.customer = customer
    doc.portal_profile = profile
    doc.user = user
    doc.role = role
    doc.enabled = 1
    
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
def get_available_modules():
    """Get list of available modules that can be assigned to users."""
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
    """Get dashboard statistics for the portal management page."""
    if not is_portal_admin():
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

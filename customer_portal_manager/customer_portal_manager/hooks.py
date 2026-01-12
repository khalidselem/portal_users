"""
Hooks configuration for Customer Portal Manager.
Defines app metadata, permissions, and custom configurations.
"""

app_name = "customer_portal_manager"
app_title = "Customer Portal Manager"
app_publisher = "Your Company"
app_description = "Single-screen management portal for customer users with company branding"
app_email = "info@yourcompany.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

# App includes
# -------------

# CSS and JS to include in desk
app_include_css = "/assets/customer_portal_manager/css/customer_portal.css"
app_include_js = "/assets/customer_portal_manager/js/customer_portal.js"

# Fixtures - Export roles and custom fields
# ------------------------------------------
fixtures = [
    {
        "doctype": "Role",
        "filters": [
            ["name", "in", ["Customer Portal Admin", "Customer Portal User"]]
        ]
    }
]

# Document Events
# ----------------
doc_events = {
    "Customer Portal User": {
        "validate": "customer_portal_manager.customer_portal_manager.doctype.customer_portal_user.customer_portal_user.validate_portal_user",
        "on_update": "customer_portal_manager.customer_portal_manager.doctype.customer_portal_user.customer_portal_user.on_update_portal_user"
    },
    "Customer Portal Profile": {
        "validate": "customer_portal_manager.customer_portal_manager.doctype.customer_portal_profile.customer_portal_profile.validate_portal_profile"
    }
}

# Permissions
# -----------
# Define custom permission rules here if needed

permission_query_conditions = {
    "Customer Portal Profile": "customer_portal_manager.api.portal_api.get_profile_permission_query_conditions",
    "Customer Portal User": "customer_portal_manager.api.portal_api.get_user_permission_query_conditions"
}

has_permission = {
    "Customer Portal Profile": "customer_portal_manager.api.portal_api.has_profile_permission",
    "Customer Portal User": "customer_portal_manager.api.portal_api.has_user_permission"
}

# Scheduled Tasks
# ----------------
# scheduler_events = {}

# Override Methods
# -----------------
# override_whitelisted_methods = {}

# Jinja Methods
# --------------
# jinja = {}

# Installation
# -------------
# before_install = "customer_portal_manager.install.before_install"
# after_install = "customer_portal_manager.install.after_install"

# Desk Notifications
# -------------------
# notification_config = "customer_portal_manager.notifications.get_notification_config"

# Website Route Rules
# --------------------
# website_route_rules = []

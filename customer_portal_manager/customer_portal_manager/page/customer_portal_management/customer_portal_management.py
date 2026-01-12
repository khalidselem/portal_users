"""Customer Portal Management Page - Server-side controller"""

import frappe


def get_context(context):
    """Get context for the page."""
    if not frappe.has_permission("Customer Portal Profile", "read"):
        frappe.throw(
            frappe._("You don't have permission to access this page"),
            frappe.PermissionError
        )
    
    context.no_cache = 1
    return context

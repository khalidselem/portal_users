"""
Customer Portal Management Page - Server-side controller
Handles server-side logic for the page if needed.
"""

import frappe


def get_context(context):
    """
    Get context for the page.
    This function can be used to pass server-side data to the page.
    """
    # Check permission
    if not frappe.has_permission("Customer Portal Profile", "read"):
        frappe.throw(
            frappe._("You don't have permission to access this page"),
            frappe.PermissionError
        )
    
    context.no_cache = 1
    return context

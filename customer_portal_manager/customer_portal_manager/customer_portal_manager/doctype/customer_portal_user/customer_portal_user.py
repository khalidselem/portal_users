"""
Customer Portal User - DocType Controller
Manages individual users under a customer portal profile.
"""

import frappe
from frappe import _
from frappe.model.document import Document


class CustomerPortalUser(Document):
    """
    Controller for Customer Portal User.
    
    This DocType manages individual users under a customer:
    - Customer and portal profile links
    - User account link
    - Role assignment
    - Start date and enabled status
    - Assigned modules (child table)
    """
    
    def validate(self):
        """Validate user data before saving."""
        self.validate_user_unique()
        self.auto_link_portal_profile()
        self.validate_portal_profile_enabled()
    
    def validate_user_unique(self):
        """Ensure a user can only be linked to one customer."""
        if self.is_new():
            existing = frappe.db.get_value(
                "Customer Portal User",
                {"user": self.user, "name": ["!=", self.name]},
                "name"
            )
            if existing:
                frappe.throw(
                    _("User {0} is already linked to another customer portal").format(
                        self.user
                    )
                )
    
    def auto_link_portal_profile(self):
        """Automatically link to the customer's portal profile if it exists."""
        if not self.portal_profile and self.customer:
            profile = frappe.db.get_value(
                "Customer Portal Profile",
                {"customer": self.customer},
                "name"
            )
            if profile:
                self.portal_profile = profile
    
    def validate_portal_profile_enabled(self):
        """Warn if the portal profile is disabled."""
        if self.portal_profile:
            profile_enabled = frappe.db.get_value(
                "Customer Portal Profile",
                self.portal_profile,
                "enabled"
            )
            if not profile_enabled and self.enabled:
                frappe.msgprint(
                    _("The portal profile for this customer is disabled. "
                      "This user will not have access until the profile is enabled."),
                    indicator="orange",
                    alert=True
                )
    
    def on_update(self):
        """Actions after user is updated."""
        self.sync_user_roles()
    
    def sync_user_roles(self):
        """
        Sync the assigned role to the actual Frappe user.
        Adds or removes the Customer Portal User role.
        """
        user_doc = frappe.get_doc("User", self.user)
        portal_user_role = "Customer Portal User"
        
        has_role = any(r.role == portal_user_role for r in user_doc.roles)
        
        if self.enabled and not has_role:
            # Add the portal user role
            user_doc.append("roles", {"role": portal_user_role})
            user_doc.save(ignore_permissions=True)
            frappe.msgprint(
                _("Added '{0}' role to user {1}").format(portal_user_role, self.user),
                indicator="green",
                alert=True
            )
        elif not self.enabled and has_role:
            # Check if user has other portal entries that are enabled
            other_enabled = frappe.db.count(
                "Customer Portal User",
                {"user": self.user, "enabled": 1, "name": ["!=", self.name]}
            )
            if not other_enabled:
                # Remove the role
                user_doc.roles = [r for r in user_doc.roles if r.role != portal_user_role]
                user_doc.save(ignore_permissions=True)
                frappe.msgprint(
                    _("Removed '{0}' role from user {1}").format(portal_user_role, self.user),
                    indicator="orange",
                    alert=True
                )
    
    def get_enabled_modules(self):
        """
        Get list of enabled module keys for this user.
        
        Returns:
            List of module_key strings
        """
        return [m.module_key for m in self.modules if m.enabled]


def validate_portal_user(doc, method):
    """
    Document event hook for validation.
    Called from hooks.py doc_events.
    """
    pass  # Validation is handled in the class


def on_update_portal_user(doc, method):
    """
    Document event hook for on_update.
    Called from hooks.py doc_events.
    """
    pass  # On update is handled in the class


def get_portal_user_for_user(user):
    """
    Get the Customer Portal User record for a Frappe user.
    
    Args:
        user: User email/name
        
    Returns:
        Customer Portal User document or None
    """
    portal_user_name = frappe.db.get_value(
        "Customer Portal User",
        {"user": user, "enabled": 1},
        "name"
    )
    
    if portal_user_name:
        return frappe.get_doc("Customer Portal User", portal_user_name)
    
    return None


def get_customer_for_user(user):
    """
    Get the customer linked to a user.
    
    Args:
        user: User email/name
        
    Returns:
        Customer name or None
    """
    return frappe.db.get_value(
        "Customer Portal User",
        {"user": user, "enabled": 1},
        "customer"
    )

"""
Customer Portal User - DocType Controller
"""

import frappe
from frappe import _
from frappe.model.document import Document


class CustomerPortalUser(Document):
    """Controller for Customer Portal User."""
    
    def validate(self):
        """Validate user data before saving."""
        self.validate_user_unique()
        self.auto_link_portal_profile()
    
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
    
    def on_update(self):
        """Actions after user is updated."""
        self.sync_user_roles()
    
    def sync_user_roles(self):
        """Sync the assigned role to the actual Frappe user."""
        user_doc = frappe.get_doc("User", self.user)
        portal_user_role = "Customer Portal User"
        
        has_role = any(r.role == portal_user_role for r in user_doc.roles)
        
        if self.enabled and not has_role:
            user_doc.append("roles", {"role": portal_user_role})
            user_doc.save(ignore_permissions=True)
        elif not self.enabled and has_role:
            other_enabled = frappe.db.count(
                "Customer Portal User",
                {"user": self.user, "enabled": 1, "name": ["!=", self.name]}
            )
            if not other_enabled:
                user_doc.roles = [r for r in user_doc.roles if r.role != portal_user_role]
                user_doc.save(ignore_permissions=True)


def validate_portal_user(doc, method):
    """Document event hook for validation."""
    pass


def on_update_portal_user(doc, method):
    """Document event hook for on_update."""
    pass

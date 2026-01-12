"""
Customer Portal Profile - DocType Controller
Manages company branding and commercial information for customers.
"""

import frappe
from frappe import _
from frappe.model.document import Document


class CustomerPortalProfile(Document):
    """
    Controller for Customer Portal Profile.
    
    This DocType stores company branding and commercial information:
    - Customer link (unique per customer)
    - Company name and logo
    - Commercial registration number
    - Tax ID / VAT number
    - Enabled status
    """
    
    def validate(self):
        """Validate profile data before saving."""
        self.validate_customer_unique()
        self.set_company_name_from_customer()
    
    def validate_customer_unique(self):
        """Ensure only one profile exists per customer."""
        if self.is_new():
            existing = frappe.db.exists(
                "Customer Portal Profile",
                {"customer": self.customer}
            )
            if existing:
                frappe.throw(
                    _("A portal profile already exists for customer {0}").format(
                        self.customer
                    )
                )
    
    def set_company_name_from_customer(self):
        """Auto-fill company name from customer if not provided."""
        if not self.company_name and self.customer:
            customer_doc = frappe.get_doc("Customer", self.customer)
            self.company_name = customer_doc.customer_name
    
    def on_update(self):
        """Actions after profile is updated."""
        self.update_linked_users_status()
    
    def update_linked_users_status(self):
        """
        If profile is disabled, disable all linked users.
        This ensures consistency between profile and user status.
        """
        if not self.enabled:
            frappe.db.sql("""
                UPDATE `tabCustomer Portal User`
                SET enabled = 0
                WHERE portal_profile = %s AND enabled = 1
            """, (self.name,))
            frappe.msgprint(
                _("All users linked to this profile have been disabled."),
                indicator="orange",
                alert=True
            )


def validate_portal_profile(doc, method):
    """
    Document event hook for validation.
    Called from hooks.py doc_events.
    """
    pass  # Validation is handled in the class


def get_profile_for_customer(customer):
    """
    Utility function to get the portal profile for a customer.
    
    Args:
        customer: Customer name/ID
        
    Returns:
        Customer Portal Profile document or None
    """
    profile_name = frappe.db.get_value(
        "Customer Portal Profile",
        {"customer": customer},
        "name"
    )
    
    if profile_name:
        return frappe.get_doc("Customer Portal Profile", profile_name)
    
    return None


def get_user_count(profile_name):
    """
    Get the count of users linked to a profile.
    
    Args:
        profile_name: Name of the Customer Portal Profile
        
    Returns:
        Integer count of users
    """
    return frappe.db.count(
        "Customer Portal User",
        {"portal_profile": profile_name}
    )


def get_active_user_count(profile_name):
    """
    Get the count of enabled users linked to a profile.
    
    Args:
        profile_name: Name of the Customer Portal Profile
        
    Returns:
        Integer count of enabled users
    """
    return frappe.db.count(
        "Customer Portal User",
        {"portal_profile": profile_name, "enabled": 1}
    )

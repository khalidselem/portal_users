"""
Customer Portal Profile - DocType Controller
"""

import frappe
from frappe import _
from frappe.model.document import Document


class CustomerPortalProfile(Document):
    """Controller for Customer Portal Profile."""
    
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
        if not self.enabled:
            frappe.db.sql("""
                UPDATE `tabCustomer Portal User`
                SET enabled = 0
                WHERE portal_profile = %s AND enabled = 1
            """, (self.name,))


def validate_portal_profile(doc, method):
    """Document event hook for validation."""
    pass

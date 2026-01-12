"""
Customer Portal Module - Child Table DocType Controller
"""

import frappe
from frappe.model.document import Document


class CustomerPortalModule(Document):
    """Child table for managing modules assigned to a Customer Portal User."""
    
    def validate(self):
        """Validate module data before saving."""
        if self.module_key:
            self.module_key = self.module_key.lower().replace(" ", "_")

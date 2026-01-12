"""
Customer Portal Module - Child Table DocType Controller
Defines the modules available to each portal user.
"""

import frappe
from frappe.model.document import Document


class CustomerPortalModule(Document):
    """
    Child table for managing modules assigned to a Customer Portal User.
    
    Fields:
        - module_name: Display name of the module
        - module_key: Unique identifier for the module
        - enabled: Whether the module is enabled for the user
    """
    
    def validate(self):
        """Validate module data before saving."""
        self.validate_module_key()
    
    def validate_module_key(self):
        """Ensure module_key is lowercase and without spaces."""
        if self.module_key:
            self.module_key = self.module_key.lower().replace(" ", "_")

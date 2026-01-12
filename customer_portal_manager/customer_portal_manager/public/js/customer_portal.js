/**
 * Customer Portal Manager - Main JavaScript
 * This file is loaded globally via hooks.py app_include_js
 */

// Namespace for Customer Portal Manager
frappe.customer_portal = frappe.customer_portal || {};

/**
 * Check if current user is a portal admin
 */
frappe.customer_portal.is_admin = function () {
    return frappe.user_roles.includes('Customer Portal Admin') ||
        frappe.user_roles.includes('System Manager');
};

/**
 * Check if current user is a portal user
 */
frappe.customer_portal.is_portal_user = function () {
    return frappe.user_roles.includes('Customer Portal User');
};

/**
 * Quick navigation to portal management
 */
frappe.customer_portal.go_to_management = function () {
    frappe.set_route('customer-portal-management');
};

/**
 * Format module tags for display
 */
frappe.customer_portal.format_modules = function (modules) {
    if (!modules || modules.length === 0) {
        return '<span class="text-muted">' + __('No modules') + '</span>';
    }

    return modules
        .filter(m => m.enabled)
        .map(m => `<span class="badge badge-info">${m.module_name}</span>`)
        .join(' ');
};

// Add keyboard shortcut for quick access
$(document).on('keydown', function (e) {
    // Ctrl/Cmd + Shift + P for Portal Management
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
        if (frappe.customer_portal.is_admin()) {
            frappe.customer_portal.go_to_management();
            e.preventDefault();
        }
    }
});

console.log('Customer Portal Manager loaded');

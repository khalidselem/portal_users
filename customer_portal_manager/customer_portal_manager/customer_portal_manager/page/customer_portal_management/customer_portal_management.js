/**
 * Customer Portal Management - Desk Page
 * 
 * This page provides a single-screen management portal for customer users.
 * Features:
 * - Grid-based responsive card layout
 * - Customer cards with company info and user sub-cards
 * - Actions: Edit Profile, Add/Edit User, Enable/Disable
 */

frappe.pages['customer-portal-management'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Customer Portal Management'),
        single_column: true
    });

    // Initialize the page
    new CustomerPortalManagement(page);
};

/**
 * Main class for Customer Portal Management page
 */
class CustomerPortalManagement {
    constructor(page) {
        this.page = page;
        this.wrapper = $(page.body);
        this.profiles = [];
        this.stats = {};

        this.init();
    }

    /**
     * Initialize the page
     */
    init() {
        this.setup_page_actions();
        this.render_layout();
        this.load_data();
    }

    /**
     * Setup page action buttons
     */
    setup_page_actions() {
        // Primary action - Add Profile
        this.page.set_primary_action(
            __('New Profile'),
            () => this.create_new_profile(),
            'fa fa-plus'
        );

        // Secondary action - Refresh
        this.page.set_secondary_action(
            __('Refresh'),
            () => this.load_data(),
            'fa fa-refresh'
        );

        // Menu items
        this.page.add_menu_item(__('View All Profiles'), () => {
            frappe.set_route('List', 'Customer Portal Profile');
        });

        this.page.add_menu_item(__('View All Users'), () => {
            frappe.set_route('List', 'Customer Portal User');
        });
    }

    /**
     * Render the main layout structure
     */
    render_layout() {
        this.wrapper.html(`
            <div class="customer-portal-page">
                <!-- Statistics Cards -->
                <div class="stats-container mb-4">
                    <div class="row stats-row">
                        <div class="col-md-3 col-sm-6">
                            <div class="stat-card total-profiles">
                                <div class="stat-icon">
                                    <i class="fa fa-building"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-value" id="stat-total-profiles">0</div>
                                    <div class="stat-label">${__('Total Profiles')}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 col-sm-6">
                            <div class="stat-card active-profiles">
                                <div class="stat-icon">
                                    <i class="fa fa-check-circle"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-value" id="stat-active-profiles">0</div>
                                    <div class="stat-label">${__('Active Profiles')}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 col-sm-6">
                            <div class="stat-card total-users">
                                <div class="stat-icon">
                                    <i class="fa fa-users"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-value" id="stat-total-users">0</div>
                                    <div class="stat-label">${__('Total Users')}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 col-sm-6">
                            <div class="stat-card active-users">
                                <div class="stat-icon">
                                    <i class="fa fa-user-check"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-value" id="stat-active-users">0</div>
                                    <div class="stat-label">${__('Active Users')}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Search and Filter -->
                <div class="filter-container mb-4">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="input-group">
                                <span class="input-group-prepend">
                                    <span class="input-group-text">
                                        <i class="fa fa-search"></i>
                                    </span>
                                </span>
                                <input type="text" class="form-control" id="search-input" 
                                    placeholder="${__('Search customers...')}">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <select class="form-control" id="status-filter">
                                <option value="">${__('All Status')}</option>
                                <option value="1">${__('Active')}</option>
                                <option value="0">${__('Disabled')}</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Customer Cards Grid -->
                <div class="cards-container">
                    <div class="row" id="profiles-grid">
                        <!-- Cards will be rendered here -->
                    </div>
                </div>
                
                <!-- Loading Indicator -->
                <div class="loading-indicator text-center py-5" style="display: none;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="sr-only">${__('Loading...')}</span>
                    </div>
                    <p class="mt-2 text-muted">${__('Loading customer profiles...')}</p>
                </div>
                
                <!-- Empty State -->
                <div class="empty-state text-center py-5" style="display: none;">
                    <i class="fa fa-inbox fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">${__('No customer profiles found')}</h4>
                    <p class="text-muted">${__('Create a new profile to get started.')}</p>
                    <button class="btn btn-primary" onclick="cur_page.create_new_profile()">
                        <i class="fa fa-plus"></i> ${__('Create Profile')}
                    </button>
                </div>
            </div>
        `);

        // Bind search and filter events
        this.bind_events();

        // Store reference for global access
        window.cur_page = this;
    }

    /**
     * Bind event listeners
     */
    bind_events() {
        const self = this;

        // Search input
        this.wrapper.find('#search-input').on('keyup', frappe.utils.debounce(function () {
            self.filter_profiles();
        }, 300));

        // Status filter
        this.wrapper.find('#status-filter').on('change', function () {
            self.filter_profiles();
        });
    }

    /**
     * Load data from the server
     */
    load_data() {
        this.show_loading(true);

        // Load stats and profiles in parallel
        Promise.all([
            this.fetch_stats(),
            this.fetch_profiles()
        ]).then(() => {
            this.show_loading(false);
            this.render_profiles();
        }).catch(err => {
            this.show_loading(false);
            frappe.msgprint({
                title: __('Error'),
                indicator: 'red',
                message: __('Failed to load data: ') + err.message
            });
        });
    }

    /**
     * Fetch dashboard statistics
     */
    fetch_stats() {
        return frappe.call({
            method: 'customer_portal_manager.api.portal_api.get_dashboard_stats',
            async: true
        }).then(r => {
            this.stats = r.message || {};
            this.update_stats_display();
        });
    }

    /**
     * Fetch customer profiles
     */
    fetch_profiles() {
        return frappe.call({
            method: 'customer_portal_manager.api.portal_api.get_portal_profiles',
            async: true
        }).then(r => {
            this.profiles = r.message || [];
        });
    }

    /**
     * Update statistics display
     */
    update_stats_display() {
        $('#stat-total-profiles').text(this.stats.total_profiles || 0);
        $('#stat-active-profiles').text(this.stats.active_profiles || 0);
        $('#stat-total-users').text(this.stats.total_users || 0);
        $('#stat-active-users').text(this.stats.active_users || 0);
    }

    /**
     * Show/hide loading indicator
     */
    show_loading(show) {
        this.wrapper.find('.loading-indicator').toggle(show);
        this.wrapper.find('.cards-container').toggle(!show);
    }

    /**
     * Render all customer profile cards
     */
    render_profiles() {
        const grid = this.wrapper.find('#profiles-grid');
        grid.empty();

        if (this.profiles.length === 0) {
            this.wrapper.find('.empty-state').show();
            this.wrapper.find('.cards-container').hide();
            return;
        }

        this.wrapper.find('.empty-state').hide();
        this.wrapper.find('.cards-container').show();

        this.profiles.forEach(profile => {
            grid.append(this.render_profile_card(profile));
        });

        // Bind card events
        this.bind_card_events();
    }

    /**
     * Render a single profile card
     */
    render_profile_card(profile) {
        const statusClass = profile.enabled ? 'status-active' : 'status-disabled';
        const statusText = profile.enabled ? __('Active') : __('Disabled');
        const logoUrl = profile.company_logo || '/assets/frappe/images/default-avatar.png';

        return `
            <div class="col-xl-4 col-lg-6 col-md-6 mb-4 profile-card-wrapper" 
                 data-profile="${profile.name}" 
                 data-customer="${profile.customer}"
                 data-enabled="${profile.enabled}">
                <div class="profile-card ${!profile.enabled ? 'disabled' : ''}">
                    <!-- Card Header -->
                    <div class="profile-card-header">
                        <div class="profile-logo">
                            <img src="${logoUrl}" alt="${profile.company_name}" 
                                 onerror="this.src='/assets/frappe/images/default-avatar.png'">
                        </div>
                        <div class="profile-info">
                            <h4 class="company-name">${profile.company_name}</h4>
                            <span class="status-badge ${statusClass}">${statusText}</span>
                        </div>
                        <div class="profile-actions dropdown">
                            <button class="btn btn-sm btn-light dropdown-toggle" 
                                    data-toggle="dropdown">
                                <i class="fa fa-ellipsis-v"></i>
                            </button>
                            <div class="dropdown-menu dropdown-menu-right">
                                <a class="dropdown-item edit-profile" href="#" 
                                   data-profile="${profile.name}">
                                    <i class="fa fa-edit"></i> ${__('Edit Profile')}
                                </a>
                                <a class="dropdown-item add-user" href="#" 
                                   data-customer="${profile.customer}">
                                    <i class="fa fa-user-plus"></i> ${__('Add User')}
                                </a>
                                <div class="dropdown-divider"></div>
                                <a class="dropdown-item toggle-profile ${profile.enabled ? 'text-danger' : 'text-success'}" 
                                   href="#" data-profile="${profile.name}" data-enabled="${profile.enabled}">
                                    <i class="fa fa-${profile.enabled ? 'ban' : 'check'}"></i> 
                                    ${profile.enabled ? __('Disable Profile') : __('Enable Profile')}
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Commercial Info -->
                    <div class="profile-commercial-info">
                        <div class="info-row">
                            <span class="info-label">${__('Commercial Reg.')}</span>
                            <span class="info-value">${profile.commercial_number || '-'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">${__('Tax ID')}</span>
                            <span class="info-value">${profile.tax_id || '-'}</span>
                        </div>
                    </div>
                    
                    <!-- User Count -->
                    <div class="profile-user-count">
                        <div class="user-count-badge">
                            <i class="fa fa-users"></i>
                            <span>${profile.user_count || 0} ${__('Users')}</span>
                            <span class="text-muted">(${profile.active_user_count || 0} ${__('active')})</span>
                        </div>
                        <button class="btn btn-sm btn-outline-primary toggle-users" 
                                data-profile="${profile.name}">
                            <i class="fa fa-chevron-down"></i> ${__('Show Users')}
                        </button>
                    </div>
                    
                    <!-- Users Section (Collapsible) -->
                    <div class="profile-users-section" style="display: none;" 
                         id="users-${profile.name.replace(/\s+/g, '-')}">
                        ${this.render_users_list(profile.users || [])}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render users list for a profile
     */
    render_users_list(users) {
        if (!users || users.length === 0) {
            return `
                <div class="no-users text-center py-3 text-muted">
                    <i class="fa fa-user-slash"></i>
                    <p class="mb-0">${__('No users assigned')}</p>
                </div>
            `;
        }

        let html = '<div class="users-list">';

        users.forEach(user => {
            html += this.render_user_card(user);
        });

        html += '</div>';
        return html;
    }

    /**
     * Render a single user card
     */
    render_user_card(user) {
        const statusClass = user.enabled ? 'status-active' : 'status-disabled';
        const statusText = user.enabled ? __('Active') : __('Disabled');
        const userImage = user.user_image || '/assets/frappe/images/default-avatar.png';
        const startDate = user.start_date ? frappe.datetime.str_to_user(user.start_date) : '-';

        // Render module tags
        let moduleTags = '';
        if (user.modules && user.modules.length > 0) {
            const enabledModules = user.modules.filter(m => m.enabled);
            moduleTags = enabledModules.slice(0, 3).map(m =>
                `<span class="module-tag">${m.module_name}</span>`
            ).join('');

            if (enabledModules.length > 3) {
                moduleTags += `<span class="module-tag more">+${enabledModules.length - 3}</span>`;
            }
        }

        return `
            <div class="user-card ${!user.enabled ? 'disabled' : ''}" data-user="${user.name}">
                <div class="user-avatar">
                    <img src="${userImage}" alt="${user.full_name}"
                         onerror="this.src='/assets/frappe/images/default-avatar.png'">
                </div>
                <div class="user-details">
                    <div class="user-name">${user.full_name}</div>
                    <div class="user-email text-muted">${user.user_email || user.user}</div>
                    <div class="user-meta">
                        <span class="role-badge">${user.role_name || __('No Role')}</span>
                        <span class="start-date">
                            <i class="fa fa-calendar"></i> ${startDate}
                        </span>
                    </div>
                    <div class="user-modules">
                        ${moduleTags || '<span class="text-muted">' + __('No modules') + '</span>'}
                    </div>
                </div>
                <div class="user-status">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="user-actions">
                    <button class="btn btn-sm btn-light edit-user" data-user="${user.name}" 
                            title="${__('Edit User')}">
                        <i class="fa fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-light toggle-user ${user.enabled ? 'text-danger' : 'text-success'}" 
                            data-user="${user.name}" data-enabled="${user.enabled}"
                            title="${user.enabled ? __('Disable User') : __('Enable User')}">
                        <i class="fa fa-${user.enabled ? 'ban' : 'check'}"></i>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Bind events on profile and user cards
     */
    bind_card_events() {
        const self = this;

        // Toggle users list
        this.wrapper.find('.toggle-users').off('click').on('click', function (e) {
            e.preventDefault();
            const profile = $(this).data('profile');
            const usersSection = $(`#users-${profile.replace(/\s+/g, '-')}`);
            const icon = $(this).find('i');

            usersSection.slideToggle(200);
            icon.toggleClass('fa-chevron-down fa-chevron-up');
            $(this).html(
                usersSection.is(':visible')
                    ? `<i class="fa fa-chevron-up"></i> ${__('Hide Users')}`
                    : `<i class="fa fa-chevron-down"></i> ${__('Show Users')}`
            );
        });

        // Edit profile
        this.wrapper.find('.edit-profile').off('click').on('click', function (e) {
            e.preventDefault();
            const profile = $(this).data('profile');
            frappe.set_route('Form', 'Customer Portal Profile', profile);
        });

        // Add user
        this.wrapper.find('.add-user').off('click').on('click', function (e) {
            e.preventDefault();
            const customer = $(this).data('customer');
            self.add_user_dialog(customer);
        });

        // Toggle profile status
        this.wrapper.find('.toggle-profile').off('click').on('click', function (e) {
            e.preventDefault();
            const profile = $(this).data('profile');
            const enabled = $(this).data('enabled');
            self.toggle_profile_status(profile, !enabled);
        });

        // Edit user
        this.wrapper.find('.edit-user').off('click').on('click', function (e) {
            e.preventDefault();
            const user = $(this).data('user');
            frappe.set_route('Form', 'Customer Portal User', user);
        });

        // Toggle user status
        this.wrapper.find('.toggle-user').off('click').on('click', function (e) {
            e.preventDefault();
            const user = $(this).data('user');
            const enabled = $(this).data('enabled');
            self.toggle_user_status(user, !enabled);
        });
    }

    /**
     * Filter profiles based on search and status
     */
    filter_profiles() {
        const searchTerm = this.wrapper.find('#search-input').val().toLowerCase();
        const statusFilter = this.wrapper.find('#status-filter').val();

        this.wrapper.find('.profile-card-wrapper').each(function () {
            const $card = $(this);
            const customer = $card.data('customer').toString().toLowerCase();
            const enabled = $card.data('enabled').toString();

            let show = true;

            // Apply search filter
            if (searchTerm && !customer.includes(searchTerm)) {
                const companyName = $card.find('.company-name').text().toLowerCase();
                if (!companyName.includes(searchTerm)) {
                    show = false;
                }
            }

            // Apply status filter
            if (statusFilter !== '' && enabled !== statusFilter) {
                show = false;
            }

            $card.toggle(show);
        });
    }

    /**
     * Create new profile dialog
     */
    create_new_profile() {
        frappe.new_doc('Customer Portal Profile');
    }

    /**
     * Add user dialog for a customer
     */
    add_user_dialog(customer) {
        const self = this;

        const dialog = new frappe.ui.Dialog({
            title: __('Add Portal User'),
            fields: [
                {
                    fieldname: 'customer',
                    fieldtype: 'Link',
                    label: __('Customer'),
                    options: 'Customer',
                    default: customer,
                    read_only: 1
                },
                {
                    fieldname: 'user',
                    fieldtype: 'Link',
                    label: __('User'),
                    options: 'User',
                    reqd: 1,
                    filters: {
                        enabled: 1
                    }
                },
                {
                    fieldname: 'role',
                    fieldtype: 'Link',
                    label: __('Role'),
                    options: 'Role'
                },
                {
                    fieldname: 'modules_section',
                    fieldtype: 'Section Break',
                    label: __('Modules')
                },
                {
                    fieldname: 'modules_html',
                    fieldtype: 'HTML',
                    options: '<div id="modules-checkboxes"></div>'
                }
            ],
            primary_action_label: __('Add User'),
            primary_action: function () {
                const values = dialog.get_values();
                if (!values.user) return;

                // Collect selected modules
                const modules = [];
                dialog.$wrapper.find('.module-checkbox:checked').each(function () {
                    modules.push({
                        module_name: $(this).data('name'),
                        module_key: $(this).val(),
                        enabled: 1
                    });
                });

                frappe.call({
                    method: 'customer_portal_manager.api.portal_api.create_portal_user',
                    args: {
                        customer: values.customer,
                        user: values.user,
                        role: values.role,
                        modules: modules
                    },
                    callback: function (r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: r.message.message,
                                indicator: 'green'
                            });
                            dialog.hide();
                            self.load_data();
                        }
                    }
                });
            }
        });

        dialog.show();

        // Load available modules
        frappe.call({
            method: 'customer_portal_manager.api.portal_api.get_available_modules',
            callback: function (r) {
                const modules = r.message || [];
                let html = '<div class="row">';
                modules.forEach(m => {
                    html += `
                        <div class="col-md-6 mb-2">
                            <label class="d-flex align-items-center">
                                <input type="checkbox" class="module-checkbox mr-2" 
                                       value="${m.module_key}" data-name="${m.module_name}">
                                ${m.module_name}
                            </label>
                        </div>
                    `;
                });
                html += '</div>';
                dialog.$wrapper.find('#modules-checkboxes').html(html);
            }
        });
    }

    /**
     * Toggle profile status
     */
    toggle_profile_status(profile, enabled) {
        const self = this;
        const action = enabled ? __('enable') : __('disable');

        frappe.confirm(
            __('Are you sure you want to {0} this profile?', [action]),
            function () {
                frappe.call({
                    method: 'customer_portal_manager.api.portal_api.toggle_profile_status',
                    args: {
                        profile_name: profile,
                        enabled: enabled ? 1 : 0
                    },
                    callback: function (r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: r.message.message,
                                indicator: 'green'
                            });
                            self.load_data();
                        }
                    }
                });
            }
        );
    }

    /**
     * Toggle user status
     */
    toggle_user_status(user, enabled) {
        const self = this;
        const action = enabled ? __('enable') : __('disable');

        frappe.confirm(
            __('Are you sure you want to {0} this user?', [action]),
            function () {
                frappe.call({
                    method: 'customer_portal_manager.api.portal_api.toggle_user_status',
                    args: {
                        portal_user_name: user,
                        enabled: enabled ? 1 : 0
                    },
                    callback: function (r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({
                                message: r.message.message,
                                indicator: 'green'
                            });
                            self.load_data();
                        }
                    }
                });
            }
        );
    }
}

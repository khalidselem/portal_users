/**
 * Customer Portal Management - Desk Page
 */

frappe.pages['customer-portal-management'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Customer Portal Management'),
        single_column: true
    });

    new CustomerPortalManagement(page);
};

class CustomerPortalManagement {
    constructor(page) {
        this.page = page;
        this.wrapper = $(page.body);
        this.profiles = [];
        this.stats = {};

        this.init();
    }

    init() {
        this.setup_page_actions();
        this.render_layout();
        this.load_data();
    }

    setup_page_actions() {
        this.page.set_primary_action(
            __('New Profile'),
            () => this.create_new_profile(),
            'fa fa-plus'
        );

        this.page.set_secondary_action(
            __('Refresh'),
            () => this.load_data(),
            'fa fa-refresh'
        );
    }

    render_layout() {
        this.wrapper.html(`
            <div class="customer-portal-page">
                <!-- Statistics Cards -->
                <div class="stats-container mb-4">
                    <div class="row">
                        <div class="col-md-3 col-sm-6">
                            <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                                <div class="stat-icon"><i class="fa fa-building"></i></div>
                                <div class="stat-content">
                                    <div class="stat-value" id="stat-total-profiles">0</div>
                                    <div class="stat-label">${__('Total Profiles')}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 col-sm-6">
                            <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                                <div class="stat-icon"><i class="fa fa-check-circle"></i></div>
                                <div class="stat-content">
                                    <div class="stat-value" id="stat-active-profiles">0</div>
                                    <div class="stat-label">${__('Active Profiles')}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 col-sm-6">
                            <div class="stat-card" style="background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);">
                                <div class="stat-icon"><i class="fa fa-users"></i></div>
                                <div class="stat-content">
                                    <div class="stat-value" id="stat-total-users">0</div>
                                    <div class="stat-label">${__('Total Users')}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 col-sm-6">
                            <div class="stat-card" style="background: linear-gradient(135deg, #00c6fb 0%, #005bea 100%);">
                                <div class="stat-icon"><i class="fa fa-user-check"></i></div>
                                <div class="stat-content">
                                    <div class="stat-value" id="stat-active-users">0</div>
                                    <div class="stat-label">${__('Active Users')}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Search -->
                <div class="filter-container mb-4">
                    <div class="row">
                        <div class="col-md-6">
                            <input type="text" class="form-control" id="search-input" 
                                placeholder="${__('Search customers...')}">
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
                
                <!-- Customer Cards -->
                <div class="cards-container">
                    <div class="row" id="profiles-grid"></div>
                </div>
                
                <!-- Loading -->
                <div class="loading-indicator text-center py-5" style="display: none;">
                    <div class="spinner-border text-primary"></div>
                    <p class="mt-2 text-muted">${__('Loading...')}</p>
                </div>
                
                <!-- Empty -->
                <div class="empty-state text-center py-5" style="display: none;">
                    <i class="fa fa-inbox fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">${__('No customer profiles found')}</h4>
                </div>
            </div>
            
            <style>
                .customer-portal-page { padding: 20px; max-width: 1600px; margin: 0 auto; }
                .stat-card { border-radius: 12px; padding: 20px; color: white; display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
                .stat-icon { font-size: 2.5rem; opacity: 0.8; }
                .stat-value { font-size: 2rem; font-weight: 700; }
                .stat-label { font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; }
                .profile-card { background: var(--card-bg); border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 20px; border: 1px solid var(--border-color); }
                .profile-card.disabled { opacity: 0.7; }
                .profile-card-header { display: flex; align-items: center; padding: 20px; gap: 15px; border-bottom: 1px solid var(--border-color); }
                .profile-logo { width: 60px; height: 60px; border-radius: 10px; overflow: hidden; }
                .profile-logo img { width: 100%; height: 100%; object-fit: cover; }
                .profile-info { flex: 1; }
                .company-name { font-size: 1.1rem; font-weight: 600; margin: 0 0 5px 0; }
                .profile-commercial-info { padding: 15px 20px; border-bottom: 1px solid var(--border-color); }
                .info-row { display: flex; justify-content: space-between; padding: 5px 0; }
                .info-label { color: var(--text-muted); font-size: 0.85rem; }
                .info-value { font-weight: 500; }
                .profile-user-count { padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
                .status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
                .status-badge.status-active { background: rgba(56,239,125,0.15); color: #11998e; }
                .status-badge.status-disabled { background: rgba(255,82,82,0.15); color: #ff5252; }
                .user-card { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--card-bg); border-radius: 8px; margin-bottom: 10px; border: 1px solid var(--border-color); }
                .user-avatar { width: 40px; height: 40px; border-radius: 50%; overflow: hidden; }
                .user-avatar img { width: 100%; height: 100%; object-fit: cover; }
                .user-details { flex: 1; }
                .user-name { font-weight: 600; }
                .module-tag { background: rgba(102,126,234,0.15); color: #667eea; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-right: 5px; }
                .profile-users-section { border-top: 1px solid var(--border-color); padding: 15px; background: rgba(0,0,0,0.02); }
            </style>
        `);

        this.bind_events();
        window.cur_page = this;
    }

    bind_events() {
        const self = this;

        this.wrapper.find('#search-input').on('keyup', frappe.utils.debounce(function () {
            self.filter_profiles();
        }, 300));

        this.wrapper.find('#status-filter').on('change', function () {
            self.filter_profiles();
        });
    }

    load_data() {
        this.show_loading(true);

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

    fetch_stats() {
        return frappe.call({
            method: 'customer_portal_manager.api.portal_api.get_dashboard_stats',
            async: true
        }).then(r => {
            this.stats = r.message || {};
            this.update_stats_display();
        });
    }

    fetch_profiles() {
        return frappe.call({
            method: 'customer_portal_manager.api.portal_api.get_portal_profiles',
            async: true
        }).then(r => {
            this.profiles = r.message || [];
        });
    }

    update_stats_display() {
        $('#stat-total-profiles').text(this.stats.total_profiles || 0);
        $('#stat-active-profiles').text(this.stats.active_profiles || 0);
        $('#stat-total-users').text(this.stats.total_users || 0);
        $('#stat-active-users').text(this.stats.active_users || 0);
    }

    show_loading(show) {
        this.wrapper.find('.loading-indicator').toggle(show);
        this.wrapper.find('.cards-container').toggle(!show);
    }

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

        this.bind_card_events();
    }

    render_profile_card(profile) {
        const statusClass = profile.enabled ? 'status-active' : 'status-disabled';
        const statusText = profile.enabled ? __('Active') : __('Disabled');
        const logoUrl = profile.company_logo || '/assets/frappe/images/default-avatar.png';

        let usersHtml = '';
        if (profile.users && profile.users.length > 0) {
            usersHtml = profile.users.map(u => this.render_user_card(u)).join('');
        } else {
            usersHtml = `<div class="text-center text-muted py-3">${__('No users assigned')}</div>`;
        }

        return `
            <div class="col-xl-4 col-lg-6 col-md-6 profile-card-wrapper" 
                 data-profile="${profile.name}" 
                 data-customer="${profile.customer}"
                 data-enabled="${profile.enabled}">
                <div class="profile-card ${!profile.enabled ? 'disabled' : ''}">
                    <div class="profile-card-header">
                        <div class="profile-logo">
                            <img src="${logoUrl}" alt="${profile.company_name}" 
                                 onerror="this.src='/assets/frappe/images/default-avatar.png'">
                        </div>
                        <div class="profile-info">
                            <h4 class="company-name">${profile.company_name}</h4>
                            <span class="status-badge ${statusClass}">${statusText}</span>
                        </div>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-light" data-toggle="dropdown">
                                <i class="fa fa-ellipsis-v"></i>
                            </button>
                            <div class="dropdown-menu dropdown-menu-right">
                                <a class="dropdown-item edit-profile" href="#" data-profile="${profile.name}">
                                    <i class="fa fa-edit"></i> ${__('Edit Profile')}
                                </a>
                                <a class="dropdown-item add-user" href="#" data-customer="${profile.customer}">
                                    <i class="fa fa-user-plus"></i> ${__('Add User')}
                                </a>
                                <div class="dropdown-divider"></div>
                                <a class="dropdown-item toggle-profile" href="#" 
                                   data-profile="${profile.name}" data-enabled="${profile.enabled}">
                                    <i class="fa fa-${profile.enabled ? 'ban' : 'check'}"></i> 
                                    ${profile.enabled ? __('Disable') : __('Enable')}
                                </a>
                            </div>
                        </div>
                    </div>
                    
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
                    
                    <div class="profile-user-count">
                        <span><i class="fa fa-users"></i> ${profile.user_count || 0} ${__('Users')}</span>
                        <button class="btn btn-sm btn-outline-primary toggle-users" data-profile="${profile.name}">
                            <i class="fa fa-chevron-down"></i>
                        </button>
                    </div>
                    
                    <div class="profile-users-section" style="display: none;" id="users-${profile.name.replace(/\s+/g, '-')}">
                        ${usersHtml}
                    </div>
                </div>
            </div>
        `;
    }

    render_user_card(user) {
        const statusClass = user.enabled ? 'status-active' : 'status-disabled';
        const userImage = user.user_image || '/assets/frappe/images/default-avatar.png';

        let moduleTags = '';
        if (user.modules && user.modules.length > 0) {
            moduleTags = user.modules.filter(m => m.enabled).slice(0, 3)
                .map(m => `<span class="module-tag">${m.module_name}</span>`).join('');
        }

        return `
            <div class="user-card ${!user.enabled ? 'disabled' : ''}" data-user="${user.name}">
                <div class="user-avatar">
                    <img src="${userImage}" onerror="this.src='/assets/frappe/images/default-avatar.png'">
                </div>
                <div class="user-details">
                    <div class="user-name">${user.full_name}</div>
                    <div class="text-muted" style="font-size: 0.8rem;">${user.role_name || __('No Role')}</div>
                    <div class="mt-1">${moduleTags}</div>
                </div>
                <span class="status-badge ${statusClass}">${user.enabled ? __('Active') : __('Disabled')}</span>
                <button class="btn btn-sm btn-light toggle-user" data-user="${user.name}" data-enabled="${user.enabled}">
                    <i class="fa fa-${user.enabled ? 'ban' : 'check'}"></i>
                </button>
            </div>
        `;
    }

    bind_card_events() {
        const self = this;

        this.wrapper.find('.toggle-users').off('click').on('click', function (e) {
            e.preventDefault();
            const profile = $(this).data('profile');
            const section = $(`#users-${profile.replace(/\s+/g, '-')}`);
            section.slideToggle(200);
            $(this).find('i').toggleClass('fa-chevron-down fa-chevron-up');
        });

        this.wrapper.find('.edit-profile').off('click').on('click', function (e) {
            e.preventDefault();
            frappe.set_route('Form', 'Customer Portal Profile', $(this).data('profile'));
        });

        this.wrapper.find('.add-user').off('click').on('click', function (e) {
            e.preventDefault();
            self.add_user_dialog($(this).data('customer'));
        });

        this.wrapper.find('.toggle-profile').off('click').on('click', function (e) {
            e.preventDefault();
            const profile = $(this).data('profile');
            const enabled = $(this).data('enabled');
            self.toggle_profile_status(profile, !enabled);
        });

        this.wrapper.find('.toggle-user').off('click').on('click', function (e) {
            e.preventDefault();
            const user = $(this).data('user');
            const enabled = $(this).data('enabled');
            self.toggle_user_status(user, !enabled);
        });
    }

    filter_profiles() {
        const searchTerm = this.wrapper.find('#search-input').val().toLowerCase();
        const statusFilter = this.wrapper.find('#status-filter').val();

        this.wrapper.find('.profile-card-wrapper').each(function () {
            const $card = $(this);
            const companyName = $card.find('.company-name').text().toLowerCase();
            const enabled = $card.data('enabled').toString();

            let show = true;
            if (searchTerm && !companyName.includes(searchTerm)) show = false;
            if (statusFilter !== '' && enabled !== statusFilter) show = false;

            $card.toggle(show);
        });
    }

    create_new_profile() {
        frappe.new_doc('Customer Portal Profile');
    }

    add_user_dialog(customer) {
        const self = this;

        const dialog = new frappe.ui.Dialog({
            title: __('Add Portal User'),
            fields: [
                { fieldname: 'customer', fieldtype: 'Link', label: __('Customer'), options: 'Customer', default: customer, read_only: 1 },
                { fieldname: 'user', fieldtype: 'Link', label: __('User'), options: 'User', reqd: 1 },
                { fieldname: 'role', fieldtype: 'Link', label: __('Role'), options: 'Role' }
            ],
            primary_action_label: __('Add User'),
            primary_action: function () {
                const values = dialog.get_values();
                if (!values.user) return;

                frappe.call({
                    method: 'customer_portal_manager.api.portal_api.create_portal_user',
                    args: { customer: values.customer, user: values.user, role: values.role },
                    callback: function (r) {
                        if (r.message && r.message.success) {
                            frappe.show_alert({ message: r.message.message, indicator: 'green' });
                            dialog.hide();
                            self.load_data();
                        }
                    }
                });
            }
        });

        dialog.show();
    }

    toggle_profile_status(profile, enabled) {
        const self = this;
        frappe.call({
            method: 'customer_portal_manager.api.portal_api.toggle_profile_status',
            args: { profile_name: profile, enabled: enabled ? 1 : 0 },
            callback: function (r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({ message: r.message.message, indicator: 'green' });
                    self.load_data();
                }
            }
        });
    }

    toggle_user_status(user, enabled) {
        const self = this;
        frappe.call({
            method: 'customer_portal_manager.api.portal_api.toggle_user_status',
            args: { portal_user_name: user, enabled: enabled ? 1 : 0 },
            callback: function (r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({ message: r.message.message, indicator: 'green' });
                    self.load_data();
                }
            }
        });
    }
}

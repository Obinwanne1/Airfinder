// Admin panel shared logic
const Admin = {
  async loadDashboard() {
    return api.get('/admin/dashboard');
  },

  async loadCustomers(page = 1, search = '') {
    return api.get(`/admin/customers?page=${page}&search=${encodeURIComponent(search)}`);
  },

  async loadAllBookings(page = 1, status = '') {
    return api.get(`/admin/bookings?page=${page}&status=${status}`);
  },

  async loadStaff() {
    return api.get('/admin/staff');
  },

  async createStaff(data) {
    return api.post('/admin/staff', data);
  },

  async updateStaff(id, data) {
    return api.put(`/admin/staff/${id}`, data);
  },

  async resetStaffPassword(id) {
    return api.post(`/admin/staff/${id}/reset-password`, {});
  },

  async updateBooking(id, data) {
    return api.put(`/admin/bookings/${id}`, data);
  },

  async loadFinance() {
    return api.get('/admin/finance/summary');
  },

  formatCurrency(usd) {
    return `$${Number(usd).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  },

  statusBadge(status) {
    const map = {
      confirmed: 'badge-green',
      pending: 'badge-amber',
      cancelled: 'badge-red',
      refunded: 'badge-blue',
    };
    return `<span class="badge ${map[status] || 'badge-gray'}">${status}</span>`;
  },

  roleBadge(role) {
    const map = {
      super_admin: 'badge-red',
      admin: 'badge-blue',
      agent: 'badge-green',
      finance: 'badge-amber',
    };
    const label = role.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
    return `<span class="badge ${map[role] || 'badge-gray'}">${label}</span>`;
  },

  // Render sidebar active link
  setActiveLink(href) {
    document.querySelectorAll('.admin-nav-link').forEach(el => {
      el.classList.toggle('active', el.getAttribute('href') === href);
    });
  },

  // Setup sidebar with user info
  initSidebar() {
    const user = Auth.getUser();
    if (!user) return;
    const nameEl = document.getElementById('sidebar-name');
    const roleEl = document.getElementById('sidebar-role');
    const avatarEl = document.getElementById('sidebar-avatar');
    if (nameEl) nameEl.textContent = `${user.first_name} ${user.last_name}`;
    if (roleEl) roleEl.textContent = user.role.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
    if (avatarEl) avatarEl.textContent = (user.first_name?.[0] || '') + (user.last_name?.[0] || '');

    // Hide role-restricted nav items
    document.querySelectorAll('[data-role-only]').forEach(el => {
      const allowed = el.dataset.roleOnly.split(',').map(s => s.trim());
      if (!allowed.includes(user.role)) el.style.display = 'none';
    });
  },

  showToast(msg, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;min-width:280px;box-shadow:var(--shadow)';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  },
};

window.Admin = Admin;

document.addEventListener('DOMContentLoaded', () => {
  // Guard: all admin pages require staff
  if (!Auth.requireStaff()) return;
  Admin.initSidebar();

  // Logout button
  document.querySelectorAll('[data-admin-logout]').forEach(btn => {
    btn.addEventListener('click', () => {
      Auth.logout();
      window.location.href = '/admin/login.html';
    });
  });
});

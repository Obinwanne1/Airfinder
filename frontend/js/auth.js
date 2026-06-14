const Auth = {
  TOKEN_KEY: 'af_token',
  USER_KEY: 'af_user',
  ROLE_KEY: 'af_role',

  save(token, user) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    localStorage.setItem(this.ROLE_KEY, user.role || 'customer');
  },

  saveStaff(token, staff) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(staff));
    localStorage.setItem(this.ROLE_KEY, staff.role);
  },

  getToken() { return localStorage.getItem(this.TOKEN_KEY); },
  getUser() {
    try { return JSON.parse(localStorage.getItem(this.USER_KEY)); }
    catch { return null; }
  },
  getRole() { return localStorage.getItem(this.ROLE_KEY); },

  isLoggedIn() { return !!this.getToken(); },
  isStaff() { return ['super_admin','admin','agent','finance'].includes(this.getRole()); },
  isCustomer() { return this.getRole() === 'customer'; },

  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    localStorage.removeItem(this.ROLE_KEY);
  },

  requireLogin(redirectTo = '/auth/login.html') {
    if (!this.isLoggedIn()) { window.location.href = redirectTo; return false; }
    return true;
  },

  requireStaff() {
    if (!this.isLoggedIn() || !this.isStaff()) {
      window.location.href = '/admin/login.html';
      return false;
    }
    return true;
  },

  requireRole(...roles) {
    if (!this.requireStaff()) return false;
    if (!roles.includes(this.getRole())) {
      alert('Access denied. Insufficient permissions.');
      history.back();
      return false;
    }
    return true;
  },

  redirectIfLoggedIn(to = '/account/dashboard.html') {
    if (this.isLoggedIn() && this.isCustomer()) window.location.href = to;
    if (this.isLoggedIn() && this.isStaff()) window.location.href = '/admin/dashboard.html';
  },
};

window.Auth = Auth;

// Update navbar state
document.addEventListener('DOMContentLoaded', () => {
  const user = Auth.getUser();
  const loginLinks = document.querySelectorAll('[data-auth-login]');
  const logoutLinks = document.querySelectorAll('[data-auth-logout]');
  const userNameEl = document.querySelectorAll('[data-auth-name]');

  if (Auth.isLoggedIn() && user) {
    loginLinks.forEach(el => el.classList.add('hidden'));
    logoutLinks.forEach(el => el.classList.remove('hidden'));
    userNameEl.forEach(el => el.textContent = user.first_name || user.email);
  } else {
    loginLinks.forEach(el => el.classList.remove('hidden'));
    logoutLinks.forEach(el => el.classList.add('hidden'));
  }

  logoutLinks.forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      Auth.logout();
      window.location.href = '/';
    });
  });

  // Mobile navbar hamburger toggle
  const navInner = document.querySelector('.navbar-inner');
  const navLinks = document.querySelector('.navbar-links');
  if (navInner && navLinks) {
    const btn = document.createElement('button');
    btn.className = 'navbar-menu';
    btn.setAttribute('aria-label', 'Toggle navigation');
    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
    navInner.appendChild(btn);
    btn.addEventListener('click', () => navLinks.classList.toggle('mobile-open'));
    navLinks.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => navLinks.classList.remove('mobile-open'));
    });
  }
});

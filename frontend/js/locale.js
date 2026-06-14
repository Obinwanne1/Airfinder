// Locale: Germany / Europe — EUR currency, Europe/Berlin timezone
const _curr = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' });
const _date = new Intl.DateTimeFormat('de-DE', { timeZone: 'Europe/Berlin', day: '2-digit', month: '2-digit', year: 'numeric' });
const _dt   = new Intl.DateTimeFormat('de-DE', { timeZone: 'Europe/Berlin', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

function fmtCurrency(amount) {
  if (amount == null || isNaN(amount)) return '—';
  return _curr.format(Number(amount));
}
function fmtDate(isoStr) {
  if (!isoStr) return '—';
  try { return _date.format(new Date(isoStr)); } catch { return isoStr; }
}
function fmtDateTime(isoStr) {
  if (!isoStr) return '—';
  try { return _dt.format(new Date(isoStr)); } catch { return isoStr; }
}

window.fmtCurrency = fmtCurrency;
window.fmtDate = fmtDate;
window.fmtDateTime = fmtDateTime;

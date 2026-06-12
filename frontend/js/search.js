// Flight search logic
const Search = {
  results: [],
  filteredResults: [],

  async searchFlights(params) {
    const qs = new URLSearchParams({
      origin: params.origin,
      destination: params.destination,
      departure_date: params.departure_date,
      passengers: params.passengers || 1,
      cabin: params.cabin || 'economy',
      ...(params.return_date ? { return_date: params.return_date } : {}),
    });
    return api.get(`/flights/search?${qs}`);
  },

  async aiSearch(query) {
    return api.post('/flights/search/ai', { query });
  },

  async loadFeatured() {
    return api.get('/flights/featured');
  },

  async loadAirports() {
    return api.get('/flights/airports');
  },

  formatDuration(hours) {
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  },

  trustColor(score) {
    if (score >= 4.5) return 'trust-score-high';
    if (score >= 3.5) return 'trust-score-mid';
    return 'trust-score-low';
  },

  renderFlightCard(flight) {
    const p = flight.pricing;
    const isAfrica = flight.is_africa_route;

    const africaBadge = isAfrica
      ? `<span class="africa-badge">✈ Africa Direct</span>`
      : '';

    const breakdown = `
      <div class="true-cost-breakdown">
        <span class="cost-item">Base $${p.base_fare}</span>
        <span class="cost-item">Markup $${p.markup}</span>
        <span class="cost-item">Service $${p.service_fee}</span>
        ${p.baggage_fee > 0 ? `<span class="cost-item">Baggage $${p.baggage_fee}</span>` : ''}
        ${p.seat_fee > 0 ? `<span class="cost-item">Seat $${p.seat_fee}</span>` : ''}
      </div>
    `;

    const otaOptions = flight.ota_options.map((ota, i) => `
      <div class="ota-option ${i === 0 ? 'best' : ''}" onclick="selectOTA('${flight.id}', '${ota.ota_id}', ${ota.price})">
        <span class="ota-name">${ota.ota_name}</span>
        <span class="${ota.verified ? 'ota-verified' : 'ota-unverified'}">${ota.verified ? '✓' : '⚠'}</span>
        <div class="trust-score ${this.trustColor(ota.trust_score)}">★${ota.trust_score}</div>
        <span class="ota-price">$${ota.price.toFixed(2)}</span>
      </div>
    `).join('');

    return `
      <div class="flight-card ${isAfrica ? 'africa-direct' : ''}" data-flight-id="${flight.id}">
        <div class="flight-card-header">
          <div class="flight-airline">
            <div class="airline-logo">${flight.airline_code}</div>
            <div>
              <div class="airline-name">${flight.airline}</div>
              <div class="airline-flight">${flight.flight_number}</div>
            </div>
          </div>
          <div style="flex:1;display:flex;align-items:center;justify-content:center;gap:16px;padding:0 16px;">
            <div class="flight-time">
              <div class="flight-time-val">${flight.departure_time}</div>
              <div class="flight-time-code">${flight.origin}</div>
            </div>
            <div class="flight-line">
              <div class="flight-line-track">
                <div class="line"></div>
                <span class="plane-icon">✈</span>
                <div class="line"></div>
              </div>
              <div class="flight-duration">${this.formatDuration(flight.duration_hours)}</div>
              <div class="flight-stops ${flight.stops === 0 ? 'nonstop' : ''}">${flight.stops_label}</div>
            </div>
            <div class="flight-time">
              <div class="flight-time-val">${flight.arrival_time}</div>
              <div class="flight-time-code">${flight.destination}</div>
            </div>
          </div>
          <div style="text-align:right;">
            ${africaBadge}
            <div class="text-sm text-gray">${flight.available_seats} seats left</div>
          </div>
        </div>
        <div class="flight-card-pricing">
          <div class="true-cost">
            <div class="true-cost-label">Total True Cost — no surprises</div>
            <div class="true-cost-total">$${p.total.toFixed(2)}</div>
            ${breakdown}
          </div>
          <div class="flight-card-actions">
            <button class="btn btn-primary" onclick="bookFlight('${flight.id}')">Book Now</button>
            <button class="price-hold-btn" onclick="holdPrice('${flight.id}', ${p.total})">⏱ Hold Price 24h</button>
          </div>
        </div>
        <div class="ota-options">
          <span style="font-size:12px;font-weight:700;color:var(--gray-400);align-self:center;margin-right:6px;">Book via:</span>
          ${otaOptions}
        </div>
      </div>
    `;
  },

  renderFeaturedRoute(route) {
    return `
      <div class="route-card" onclick="quickSearch('${route.origin}','${route.destination}')">
        <div class="route-from">${route.origin} → ${route.destination}</div>
        <div class="route-to">${route.label}</div>
        <div class="route-airline">${route.airline}</div>
        <div class="route-price">
          <span class="route-price-from">from </span>$${route.price_from}
        </div>
      </div>
    `;
  },
};

window.Search = Search;

// Store current flight for booking
window.currentFlight = null;

function bookFlight(flightId) {
  const flight = Search.results.find(f => f.id === flightId);
  if (!flight) return;
  sessionStorage.setItem('af_flight', JSON.stringify(flight));
  window.location.href = '/booking.html';
}

function selectOTA(flightId, otaId, price) {
  const flight = Search.results.find(f => f.id === flightId);
  if (!flight) return;
  const ota = flight.ota_options.find(o => o.ota_id === otaId);
  flight._selectedOta = ota;
  sessionStorage.setItem('af_flight', JSON.stringify(flight));
  window.location.href = '/booking.html';
}

function holdPrice(flightId, price) {
  if (!Auth.isLoggedIn()) {
    sessionStorage.setItem('af_redirect_after_login', window.location.href);
    window.location.href = '/auth/login.html';
    return;
  }
  alert(`Price held for 24 hours at $${price.toFixed(2)}. A small hold fee of $5 will be charged. (Demo mode — no actual charge)`);
}

function quickSearch(origin, destination) {
  const today = new Date();
  today.setDate(today.getDate() + 14);
  const date = today.toISOString().split('T')[0];
  window.location.href = `/results.html?origin=${origin}&destination=${destination}&departure_date=${date}&passengers=1&cabin=economy`;
}

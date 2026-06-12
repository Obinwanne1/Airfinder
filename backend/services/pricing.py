from backend.config import Config

BAGGAGE_FEES = {
    'carry_on': 0,
    'checked_1': 35,
    'checked_2': 60,
}

SEAT_FEES = {
    'standard': 0,
    'extra_legroom': 45,
    'front_row': 30,
    'window': 15,
    'aisle': 10,
}

def calculate_total(base_fare, passengers=1, baggage_option='carry_on', seat_option='standard',
                    markup_pct=None, service_fee=None, commission_pct=None):
    markup_pct = markup_pct if markup_pct is not None else Config.MARKUP_PERCENT
    service_fee = service_fee if service_fee is not None else Config.SERVICE_FEE_USD
    commission_pct = commission_pct if commission_pct is not None else Config.COMMISSION_PERCENT

    markup = round(base_fare * (markup_pct / 100), 2)
    baggage_fee = BAGGAGE_FEES.get(baggage_option, 0) * passengers
    seat_fee = SEAT_FEES.get(seat_option, 0) * passengers
    commission = round(base_fare * (commission_pct / 100), 2)

    subtotal = base_fare + markup + service_fee + baggage_fee + seat_fee
    total = round(subtotal * passengers, 2)

    return {
        'base_fare': base_fare,
        'markup': markup,
        'markup_pct': markup_pct,
        'service_fee': service_fee,
        'baggage_fee': baggage_fee,
        'seat_fee': seat_fee,
        'commission': commission,
        'commission_pct': commission_pct,
        'subtotal_per_pax': round(base_fare + markup + service_fee + (baggage_fee / passengers) + (seat_fee / passengers), 2),
        'total': total,
        'passengers': passengers,
        'currency': 'USD',
    }

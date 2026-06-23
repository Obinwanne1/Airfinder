import json
import random
import string
from flask import Blueprint, request, jsonify, g
from backend.models.database import db
from backend.models.booking import Booking, BookingStatus, generate_reference
from backend.models.user import User
from backend.middleware.jwt_guard import jwt_required
from backend.services.pricing import calculate_total
from backend.services.email_service import send_booking_confirmation_email
from backend.extensions import limiter

bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

@bp.route('', methods=['POST'])
@jwt_required
@limiter.limit("10 per minute")
def create_booking():
    data = request.get_json()
    required = ['flight_id', 'origin', 'destination', 'departure_date', 'airline', 'base_fare', 'passengers']
    if not all(data.get(f) for f in required):
        return jsonify({'error': f'Required fields: {", ".join(required)}'}), 400

    pricing = calculate_total(
        base_fare=float(data['base_fare']),
        passengers=len(data['passengers']),
        baggage_option=data.get('baggage', 'carry_on'),
        seat_option=data.get('seat', 'standard'),
    )

    # Prevent duplicate booking reference collision
    ref = generate_reference()
    while Booking.query.filter_by(reference=ref).first():
        ref = generate_reference()

    booking = Booking(
        reference=ref,
        user_id=g.user_id,
        flight_id=data['flight_id'],
        origin=data['origin'].upper(),
        destination=data['destination'].upper(),
        departure_date=data['departure_date'],
        airline=data['airline'],
        flight_number=data.get('flight_number'),
        cabin_class=data.get('cabin', 'economy'),
        passengers_json=json.dumps(data['passengers']),
        passenger_count=len(data['passengers']),
        base_fare_usd=pricing['base_fare'],
        markup_usd=pricing['markup'],
        service_fee_usd=pricing['service_fee'],
        baggage_fee_usd=pricing['baggage_fee'],
        seat_fee_usd=pricing['seat_fee'],
        total_usd=pricing['total'],
        commission_usd=pricing['commission'],
        status=BookingStatus.CONFIRMED,
    )
    db.session.add(booking)
    db.session.commit()

    user = User.query.get(g.user_id)
    if user:
        send_booking_confirmation_email(user.email, user.first_name, booking.to_dict())

    return jsonify({'booking': booking.to_dict(), 'message': 'Booking confirmed!'}), 201

@bp.route('/multicity', methods=['POST'])
@jwt_required
@limiter.limit("5 per minute")
def create_multicity_booking():
    data = request.get_json()
    legs = data.get('legs', [])
    passengers = data.get('passengers', [])
    baggage = data.get('baggage', 'carry_on')
    seat = data.get('seat', 'standard')
    cabin = data.get('cabin', 'economy')

    if len(legs) < 2:
        return jsonify({'error': 'At least 2 legs required for multi-city booking'}), 400
    if not passengers:
        return jsonify({'error': 'passengers required'}), 400

    group_ref = 'AF' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    created = []
    combined_total = 0.0

    for leg in legs:
        pricing = calculate_total(
            base_fare=float(leg['base_fare']),
            passengers=len(passengers),
            baggage_option=baggage,
            seat_option=seat,
        )
        ref = generate_reference()
        while Booking.query.filter_by(reference=ref).first():
            ref = generate_reference()

        booking = Booking(
            reference=ref,
            user_id=g.user_id,
            flight_id=leg['flight_id'],
            origin=leg['origin'].upper(),
            destination=leg['destination'].upper(),
            departure_date=leg['date'],
            airline=leg['airline'],
            flight_number=leg.get('flight_number'),
            cabin_class=cabin,
            passengers_json=json.dumps(passengers),
            passenger_count=len(passengers),
            base_fare_usd=pricing['base_fare'],
            markup_usd=pricing['markup'],
            service_fee_usd=pricing['service_fee'],
            baggage_fee_usd=pricing['baggage_fee'],
            seat_fee_usd=pricing['seat_fee'],
            total_usd=pricing['total'],
            commission_usd=pricing['commission'],
            group_reference=group_ref,
            is_multicity=True,
            status=BookingStatus.CONFIRMED,
        )
        db.session.add(booking)
        created.append(booking)
        combined_total += pricing['total']

    db.session.commit()

    user = User.query.get(g.user_id)
    if user and created:
        send_booking_confirmation_email(user.email, user.first_name, created[0].to_dict())

    return jsonify({
        'group_reference': group_ref,
        'bookings': [b.to_dict() for b in created],
        'total_legs': len(created),
        'combined_total_usd': round(combined_total, 2),
        'message': f'Multi-city booking confirmed! {len(created)} flights booked.',
    }), 201

@bp.route('', methods=['GET'])
@jwt_required
def my_bookings():
    role = g.role
    if role == 'customer':
        bookings = Booking.query.filter_by(user_id=g.user_id).order_by(Booking.created_at.desc()).all()
    else:
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings])

@bp.route('/<booking_id>', methods=['GET'])
@jwt_required
def get_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if g.role == 'customer' and booking.user_id != g.user_id:
        return jsonify({'error': 'Access denied'}), 403
    return jsonify(booking.to_dict())

@bp.route('/<booking_id>/cancel', methods=['POST'])
@jwt_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if g.role == 'customer' and booking.user_id != g.user_id:
        return jsonify({'error': 'Access denied'}), 403

    if booking.status == BookingStatus.CANCELLED:
        return jsonify({'error': 'Booking already cancelled'}), 400

    booking.status = BookingStatus.CANCELLED
    db.session.commit()
    return jsonify({'message': 'Booking cancelled', 'booking': booking.to_dict()})

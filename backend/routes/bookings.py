import json
from flask import Blueprint, request, jsonify, g
from backend.models.database import db
from backend.models.booking import Booking, BookingStatus, generate_reference
from backend.models.user import User
from backend.middleware.jwt_guard import jwt_required
from backend.services.pricing import calculate_total
from backend.services.email_service import send_booking_confirmation_email

bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

@bp.route('', methods=['POST'])
@jwt_required
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

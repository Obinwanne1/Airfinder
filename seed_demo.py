"""One-time demo data seed. Run: python seed_demo.py"""
import sys, os, random, json, uuid, string
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import create_app
from backend.models.database import db
from backend.models.user import User
from backend.models.booking import Booking, BookingStatus, generate_reference

app = create_app()

DEMO_USERS = [
    {'first_name': 'Emeka',     'last_name': 'Okafor',   'email': 'emeka.okafor@techcorp.ng',          'phone': '+2348012345678'},
    {'first_name': 'Ngozi',     'last_name': 'Adeyemi',  'email': 'ngozi.adeyemi@techcorp.ng',         'phone': '+2348023456789'},
    {'first_name': 'Babatunde', 'last_name': 'Ibrahim',  'email': 'b.ibrahim@globalventures.com.ng',   'phone': '+2348034567890'},
    {'first_name': 'Chisom',    'last_name': 'Eze',      'email': 'chisom.eze@firstbankng.com',        'phone': '+2348045678901'},
    {'first_name': 'Seun',      'last_name': 'Adeleke',  'email': 'seun.adeleke@dangote.com',          'phone': '+2348056789012'},
    {'first_name': 'Adaeze',    'last_name': 'Okonkwo',  'email': 'a.okonkwo@zenithbank.com',          'phone': '+2348067890123'},
    {'first_name': 'Kayode',    'last_name': 'Fashola',  'email': 'k.fashola@accessbank.com',          'phone': '+2348078901234'},
    {'first_name': 'Blessing',  'last_name': 'Nwosu',    'email': 'blessing.nwosu@gtbank.com',         'phone': '+2348089012345'},
    {'first_name': 'Ahmed',     'last_name': 'Abubakar', 'email': 'ahmed.abubakar@zenithbank.com',     'phone': '+2348090123456'},
    {'first_name': 'Ifeanyi',   'last_name': 'Chukwu',   'email': 'ifeanyi.chukwu@mtn.com.ng',        'phone': '+2348001234567'},
]

ROUTES = [
    {'o': 'LOS', 'd': 'LHR', 'airlines': ['British Airways', 'Air Peace', 'Virgin Atlantic'],   'eco': (750,1100),  'biz': (3200,5500)},
    {'o': 'ABV', 'd': 'DXB', 'airlines': ['Emirates', 'Air Peace', 'Turkish Airlines'],         'eco': (480,780),   'biz': (1800,3200)},
    {'o': 'LOS', 'd': 'JFK', 'airlines': ['United Airlines', 'Delta', 'Air France'],            'eco': (820,1250),  'biz': (4000,6500)},
    {'o': 'LOS', 'd': 'CDG', 'airlines': ['Air France', 'British Airways', 'KLM'],              'eco': (680,980),   'biz': (2800,4500)},
    {'o': 'ABV', 'd': 'LHR', 'airlines': ['British Airways', 'Ethiopian Airlines'],             'eco': (700,1050),  'biz': (3000,5000)},
    {'o': 'LOS', 'd': 'AMS', 'airlines': ['KLM', 'Air France'],                                'eco': (650,950),   'biz': (2600,4200)},
    {'o': 'LOS', 'd': 'IAH', 'airlines': ['United Airlines', 'British Airways'],                'eco': (900,1350),  'biz': (4500,7000)},
    {'o': 'ABV', 'd': 'CDG', 'airlines': ['Air France', 'Turkish Airlines'],                   'eco': (600,900),   'biz': (2400,4000)},
    {'o': 'LOS', 'd': 'DXB', 'airlines': ['Emirates', 'Qatar Airways'],                        'eco': (520,820),   'biz': (2000,3500)},
    {'o': 'LOS', 'd': 'YYZ', 'airlines': ['Air Canada', 'British Airways'],                    'eco': (870,1300),  'biz': (3800,6000)},
]

IATA_PREFIX = {
    'British Airways': 'BA', 'Air Peace': 'P4', 'Virgin Atlantic': 'VS',
    'Emirates': 'EK', 'Turkish Airlines': 'TK', 'United Airlines': 'UA',
    'Delta': 'DL', 'Air France': 'AF', 'KLM': 'KL', 'Ethiopian Airlines': 'ET',
    'Qatar Airways': 'QR', 'Air Canada': 'AC',
}

MARKUP_PCT = 0.08
SERVICE_FEE = 15.0
COMMISSION_PCT = 0.03

# 21 confirmed, 6 pending, 3 cancelled
STATUS_POOL = [BookingStatus.CONFIRMED]*21 + [BookingStatus.PENDING]*6 + [BookingStatus.CANCELLED]*3


def seed():
    with app.app_context():
        import bcrypt

        if User.query.filter(User.email.like('%techcorp.ng')).first():
            print('[SEED] Demo data already seeded. Delete airfinder.db to re-seed.')
            return

        demo_hash = bcrypt.hashpw(b'Demo@2024!', bcrypt.gensalt()).decode('utf-8')
        users = []
        for ud in DEMO_USERS:
            u = User(
                email=ud['email'],
                password_hash=demo_hash,
                first_name=ud['first_name'],
                last_name=ud['last_name'],
                phone=ud['phone'],
                is_active=True,
                is_verified=True,
            )
            db.session.add(u)
            users.append(u)

        db.session.flush()  # assign user IDs before referencing them in bookings

        statuses = STATUS_POOL[:]
        random.shuffle(statuses)

        for i in range(30):
            user = random.choice(users)
            route = random.choice(ROUTES)
            cabin = random.choices(['economy', 'business'], weights=[75, 25])[0]
            airline = random.choice(route['airlines'])

            fare_range = route['eco'] if cabin == 'economy' else route['biz']
            base_fare = round(random.uniform(*fare_range), 2)
            markup = round(base_fare * MARKUP_PCT, 2)
            total = round(base_fare + markup + SERVICE_FEE, 2)
            commission = round(base_fare * COMMISSION_PCT, 2)

            days_ago = random.randint(0, 90)
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            dep_date = (created_at + timedelta(days=random.randint(3, 45))).strftime('%Y-%m-%d')

            prefix = IATA_PREFIX.get(airline, 'XX')
            flight_number = f"{prefix}{random.randint(100, 999)}"

            passengers_json = json.dumps([{
                'first_name': user.first_name,
                'last_name': user.last_name,
                'dob': '1985-06-15',
                'passport': f'A{random.randint(10000000, 99999999)}',
                'nationality': 'NG',
            }])

            b = Booking(
                id=str(uuid.uuid4()),
                reference=generate_reference(),
                user_id=user.id,
                flight_id=f'{route["o"]}-{route["d"]}-{flight_number}',
                origin=route['o'],
                destination=route['d'],
                departure_date=dep_date,
                airline=airline,
                flight_number=flight_number,
                cabin_class=cabin,
                passengers_json=passengers_json,
                passenger_count=1,
                base_fare_usd=base_fare,
                markup_usd=markup,
                service_fee_usd=SERVICE_FEE,
                baggage_fee_usd=0.0,
                seat_fee_usd=0.0,
                total_usd=total,
                commission_usd=commission,
                status=statuses[i],
                created_at=created_at,
            )
            db.session.add(b)

        db.session.commit()

        confirmed = sum(1 for s in statuses if s == BookingStatus.CONFIRMED)
        total_rev = sum(
            b.total_usd for b in Booking.query.filter_by(status=BookingStatus.CONFIRMED).all()
        )
        print(f'[SEED] {len(DEMO_USERS)} customers + 30 bookings created.')
        print(f'[SEED] {confirmed} confirmed | Revenue: ${total_rev:,.2f}')


if __name__ == '__main__':
    seed()

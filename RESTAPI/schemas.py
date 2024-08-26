from flask_marshmallow import Marshmallow
from models import VehicleBooking  # Adjust the import path if necessary

ma = Marshmallow()

class VehicleBookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VehicleBooking

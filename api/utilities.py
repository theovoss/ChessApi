import arrow
import uuid


def get_current_datetime():
    return arrow.now().datetime


def generate_uuid():
    an_id = uuid.uuid4()
    print("id created is: " + str(an_id))
    return an_id

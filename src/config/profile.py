from service.profile import Profile


def load_profiles():
    """ Return list of profiles """
    data = [{
        "address": "first",
        "userName": "first",
        "email": "first"
    }]
    for profile in data:
        Profile().create_one(profile)

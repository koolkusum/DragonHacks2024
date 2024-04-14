from app import *

def generate_reviews_for_profs():
    profs = Professor.objects()
    for prof in profs:
        if not prof.reviews:
            print(f"Generating reviews for {prof.name}")
            prof.generate_reviews()
        else:
            print(f"Reviews already exist for {prof.name}")
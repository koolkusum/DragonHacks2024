from app import *

def generate_reviews_for_profs():
    # select prof pid 5 and leave review
    professor = Professor.objects(pid=5).first()
    professor.add_review("Great professor!", )
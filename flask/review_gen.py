from app import *

def generate_reviews_for_profs():
    # for each course of professor get name and description
    prompt = ""
    # test with prof 5 use member method create_review()
    prof = Professor.objects(pid=5).first()
    if prof:
        courses = prof.get_courses()
        for course in courses:
            course_info = Course.objects(cid=course).first()
            if course_info:
                prompt += f"{course_info.course_name} {course_info.description}"
                reviews = course_info.get_reviews()
                for review in reviews:
                    prompt += f"{review.review_text}"
    else:
        print("Professor not found.")
            
import json
from app import *
import google.generativeai as genai


def generate_reviews_for_profs():
    # for each course of professor get name and description
    prompt = """Generate a review for a professor that relates to the following topics below. Emulate the language a student would use on the casual, this is a place for students to conversate with one another and stay in first person.
    Provide a title and description, follow the following json format do not edit or you will be terminated. {"title:" "", "description:" ""}
    Separate each json entry with a ',' and do not include any spaces between the json entries.
    Do at most three reviews per professor, include some randomness in positivity and negativity, but keep it civil.
     The professor is """
    # test with prof 5 use member method create_review()
    prof = Professor.objects(pid=5).first()
    if prof:
        prompt += prof.name + "\n"
        # get courses using cids
        prompt += "Courses professor teaches: \n"
        for cid in prof.cids:
            course = Course.objects(cid=cid).first()
            if course:
                prompt += course.name + '\n' + '-'*50 + '\n'
                
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content(prompt)
    print(response.text)



generate_reviews_for_profs()
            
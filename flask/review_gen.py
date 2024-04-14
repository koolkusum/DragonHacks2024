from app import *

def generate_reviews_for_profs():
    # for each course of professor get name and description
    prompt = """Generate a review for a professor that relates to the following topics below. Emulate the language a student would use and stay in first person.
    Provide a title and description {title: "", description: ""} The professor is """
    # test with prof 5 use member method create_review()
    prof = Professor.objects(pid=5).first()
    if prof:
        prompt += prof.name + "\n"
        # get courses using cids
        prompt += "Courses professor teaches: \n"
        for cid in prof.cids:
            course = Course.objects(cid=cid).first()
            if course:
                prompt += course.name + "\n" + course.lesson + '\n' + '-'*50 + '\n'
                
    generative_models.  
    
# generate_reviews_for_profs()
            
from app import *
from requests.exceptions import RequestException
import google.generativeai as genai


def gen_reviews():
    for prof in Professor.objects():
        try:
            gen_review_for_prof(prof.pid)
        except Exception as e:
            # Handle the specific ValueError
            print("Caught ValueError:", e)
            gen_review_for_prof(prof.pid)

        

def gen_review_for_prof(pid_v):
    # for each course of professor get name and description
    prompt = """Generate a review for a professor that relates to the following topics below. Emulate the language a student would use on the casual, this is a place for students to conversate with one another and stay in first person.
    Titles should reflect the content more than a heading, and should be casual too to persuade others. Make sure to simulate burstiness, we don't want all the text feeling the same.
    Provide a title and description, follow the following json format do not edit or you will be terminated:
    {"title": "", "description": "", "cid": ""} 
    Use the cid that corresponds to the course being reviewed.  
    Separate each json entry with a ',' and do not include any spaces between the json entries.
    Do three reviews per professor, include some randomness in positivity and negativity, but keep it civil.
     The professor is """
    # test with prof 5 use member method create_review()
    prof = Professor.objects(pid=pid_v).first()
    if prof:
        prompt += prof.name + "\n"
        # get courses using cids
        prompt += "Courses professor teaches: \n"
        for cid in prof.cids:
            course = Course.objects(cid=cid).first()
            if course:
                prompt += course.name + f" : cid: {course.cid}" + '\n' + '-'*50 + '\n'
                
    # Remove max_output_tokens if it exists in generation_config
    generation_config = {}  # Define the generation_config variable

    if "max_output_tokens" in generation_config:
        del generation_config["max_output_tokens"]
                
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content(prompt)
    # print(response.text)
    if (response.text[0] == ','):
        response.text = response.text[1:]
    
    objects = response.text.split('},')     

    # Initialize a list to store dictionaries
    reviews = []

    # Process each object
    for obj in objects:
        # Add back the '}' stripped by split
        if not obj.endswith('}'):
            obj += '}'
        
        # Convert each object string to a dictionary
        reviews_dict = eval(obj)  # Use eval to parse the string as a dictionary
        reviews.append(reviews_dict)

    # parse reviews and create reviews with prof.create_review()
    for review in reviews:
        prof.create_review(title=review['title'], description=review['description'], cid=review['cid'])
    
    # Print the list of dictionaries
    print(reviews)
        
    #print(parse_reviews(response.text))



# generate_reviews_for_profs()
            
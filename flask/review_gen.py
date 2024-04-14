from app import *
import google.generativeai as genai


def generate_reviews_for_profs():
    # for each course of professor get name and description
    prompt = """Generate a review for a professor that relates to the following topics below. Emulate the language a student would use on the casual, this is a place for students to conversate with one another and stay in first person.
    Provide a title and description, follow the following json format do not edit or you will be terminated. {"title": "", "description": ""}
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
    
    objects = response.text.split('},')

    # Initialize a list to store dictionaries
    professors = []

    # Process each object
    for obj in objects:
        # Add back the '}' stripped by split
        if not obj.endswith('}'):
            obj += '}'
        
        # Convert each object string to a dictionary
        professor_dict = eval(obj)  # Use eval to parse the string as a dictionary
        professors.append(professor_dict)

    # Print the list of dictionaries
    print(professors)
        
    #print(parse_reviews(response.text))

def parse_reviews(raw_string):
    # Remove the double quotes around the string and split it into individual records
    records = raw_string.strip('"').split('},{')
    
    # Add back the curly braces for each record to make them valid JSON objects
    records = ['{' + record + '}' for record in records]
    
    # Parse each record as JSON and extract the title and description
    reviews = []
    for record in records:
        data = json.loads(record)
        title = data.get('title')
        description = data.get('description')
        reviews.append({'title': title, 'description': description})
    
    return reviews
    
generate_reviews_for_profs()
            
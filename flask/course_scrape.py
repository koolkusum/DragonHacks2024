import random
import requests
from bs4 import BeautifulSoup

def get_course_urls(url='https://www.cs.rutgers.edu/academics/undergraduate/course-synopses'):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all elements with class 'latestnews-item'
        course_elements = soup.find_all(class_='latestnews-item')

        # Extract course URLs from each element
        course_urls = []
        for course_element in course_elements:
            # Find the <a> tag within each element
            course_link = course_element.find('a')
            if course_link:
                # Extract the href attribute containing the URL
                course_url = course_link['href']
                # Append the complete URL to the list
                course_urls.append(f'https://www.cs.rutgers.edu{course_url}')

        return course_urls
    else:
        print('Failed to retrieve the page.')
        return None
    
def get_course_info(course_url):
    # Send a GET request to the course URL
    response = requests.get(course_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the course name from <h2> tag
        course_name_element = soup.find('h2', itemprop='name')
        if course_name_element:
            course_name = course_name_element.get_text(strip=True)
        else:
            course_name = None
            
        field_entries_data = {}
        course_name = course_name.split('-')
        if course_name == None:
            field_entries_data['Course Name:'] = 'N/A'
        elif len(course_name) > 1:
            field_entries_data['Course Name:'] = course_name[1]
        else:
            field_entries_data['Course Name:'] = course_name[0]

        # Extract course number from the first <span> with class 'field-value'  
        course_number_element = soup.find('span', class_='field-value')
        if course_number_element:
            course_number_full = course_number_element.get_text(strip=True)
            course_number_split = course_number_full.split(':')
            course_number = course_number_split[-1] if len(course_number_split) > 1 else None
        else:
            course_number = None

        # Extract field entries labels and values
        field_entries = soup.find_all('li', class_='field-entry')
        for entry in field_entries:
            label_element = entry.find('span', class_='field-label')
            value_element = entry.find('span', class_='field-value')
            if label_element and value_element:
                label = label_element.get_text(strip=True)
                value = value_element.get_text(strip=True)
                # Replace course number value in fields
                if label == 'Course Number:':
                    value = course_number
                field_entries_data[label] = value

        return {
            'course_name': course_name.split(' - ')[1] if course_name else None,
            'field_entries': field_entries_data
        }
    else:
        print('Failed to retrieve the course page.')
        return None
    
def print_retrieved_urls():
    course_urls = get_course_urls()
    if course_urls:
        for course_url in course_urls:
            print(course_url)
    
def print_course_contents(course_url):
    course_details = get_course_info(course_url)
    if course_details:
        field_entries = course_details['field_entries']
        #print(f'Course Name: {course_details["course_name"]}')
        if field_entries:
            for label, value in field_entries.items():
                print(f'{label} {value}')
        print('-' * 50)
        
def print_all_courses():
    # Get course URLs
    course_urls = get_course_urls()
    if course_urls:
        # Print contents of each course
        for course_url in course_urls:
            print_course_contents(course_url)
    else:
        print('No course URLs found.')
    
from app import Course, Professor
    
def add_pid_to_course(cid, pid):
    course = Course.objects(cid=cid).first()
    if course:
        course.add_pid(pid)
        print(f"PID {pid} added to course with CID {cid}")
    else:
        print(f"Course with CID {cid} not found.")
        
def add_course_to_prof(pid, cid):
    professor = Professor.objects(pid=pid).first()
    if professor:
        professor.add_cid(cid)
        print(f"CID {cid} added to professor with PID {pid}")
    else:
        print(f"Professor with PID {pid} not found.")
        
def update_existing_info():
    course_details = get_course_urls()
    for course_url in course_details:
        course_info = get_course_info(course_url)
        if course_info:
            field_entries = course_info['field_entries']
            if field_entries:
                # does course exist
                if 'Course Number:' not in field_entries:
                    print("Course info not found.")
                    return
                course = Course.objects(cid=field_entries['Course Number:']).first()
                if not course:
                    if 'Syllabus' not in field_entries:
                        field_entries['Syllabus:'] = 'N/A'
                    course = Course(cid=field_entries['Course Number:'], name=field_entries['Course Name:'], lesson=field_entries["Description:"], coding=True, theory=False)
                    course.save()
                    print(f"Course {field_entries['Course Number:']} added.")
                else:
                    if ("Description:" in field_entries):
                        course.set_lesson(field_entries['Description:'])
                    print(f"Course {field_entries['Course Number:']} already exists.")
                
                if 'Instructor:' in field_entries:
                    profs = field_entries['Instructor:']
                    prof_list = profs.split(',')
                    for prof in prof_list:
                        prof = prof.strip()
                        professor = Professor.objects(name=prof).first()
                        if not professor:
                            professor = Professor(name=prof, desc="Computer Science Professor", rating=random.randint(1, 5), attendance=bool(random.getrandbits(1)))
                            professor.save()
                            print(f"Professor {prof} added.")
                        else:
                            print(f"Professor {prof} already exists.")
                        add_pid_to_course(field_entries['Course Number:'], professor.pid)
                        add_course_to_prof(professor.pid, field_entries['Course Number:'])
                else:
                    print("Instructor(s) not found.")
            else:
                print("No field entries found.")
        else:
            print("Course info not found.")
            
def cleanup_prof_cids():
    # remove cid duplicates from professor
    professors = Professor.objects()
    for professor in professors:
        cids = professor.cids
        cids = list(set(cids))
        professor.cids = cids
        professor.save()
        print(f"Professor {professor.name} cleaned up.")
    
def clear_specified_pid(pid):
    # remove specified pid from all courses
    courses = Course.objects()
    for course in courses:
        if pid in course.pids:
            course.pids.remove(pid)
            course.save()
            print(f"PID {pid} removed from course {course.cid}")
        else:
            print(f"PID {pid} not found in course {course.cid}")

# Example usage
# course_urls = get_course_urls()
# if course_urls:
#     for course_url in course_urls:
#         print(course_url)

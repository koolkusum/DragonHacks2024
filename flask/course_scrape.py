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
        field_entries_data = {}
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
        try:
            if course_name:
                course_name = course_name.split(' - ')[1]
            else:
                course_name = ""
        except IndexError:
            course_name = ""
        return {
            'course_name': course_name,
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
        print(f'Course Name: {course_details["course_name"]}')
        if field_entries:
            for label, value in field_entries.items():
                print(f'{label}: {value}')
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
    
# Example usage
course_urls = get_course_urls()
if course_urls:
    print_all_courses()

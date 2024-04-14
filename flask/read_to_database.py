def parse_boolean(value):
    return value.strip().lower() == 'true'

with open('course.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
courses = []
current_course = {}

for line in lines:
    clean_line = line.strip()
    
    if clean_line:
        if len(current_course) == 0:
            current_course['title'] = clean_line
        elif len(current_course) == 1:
            current_course['section'] = int(clean_line)
        elif len(current_course) == 2:
            current_course['description'] = clean_line
        elif len(current_course) == 3:
            current_course['professor'] = clean_line
        elif len(current_course) == 4:
            current_course['coding'] = parse_boolean(clean_line)
        elif len(current_course) == 5:
            current_course['theory'] = parse_boolean(clean_line)
            courses.append(current_course)
            current_course = {}
for course in courses:
    print(f"{course['title']}")
    print(f"{course['section']}")
    print(f"{course['description']}")
    print(f"{course['professor']}")
    print(f"{course['coding']}")
    print(f"{course['theory']}")
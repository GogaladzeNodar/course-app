structure of database - https://drawsql.app/teams/nodaaaaa/diagrams/online-course-management-system



COURSE_APP FUNCTIONAL - 
Key Features

Role-Based Access: The API strictly enforces permissions based on user roles (Teacher or Student).

# Course Creation & Management:

    Teachers can create, update, and delete courses.

    Only the course owner can modify a course's details or delete it.

# Dynamic Course Listings:

    Non-authenticated users can browse public courses.

    Students can view all public and their own enrolled courses.

    Teachers can view all public and their own courses (created or assigned).

# Teacher & Student Management:

    Course owners can add co-teachers via email.

    Course owners can remove co-teachers and students from the course.

# Flexible Enrollment System:

    Open Courses: On PUBLIC courses, students are automatically enrolled with an ACCEPTED status.

    Invite-Only Courses: On PRIVATE or INVITE_ONLY courses, a student's enrollment status is initially set to PENDING.

# Enrollment Request Management:

    Course teachers can view a list of all PENDING enrollment requests for their courses.

    Course teachers can update the status of a pending enrollment to either ACCEPTED or REJECTED.


ENDPOINTS
The following routes are available under the api/courses/ endpoint:

### Endpoints

| Endpoint                        | Method | Description                                          | Permissions                 |
|---------------------------------|--------|------------------------------------------------------|-------------------------------|
| `/`                             | GET    | Retrieve a list of accessible courses.               | IsAuthenticated, or none     |
| `/`                             | POST   | Create a new course.                                | IsAuthenticated & IsTeacher   |
| `/{id}/`                        | GET    | Retrieve course details.                            | Varies by role & visibility   |
| `/{id}/`                        | PATCH  | Update course details.                              | IsCourseOwner                 |
| `/{id}/`                        | DELETE | Delete a course.                                    | IsCourseOwner                 |
| `/{id}/add-teacher/`            | POST   | Add a teacher to a course.                          | IsCourseOwner                 |
| `/{id}/teachers/{teacher_id}/`  | DELETE | Remove a teacher from a course.                     | IsCourseOwner                 |
| `/{id}/enroll-student/`         | POST   | Request to enroll in a course.                      | IsStudent                     |
| `/{id}/students/{student_id}/`  | DELETE | Remove a student from a course.                     | IsCourseTeacher               |
| `/{id}/pending-enrollments/`    | GET    | List all pending enrollment requests.               | IsCourseTeacher               |
| `/{id}/enrollments/{enrollment_id}/` | PATCH | Update a student's enrollment status.           | IsCourseTeacher               |
| `/{id}/teachers/`               | GET    | List all teachers in a course.                      | IsAuthenticated               |
| `/{id}/students/`               | GET    | List all enrolled students in a course.             | IsAuthenticated               |

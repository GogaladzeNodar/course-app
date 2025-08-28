structure of database - https://drawsql.app/teams/nodaaaaa/diagrams/online-course-management-system



### COURSE_APP FUNCTIONAL - 
## Key Features

Role-Based Access: The API strictly enforces permissions based on user roles (Teacher or Student).

## Course Creation & Management:

    Teachers can create, update, and delete courses.

    Only the course owner can modify a course's details or delete it.

## Dynamic Course Listings:

    Non-authenticated users can browse public courses.

    Students can view all public and their own enrolled courses.

    Teachers can view all public and their own courses (created or assigned).

## Teacher & Student Management:

    Course owners can add co-teachers via email.

    Course owners can remove co-teachers and students from the course.

## Flexible Enrollment System:

    Open Courses: On PUBLIC courses, students are automatically enrolled with an ACCEPTED status.

    Invite-Only Courses: On PRIVATE or INVITE_ONLY courses, a student's enrollment status is initially set to PENDING.

## Enrollment Request Management:

    Course teachers can view a list of all PENDING enrollment requests for their courses.

    Course teachers can update the status of a pending enrollment to either ACCEPTED or REJECTED.


ENDPOINTS
The following routes are available under the api/courses/ endpoint:

## Endpoints

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



### Lectures & Assignments
This module allows teachers to manage course content by creating lectures and homework assignments, which students can then view and submit.

## Key Features

Content Management: Teachers have full CRUD access (Create, Read, Update, Delete) to lectures and homework assignments within their courses.

Content Visibility: Teachers can control the visibility of lectures using a is_published flag, allowing them to prepare content in advance without students seeing it.

Hierarchical Structure: Lectures are nested under courses, and homework assignments are nested under lectures, creating a clear and logical content hierarchy.

Student Access: Students can view lectures and assignments for courses in which they are enrolled or which are public.

### Lecture & Assignment Endpoints

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/courses/{course_id}/lectures/` | GET | List all lectures for a specific course. | `IsEnrolledStudentOrCourseTeacher` |
| `/api/courses/{course_id}/lectures/` | POST | Create a new lecture for a course. | `IsCourseTeacher` |
| `/api/courses/{course_id}/lectures/{id}/` | GET | Retrieve details for a specific lecture. | `IsEnrolledStudentOrCourseTeacher` |
| `/api/courses/{course_id}/lectures/{id}/` | PATCH | Update a lecture's details. | `IsCourseTeacher` |
| `/api/courses/{course_id}/lectures/{id}/` | DELETE | Delete a lecture. | `IsCourseTeacher` |
| `/api/courses/{course_id}/lectures/{id}/publish/` | POST | Publish a lecture, making it visible to students. | `IsCourseTeacher` |
| `/api/courses/{course_id}/lectures/{id}/unpublish/` | POST | Unpublish a lecture. | `IsCourseTeacher` |
| `/api/courses/{course_id}/lectures/{lecture_id}/assignments/` | GET | List all assignments for a specific lecture. | `IsEnrolledStudentOrCourseTeacher` |
| `/api/courses/{course_id}/lectures/{lecture_id}/assignments/` | POST | Create a new assignment for a lecture. | `IsCourseTeacher` |
| `/api/courses/{course_id}/lectures/{lecture_id}/assignments/{id}/` | GET | Retrieve details for a specific assignment. | `IsEnrolledStudentOrCourseTeacher` |
| `/api/courses/{course_id}/lectures/{lecture_id}/assignments/{id}/` | PATCH | Update an assignment's details. | `IsCourseTeacher` |
| `/api/courses/{course_id}/lectures/{lecture_id}/assignments/{id}/` | DELETE | Delete an assignment. | `IsCourseTeacher` |



### submissions - app
manage submissions for assignements

## Key Features

Submission Management: Students can submit their assignments, update them before the deadline, and delete them if needed. The system can handle single or multiple submissions based on the allow_multiple_submissions flag.

Role-Based Access: The API strictly enforces permissions to ensure security:

Students can only view and manage their own submissions and grades.

Teachers can view all submissions for their courses and are the only ones who can create or modify a grade.

Grading System: Teachers can grade submitted assignments, with the ability to update a grade if needed.

Feedback & Communication: The system allows for comments to be added to a grade, enabling communication between the teacher and the student about the assessment.

### submissions Endpoints

| Endpoint                                           | Method | Description                                       | Permissions                          |
|----------------------------------------------------|--------|---------------------------------------------------|--------------------------------------|
| /submissions/                                      | GET    | Retrieve a list of submissions for a specific assignment. | IsCourseTeacher                      |
| /submissions/                                      | POST   | Submit a homework assignment.                    | IsStudent & IsEnrolledStudent        |
| /submissions/{id}/                                 | GET    | Retrieve details of a specific submission.        | IsSubmissionOwnerOrCourseTeacher     |
| /submissions/{id}/                                 | PATCH  | Update a submitted assignment.                   | IsSubmissionOwnerOrCourseTeacher     |
| /submissions/{id}/                                 | DELETE | Delete a submitted assignment.                   | IsSubmissionOwnerOrCourseTeacher     |
| /submissions/mine/                                 | GET    | Retrieve a list of all submissions made by the current user. | IsAuthenticated                      |
| /submissions/{submission_id}/grades/               | GET    | Retrieve the grade for a specific submission.    | IsEnrolledStudentOrCourseTeacher     |
| /submissions/{submission_id}/grades/               | POST   | Create or update a grade for a specific submission. | IsCourseTeacher                      |
| /submissions/{submission_id}/grades/{grade_id}/comments/ | GET    | Retrieve comments for a specific grade.          | IsEnrolledStudentOrCourseTeacher     |
| /submissions/{submission_id}/grades/{grade_id}/comments/ | POST   | Add a comment to a grade.                        | IsAuthenticated                      |

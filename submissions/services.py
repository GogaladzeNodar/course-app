from .models import Submission, Grade
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from lectures.models import HomeworkAssignment


class SubmissionService:
    @staticmethod
    def create_submission(assignment, student, text=None):
        last_one = (
            Submission.objects.filter(assignment=assignment, student=student)
            .order_by("-submission_number")
            .first()
        )
        submission_number = (last_one.submission_number + 1) if last_one else 1

        submit_time = timezone.now()
        if assignment.due_date and submit_time > assignment.due_date:
            status = Submission.SubmissionStatus.LATE
        else:
            status = (
                Submission.SubmissionStatus.RESUBMITTED
                if last_one
                else Submission.SubmissionStatus.SUBMITTED
            )

        submission = Submission(
            assignment=assignment,
            student=student,
            submission_number=submission_number,
            text=text,
            status=status,
        )
        submission.full_clean()
        submission.save()
        return submission


class GradeService:
    @staticmethod
    def grade_letter(score):
        if score is None:
            return "NA"
        elif score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    @staticmethod
    def create_or_update_grade(submission, score, feedback, graded_by):
        try:
            grade = Grade.objects.get(submission=submission)
            grade.score = score
            grade.grade_letter = GradeService.grade_letter(score)
            grade.feedback = feedback
            grade.graded_by = graded_by
            grade.graded_at = timezone.now()
            grade.full_clean()
            grade.save()
        except ObjectDoesNotExist:
            grade = Grade(
                submission=submission,
                score=score,
                grade_letter=GradeService.grade_letter(score),
                feedback=feedback,
                graded_by=graded_by,
                graded_at=timezone.now(),
            )
            grade.full_clean()
            grade.save()
        return grade

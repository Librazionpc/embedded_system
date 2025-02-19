from sqlalchemy.ext.asyncio import AsyncSession
from v1.models.attendance import Attendance
from fastapi import HTTPException, status
from ...models.course import Course
from ...models.student import Student
from ...models.lecturer import Lecturer
from ...hardware.camera import recognize_face
from ...hardware.fingerprint import recognize_fingerprint
from datetime import datetime

class AttendanceAuthService:
    @staticmethod
    async def start_attendance_session(data: dict, session: AsyncSession):
        """
        Lecturer triggers this method to start the attendance session.
        It will check for face or fingerprint recognition for each student.
        Before starting, it verifies if the lecturer owns the course.
        """
        coursecode = data.get("coursecode")
        lecturer_email = data.get("lectureremail")
        if not lecturer_email:
            raise HTTPException(status_code=403, detail="invailid email")
        
        
        try:
            # Step 1: Verify if the lecturer owns the course by email
            course = await Course.filter_by(session, coursecode=coursecode)

            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
            
            # Check if the lecturer email matches the course's owner email
            if course.lecturer_email != lecturer_email:
                raise HTTPException(status_code=403, detail="You are not the owner of this course")

            # Step 2: Fetch all registered students for the course
            students = await Student.filter_by(session, course_id=course.id)

            if not students:
                raise HTTPException(status_code=404, detail="No students found for the course")

            attendance_list = []

            # Step 3: Iterate over all students and check for face/fingerprint
            for student in students:
                # Attempt face recognition
                # face_recognized = recognize_face(student.student_name)
                fingerprint_recognized = recognize_fingerprint(student.student_name)

                # Mark attendance
                if fingerprint_recognized:
                    # Attendance marked as present
                    attendance_status = True
                else:
                    # Attendance marked as absent
                    attendance_status = False

                # Record the attendance
                attendance = Attendance(
                    student_id=student.id,
                    course_id=course.id,
                    attendance_time=datetime.now(),
                    status=attendance_status
                )
                await attendance.new(session, attendance)
                attendance_list.append({
                    "student_name": student.student_name,
                    "status": "Present" if attendance_status else "Absent"
                })

            return {"message": "Attendance session completed", "attendance": attendance_list}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error starting attendance session: {str(e)}")

    @staticmethod
    async def mark_attendance(data: dict, session: AsyncSession):
        """Mark student attendance."""
        student_id = data.get("student_id")
        course_id = data.get("course_id")
        department_id = data.get("department_id")
        ispresent = data.get("ispresent")

        if not student_id or not course_id or not department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID, Course ID, and Department ID are required"
            )

        attendance = Attendance(
            student_id=student_id,
            course_id=course_id,
            department_id=department_id,
            ispresent=ispresent
        )

        await attendance.new(session, attendance)
        return {"message": "Attendance marked successfully"}
    
    #@staticmethod
    #async def mark_attendance_by_face(image_path, session: AsyncSession):
        """Mark attendance using face recognition."""
        try:
            # Step 1: Get the face recognition hash
            face_hash = recognize_face(image_path)
            if not face_hash:
                raise HTTPException(status_code=400, detail="Face not recognized")

            # Step 2: Find student by face hash
            student = await Student.filter_by(session, face_rec=face_hash)
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")

            # Step 3: Record attendance
            attendance = Attendance(
                student_id=student.id,
                course_id=student.course_id,
                attendance_time=datetime.now(),
                status=True  # Mark as present
            )
            await attendance.new(session, attendance)
            return {"message": "Attendance marked for student by face recognition."}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def mark_attendance_by_fingerprint(fingerprint_data, session: AsyncSession):
        """Mark attendance using fingerprint recognition."""
        try:
            # Step 1: Get the fingerprint recognition hash
            fingerprint_hash = recognize_fingerprint(fingerprint_data)
            if not fingerprint_hash:
                raise HTTPException(status_code=400, detail="Fingerprint not recognized")

            # Step 2: Find student by fingerprint hash
            student = await Student.filter_by(session, fingerprint=fingerprint_hash)
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")

            # Step 3: Record attendance
            attendance = Attendance(
                student_id=student.id,
                course_id=student.course_id,
                attendance_time=datetime.now(),
                status=True  # Mark as present
            )
            await attendance.new(session, attendance)
            return {"message": "Attendance marked for student by fingerprint."}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    @staticmethod
    async def get_attendance(student_id: int, session: AsyncSession):
        """Retrieve attendance records for a specific student."""
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID is required"
            )
        
        attendances = await Attendance.filter_by(session, student_id=student_id)
        if not attendances:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No attendance records found"
            )
        
        return attendances

    @staticmethod
    async def get_attendance_for_course(course_id: int, session: AsyncSession):
        """Retrieve attendance records for all students in a specific course."""
        if not course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course ID is required"
            )
        
        attendances = await Attendance.filter_by(session, course_id=course_id)
        if not attendances:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No attendance records found for this course"
            )
        
        return attendances

    @staticmethod
    async def get_all_attendance(session: AsyncSession):
        """Retrieve all attendance records for all students and courses."""
        attendances = await Attendance.all(session)
        if not attendances:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No attendance records found"
            )
        
        return attendances

    @staticmethod
    async def get_student_attendance_for_course(student_id: int, course_id: int, session: AsyncSession):
        """Retrieve attendance records for a specific student in a specific course."""
        if not student_id or not course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID and Course ID are required"
            )
        
        attendance = await Attendance.filter_by(session, student_id=student_id, course_id=course_id)
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No attendance records found for this student in the specified course"
            )
        
        return attendance

    @staticmethod
    async def update_attendance(attendance_id: int, data: dict, session: AsyncSession):
        """Update an existing attendance record."""
        attendance = await Attendance.get(session, attendance_id)

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        # Update fields if provided in the data
        student_id = data.get("student_id")
        course_id = data.get("course_id")
        department_id = data.get("department_id")
        ispresent = data.get("ispresent")

        if student_id:
            attendance.student_id = student_id
        if course_id:
            attendance.course_id = course_id
        if department_id:
            attendance.department_id = department_id
        if ispresent is not None:
            attendance.ispresent = ispresent

        # Commit changes to the database
        await session.commit()

        return {"message": "Attendance record updated successfully"}
    
    @staticmethod
    async def add_student_to_attendance(session: AsyncSession, lecturer_id: int, data: dict):
        """Add a student to an attendance sheet for a course."""
        student_email = data.get("studentemail")
        course_id = data.get("course_id")

        if not student_email or not course_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student email and course ID are required")

        lecturer = await Lecturer.filter_by(session, id=lecturer_id)
        if not lecturer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")

        course = await Course.filter_by(session, id=course_id, lecturer_id=lecturer_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or not owned by lecturer")

        student = await Student.filter_by(session, studentemail=student_email)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        attendance = Attendance(student_id=student.id, course_id=course.id, department_id=lecturer.department_id, ispresent=False)
        await attendance.new(session, attendance)

        return {"message": f"Student {student_email} added to attendance sheet for {course.coursename}"}
    
    @staticmethod
    async def remove_student_from_attendance(session: AsyncSession, lecturer_id: int, data: dict):
        """Remove a student from the attendance sheet."""
        student_id = data.get("student_id")
        course_id = data.get("course_id")

        if not student_id or not course_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student ID and Course ID are required")

        lecturer = await Lecturer.filter_by(session, id=lecturer_id)
        if not lecturer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")

        attendance = await Attendance.filter_by(session, student_id=student_id, course_id=course_id)
        if not attendance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")

        await Attendance.delete(session, attendance)
        return {"message": "Student removed from attendance sheet"}

    @staticmethod
    async def delete_attendance(attendance_id: int, session: AsyncSession):
        """Delete an attendance record."""
        attendance = await Attendance.get(session, attendance_id)

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        await Attendance.delete(session, attendance)
        await session.commit()
        return {"message": "Attendance record deleted successfully"}

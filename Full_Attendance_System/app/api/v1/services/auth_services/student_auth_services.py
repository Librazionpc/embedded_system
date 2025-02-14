from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.models.student import Student
from app.api.v1.utils.jwt import JWTUtils
from app.api.v1.utils.hash_pwd import HashUtils
from app.api.v1.services.otp.generate_otp import OTP
from app.api.v1.services.emailservices.emailservice import EmailService
from fastapi import HTTPException, status

class StudentAuthService:
    
    @staticmethod
    async def register_student(data: dict, session: AsyncSession):
        """Register a new student with hashed password."""
        email = data.get("studentemail")
        password = data.get("password")

        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )

        hashed_password = HashUtils.hash_password(password)

        new_student = Student(
            studentname=data.get("studentname"),
            studentemail=email,
            studentphone=data.get("studentphone"),
            department_id=data.get("department_id"),
            password=hashed_password,
            fingerprint=data.get('fingerprint')
        )

        await new_student.new(session, new_student)
        return {"message": "Student registered successfully", "student": new_student}

    @staticmethod
    async def authenticate_student(data: dict, session: AsyncSession):
        """Authenticate student by checking email, password, and fingerprint."""
        email = data.get("studentemail")
        password = data.get("password")
        fingerprint = data.get('fingerprint')

        if not email or not password or not fingerprint:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email, password, and fingerprint are required"
            )

        student = await Student.filter_by(session, studentemail=email)

        if not student or not HashUtils.verify_password(password, student.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if student.fingerprint != fingerprint:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unknown device"
            )

        token = JWTUtils.generate_token(student.id, "student", fingerprint)
        return {"message": "Authentication successful", "token": token}

    @staticmethod
    async def validate_email(data: dict, session: AsyncSession):
        """Validate email by generating an OTP."""
        email = data.get("email")
        fingerprint = data.get("fingerprint")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )

        user = await OTP.get_otp(data, session, Student, fingerprint)
        await EmailService.send_otp(email=email, otp=user.otp)
        return {"message": "OTP sent to email"}

    @staticmethod
    async def reset_password(data: dict, session: AsyncSession):
        """Reset student password after validating OTP."""
        email = data.get("studentemail")
        password = data.get("password")
        newpassword = data.get("newpassword")
        otp = data.get("otp-code")
        fingerprint = data.get('fingerprint')

        if not email or not password or not otp or not fingerprint:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required"
            )

        student = await Student.filter_by(session, studentemail=email)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        if HashUtils.verify_password(newpassword, student.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the old password"
            )
        
        is_valid = await OTP.validate_otp(data, session, student)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )

        if student.fingerprint != fingerprint:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unknown device"
            )

        hashed_password = HashUtils.hash_password(newpassword)
        student.password = hashed_password
        await Student.update(session, student)

        return {"message": "Password reset successful"}

    @staticmethod
    async def delete(data: dict, session: AsyncSession):
        """Delete a student record."""
        studentemail = data.get("studentemail")
        if not studentemail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided"
            )

        student = await Student.filter_by(session=session, studentemail=studentemail)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        await Student.delete(session, student)
        return {"message": "Student record deleted successfully"}

    @staticmethod
    async def update_student(data: dict, session: AsyncSession, student_id: int):
        """Update a student's details."""
        student = await Student.get(session, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        # Update fields if provided in the data
        studentname = data.get("studentname")
        studentphone = data.get("studentphone")
        department_id = data.get("department_id")


        if studentname:
            student.studentname = studentname
        if studentphone:
            student.studentphone = studentphone
        if department_id:
            student.department_id = department_id


        # Commit changes to the database
        await session.commit()

        return {"message": "Student details updated successfully", "student": student}

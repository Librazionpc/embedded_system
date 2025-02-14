from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.models.lecturer import Lecturer
from app.api.v1.utils.jwt import JWTUtils
from app.api.v1.utils.hash_pwd import HashUtils
from app.api.v1.services.otp.generate_otp import OTP
from app.api.v1.services.emailservices.emailservice import EmailService

class LecturerAuthService:

    @staticmethod
    async def register_lecturer(data: dict, session: AsyncSession):
        """Register a new lecturer with hashed password."""
        email = data.get("lectureremail")
        password = data.get("password")

        if not email or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password required")

        hashed_password = HashUtils.hash_password(password)

        new_lecturer = Lecturer(
            lecturername=data.get("lecturername"),
            lectureremail=email,
            lecturerphone=data.get("lecturerphone"),
            department_id=data.get("department_id"),
            password=hashed_password,
            fingerprint=data.get('fingerprint')
        )

        await new_lecturer.new(session, new_lecturer)
        return new_lecturer

    @staticmethod
    async def authenticate_lecturer(data: dict, session: AsyncSession):
        """Authenticate lecturer by checking email, password, and fingerprint."""
        email = data.get("lectureremail")
        password = data.get("password")
        fingerprint = data.get('fingerprint')

        if not email or not password or not fingerprint:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email, password, and fingerprint are required")

        lecturer = await Lecturer.filter_by(session, email=email)

        if not lecturer or not HashUtils.verify_password(password, lecturer.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        if lecturer.fingerprint != fingerprint:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown device")

        return JWTUtils.generate_token(lecturer.id, "lecturer", fingerprint)

    @staticmethod
    async def validate_email(data: dict, session: AsyncSession):
        """Validate email by generating an OTP"""
        email = data.get("lectureremail")
        fingerprint = data.get("fingerprint")
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")

        user = await OTP.get_otp(data, session, Lecturer, fingerprint)
        return await EmailService.send_otp(email=email, otp=user.otp)

    @staticmethod
    async def update_lecturer(data: dict, session: AsyncSession, lecturer_id: int):
        """Update lecturer information."""
        lecturer = await Lecturer.filter_by(session, id=lecturer_id)

        if not lecturer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")

        # Update fields
        lecturer.lecturername = data.get("lecturername", lecturer.lecturername)
        lecturer.lecturerphone = data.get("lecturerphone", lecturer.lecturerphone)
        lecturer.department_id = data.get("department_id", lecturer.department_id)
    

        return await lecturer.update(session, lecturer)
    
    @staticmethod
    async def reset_password(data: dict, session: AsyncSession):
        """Reset lecturer password after validating OTP."""
        email = data.get("lectureremail")
        password = data.get("password")
        newpassword = data.get("newPassword")
        otp = data.get("otp-code")
        fingerprint = data.get('fingerprint')

        if not email or not password or not otp or not fingerprint:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All fields are required")

        lecturer = await Lecturer.filter_by(session, email=email)
        if not lecturer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")
        if HashUtils.verify_password(newpassword, lecturer.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different from the old password")
        
        is_valid = await OTP.validate_otp(data, session, lecturer)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

        if lecturer.fingerprint != fingerprint:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown device")

        hashed_password = HashUtils.hash_password(newpassword)
        lecturer.password = hashed_password

        return await lecturer.update(session, lecturer)
    
    @staticmethod
    async def delete(data: dict, session: AsyncSession):
        lectureremail = data.get("lectureremail")
        if not lectureremail:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided")

        lecturer = await Lecturer.filter_by(session=session, email=lectureremail)
        if not lecturer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")
        return await Lecturer.delete(session, lecturer)

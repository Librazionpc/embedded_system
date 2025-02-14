from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.models.facultyadmin import FacultyAdmin
from app.api.v1.utils.jwt import JWTUtils
from app.api.v1.utils.hash_pwd import HashUtils
from app.api.v1.services.otp.generate_otp import OTP
from app.api.v1.services.emailservices.emailservice import EmailService

class FacultyAdminAuthService:
    
    @staticmethod
    async def register_admin(data: dict, session: AsyncSession):
        """Register a new admin with hashed password."""
        email = data.get("facultyemail")
        password = data.get("password")

        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")
        elif not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password required")
        
        hashed_password = HashUtils.hash_password(password)

        new_admin = FacultyAdmin(
            facultyname=data.get("facultyname"),
            facultyemail=email,
            facultyphone=data.get("facultyphone"),
            facultyaddress=data.get("facultyaddress"),
            password=hashed_password,
            fingerprint=data.get("fingerprint")
        )

        await new_admin.new(session, new_admin)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Admin registered successfully", "data": new_admin.to_dict()})

    @staticmethod
    async def authenticate_admin(data: dict, session: AsyncSession):
        """Authenticate admin by checking email, password, and fingerprint."""
        email = data.get("facultyemail")
        password = data.get("password")
        fingerprint = data.get("fingerprint")

        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")
        elif not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password required")
        
        admin = await FacultyAdmin.filter_by(session, email=email)
        if not admin or not HashUtils.verify_password(password, admin.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if admin.fingerprint != fingerprint:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown device")

        token = JWTUtils.generate_token(admin.id, "admin", fingerprint)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Login successful", "token": token})

    @staticmethod
    async def validate_email(data: dict, session: AsyncSession):
        """Validate email by generating an OTP."""
        email = data.get("email")
        fingerprint = data.get("fingerprint")
        
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")
        
        user = await OTP.get_otp(data, session, FacultyAdmin, fingerprint)
        await EmailService.send_otp(email=email, otp=user.otp)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "OTP sent successfully"})

    @staticmethod
    async def reset_password(data: dict, session: AsyncSession):
        """Reset admin password after validating OTP."""
        email = data.get("facultyemail")
        password = data.get("password")
        otp = data.get("otp")
        newpassword = data.get("newpassword")
        fingerprint = data.get("fingerprint")

        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")
        elif not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password required")
        elif not newpassword:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password required")
        elif not otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP required")

        admin = await FacultyAdmin.filter_by(session, email=email)
        if not admin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

        if HashUtils.verify_password(newpassword, admin.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different from the old password")
        
        is_valid = await OTP.validate_otp(data, session, FacultyAdmin)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

        if admin.fingerprint != fingerprint:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown device")

        hashed_password = HashUtils.hash_password(newpassword)
        admin.password = hashed_password
        admin.fingerprint = fingerprint
        await FacultyAdmin.update(session, admin)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password reset successfully"})

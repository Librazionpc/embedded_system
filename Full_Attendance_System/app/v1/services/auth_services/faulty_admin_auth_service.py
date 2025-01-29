from sqlalchemy.ext.asyncio import AsyncSession
from app.v1.models.faultyadmin import FaultyAdmin
from app.v1.utils.jwt import JWTUtils
from app.v1.utils.hash_pwd import HashUtils
from app.v1.services.otp.generate_otp import OTP
from app.v1.services.emailservices.emailservice import EmailService

class FaultyAdminAuthService:
    
    @staticmethod
    async def register_admin(data: dict, session: AsyncSession):
        """Register a new admin with hashed password."""
        email = data.get("faultyemail")
        password = data.get("password")

        if not email or not password:
            return {"error": "Email and password required"}
        
        hashed_password = HashUtils.hash_password(password)

        new_admin = FaultyAdmin(
            faultyname=data.get("faultyname"),
            faultyemail=email,
            faultyphone=data.get("faultyphone"),
            faultyaddress=data.get("faultyaddress"),
            department_id=data.get("department_id"),
            password=hashed_password,
            fingerprint=data.get('fingerprint')
        )

        await new_admin.new(session, new_admin)
        return new_admin

    @staticmethod
    async def authenticate_admin(data: dict, session: AsyncSession):
        """Authenticate admin by checking email, password, and fingerprint."""
        email = data.get("faultyemail")
        password = data.get("password")
        fingerprint = data.get('fingerprint')

        if not email or not password or not fingerprint:
            return {"error": "Email, password, and fingerprint are required"}

        admin = await FaultyAdmin.filter_by(session, email=email)

        if not admin or not HashUtils.verify_password(password, admin.password):
            return {"error": "Invalid credentials"}

        if admin.fingerprint != fingerprint:
            return {"error": "Unknown device"}

        return JWTUtils.generate_token(admin.id, "admin", fingerprint)

    @staticmethod
    async def validate_email(data: dict, session: AsyncSession):
        """Validate email by generating an OTP"""
        email = data.get("email")
        fingerprint = data.get("fingerprint")
        if not email:
            return {"error": "Email required"}

        user = await OTP.get_otp(data, session, FaultyAdmin, fingerprint)
        return await EmailService.send_otp(email=email, otp=user.otp)

    @staticmethod
    async def reset_password(data: dict, session: AsyncSession):
        """Reset admin password after validating OTP."""
        email = data.get("faultyemail")
        password = data.get("password")
        newpassword = data.get("newpassword")
        otp = data.get("otp-code")
        fingerprint = data.get('fingerprint')

        if not email or not password or not otp or not fingerprint:
            return {"error": "All fields are required"}

        admin = await FaultyAdmin.filter_by(session, email=email)
        if not admin:
            return {"error": "Admin not found"}

        if HashUtils.verify_password(newpassword, FaultyAdmin.password):
            return {"Error: New password must be different from the old password"}
        
        is_valid = await OTP.validate_otp(data, session, FaultyAdmin)
        if not is_valid:
            return {"error": "Invalid OTP"}

        if admin.fingerprint != fingerprint:
            return {"error": "Unknown device"}

        hashed_password = HashUtils.hash_password(newpassword)
        admin.password = hashed_password
        admin.fingerprint = fingerprint

        return await FaultyAdmin.update(session, admin)

from sqlalchemy.ext.asyncio import AsyncSession
from app.v1.models.faultyadmin import FaultyAdmin
from app.v1.utils.jwt import JWTUtils
from app.v1.utils.hash_pwd import HashUtils

class FaultyAdminAuthService:
    
    @staticmethod
    async def register_admin(data: dict, session: AsyncSession):
        """
        Register a new admin with hashed password.
        Extracts email and password from the data dictionary.
        """
        email = data.get("faultyemail")
        password = data.get("password")
        
        if not email or not password:
            return None  # Return an appropriate response or raise an exception if email or password is missing
        
        hashed_password = HashUtils.hash_password(password)
        
        # Creating the new admin instance with other details from data
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
        """
        Authenticate admin by checking email and password.
        Extracts email and password from the data dictionary.
        """
        email = data.get("faultyemail")
        password = data.get("password")
        fingerprint= data.get('fingerprint')

        if not email or not password or not fingerprint:
            return None  # Return an appropriate response or raise an exception if email or password is missing
        
        
        admin = await FaultyAdmin.filter_by(session, email=email)
        
        if admin.fingerprint != fingerprint:
            print("unkown device")

        if not admin or not HashUtils.verify_password(password, admin.password):
            return None  # Authentication failed

        # Generate JWT token upon successful authentication
        return JWTUtils.generate_token(admin.id, "admin", fingerprint)

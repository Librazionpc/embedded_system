from sqlalchemy.ext.asyncio import AsyncSession
class OTP:
    @staticmethod
    async def get_otp(data: dict, session: AsyncSession, model, fingerprint):
        """Fetch OTP for any model dynamically"""
        email = data.get("email")
        if not email:
            return {"error": "Email required"}

        otp_data = await model.get_otp(session, email, fingerprint)
        return otp_data

    @staticmethod
    async def validate_otp(data: dict, session: AsyncSession, model):
        email = data.get('email')
        otp = data.get("otp-code")

        return await model.validate(session, email, otp_code=otp)

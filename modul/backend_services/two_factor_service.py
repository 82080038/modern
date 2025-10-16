"""
Two-Factor Authentication Service
Implementasi TOTP (Time-based One-Time Password) untuk keamanan trading platform
"""
import pyotp
import qrcode
import io
import base64
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.security import User, TwoFactorAuth
from app.database import get_db
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class TwoFactorService:
    """Service untuk Two-Factor Authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_secret(self, user_id: int) -> Dict:
        """Generate TOTP secret untuk user"""
        try:
            # Check if 2FA is enabled
            if not settings.TWO_FACTOR_ENABLED:
                return {
                    "error": "Two-Factor Authentication is disabled in development mode",
                    "development_mode": True
                }
            # Generate random secret
            secret = pyotp.random_base32()
            
            # Get user info
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Create TOTP object
            totp = pyotp.TOTP(secret)
            
            # Generate QR code
            qr_data = totp.provisioning_uri(
                name=user.email,
                issuer_name="Trading Platform Modern"
            )
            
            # Create QR code image
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Convert to base64
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Save to database
            two_factor = TwoFactorAuth(
                user_id=user_id,
                secret=secret,
                is_enabled=False
            )
            self.db.add(two_factor)
            self.db.commit()
            
            return {
                "secret": secret,
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "manual_entry_key": secret,
                "issuer": "Trading Platform Modern",
                "account_name": user.email
            }
            
        except Exception as e:
            logger.error(f"Error generating 2FA secret: {e}")
            return {"error": str(e)}
    
    def verify_token(self, user_id: int, token: str) -> Dict:
        """Verify TOTP token"""
        try:
            # Check if 2FA is enabled
            if not settings.TWO_FACTOR_ENABLED:
                return {
                    "valid": True,
                    "message": "2FA is disabled in development mode",
                    "development_mode": True
                }
            # Get user's 2FA record
            two_factor = self.db.query(TwoFactorAuth).filter(
                TwoFactorAuth.user_id == user_id
            ).first()
            
            if not two_factor:
                return {"error": "2FA not set up for user"}
            
            # Create TOTP object
            totp = pyotp.TOTP(two_factor.secret)
            
            # Verify token
            is_valid = totp.verify(token, valid_window=1)
            
            if is_valid:
                return {"valid": True, "message": "Token verified successfully"}
            else:
                return {"valid": False, "message": "Invalid token"}
                
        except Exception as e:
            logger.error(f"Error verifying 2FA token: {e}")
            return {"error": str(e)}
    
    def enable_2fa(self, user_id: int, token: str) -> Dict:
        """Enable 2FA setelah verifikasi token"""
        try:
            # Verify token first
            verification = self.verify_token(user_id, token)
            if not verification.get("valid"):
                return {"error": "Invalid token"}
            
            # Enable 2FA
            two_factor = self.db.query(TwoFactorAuth).filter(
                TwoFactorAuth.user_id == user_id
            ).first()
            
            if two_factor:
                two_factor.is_enabled = True
                self.db.commit()
                
                return {"success": True, "message": "2FA enabled successfully"}
            else:
                return {"error": "2FA setup not found"}
                
        except Exception as e:
            logger.error(f"Error enabling 2FA: {e}")
            return {"error": str(e)}
    
    def disable_2fa(self, user_id: int, token: str) -> Dict:
        """Disable 2FA dengan verifikasi token"""
        try:
            # Verify token first
            verification = self.verify_token(user_id, token)
            if not verification.get("valid"):
                return {"error": "Invalid token"}
            
            # Disable 2FA
            two_factor = self.db.query(TwoFactorAuth).filter(
                TwoFactorAuth.user_id == user_id
            ).first()
            
            if two_factor:
                two_factor.is_enabled = False
                self.db.commit()
                
                return {"success": True, "message": "2FA disabled successfully"}
            else:
                return {"error": "2FA setup not found"}
                
        except Exception as e:
            logger.error(f"Error disabling 2FA: {e}")
            return {"error": str(e)}
    
    def is_2fa_enabled(self, user_id: int) -> bool:
        """Check if 2FA is enabled for user"""
        try:
            two_factor = self.db.query(TwoFactorAuth).filter(
                TwoFactorAuth.user_id == user_id,
                TwoFactorAuth.is_enabled == True
            ).first()
            
            return two_factor is not None
            
        except Exception as e:
            logger.error(f"Error checking 2FA status: {e}")
            return False
    
    def generate_backup_codes(self, user_id: int) -> Dict:
        """Generate backup codes untuk 2FA"""
        try:
            import secrets
            import string
            
            # Generate 10 backup codes
            backup_codes = []
            for _ in range(10):
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                backup_codes.append(code)
            
            # Save backup codes (hashed)
            import hashlib
            hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes]
            
            # Update user's backup codes
            two_factor = self.db.query(TwoFactorAuth).filter(
                TwoFactorAuth.user_id == user_id
            ).first()
            
            if two_factor:
                two_factor.backup_codes = hashed_codes
                self.db.commit()
            
            return {
                "backup_codes": backup_codes,
                "message": "Save these backup codes securely. They can only be used once."
            }
            
        except Exception as e:
            logger.error(f"Error generating backup codes: {e}")
            return {"error": str(e)}
    
    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """Verify backup code"""
        try:
            import hashlib
            
            two_factor = self.db.query(TwoFactorAuth).filter(
                TwoFactorAuth.user_id == user_id
            ).first()
            
            if not two_factor or not two_factor.backup_codes:
                return False
            
            # Check if code matches any backup code
            hashed_code = hashlib.sha256(code.encode()).hexdigest()
            
            if hashed_code in two_factor.backup_codes:
                # Remove used backup code
                two_factor.backup_codes.remove(hashed_code)
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying backup code: {e}")
            return False

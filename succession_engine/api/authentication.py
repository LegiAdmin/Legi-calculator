
import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SupabaseUser:
    """
    Ephemeral user object for Supabase JWT authentication.
    DRF requires request.user to have is_authenticated property.
    """
    def __init__(self, uid, email=None):
        self.id = uid
        self.pk = uid
        self.email = email
        self.username = email or uid

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class SupabaseAuthentication(BaseAuthentication):
    """
    Custom Authentication class to verify Supabase JWT tokens.
    """

    def authenticate(self, request):
        # 1. Get the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None  # No header = No auth attempted (DRF handles 401 if permission required)

        try:
            # 2. Parse Bearer token
            prefix, token = auth_header.split()
            if prefix.lower() != 'bearer':
                raise AuthenticationFailed('Authorization header must start with Bearer')
            
            # 3. Verify Token
            # We use the SUPABASE_JWT_SECRET from settings to decode and verify the signature
            # Algorithms is usually HS256 for Supabase
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=['HS256'],
                audience="authenticated" # Supabase default audience
            )
            
            # 4. Create Ephemeral User
            user_id = payload.get('sub')
            email = payload.get('email', '')
            
            # Return SupabaseUser (not Django User to avoid is_authenticated setter issue)
            user = SupabaseUser(uid=user_id, email=email)
            
            return (user, payload)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except ValueError:
            raise AuthenticationFailed('Invalid Authorization header format')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')

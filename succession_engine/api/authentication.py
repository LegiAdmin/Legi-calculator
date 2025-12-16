
import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

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
            
            # 4. Create/Get User (Stateless)
            # We map the Supabase UUID 'sub' to a Django User.
            # Strategy: We don't necessarily need to persist users in SQLite if logic is stateless.
            # But DRF expects a request.user.
            # We create a simple ephemeral user or look it up.
            
            user_id = payload.get('sub')
            email = payload.get('email', '')
            
            # Option A: Ephemeral User (Fastest for pure logic API)
            user = User(username=user_id, email=email)
            user.is_authenticated = True
            
            return (user, payload)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except ValueError:
            raise AuthenticationFailed('Invalid Authorization header format')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')

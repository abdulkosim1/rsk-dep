from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from client.models import CustomToken
from rest_framework_simplejwt.authentication import JWTAuthentication

class ClientTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            auth_type, token = auth_header.split()
        except ValueError:
            return None

        if auth_type.lower() != 'bearer' and auth_type.lower() != 'token':
            return None

        try:
            client = CustomToken.objects.get(key=token).client
        except CustomToken.DoesNotExist:
            # If the token is not found in CustomToken, try JWTAuthentication
            user, _ = JWTAuthentication().authenticate(request)
            if user:
                return (user, None)
            raise AuthenticationFailed('Invalid token.')

        return (client, None)

    def authenticate_header(self, request):
        return 'Token'
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
import requests
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.conf import settings
import jwt
from django.conf import settings
from .models import UserProfile, Role
from jwt.algorithms import RSAAlgorithm
import json
from django.contrib.auth import authenticate
from django.http import HttpResponse

@login_required(login_url='login_redirect')
def home(request):
    return render(request, 'core/home.html')
    
def health_check(request):
    return HttpResponse("OK", status=200)

def login_redirect(request):
    login_url = (
        f'https://{settings.COGNITO_DOMAIN}/login'
        f'?response_type=code'
        f'&client_id={settings.COGNITO_CLIENT_ID}'
        f'&redirect_uri={settings.COGNITO_REDIRECT_URI}'
    )
    return redirect(login_url)


def role_redirect(request, user):
    if not user.is_authenticated:
        return redirect('login')
    if user.role.role_id == 'Administrator':
        return redirect('user_management')
    elif user.role.role_id == 'Manager':
        return redirect('subject_instances')
    elif user.role.role_id == 'Lecturer':
        return redirect('instance_list')
    return redirect('home')


def cognito_callback(request):
    code = request.GET.get('code')
    if code:
        # Exchange code for tokens
        token_response = exchange_code_for_tokens(code)
        if token_response:
            id_token = token_response.get('id_token')
            user_info = decode_id_token(id_token)
            if user_info:
                user = authenticate_cognito_user(user_info)
                if user:
                    login(request, user)
                    return role_redirect(request, user)
    return redirect('home')  # Redirect to home on failure


def exchange_code_for_tokens(code):
    token_url = f'https://{settings.COGNITO_DOMAIN}/oauth2/token'
    redirect_uri = settings.COGNITO_REDIRECT_URI
    client_id = settings.COGNITO_CLIENT_ID
    client_secret = settings.COGNITO_CLIENT_SECRET

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
    }
    auth = (client_id, client_secret)  # If using client secret

    response = requests.post(token_url, data=data, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def decode_id_token(id_token):
    # Fetch Cognito's public keys
    jwk_url = f'https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json'
    jwk_response = requests.get(jwk_url)
    jwk_keys = jwk_response.json()['keys']

    # Get the kid from the token header
    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header['kid']

    # Find the public key in the JWKS with a matching kid
    public_key = None
    for jwk_key in jwk_keys:
        if jwk_key['kid'] == kid:
            public_key = RSAAlgorithm.from_jwk(json.dumps(jwk_key))
            break

    if public_key is None:
        print('Public key not found in JWKS')
        return None

    # Decode the token
    try:
        decoded_token = jwt.decode(
            id_token,
            public_key,
            algorithms=['RS256'],
            audience=settings.COGNITO_CLIENT_ID,
        )
        return decoded_token
    except jwt.InvalidTokenError as e:
        print('Invalid token:', e)
        return None


def authenticate_cognito_user(user_info):
    user = authenticate(user_info=user_info)
    return user


def logout_view(request):
    logout(request)
    return redirect('home')


def is_lecturer(user):
    return user.is_authenticated and user.role.role_id == 'Lecturer'


def set_testing_role(request):
    if request.user.email == 'testing@fakeuniversity.edu':
        testing_role = Role.objects.get(role_id='Testing')
        request.user.role = testing_role
        request.user.save()
    print(request.user.role.role_id)
    return redirect('home')

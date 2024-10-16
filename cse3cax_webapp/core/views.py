# 
# Views for University Testing System
# ====================================
# This file defines the view functions for handling user authentication, redirection based on roles, 
# Cognito integration, and health checks.
#
# File: views.py
# Author: Jacob Paff
# Revisions:
#   - 17-09-24: Initial file created by Jacob Paff. Added basic role redirection, login, and logout.
#   - 19-09-24: Implemented Cognito callback handling and role assignment for testing users.
#   - 08-10-24: Fixed bug in role_redirect where unauthenticated users were redirected incorrectly.
#     19-09-24: Added health check endpoint

from django.contrib.auth import logout
from django.shortcuts import redirect, render
import requests
from django.contrib.auth import login
from django.conf import settings
import jwt
from django.conf import settings
from .models import Role
from jwt.algorithms import RSAAlgorithm
import json
from django.contrib.auth import authenticate
from django.http import HttpResponse

# View for rendering the home page
def home(request):
    return render(request, 'home.html')

# Health check view to return a simple status
def health_check(request):
    return HttpResponse("OK", status=200)

# Redirect to Cognito login page
def login_redirect(request):
    login_url = (
        f'https://{settings.COGNITO_DOMAIN}/login'
        f'?response_type=code'
        f'&client_id={settings.COGNITO_CLIENT_ID}'
        f'&redirect_uri={settings.COGNITO_REDIRECT_URI}'
    )
    return redirect(login_url)

# Redirect users to the correct dashboard based on their role
def role_redirect(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login_redirect')
    if user.role_id == 'Testing':
        return redirect('user_management')
    if user.role_id == 'Administrator':
        return redirect('user_management')
    elif user.role_id == 'Manager':
        return redirect('subject_instances')
    elif user.role_id == 'Lecturer':
        return redirect('instance_list')
    return redirect('login')

# Handle Cognito callback and authenticate the user
def cognito_callback(request):
    code = request.GET.get('code')
    if code:
        # Exchange authorization code for tokens
        token_response = exchange_code_for_tokens(code)
        if token_response:
            id_token = token_response.get('id_token')
            user_info = decode_id_token(id_token)
            if user_info:
                user = authenticate_cognito_user(user_info)
                if user:
                    login(request, user)
                    return role_redirect(request)
    return redirect('home')

# Exchange authorization code for Cognito tokens
def exchange_code_for_tokens(code):
    token_url = f'https://{settings.COGNITO_DOMAIN}/oauth2/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.COGNITO_REDIRECT_URI,
        'client_id': settings.COGNITO_CLIENT_ID,
    }
    auth = (settings.COGNITO_CLIENT_ID, settings.COGNITO_CLIENT_SECRET)

    response = requests.post(token_url, data=data, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Decode the ID token using Cognito's public keys
def decode_id_token(id_token):
    jwk_url = f'https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json'
    jwk_response = requests.get(jwk_url)
    jwk_keys = jwk_response.json()['keys']

    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header['kid']

    public_key = None
    for jwk_key in jwk_keys:
        if jwk_key['kid'] == kid:
            public_key = RSAAlgorithm.from_jwk(json.dumps(jwk_key))
            break

    if public_key is None:
        return None

    try:
        decoded_token = jwt.decode(
            id_token,
            public_key,
            algorithms=['RS256'],
            audience=settings.COGNITO_CLIENT_ID,
        )
        return decoded_token
    except jwt.InvalidTokenError as e:
        return None

# Authenticate the Cognito user
def authenticate_cognito_user(user_info):
    user = authenticate(user_info=user_info)
    return user

# Logout the current user
def logout_view(request):
    logout(request)
    return redirect('home')

# Check if a user is a lecturer
def is_lecturer(user):
    return user.is_authenticated and user.role.role_id == 'Lecturer'

# Set the testing role for specific users
def set_testing_role(request):
    if request.user.email == 'testing@fakeuniversity.edu':
        testing_role = Role.objects.get(role_id='Testing')
        request.user.role = testing_role
        request.user.save()
    return redirect('home')

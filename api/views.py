import datetime
import json
import random as r
import re
from braces.views import CsrfExemptMixin
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from rest_framework import viewsets, renderers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_social_oauth2.views import ConvertTokenView, TokenView
from oauth2_provider.admin import access_token_model, application_model

from backend import settings
from . import permissions

from .serializers import *


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


@api_view(['GET'])
@permission_classes([AllowAny])
def send_confirm_code(request, phone):
    twenty_min = datetime.datetime.now() - datetime.timedelta(minutes=20)
    try:
        mobile_user = User.objects.get(username=phone)
        return Response({}, status=status.HTTP_409_CONFLICT)
    except User.DoesNotExist:
        pass
    phone_confirmation = ref_model.PhoneConfirmationCode.objects.filter(phone=phone, is_active=True,
                                                                        is_confirm=False,
                                                                        created_at__range=[twenty_min,
                                                                                           datetime.datetime.now()]).last()
    if not phone_confirmation:
        otp = ""
        for i in range(6):
            otp += str(r.randint(1, 9))
        ref_model.PhoneConfirmationCode.objects.create(code=otp, phone=phone, is_active=True)

    return Response({}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def forgot_send_confirm_code(request, phone):
    twenty_min = datetime.datetime.now() - datetime.timedelta(minutes=20)

    mobile_user = get_object_or_404(User, username=phone)
    phone_confirmation = ref_model.ForgotPassConfirmationCode.objects.filter(phone=phone, is_active=True,
                                                                             is_confirm=False,
                                                                             created_at__range=[twenty_min,
                                                                                                datetime.datetime.now()]).last()

    if not phone_confirmation:
        otp = ""
        for i in range(6):
            otp += str(r.randint(1, 9))
        ref_model.ForgotPassConfirmationCode.objects.create(code=otp, phone=phone, is_active=True)

    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_confirm_code(request):
    confirm_serializer = ForgotConfirmCodeSerializer(data=request.data, partial=True)
    if confirm_serializer.is_valid():
        confirm_phone = get_object_or_404(ref_model.ForgotPassConfirmationCode.objects,
                                          **confirm_serializer.validated_data)
        confirm_serializer.update(confirm_phone, validated_data=confirm_serializer.validated_data)
    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_new_pass(request):
    confirm_serializer = ForgotNewPassSerializer(data=request.data, partial=True)
    if confirm_serializer.is_valid():
        user = User.objects.get(username=confirm_serializer.data['phone'])
        user.set_password(confirm_serializer.data['password'])
        user.save()
        return Response({}, status=status.HTTP_200_OK)
    return Response(confirm_serializer.data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_phone_code(request):
    confirm_serializer = PhoneConfirmCodeSerializer(data=request.data, partial=True)
    if confirm_serializer.is_valid():
        confirm_phone = get_object_or_404(ref_model.PhoneConfirmationCode.objects, **confirm_serializer.validated_data)
        confirm_serializer.update(confirm_phone, validated_data=confirm_serializer.validated_data)
    return Response({}, status=status.HTTP_200_OK)




def _get_profile(user):
    profile_serializer =  FarmerProfileSerializer(user.farmer, many=False, read_only=True)

    return profile_serializer


class UserRegister(CsrfExemptMixin, OAuthLibMixin, APIView):
    permission_classes = (AllowAny,)
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def post(self, request):
        if request.auth is None:
            request._request.POST = request._request.POST.copy()
            request._request.POST["grant_type"] = "password"
            request._request.POST["client_id"] = application_model.objects.last(
            ).client_id
            request._request.POST["client_secret"] = application_model.objects.last(
            ).client_secret
            request._request.POST["username"] = request.data.get('username')
            request._request.POST["password"] = request.data.get('password')

            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        req_data = serializer.validated_data

                        user = User.objects.create_user(username=req_data['username'])
                        user.set_password(req_data['password'])
                        user.first_name = req_data['name']
                        user.save()
                        register_role_type(user, req_data)

                    url, headers, body, token_status = self.create_token_response(request._request)
                    if token_status != 200:
                        raise Exception(json.loads(body).get("error_description", ""))
                    response = Response(data=json.loads(body), status=token_status)
                    for k, v in headers.items():
                        response[k] = v
                    if not response.status_code == 200:
                        return response
                    reg_user = access_token_model.objects.get(
                        token=response.data['access_token']).user
                    response.data['profile'] = _get_profile(reg_user).data

                    return response
                except Exception as e:
                    print(e)
                    return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
        else:
            if request.user.is_authenticated:
                register_role_type(request.user, request.data)
                reg_user = User.objects.get(pk=request.user.pk)
                return Response({'profile': {**_get_profile(reg_user).data},
                              },
                                status=status.HTTP_200_OK)
            else:
                return Response(data={"error": 'Ийм хэрэглэгчийн нэртэй хэрэглэгч өмнө нь бүртгүүлсэн байна.'},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({reg}, status=status.HTTP_403_FORBIDDEN)


class AdminTokenView(TokenView):

    def post(self, request, *args, **kwargs):
        request._request.POST = request._request.POST.copy()
        request._request.POST["grant_type"] = "password"
        request._request.POST["client_id"] = application_model.objects.last(
        ).client_id
        request._request.POST["client_secret"] = application_model.objects.last(
        ).client_secret
        request._request.POST["username"] = request.data.get('username')
        request._request.POST["password"] = request.data.get('password')

        url, headers, body, status = self.create_token_response(
            request._request)
        response = Response(data=json.loads(body), status=status)

        for k, v in headers.items():
            response[k] = v
        if not response.status_code == 200:
            return response
        user = access_token_model.objects.get(
            token=response.data['access_token']).user
        if user.role.is_admin or user.role.is_agronomer:
            response.data['user_id'] = user.id
            response.data['role'] = user.role.user_type
        else:
            raise PermissionDenied('your not admin or agro guy go fuck')

        return response


class MyTokenView(TokenView):

    def post(self, request, *args, **kwargs):
        request._request.POST = request._request.POST.copy()
        request._request.POST["grant_type"] = "password"
        request._request.POST["client_id"] = application_model.objects.last(
        ).client_id
        request._request.POST["client_secret"] = application_model.objects.last(
        ).client_secret
        request._request.POST["username"] = request.data.get('username')
        request._request.POST["password"] = request.data.get('password')
        url, headers, body, status = self.create_token_response(
            request._request)
        response = Response(data=json.loads(body), status=status)

        for k, v in headers.items():
            response[k] = v
        if not response.status_code == 200:
            return response
        user = access_token_model.objects.get(
            token=response.data['access_token']).user

        fcm_token = request.data.get('fcmToken')
        if fcm_token:
            user.role.mobileuser.fcm_id = fcm_token
            user.role.mobileuser.save()

        response.data['profile'] = _get_profile(user).data

        response.data['is_register_finish'] = user.role.is_register_finish

        return response


class MySocialTokenView(ConvertTokenView):

    def post(self, request, *args, **kwargs):
        backend = request.data.get('backend')
        request._request.POST = request._request.POST.copy()
        request._request.POST["grant_type"] = "convert_token"
        request._request.POST["backend"] = backend
        request._request.POST["client_id"] = application_model.objects.last(
        ).client_id
        request._request.POST["client_secret"] = application_model.objects.last(
        ).client_secret
        # The only thing send from my client.
        request._request.POST["token"] = request.data.get('user_access_token')

        url, headers, body, status = self.create_token_response(
            request._request)
        response = Response(data=json.loads(body), status=status)

        for k, v in headers.items():
            response[k] = v
        if not response.status_code == 200:
            return response
        user = access_token_model.objects.get(
            token=response.data['access_token']).user

        if user.role.is_register_finish:
            response.data['profile'] = _get_profile(user).data
        response.data['is_register_finish'] = user.role.is_register_finish

        return response


class RefreshTokenView(TokenView):

    def post(self, request, *args, **kwargs):
        backend = request.data.get('backend')
        request._request.POST = request._request.POST.copy()
        request._request.POST["grant_type"] = "refresh_token"
        request._request.POST["backend"] = backend
        request._request.POST["client_id"] = application_model.objects.last(
        ).client_id
        request._request.POST["client_secret"] = application_model.objects.last(
        ).client_secret
        # The only thing send from my client.
        request._request.POST["refresh_token"] = request.data.get('refresh_token')

        url, headers, body, status = self.create_token_response(
            request._request)
        response = Response(data=json.loads(body), status=status)

        for k, v in headers.items():
            response[k] = v
        if not response.status_code == 200:
            return response
        user = access_token_model.objects.get(
            token=response.data['access_token']).user


        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_login(request):
    role = request.user.role
    profile_serializer = RoleSerializer(role, many=False)

    # profile = user_model.Profile.objects.get(user=user)
    return Response(profile_serializer.data, status=status.HTTP_200_OK)


def register_role_type(user, req_data):
    with transaction.atomic():
        user_role = user.role

        if req_data['user_type'] == 0:
            user_role.user_type = user_model.Role.NORMAL
        elif req_data['user_type'] == 1:
            user_role.user_type = user_model.Role.FARMER
        else:
            user_role.user_type = user_model.Role.SPECIALIST
        user_role.is_register_finish = True
        user_role.save()

        try:
            user_model.MobileUser.objects.get(role=user_role)
        except user_model.MobileUser.DoesNotExist as ex:
            user_model.MobileUser.objects.create(
                phone_number=req_data['username'],
                role=user.role, gender=str(req_data['gender']),
                age=req_data['age'],
                fcm_id=req_data.get('fcm_id', ''),
            )
 
        try:
            farmer_model.Farmer.objects.create(user=user,
                                               owner_name=req_data['name'],
                                               ref_province_id=req_data['province_id'],
                                               ref_sum_id=req_data['sum_id'])
        except Exception as ex:
            print(ex)
        user.farmer.start_trial()
      



# NOTIFICATION
@api_view(['GET'])
@permission_classes([IsAuthenticated, permissions.IsMobileUser])
def notification_count(request):
    count = user_model.Notifications.objects.filter(user=request.user, is_read=False,
                                                    type=user_model.Notifications.MOBILE).count()
    return Response({'count': count}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, permissions.IsMobileUser])
def notification_read(request, pk):
    notification = get_object_or_404(user_model.Notifications, pk=pk)
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    return Response({}, status=status.HTTP_200_OK)


class NotificationsViewSet(viewsets.ModelViewSet):
    queryset = user_model.Notifications.objects.all()
    pagination_class = None
    serializer_class = NotificationsSerializer
    permission_classes = [permissions.IsAdmin]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        notification = self.get_object()
        return Response(notification.highlighted)

    def perform_create(self, serializer):
        serializer.save()


class NotificationsList(ListAPIView):
    permission_classes = [IsAuthenticated, permissions.IsMobileUser]
    pagination_class = StandardResultsSetPagination
    serializer_class = MobileNotificationSerializer

    def get_queryset(self):
        notifications = user_model.Notifications.objects.filter(user=self.request.user,
                                                                type=user_model.Notifications.MOBILE).all()
        user_model.Notifications.objects.filter(user=self.request.user,
                                                type=user_model.Notifications.MOBILE, is_read=False).all().update(
            is_read=True)
        return notifications


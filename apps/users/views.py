from django.shortcuts import render
from django.contrib.auth.views import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from random import choices
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler
from rest_framework import permissions

from .models import VerifyCode
from .serializers import SmsSerializer, UserRegSerializer, UserSerializer
from utils.yunpian import YunPian
from onmall.settings import APIKEY

# Create your views here.
User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户验证 默认会被django调用 因为jwt也是用的django的用户验证
    """

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmscodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    queryset = VerifyCode.objects.all()
    serializer_class = SmsSerializer

    def gennerate_code(self):
        """
        生成随机数字
        :return:
        """
        random_str = []
        chars = "0123456789"
        for i in range(4):
            random_str.append(choices(chars))
        return ''.join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']

        yun_pian = YunPian(APIKEY)
        code = self.gennerate_code()
        sms_status = yun_pian.send_sms(code=code, mobile=mobile)

        if sms_status['code'] != 0:
            return Response({
                "mobile": sms_status['msg']
            }, status.HTTP_400_BAD_REQUEST
            )
        else:
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                'mobile': sms_status['msg']
            }, status=status.HTTP_201_CREATED)


class UserViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    # serializer_class = UserRegSerializer
    queryset = User.objects.all()

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserSerializer
        elif self.action == 'create':
            return UserRegSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated]
        elif self.action == 'create':
            return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)

        re_dict['token'] = jwt_encode_handler(payload)
        re_dict['username'] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()

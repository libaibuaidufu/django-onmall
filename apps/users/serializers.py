# coding:utf-8
__author__ = "dfk"
__date__ = "2018/2/19 11:04"
from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
from datetime import datetime, timedelta
from rest_framework.validators import UniqueValidator

from .models import VerifyCode, UserProfile
from onmall.settings import REGEX_MOBILE

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """
        验证手机号
        :param mobile:
        :return:
        """
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("手机号码已经存在")

        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码格式不对")

        one_mintes_ago = datetime.now() - timedelta(minutes=1)
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile):
            raise serializers.ValidationError("距离上一次发送未超过60s")

        return mobile


class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=4, min_length=4, label="验证码", write_only=True,
                                 required=True,
                                 error_messages={
                                     'required': "请输入验证码",
                                     'blank': "请输入验证码",
                                     'max_length': "验证码格式错误",
                                     'min_length': "验证码格式错误",
                                 })
    username = serializers.CharField(max_length=20, label="用户名",
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户名已使用")],
                                     required=True, allow_blank=False)
    password = serializers.CharField(required=True, style={'input_type': 'password'}, label='密码',write_only=True)

    # style = {'input_type': 'password'} 前端就会直接把密码 给 挡住

    def validated_code(self, code):
        # initial_data 前端form 传送过来的数据都放在这里面 我们就直接使用  debug
        verify_record = VerifyCode.objects.filter(mobile=self.initial_data['username']).order_by('-add_time')
        if verify_record:
            last_records = verify_record[0]  # 获取最后一条  最新的
            five_mintes_ago = datetime.now() - timedelta(minutes=5)
            if five_mintes_ago > last_records.add_time:
                raise serializers.ValidationError("验证码过期")
            if last_records.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        attrs['mobile'] = attrs['username']
        del attrs['code']
        return attrs

    class Meta:
        model = User
        fields = ["username", "mobile", 'code', 'password']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'gender', 'birthday', 'email', 'mobile']

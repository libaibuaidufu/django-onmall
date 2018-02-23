# coding:utf-8
__author__ = "dfk"
__date__ = "2018/2/20 17:49"
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
import re

from onmall.settings import REGEX_MOBILE
from .models import UserFav, UserLeavingMessage, UserAddress
from goods.serializers import GoodsSerializer


class UserFavDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ['goods', 'id']


class UserFavSerializer(serializers.ModelSerializer):
    # 获取当前用户 如果不定义 直接用user字段 就会把所有用户都取出来
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserFav
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏"
            )
        ]
        fields = ['user', 'goods', 'id']


class UserCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')  # read_only 只返回不提交

    class Meta:
        model = UserLeavingMessage
        fields = ['user', 'msg_type', 'subject', 'message', 'file', 'id', 'add_time']


class UseraddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    signer_mobile = serializers.CharField(max_length=11, min_length=11, required=True)

    def validated_signer_mobile(self, signer_mobile):
        """
                验证手机号码
                :param data:
                :return:
                """
        # 验证手机号码是否合法
        if not re.match(REGEX_MOBILE, signer_mobile):
            raise serializers.ValidationError('手机号码非法')

        return signer_mobile

    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'address', 'province', 'city', 'district', 'signer_name', 'signer_mobile']

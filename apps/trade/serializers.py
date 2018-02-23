# coding:utf-8
__author__ = "dfk"
__date__ = "2018/2/22 10:50"
import time
from random import Random
from rest_framework import serializers

from .models import ShoppingCart, OrderInfo, OrderGoods
from goods.serializers import GoodsSerializer
from goods.models import Goods
from utils.alipay import AliPay
from onmall.settings import alipay_id,private_key_path,ali_pub_key_path,app_notify_url


class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = "__all__"


class ShopCartSerializer(serializers.Serializer):
    # 使用serializer就要自己重写create update这些方法
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    goods = serializers.PrimaryKeyRelatedField(queryset=Goods.objects.all(), required=True)
    nums = serializers.IntegerField(label="数量", required=True, min_value=1, error_messages={
        'min_value': "商品数量不能小于一",
        "required": "请选择购买数量",
    })

    def create(self, validated_data):
        user = self.context['request'].user
        goods = validated_data['goods']
        nums = validated_data['nums']

        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        if existed:
            existed = existed[0]
            existed.nums += nums  # 这里使用+= 因为是用户在商品页再次点击购买
        else:
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        """
        这里才是进行商品数量的修改
        :param instance:
        :param validated_data:
        :return:
        """
        instance.nums = validated_data['nums']
        instance.save()
        return instance


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        alipay = AliPay(
            appid=alipay_id,
            app_notify_url=app_notify_url,
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url=app_notify_url
        )

        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.trade_no,
            total_amount=obj.order_mount,
            # return_url=return_url
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url

    class Meta:
        model = OrderInfo
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    pay_status = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True)

    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):  # obj 就是serializer
        alipay = AliPay(
            appid=alipay_id,
            app_notify_url=app_notify_url,
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url=app_notify_url
        )

        # for key, value in query.items():
        #     processed_query[key] = value[0]
        # print (alipay.verify(processed_query, ali_sign))

        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url

    def generate_order_sn(self):
        random_ins = Random()
        order_sn = "{time_str}{userid}{random_str}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                           userid=self.context['request'].user.id,
                                                           random_str=random_ins.randint(10, 99))
        return order_sn

    # 不返回给前端
    def validate(self, attrs):
        attrs['order_sn'] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"

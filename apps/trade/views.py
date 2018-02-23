from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect

from .serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from .models import ShoppingCart, OrderGoods, OrderInfo
from utils.permissions import IsOwnerOrReadOnly
from utils.alipay import AliPay
from onmall.settings import private_key_path, ali_pub_key_path, alipay_id, app_notify_url


# Create your views here.


class ShoppingcartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    lookup_field = "goods_id"

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

    def perform_create(self, serializer):
        shopcart = serializer.save()  # 获取购物车商品
        goods = shopcart.goods  # 外键
        goods.goods_num -= shopcart.nums  # 商品本身数量 减去购买数量
        goods.save()

    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num -= instance.nums
        goods.save()
        instance.delete()

    def perform_update(self, serializer):
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)
        existed_nums = existed_record.nums
        save_record = serializer.save()
        nums = save_record.nums - existed_nums
        goods = save_record.goods
        goods.goods_num -= nums
        goods.save()


class OrderViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                   mixins.CreateModelMixin):
    """
    订单
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()

            shop_cart.delete()
        return order


class AlipayView(APIView):
    def get(self, request):
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value
        sign = processed_dict.pop('sign', None)

        alipay = AliPay(
            appid=alipay_id,
            app_notify_url="http://127.0.0.1:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/alipay/return/"
        )
        verify_re = alipay.verify(processed_dict, sign)
        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)
            trade_status = processed_dict.get('trade_status', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()

                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()
            response = redirect("index")  # 从支付宝 回跳到 我们的页面
            response.set_cookie("nextPath", "pay", max_age=3)  # 获取cookie 跳转到pay页面
            return response
        else:
            response = redirect("index")  # 如果没有 就算了
            return response

    def post(self, request):
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value
        sign = processed_dict.pop('sign', None)

        alipay = AliPay(
            appid=alipay_id,
            app_notify_url="http://127.0.0.1:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/alipay/return/"
        )
        verify_re = alipay.verify(processed_dict, sign)
        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)
            trade_status = processed_dict.get('trade_status', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()
            return Response("success")

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from .models import UserFav, UserLeavingMessage, UserAddress
from .serializers import UserFavSerializer, UserFavDetailSerializer, UserCommentSerializer, UseraddressSerializer
from utils.permissions import IsOwnerOrReadOnly


# Create your views here.

class UserFavViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    """
    用户收藏
    """
    serializer_class = UserFavSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = "goods_id"  # 以前后缀跟着是 id 现在改为

    def get_serializer_class(self):
        if self.action == 'list':
            return UserFavDetailSerializer
        elif self.action == 'create':
            return UserFavSerializer
        return UserFavSerializer

    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)

    # #收藏商品数 加减 同样也可以使用singals 来控制
    # def perform_create(self, serializer):
    #     instance = serializer.save()
    #     goods = instance.goods
    #     goods.goods_num += 1
    #     goods.save()
    #
    # def perform_destroy(self, instance):
    #     goods = instance.goods
    #     goods.goods_num -= 1
    #     goods.save()
    #     instance.delete()


class UserCommentViewset(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                         mixins.DestroyModelMixin):
    """
    用户留言
    """
    serializer_class = UserCommentSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


class UseraddressViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin,
                         mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    """
    收获地址管理
    list:
        获取收货地址
    create:
        添加收货地址
    delete:
        删除收货地址
    update:
        更新收货地址
    """
    serializer_class = UseraddressSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

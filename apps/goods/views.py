from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework import filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework_extensions.mixins import CacheResponseMixin

from .models import Goods, GoodsCategory, HotSearchWords, Banner
from .serializers import GoodsSerializer, CategorySerializer, HotWordsSerializer, BannerSerializer, \
    IndexCategorySerializer
from .filters import GoodsFilter
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class GoodsPagination(PageNumberPagination):
    """
    定制分页 更加灵活 前端可以自定义分页大小
    """
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 100


# 通过GenericAPIView 来写
# class GoodsListViewset2(mixins.ListModelMixin,generics.GenericAPIView):
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

# Create your views here.
class GoodsListViewSet(CacheResponseMixin,mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表页，分页，搜索，过滤，排序
    """
    throttle_classes = (UserRateThrottle, AnonRateThrottle)  # 配置 throttle来限制用户访问次数
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    # throttle_classes =
    # authentication_classes = (TokenAuthentication,) #动态设置token验证 这里不需要
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_class = GoodsFilter
    search_fields = ('name', 'goods_brief', 'goods_desc')
    ordering_fields = ('shop_price', 'sold_num')

    # 重写RetrieveModelMixin 中的方法
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # get_objcet获取到serializer的实例
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)




class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    List:
        category列表页
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer


class HotSearchsViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取热搜词列表
    """
    queryset = HotSearchWords.objects.all().order_by("-index")
    serializer_class = HotWordsSerializer


class BannerViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    轮播图
    """
    serializer_class = BannerSerializer
    queryset = Banner.objects.all().order_by("index")


class IndexCategoryViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True)
    serializer_class = IndexCategorySerializer

# coding:utf-8
__author__ = "dfk"
__date__ = "2018/2/13 15:21"

import django_filters
from django.db.models import Q

from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    商品的过滤类
    """
    # gte 大于等于  lte小于等于
    pricemin = django_filters.NumberFilter(name="shop_price", lookup_expr='gte')
    pricemax = django_filters.NumberFilter(name="shop_price", lookup_expr='lte')
    # name = filters.CharFilter(name='name', lookup_expr='icontains')
    top_category = django_filters.NumberFilter(method='top_category_filter')

    # 假如传递过来的是一级类目 就是第一个  id 等于传递过来的value
    def top_category_filter(self, queryset, name, value):
        # return queryset.filter(category_id=value)
        return queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(
            category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['pricemin', 'pricemax', 'top_category', 'is_hot', 'is_new']

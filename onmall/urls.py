"""onmall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import xadmin
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from onmall.settings import MEIDA_ROOT
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token

from goods.views import GoodsListViewSet, CategoryViewSet, HotSearchsViewset, BannerViewset, IndexCategoryViewset
from users.views import UserViewset, SmscodeViewset
from user_opreation.views import UserFavViewset, UseraddressViewset, UserCommentViewset
from trade.views import ShoppingcartViewset, OrderViewset

router = DefaultRouter()
# 配置goods的url
router.register(r'goods', GoodsListViewSet, base_name="goods")
# category
router.register(r'categorys', CategoryViewSet, base_name="categorys")
# 验证码
router.register(r'code', SmscodeViewset, base_name='code')
# 注册
router.register(r'users', UserViewset, base_name="users")
# 热搜
router.register(r'hotsearchs', HotSearchsViewset, base_name="hotsearchs")
# 用户收藏
router.register(r'userfavs', UserFavViewset, base_name="userfavs")
# 留言
router.register(r'messages', UserCommentViewset, base_name="leavingmessage")
# 收货地址
router.register(r'address', UseraddressViewset, base_name="address")
# 购物车
router.register(r'shopcarts', ShoppingcartViewset, base_name="shopcarts")
# 订单
router.register(r'orders', OrderViewset, base_name="orders")
# 轮播图
router.register(r'banners', BannerViewset, base_name="banners")
# 首页商品系列数据
router.register(r'indexgoods', IndexCategoryViewset, base_name="indexgoods")

from trade.views import AlipayView

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    # 商品列表页
    url(r'^', include(router.urls)),

    # media相关配置
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEIDA_ROOT}),
    # drf 登录模块 自带的
    url(r'^api-auth/', include('rest_framework.urls')),
    # drf 自动生成文档  需要安装一些 coreapi 之类的
    url(r'^docs/', include_docs_urls(title="幕学生鲜")),
    # drf 自带token验证
    url(r'^api-token-auth/', views.obtain_auth_token),
    # jwt认证接口
    url(r'^login/$', obtain_jwt_token),
    # 支付宝接口
    url(r'^alipay/return/', AlipayView.as_view(), name='alipay'),
    # 第三方登录接口
    url('', include('social_django.urls', namespace='social')),
]

# coding:utf-8
__author__ = "dfk"
__date__ = "2018/2/23 13:24"

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from user_opreation.models import UserFav


# 使用信号量来控制商品收藏数量
@receiver(post_save, sender=UserFav)
def create_userfav(sender, instance=None, created=False, **kwargs):
    if created:
        goods = instance.goods
        goods.fav_num += 1
        goods.save()
        # Token.objects.create(user=instance)


@receiver(post_delete, sender=UserFav)
def delete_userfav(sender, instance=None, created=False, **kwargs):
    goods = instance.goods
    goods.fav_num -= 1
    goods.save()

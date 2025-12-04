# coding: utf-8

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.core.models import Stub  # ,User, Ticket, Shop

# class ShopSerializer(ModelSerializer):
#     class Meta:
#         model = Shop
#         fields = ['name', 'comment']

# # class TicketSerializer(ModelSerializer):
# #     class Meta:
# #         model = Ticket
# #         fields = ['pk', 'is_pay']


class StubSerializer(ModelSerializer):
    user_pk = serializers.IntegerField(source='ticket.owner.pk')

    class Meta:
        model = Stub
        fields = ('pk', 'user_id', 'time')

# # class UserTicketSerializer(ModelSerializer):
# #     ticketcount = SerializerMethodField()
# #     class Meta:
# #         model = User
# #         fields = ['pk','ticketcount']

# #     def get_ticketcount(self, obj):
# #         try:
# #             owned_tickets = TicketSerializer(
# #                 Ticket.objects.all().filter(
# #                     owner = User.objects.get(id=obj.id)
# #                 ), many=True
# #             ).data
# #             #↑ここを"Comment.objects.all().filter(target_article = Article.objects.get(id=obj.id)"
# #             #とだけにすると、"Item is not JSON serializable"というエラーが出ますので
# #             #Serializer(出力させたいもの).data　という処理が必要です。
# #             return owned_tickets
# #         except:
# #             owned_tickets = None
# #             return owned_tickets

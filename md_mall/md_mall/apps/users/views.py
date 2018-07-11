from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import User
from .serializers import CreateUserSerializer
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated


class UserView(CreateAPIView):
    serializer_class = CreateUserSerializer


class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count,
        }
        return Response(data)

class MobilesCountView(APIView):
    def get(self, request, mobiles):
        count = User.objects.filter(mobile=mobiles).count()
        data = {
            'username': mobiles,
            'count': count,
        }
        return Response(data)

class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EmailSerializer

    def get_object(self):
        return self.request.user
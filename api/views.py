import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import EMAIL_ADMIN

from .filters import CategoriesFilter, GenresFilter, TitlesFilter
from .models import Category, Genre, Review, Title, User
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrAdminOrModerator
from .serializers import (CategorySerializer, CheckConfirmationCodeSerializer,
                          CommentSerializer, GenreSerializer, ReviewSerializer,
                          SendCodeSerializer, TitleCreateSerializer,
                          TitleListSerializer, UserSerializer)


class CreateDeleteListViewSet(mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    pass


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('id')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TitlesFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update', 'create'):
            return TitleCreateSerializer

        return TitleListSerializer


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrModerator]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id),
            pk=review_id
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        review = get_object_or_404(
            Review.objects.filter(title_id=title_id),
            pk=review_id
        )
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthorOrAdminOrModerator,
        permissions.IsAuthenticatedOrReadOnly
    ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])

        serializer.save(author=self.request.user, title=title)


class CategoryViewSet(CreateDeleteListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination
    filterset_class = CategoriesFilter
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(CreateDeleteListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination
    filterset_class = GenresFilter
    permission_classes = [IsAdminOrReadOnly]


@api_view(['POST'])
def send_confirmation_code(request):
    serializer = SendCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']

    if serializer.is_valid():
        confirmation_code = uuid.uuid4()
        user = User.objects.filter(email=email).exists()
        if not user:
            User.objects.create_user(email=email)

        User.objects.filter(email=email).update(
            confirmation_code=make_password(
                confirmation_code,
                salt=None,
                hasher='default'
            )
        )

        mail_subject = 'Confirmation code on Yamdb.ru'
        message = f'Your confirmation code: {confirmation_code}'
        send_mail(mail_subject, message, f'Yamdb.ru <{EMAIL_ADMIN}>', [email])

        return Response(
            f'Code was sent to {email}, please check',
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def get_jwt_token(request):
    serializer = CheckConfirmationCodeSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        confirmation_code = serializer.data['confirmation_code']
        user = get_object_or_404(User, email=email)

        if check_password(confirmation_code, user.confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'token': f'{token}'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'confirmation_code': 'Wrong confirmation code'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ['user__username']


class APIUser(APIView):
    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated],
            url_path='me', url_name='me')
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)

        return Response(
            'You are not authenticated',
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(methods=['patch'], detail=False,
            permission_classes=[IsAuthenticated],
            url_path='me', url_name='me')
    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            'You are not authenticated',
            status=status.HTTP_401_UNAUTHORIZED
        )

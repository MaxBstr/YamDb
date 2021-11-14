from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (APIUser, CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, get_jwt_token,
                    send_confirmation_code)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('titles', TitleViewSet, basename='Title')
router.register('genres', GenreViewSet, basename='Genre')
router.register('categories', CategoryViewSet, basename='Category')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

urlpatterns = [
    path(
        'v1/auth/email/',
        send_confirmation_code,
        name='send_confirmation_code'
    ),
    path('v1/auth/token/', get_jwt_token, name='get_token'),
    path('v1/users/me/', APIUser.as_view()),
    path('v1/', include(router.urls)),
]

from django.conf import settings as st
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import year_validator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        new_user = self.model(
            email=email,
            **kwargs
        )

        new_user.set_password(password)
        new_user.save()
        return new_user

    def create_superuser(self, email, password, **kwargs):
        new_user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            **kwargs
        )

        new_user.set_password(password)
        new_user.save()
        return new_user


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    bio = models.TextField(
        max_length=300,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=6,
        default='000000'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    USER_ROLES = [
        (st.USER, 'Просто пользователь!'),
        (st.MODERATOR, 'Модератор'),
        (st.ADMIN, 'Администратор'),
    ]

    role = models.CharField(
        max_length=9,
        choices=USER_ROLES,
        default='user'
    )
    objects = UserManager()

    class Meta:
        ordering = ['-id']


class Category(models.Model):
    name = models.CharField(
        verbose_name='Category',
        max_length=400,
        help_text='Enter new category',
        blank=False,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Category slug',
        max_length=25,
        unique=True,
        help_text='Unique slug using: A-Z, 0-9, - и _'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Genre',
        max_length=400,
        help_text='Enter new genre',
        blank=False,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Genre slug',
        max_length=25,
        unique=True,
        help_text='Unique slug using: A-Z, 0-9, - и _'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        verbose_name='Title header',
        max_length=400,
        help_text='Enter title header',
        blank=False
    )
    year = models.IntegerField(
        verbose_name='Release year',
        validators=[year_validator],
        help_text='Enter title"s release year',
        blank=True,
        null=True
    )
    description = models.TextField(
        max_length=400,
        verbose_name='Title description',
        help_text='Enter title description',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Title genre',
        help_text='Enter title genre',
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Title category',
        help_text='Enter title category',
        null=True
    )

    class Meta:
        ordering = ['-year']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(max_length=3000)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, message='Шибко мало!'),
            MaxValueValidator(10, message='Шибко много!')
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        verbose_name='Описание',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

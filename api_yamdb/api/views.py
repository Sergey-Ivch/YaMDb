from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User
from api_yamdb.settings import DOMAIN_NAME

from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminModeratorOwnerOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReadOnlyTitleSerializer,
                          RegisterDataSerializer, ReviewSerializer,
                          TitlesSerializer, TokenSerializer,
                          UserEditSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями (только для администраторов).

    Предоставляет CRUD-операции для пользователей, доступные только администраторам.
        pagination_class (Pagination): Класс пагинации (PageNumberPagination).
        permission_classes (list): Список классов разрешений (IsAdmin).
        filter_backends (tuple): Список бэкендов фильтрации (filters.SearchFilter).
        lookup_field (str): Поле для поиска пользователя (username).
        search_fields (tuple): Поля для поиска (username).

    Методы:
        users_own_profile(self, request): Endpoint для получения и редактирования собственного профиля пользователя.
        update(self, request, username, **kwargs): Запрещает операцию PUT для обновления пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)

    @action(
        methods=[
            'GET',
            'PATCH',
        ],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def users_own_profile(self, request):

        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, username, **kwargs):
        """
        Запрет операции PUT для обновления пользователя.
        """
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, username, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Регистрация нового пользователя.

    Позволяет зарегистрировать нового пользователя, отправив код подтверждения на указанный email.
    Если пользователь с таким email уже существует, повторно отправляет код подтверждения.

    """
    serializer = RegisterDataSerializer(data=request.data)
    email = request.data.get('email')
    username = request.data.get('username')
    user = User.objects.filter(email=email)

    if User.objects.filter(username=username,
                           email=email).exists():
        user = user.get(email=email)
        send_confirm_mail(user)
        return Response(
            {'message': 'Пользователь с такой электронной почтой уже '
                        'существует. Код подтверждения отправлен повторно. '
             }
        )
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    user, _ = User.objects.get_or_create(username=username, email=email)
    send_confirm_mail(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    """
    Получение JWT-токена.

    Позволяет получить JWT-токен, если предоставлен правильный username и confirmation_code.
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )

    if default_token_generator.check_token(
        user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_confirm_mail(user):
    """
    Отправка кода подтверждения на email пользователя.
    """
    confirmation_code = default_token_generator.make_token(user)
    subject = 'YaMDb registration'
    message = f'Ваш код подтверждения: {confirmation_code}'
    from_email = DOMAIN_NAME
    recipient_list = [user.email]
    return send_mail(subject, message, from_email, recipient_list)


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet
                      ):
    """
    ViewSet для модели Category.

    Предоставляет операции:
        - Получение списка категорий (list).
        - Создание категории (create).
        - Удаление категории (destroy).

    Права доступа:
        - Чтение доступно всем.
        - Создание и удаление доступны только администраторам (IsAdminOrReadOnly).

    Фильтрация:
        - Поиск по названию (name) (filters.SearchFilter).

    Атрибуты:
        queryset (QuerySet):  Набор всех категорий.
        serializer_class (Serializer):  Сериализатор для модели Category (CategorySerializer).
        permission_classes (list):  Список классов прав доступа (IsAdminOrReadOnly).
        filter_backends (tuple):  Список бэкендов фильтрации (filters.SearchFilter).
        search_fields (tuple):  Поля, по которым осуществляется поиск (name).
        lookup_field (str):  Поле, используемое для поиска отдельных объектов (slug).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet
                   ):
    """
    ViewSet для модели Genre.

    Предоставляет операции:
        - Получение списка жанров (list).
        - Создание жанра (create).
        - Удаление жанра (destroy).

    Права доступа:
        - Чтение доступно всем.
        - Создание и удаление доступны только администраторам (IsAdminOrReadOnly).

    Фильтрация:
        - Поиск по названию (name) (filters.SearchFilter).

    Атрибуты:
        queryset (QuerySet):  Набор всех жанров.
        serializer_class (Serializer):  Сериализатор для модели Genre (GenreSerializer).
        permission_classes (list):  Список классов прав доступа (IsAdminOrReadOnly).
        filter_backends (tuple):  Список бэкендов фильтрации (filters.SearchFilter).
        search_fields (tuple):  Поля, по которым осуществляется поиск (name).
        lookup_field (str):  Поле, используемое для поиска отдельных объектов (slug).
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Title (произведение).

    Предоставляет полный набор CRUD-операций (create, read, update, delete) для произведений.
    Использует разные сериализаторы для операций чтения (ReadOnlyTitleSerializer) и записи (TitlesSerializer).
    Позволяет фильтровать произведения по различным критериям.

    Права доступа:
        - Чтение доступно всем.
        - Создание, обновление и удаление доступны только администраторам (IsAdminOrReadOnly).

    Фильтрация:
        - Использует DjangoFilterBackend и TitleFilter для расширенной фильтрации произведений.

    Атрибуты:
        queryset (QuerySet):  Набор всех произведений, аннотированных средним рейтингом (rating).
                               Рейтинг вычисляется на основе связанных отзывов (`reviews__score`).
        serializer_class (Serializer):  Сериализатор по умолчанию для модели Title (TitlesSerializer).
        permission_classes (list):  Список классов прав доступа (IsAdminOrReadOnly).
        filter_backends (tuple):  Список бэкендов фильтрации (DjangoFilterBackend).
        filterset_class (FilterSet):  Класс фильтра для модели Title (TitleFilter).

    Методы:
        get_serializer_class(self):  Определяет, какой сериализатор использовать в зависимости от действия (action).
                                      Для операций "list" (получение списка) и "retrieve" (получение одного объекта)
                                      используется ReadOnlyTitleSerializer, который включает рейтинг, жанры и категорию.
                                      Для остальных операций используется TitlesSerializer, который позволяет изменять
                                      основные поля произведения.
    """
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от типа запроса (чтение или запись).
        """
        if self.action in ['list', 'retrieve']:
            return ReadOnlyTitleSerializer
        return TitlesSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Review (отзыв).

    Предоставляет полный набор CRUD-операций (create, read, update, delete) для отзывов,
    связанных с определенным произведением.
    Автоматически устанавливает автора отзыва при создании.

    Права доступа:
        - Чтение доступно всем.
        - Создание, обновление и удаление доступны только администраторам, модераторам или авторам (IsAdminModeratorOwnerOrReadOnly).

    Атрибуты:
        serializer_class (Serializer):  Сериализатор для модели Review (ReviewSerializer).
        permission_classes (list):  Список классов прав доступа (IsAdminModeratorOwnerOrReadOnly).

    Методы:
        get_queryset(self):  Возвращает queryset, содержащий только отзывы, связанные с указанным произведением.
                              Произведение определяется по параметру `title_id` в URL.
        perform_create(self, serializer):  Создает новый отзыв, автоматически связывая его с текущим пользователем
                                            (автором) и произведением.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        """
        Возвращает отзывы только для конкретного произведения.
        """
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        """
        Сохраняет новый отзыв, связывая его с текущим пользователем и произведением.
        """
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Comment (комментарий).

    Предоставляет полный набор CRUD-операций (create, read, update, delete) для комментариев,
    связанных с определенным отзывом.
    Автоматически устанавливает автора комментария и связывает его с отзывом при создании.

    Права доступа:
        - Чтение доступно всем.
        - Создание, обновление и удаление доступны только администраторам, модераторам или авторам (IsAdminModeratorOwnerOrReadOnly).

    Атрибуты:
        serializer_class (Serializer): Сериализатор для модели Comment (CommentSerializer).
        permission_classes (list): Список классов прав доступа (IsAdminModeratorOwnerOrReadOnly).

    Методы:
        get_queryset(self): Возвращает queryset, содержащий только комментарии, связанные с указанным отзывом.
                             Отзыв определяется по параметрам `review_id` и `title_id` в URL.
        perform_create(self, serializer): Создает новый комментарий, автоматически связывая его с текущим пользователем
                                          (автором) и отзывом.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        """
        Возвращает комментарии только для конкретного отзыва.
        """
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),
                                   title=self.kwargs.get('title_id')
                                   )
        return review.comments.all()

    def perform_create(self, serializer):
        """
        Сохраняет новый комментарий, связывая его с текущим пользователем и отзывом.
        """
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)

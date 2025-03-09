import datetime as dt

from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User (полная информация).

    Используется для представления полной информации о пользователе, включая роль и bio.
    Включает валидаторы для username и email, чтобы обеспечить уникальность и соответствие требованиям.

    Атрибуты:
        username (CharField):  Имя пользователя. Обязательное поле, должно быть уникальным.
                              Проверяется на соответствие UnicodeUsernameValidator и UniqueValidator.
        email (EmailField):   Адрес электронной почты. Обязательное поле, должно быть уникальным.
                              Проверяется на соответствие UniqueValidator.

    Meta:
        model (User):  Модель, для которой предназначен сериализатор (User).
        fields (tuple):  Список полей модели, которые будут сериализованы/десериализованы.
    """
    username = serializers.CharField(
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(queryset=User.objects.all())
        ],
        max_length=150,
        required=True,
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio',
                  'first_name', 'last_name')


class RegisterDataSerializer(serializers.ModelSerializer):
    '''
    Включает валидаторы для username и email, чтобы обеспечить уникальность и соответствие требованиям.
    Содержит кастомный валидатор для username, чтобы исключить использование "me".

    Атрибуты:
        username (CharField):  Имя пользователя. Обязательное поле, должно быть уникальным.
                              Проверяется на соответствие UnicodeUsernameValidator и UniqueValidator.
                              Проходит кастомную валидацию для исключения "me".
        email (EmailField):   Адрес электронной почты. Обязательное поле, должно быть уникальным.
                              Проверяется на соответствие UniqueValidator.

    Методы:
        validate_username(self, value): Кастомный валидатор для username.

    Meta:
        model (User):  Модель, для которой предназначен сериализатор (User).
        fields (tuple):  Список полей модели, которые будут сериализованы/десериализованы (username, email).
    '''
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    def validate_username(self, value):
        """
        Валидатор для username. Исключает использование username "me".
        """
        if value == 'me':
            raise serializers.ValidationError('Username me is not valid')
        return value

    class Meta:
        fields = ('username', 'email')
        model = User


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена.

    Используется для валидации данных (username и confirmation_code) при запросе токена.

    Атрибуты:
        username (CharField):  Имя пользователя.
        confirmation_code (CharField): Код подтверждения.
    """
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserEditSerializer(serializers.ModelSerializer):
    """
    Сериализатор для редактирования информации о пользователе (личный кабинет).

    Используется для редактирования профиля пользователя.
    Роль пользователя (role) не может быть изменена через этот сериализатор (read_only_fields).
    Включает валидаторы для username, чтобы обеспечить уникальность и соответствие требованиям.

    Атрибуты:
        username (CharField):  Имя пользователя. Обязательное поле, должно быть уникальным.
                              Проверяется на соответствие UnicodeUsernameValidator и UniqueValidator.

    Meta:
        model (User):  Модель, для которой предназначен сериализатор (User).
        fields (tuple):  Список полей модели, которые будут сериализованы/десериализованы.
        read_only_fields (tuple): Поля, доступные только для чтения (role).
    """
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Используется для представления информации о категории.
    Включает поля 'name' и 'slug'.

    Meta:
        model (Category):  Модель, для которой предназначен сериализатор (Category).
        fields (tuple):  Список полей модели, которые будут сериализованы/десериализованы (name, slug).
    """

    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenreTitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели GenreTitle.

    Используется для представления информации о связи жанра и произведения.
    Включает поля 'name' и 'slug'.

    Meta:
        model (GenreTitle):  Модель, для которой предназначен сериализатор (GenreTitle).
        fields (tuple):  Список полей модели, которые будут сериализованы/десериализованы (name, slug).
    """

    class Meta:
        fields = ('name', 'slug')
        model = GenreTitle


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.

    Используется для представления информации о жанре.
    Включает поля 'name' и 'slug'.

    Meta:
        model (Genre):  Модель, для которой предназначен сериализатор (Genre).
        fields (tuple):  Список полей модели, которые будут сериализованы/десериализованы (name, slug).
    """

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitlesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title.

    Используется для представления информации о произведении.
    Включает все поля модели Title.
    Использует SlugRelatedField для представления category и genre.
    Содержит валидатор для года выпуска произведения (year).

    Атрибуты:
        category (SlugRelatedField): Категория произведения.  Представляется с помощью slug.
        genre (SlugRelatedField): Жанры произведения.  Представляются с помощью slug. Может быть несколько жанров.

    Методы:
        validate_year(self, value): Валидатор для года выпуска произведения.

    Meta:
        model (Title):  Модель, для которой предназначен сериализатор (Title).
        fields (str):  Все поля модели ("__all__").
    """
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',)
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True)

    class Meta:
        fields = ('__all__')
        model = Title

    def validate_year(self, value):
        """
        Валидатор для года выпуска произведения.
        Год выпуска не может быть больше текущего года.
        """

        year = dt.date.today().year
        if year < value:
            raise serializers.ValidationError(
                'Проверьте год выхода произведения.'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review (отзыв).

    Используется для создания, чтения и обновления отзывов.
    Включает валидацию оценки (score) и проверку на существование отзыва от текущего пользователя на данное произведение.

    Атрибуты:
        title (SlugRelatedField):  Произведение, к которому относится отзыв.
                                    Представляется только названием произведения (slug_field='name').
                                    Доступно только для чтения (read_only=True).
        author (SlugRelatedField): Автор отзыва.
                                    Представляется только именем пользователя (slug_field='username').
                                    Автоматически устанавливается как текущий пользователь (default=serializers.CurrentUserDefault()).
                                    Доступно только для чтения (read_only=True).

    Методы:
        validate_score(self, value):  Валидатор для оценки.
                                      Оценка должна быть целым числом от 1 до 10.
        validate(self, data):        Валидатор для проверки существования отзыва от текущего пользователя на данное произведение.
                                      Если отзыв уже существует, выбрасывает исключение ValidationError.

    Meta:
        model (Review): Модель, для которой предназначен сериализатор (Review).
        fields (str):   Все поля модели ("__all__").
    """
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    def validate_score(self, value):
        """
        Валидатор для оценки. Оценка должна быть целым числом от 1 до 10.
        """
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                'Оценкой может быть только целое число от 1 до 10.'
            )
        return value

    def validate(self, data):
        """
        Валидатор для проверки, что пользователь еще не оставлял отзыв на это произведение.
        """
        author = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        if self.context['request'].method == 'POST':
            if Review.objects.filter(author=author, title=title).exists():
                raise serializers.ValidationError(
                    'На произведение можно оставить только один отзыв.')
        return data

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment (комментарий).

    Используется для создания, чтения и обновления комментариев к отзывам.

    Атрибуты:
        review (SlugRelatedField): Отзыв, к которому относится комментарий.
                                    Представляется только текстом отзыва (slug_field='text').
                                    Доступно только для чтения (read_only=True).
        author (SlugRelatedField): Автор комментария.
                                    Представляется только именем пользователя (slug_field='username').
                                    Доступно только для чтения (read_only=True).

    Meta:
        model (Comment): Модель, для которой предназначен сериализатор (Comment).
        fields (str):   Все поля модели ("__all__").
    """
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title (произведение) для операций только чтения.

    Используется для представления информации о произведении в операциях, где изменение данных не предполагается.
    Включает рейтинг произведения, жанры и категорию.

    Атрибуты:
        rating (IntegerField): Рейтинг произведения. Доступно только для чтения (read_only=True).
        genre (GenreSerializer): Жанры произведения. Сериализуются с помощью GenreSerializer. Доступно только для чтения (read_only=True).
        category (CategorySerializer): Категория произведения. Сериализуется с помощью CategorySerializer. Доступно только для чтения (read_only=True).

    Meta:
        model (Title): Модель, для которой предназначен сериализатор (Title).
        fields (str):   Все поля модели ("__all__").
    """
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

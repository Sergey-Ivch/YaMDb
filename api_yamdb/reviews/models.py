from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from .validators import validate_year


class User(AbstractUser):
    """
    Модель пользователя.

    Наследуется от AbstractUser, предоставляемого Django, для базовой функциональности пользователя.
    Добавляет поля 'role', 'bio' и переопределяет поля 'username' и 'email'
    для соответствия требованиям проекта.

    Атрибуты:
        ADMIN (str): Константа для роли администратора.
        MODERATOR (str): Константа для роли модератора.
        USER (str): Константа для роли обычного пользователя.
        roles (tuple): Список кортежей, определяющих возможные роли пользователя.

        username (CharField): Имя пользователя, должно быть уникальным.
        email (EmailField): Адрес электронной почты, используется для аутентификации.
        role (CharField): Роль пользователя (администратор, модератор или обычный пользователь).
        bio (TextField): Информация о пользователе.

    Свойства:
        is_moderator (bool): Возвращает True, если роль пользователя - модератор.
        is_admin (bool): Возвращает True, если роль пользователя - администратор.

    Meta:
        ordering (list): Порядок сортировки пользователей по умолчанию.
        verbose_name (str): Отображаемое имя модели в единственном числе.
        verbose_name_plural (str): Отображаемое имя модели во множественном числе.
    """
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    roles = (
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    )

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        null=True,
        unique=True
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        max_length=254,
    )

    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=roles,
        default=USER
    )

    bio = models.TextField(
        verbose_name='О себе',
        null=True,
        blank=True,
    )

    @property
    def is_moderator(self):
        """
        Возвращает True, если роль пользователя - MODERATOR.
        """
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        """
        Возвращает True, если роль пользователя - ADMIN.
        """
        return self.role == self.ADMIN

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    """
    Модель категории произведения (например, "Книги", "Фильмы").

    Атрибуты:
        name (CharField): Название категории.
        slug (SlugField): Slug категории, используется в URL.

    Meta:
        ordering (list): Порядок сортировки категорий по умолчанию.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        """
        Возвращает строковое представление объекта (название категории).
        """
        return self.name

    class Meta:
        ordering = ['name']


class Genre(models.Model):
    """
    Модель жанра произведения (например, "Фантастика", "Драма").

    Атрибуты:
        name (CharField): Название жанра.
        slug (SlugField): Slug жанра, используется в URL.

    Meta:
        ordering (list): Порядок сортировки жанров по умолчанию.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        """
        Возвращает строковое представление объекта (название жанра).
        """
        return self.name

    class Meta:
        ordering = ['id']


class Title(models.Model):
    """
    Модель произведения (например, "Книга", "Фильм").

    Атрибуты:
        name (CharField): Название произведения.
        year (PositiveIntegerField): Год выхода произведения.
        description (TextField): Описание произведения.
        genre (ManyToManyField): Жанры произведения (связь Many-to-Many с Genre через GenreTitle).
        category (ForeignKey): Категория произведения (связь One-to-Many с Category).

    Meta:
        ordering (list): Порядок сортировки произведений по умолчанию.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выхода произведения.',
        db_index=True,
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='описание произведения',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='category',
        null=True
    )

    class Meta:
        ordering = ['name']

    def get_genre(self, obj):
        """
        Возвращает строку с перечислением жанров для данного произведения.

        Этот метод, вероятно, не используется, т.к. поле genre уже является ManyToManyField.
        """
        return "\n".join([g.genres for g in obj.genre.all()])

    def __str__(self):
        """
        Возвращает строковое представление объекта (название произведения).
        """
        return self.name


class GenreTitle(models.Model):
    """
    Промежуточная модель для связи произведений и жанров (Many-to-Many).

    Атрибуты:
        title (ForeignKey): Связанное произведение (связь One-to-Many с Title).
        genre (ForeignKey): Связанный жанр (связь One-to-Many с Genre).

    Meta:
        verbose_name (str): Отображаемое имя модели в единственном числе.
        verbose_name_plural (str): Отображаемое имя модели во множественном числе.
    """
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        null=True,
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(models.Model):
    """
    Модель отзыва о произведении.

    Атрибуты:
        title (ForeignKey): Связанное произведение (связь One-to-Many с Title).
        text (TextField): Текст отзыва.
        author (ForeignKey): Автор отзыва (связь One-to-Many с User).
        score (PositiveSmallIntegerField): Оценка произведения (от 1 до 10).
        pub_date (DateTimeField): Дата публикации отзыва.

    Meta:
        verbose_name (str): Отображаемое имя модели в единственном числе.
        verbose_name_plural (str): Отображаемое имя модели во множественном числе.
        ordering (list): Порядок сортировки отзывов по умолчанию.
        constraints (list): Список ограничений для модели.
            UniqueConstraint: Гарантирует уникальность комбинации title и author (один пользователь
            может оставить только один отзыв на одно произведение).
    """
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]

from django.db import models


class Comment(models.Model):
    """
    Модель комментария к отзыву.

    Предназначена для хранения комментариев, оставленных пользователями к определенным отзывам.

    Атрибуты:
        review (ForeignKey):  Отзыв, к которому относится комментарий (связь One-to-Many с Review).
                              Используется `related_name='comments'` для доступа к комментариям отзыва.
        text (TextField):     Текст комментария.
        author (ForeignKey):  Пользователь, написавший комментарий (связь One-to-Many с User).
                              Используется `related_name='comments'` для доступа к комментариям пользователя.
        pub_date (DateTimeField): Дата и время публикации комментария.  Автоматически устанавливается при создании.
                                 Индексируется для оптимизации запросов по дате.

    Meta:
        verbose_name (str): Отображаемое имя модели в единственном числе ("Комментарий").
        verbose_name_plural (str): Отображаемое имя модели во множественном числе ("Комментарии").
        ordering (list):  Порядок сортировки комментариев по умолчанию - по дате публикации (`pub_date`).
    """
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']
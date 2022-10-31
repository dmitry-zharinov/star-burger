from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Prefetch, Sum
from django.db.models.query import QuerySet
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(QuerySet):
    def fetch_with_price(self):
        return self.prefetch_related(
            Prefetch('products',
                     queryset=OrderItem.objects.prefetch_related('product'))
        ).annotate(
            price=Sum(F('products__quantity') *
                      F('products__price'))
        )


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('NEW', 'Новый'),
        ('PROCESS', 'В обработке'),
        ('DELIVERED', 'Доставлен'),
    )
    ORDER_PAYMENT_CHOICES = (
        ('NONE', 'Не указан'),
        ('CASH', 'Наличные'),
        ('CARD', 'Картой'),
    )
    firstname = models.CharField(
        'имя',
        max_length=50
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        db_index=True
    )
    address = models.CharField(
        'адрес',
        max_length=200,
    )
    phonenumber = PhoneNumberField(
        'телефон',
        max_length=20
    )
    status = models.CharField(
        'статус',
        max_length=9,
        choices=ORDER_STATUS_CHOICES,
        default='NEW',
        db_index=True,
    )
    payment = models.CharField(
        'способ оплаты',
        max_length=4,
        choices=ORDER_PAYMENT_CHOICES,
        default='NONE',
        db_index=True,
    )
    comment = models.TextField(
        'комментарий к заказу',
        blank=True,
    )
    created_at = models.DateTimeField(
        'дата заказа',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        'дата звонка',
        null=True,
        blank=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'дата доставки',
        null=True,
        blank=True,
        db_index=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='ресторан',
        help_text='ресторан выполняющий заказ',
        blank=True,
        null=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.firstname} {self.lastname}, {self.address}"


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='товар',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='заказ',
    )
    quantity = models.PositiveIntegerField(
        'количество',
        default=1,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f"{self.product.name}"

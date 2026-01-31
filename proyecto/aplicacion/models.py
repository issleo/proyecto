import uuid

# Create your models here.

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
class Customer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    document_id = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    sku = models.CharField(
        max_length=100,
        unique=True
    )
    name = models.CharField(
        max_length=255
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def verificaciones(self):
        if self.stock < 0:
            raise ValidationError("El stock no puede ser negativo")
        if self.price < 0:
            raise ValidationError("El precio no puede ser negativo")


class Order(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    customer = models.ForeignKey(
        "Customer",
        on_delete=models.PROTECT,
        related_name="orders"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total(self):
        return sum(item.subtotal for item in self.items.all())

class OrderItem(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    qty = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        editable=False
    )
    def subtotal(self):
        return self.unit_price * self.qty

    def verificaciones(self):
        if self.qty <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0")
        if self.unit_price < 0:
            raise ValidationError("El precio unitario no puede ser negativo")
        if self.qty > self.product.stock:
            raise ValidationError(f"No hay suficiente stock para el producto {self.product.name}")
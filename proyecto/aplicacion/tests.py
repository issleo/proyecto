from django.test import TestCase
from rest_framework.test import APITestCase
from aplicacion.models import Customer, Product, Order

from rest_framework import status
from django.urls import reverse
from aplicacion.models import Order
from aplicacion.models import OrderItem




# Create your tests here.
class BaseAPITest(APITestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            full_name="Juan Pérez",
            email="juan@test.com",
            document_id="12345678"
        )

        self.product = Product.objects.create(
            sku="SKU-001",
            name="Producto Test",
            price=100,
            stock=10
        )

        self.order = Order.objects.create(
            customer=self.customer
        )



class OrderTests(BaseAPITest):

    def test_no_puede_pagar_orden_sin_items(self):
        url = reverse('order-pay', args=[self.order.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_total_se_calcula_automaticamente(self):
        self.order.items.create(
            product=self.product,
            qty=2,
            unit_price=self.product.price
        )

        self.assertEqual(self.order.total, 200)

    def test_no_se_puede_pagar_orden_en_estado_invalido(self):
        self.order.status = 'PAID'
        self.order.save()

        url = reverse('order-pay', args=[self.order.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class OrderItemTests(BaseAPITest):

    def test_no_se_pueden_agregar_items_a_orden_pagada(self):
        self.order.status = 'PAID'
        self.order.save()

        url = reverse('order-add-item', args=[self.order.id])
        data = {
            "product": str(self.product.id),
            "qty": 1
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_qty_debe_ser_mayor_a_cero(self):
        url = reverse('order-add-item', args=[self.order.id])
        data = {
            "product": str(self.product.id),
            "qty": 0
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class StockTests(BaseAPITest):

    def test_stock_se_descuenta_al_pagar(self):
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            qty=3,
            unit_price=self.product.price
        )

        self.order.status = 'SUBMITTED'
        self.order.save()

        url = reverse('order-pay', args=[self.order.id])
        response = self.client.post(url)

        self.product.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.product.stock, 7)

    def test_no_pagar_si_no_hay_stock(self):
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            qty=50,
            unit_price=self.product.price
        )

        self.order.status = 'SUBMITTED'
        self.order.save()

        url = reverse('order-pay', args=[self.order.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelar_orden_pagada_devuelve_stock(self):
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            qty=4,
            unit_price=self.product.price
        )

        self.order.status = 'SUBMITTED'
        self.order.save()

        pay_url = reverse('order-pay', args=[self.order.id])
        self.client.post(pay_url)

        cancel_url = reverse('order-cancel', args=[self.order.id])
        self.client.post(cancel_url)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

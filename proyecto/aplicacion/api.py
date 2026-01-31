from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Product, Order, OrderItem
from .serializers import CustomerSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def pay(self, request, pk=None):
        order = self.get_object()

        if order.status != 'SUBMITTED':
            return Response(
                {"error": "Solo se pueden pagar órdenes SUBMITTED"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.items.count() == 0:
            return Response(
                {"error": "No se puede pagar una orden sin items"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar stock
        for item in order.items.select_related('product'):
            if item.qty > item.product.stock:
                return Response(
                    {"error": f"Stock insuficiente para {item.product.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Transacción atómica
        with transaction.atomic():
            for item in order.items.select_related('product'):
                product = item.product
                product.stock -= item.qty
                product.save()

            order.status = 'PAID'
            order.save()

        return Response(
            {"message": "Orden pagada correctamente", "total": order.total},
            status=status.HTTP_200_OK
        )
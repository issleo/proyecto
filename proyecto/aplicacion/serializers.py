from rest_framework import serializers
from .models import Customer,Product, Order, OrderItem

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    def validar_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo")
        return value
    def validar__precio(self, precio):
        if precio < 0:
            raise serializers.ValidationError("El precio no puede ser menor que 0")
        return precio

class OrderSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Order
        fields = ['id', 'customer', 'status', 'total', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total', 'created_at', 'updated_at']

    def validate(self, data):
        instance = self.instance
        new_status = data.get('status')

        if instance and new_status in ['SUBMITTED', 'PAID']:
            if instance.items.count() == 0:
                raise serializers.ValidationError(
                    "No se puede enviar o pagar una orden sin items."
                )

        return data
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta: 
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'qty', 'unit_price', 'subtotal']
        read_only_fields = ['unit_price', 'subtotal', 'product_name']
    def validar_cantida(self, cantidad):
        if cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return cantidad
    def create(self, validated_data):
        product = validated_data['product']
        validated_data['unit_price'] = product.price
        # Verificar stock
        if validated_data['qty'] > product.stock:
            raise serializers.ValidationError(f"No hay suficiente stock para {product.name}")
        # Reducir stock automáticamente
        product.stock -= validated_data['qty']
        product.save()
        return super().create(validated_data)
    def validate(self, data):
        order = data.get('order') or self.instance.order
        if order.status == 'PAID':
            raise serializers.ValidationError(
                "No se pueden modificar items de una orden pagada."
            )
        return data
      

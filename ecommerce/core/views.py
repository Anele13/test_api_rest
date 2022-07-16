from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import ProductSerializer, OrderSerializer, OrderDetailSerializer
from .models import Product, Order, OrderDetail
from django.db.utils import IntegrityError
from rest_framework.exceptions import APIException 

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
       order = self.get_object()
       order.restore_product_stock()
       return super(OrderViewSet, self).destroy(request, *args, **kwargs)
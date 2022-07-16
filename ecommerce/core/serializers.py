from dataclasses import fields
from rest_framework import serializers
from .models import OrderDetail, Product, Order
from django.db.utils import IntegrityError
from rest_framework.exceptions import APIException 

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate_stock(self, value):
        if value <= 0:
            raise serializers.ValidationError("Stock must be greater than 0")
        return value

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta: 
        model = OrderDetail
        fields = (
            'id',
            'quantity',
            'product',
        )
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }

class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField(read_only=True, required=False)
    total_usd = serializers.SerializerMethodField(read_only=True, required=False)
    details = OrderDetailSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = (
            'id',
            'date_time',
            'total',
            'total_usd',
            'details',
        )
    
    def validate_details(self, value):
        quantity = value[0].get('quantity',None)
        if quantity <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value

    def get_total(self,obj):
        return obj.get_total()

    def get_total_usd(self, obj):
        return obj.get_total_usd()
    
    def create(self, validated_data):
        details_data = validated_data.get('details',None)
        order = Order.objects.create(date_time=validated_data.get('date_time',None))
        if details_data:
            for item_data in details_data:
                product = item_data.get('product',None)
                quantity = item_data.get('quantity',None)
                try:
                    order_detail = OrderDetail()
                    order_detail.order = order
                    product.decrease_stock(quantity)
                    order_detail.product = product
                    order_detail.quantity = quantity
                    order_detail.save()
                except IntegrityError as exc:
                    raise APIException(detail=exc)
                except Exception as e:
                    raise APIException(detail=e)
        return order

    def update(self, instance, validated_data):
        instance.date_time = validated_data.get('date_time', instance.date_time)
        details_data = validated_data.get('details',None)
        if details_data:
            for item_data in details_data:
                try:
                    order_detail = instance.details.get(id=item_data.get('id',None))
                    order_detail.quantity = order_detail.quantity_constraint(item_data.get('quantity',None))
                    order_detail.save()
                except OrderDetail.DoesNotExist:   
                    pass
                except IntegrityError as exc:
                    raise APIException(detail=exc)
                except Exception as e:
                    raise APIException(detail=e)
        instance.save()
        return instance

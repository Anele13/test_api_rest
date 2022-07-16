from django.contrib import admin
from core.models import *
# Register your models here.

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderDetail)
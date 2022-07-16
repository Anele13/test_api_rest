from django.db import models
import requests


class DolarAPI():
    """
    TODO Esta clase podria estar en otro lugar o simplemente no llamarla por cada orden
    tiene un uso ineficiente. Es solo fines demostrativos
    """
    api_url= 'https://www.dolarsi.com/api/api.php?type=valoresprincipales'

    @classmethod
    def price(self, nombre):
        try:
            request = requests.get(self.api_url)
            if request.status_code == 200:
                json = request.json()
                monto = float(list(filter(lambda d: d['casa']['nombre'] == nombre, json))[0]['casa']['venta'].replace(',','.'))
                return monto
        except Exception as e:
            raise Exception("Error en dolar API: "+str(e))

class Product(models.Model):
    name = models.CharField(max_length=20)
    price = models.FloatField()
    stock = models.PositiveIntegerField(default=0)

    def decrease_stock(self, quantity):
        diferencia = self.stock - quantity
        if self.stock == 0:
            raise Exception("No products left. Sorry")
        elif diferencia < 0:
            raise Exception(f"Only {self.stock} {self.name} left")
        else:
            self.stock -= quantity
            self.save()

    def increase_stock(self,quantity):
        if quantity < 1:
            raise Exception("Enter a positive quantity")
        else:
            self.stock += quantity
            self.save()
    
    def __str__(self):
        return self.name


class Order(models.Model):
    date_time = models.DateField()

    def get_total(self):
        total = self.details.aggregate(models.Sum('product__price'))['product__price__sum']
        if total:
            return total
        return 0

    def get_total_usd(self):
        try:
            return self.get_total() * DolarAPI.price('Dolar Blue')
        except TypeError:
            #Si es otra Exception la dejo
            return 0
        
    def restore_product_stock(self):
        for detail in self.details.all():
            detail.product.increase_stock(detail.quantity)

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    quantity = models.PositiveIntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['order', 'product'], name="unique_order_product"
                )]

    def quantity_constraint(self, q):
        if q > self.quantity:
            self.product.decrease_stock(q - self.quantity)
        elif q < self.quantity:
            self.product.increase_stock((self.quantity - q))
        return q
    

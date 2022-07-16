from email.policy import HTTP
from turtle import update
from django.test import TestCase
import json
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Product, Order, OrderDetail
from django.contrib.auth.models import User
from datetime import datetime
class CoreTestCase(TestCase):

    def setUp(self):
        user = User(
            email='user@gmail.com',
            first_name='Testing',
            last_name='Testing',
            username='testing_login'
        )
        user.set_password('admin123')
        user.save()
        client = APIClient()
        response = client.post(
                '/token/', {
                'email':'user@gmail.com',
                'username': 'testing_login',
                'password': 'admin123',
            },
            format='json'
        )
        result = json.loads(response.content)
        self.access_token = result['access']
        self.user = user


    def test_create_product(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        test_product = {
            'name': 'zapatos',
            'price': 1500.50,
            'stock': 10,
        }
        response = client.post(
            '/product/', 
            test_product,
            format='json'
        )
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertIn('price', result)
        self.assertIn('stock', result)
        if 'id' in result:
            del result['id']
        self.assertEqual(result, test_product)


    def test_update_product(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        product = Product.objects.create(name='zapatos',price=1500.50,stock=10)
        test_product_update = {
            'name': 'carteras',
            'price': 1500.50,
            'stock': 10,
        }
        response = client.put(
            f'/product/{product.id}/', 
            test_product_update,
            format='json'
        )
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'id' in result:
            del result['id']
        self.assertEqual(result, test_product_update)
        
        #Test stock < 0
        test_product_update = {
            'name': 'carteras',
            'price': 1500.50,
            'stock': -1,
        }
        response = client.put(
            f'/product/{product.id}/', 
            test_product_update,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    

    def test_delete_product(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        product = Product.objects.create(name='zapatos',price=1500.50,stock=10)
        response = client.delete(
            f'/product/{product.id}/', 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        product_exists = Product.objects.filter(id=product.id)
        self.assertFalse(product_exists)

    
    def test_get_product(self):
        #List
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        p1 = Product.objects.create(name='zapatos_2',price=1500.50,stock=10)
        Product.objects.create(name='zapatos_3',price=1500.50,stock=10)
        response = client.get('/product/')
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result), 2)
        #Get Product
        response = client.get(f'/product/{p1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content)
        self.assertEqual(p1.id, result['id'])
        self.assertEqual(p1.name, result['name'])
        self.assertEqual(p1.price,result['price'])
        self.assertEqual(p1.stock, result['stock'])

    #ORDER TEST
    def test_create_order(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        test_order = {
            'date_time': datetime.now().date()
        }
        response = client.post(
            '/order/', 
            test_order,
            format='json'
        )
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', result)
        self.assertIn('date_time', result)
        test_order['date_time'] = test_order['date_time'].strftime('%Y-%m-%d')
        del result['id']
        del result['total']
        del result['total_usd']
        del result['details']
        self.assertEqual(result, test_order)

        #Order con detalle igual a stock
        Product.objects.create(name='zapatos_2',price=1500.50,stock=10)
        test_order = {
            'date_time': datetime.now().date(),
            'details':[{
                "quantity": 10,
                "product": 1
            }]
        }
        response = client.post(
            '/order/', 
            test_order,
            format='json'
        )
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', result)
        self.assertIn('date_time', result)
        p = Product.objects.get(id=1)
        self.assertEqual(p.stock, 0)

        #Order del mismo producto pero con stock no disponible
        test_order = {
            'date_time': datetime.now().date(),
            'details':[{
                "quantity": 10,
                "product": 1
            }]
        }
        response = client.post(
            '/order/', 
            test_order,
            format='json'
        )
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        #Orden con quantity = 0
        test_order = {
            'date_time': datetime.now().date(),
            'details':[{
                "quantity": 0,
                "product": 1
            }]
        }
        response = client.post(
            '/order/', 
            test_order,
            format='json'
        )
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_order(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        p = Product.objects.create(name='zapatos_2',price=1500.50,stock=10)
        test_order = {
            'date_time': datetime.now().date(),
            'details':[{
                "quantity": 2,
                "product": 1
            }]
        }
        response = client.post(
            '/order/', 
            test_order,
            format='json'
        )
        result = json.loads(response.content)
        result_update = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', result)
        self.assertIn('date_time', result)
        self.assertIn('details', result)
        test_order['date_time'] = test_order['date_time'].strftime('%Y-%m-%d')
        del result['total']
        del result['total_usd']
        if 'id' in result:
            del result['id']
        #Remuevo id de details
        result['details'] = [{key: value for key, value in dict.items() if key != 'id'} for dict in result['details']]
        self.assertEqual(result, test_order)
        p = Product.objects.get(id=1)
        self.assertEqual(p.stock, 8)

        #Update sobre la cantidad de la orden
        r = result_update['details'][0]
        r['quantity'] = 7
        update_order = {
            'date_time' : datetime.now().date(),
            'details': [r]
        }
        order_id = result_update['id']
        response = client.put(
            f'/order/{order_id}/', 
            update_order,
            format='json'
        )
        result = json.loads(response.content)
        p = Product.objects.get(id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(p.stock, 3)
    

    def test_delete_order(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        p = Product.objects.create(name='zapatos_2',price=1500.50,stock=10)
        test_order = {
            'date_time': datetime.now().date(),
            'details':[{
                "quantity": 2,
                "product": p.id
            }]
        }
        response = client.post(
            '/order/', 
            test_order,
            format='json'
        )
        result = json.loads(response.content)
        p = Product.objects.get(id=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(p.stock, 8)
        order = Order.objects.get(id=result['id'])
        response = client.delete(
            f'/order/{order.id}/', 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        order_exists = Order.objects.filter(id=order.id)
        self.assertFalse(order_exists)
        p = Product.objects.get(id=1)
        #Check restablecer product stock
        self.assertEqual(p.stock, 10)

    def test_get_order(self):
        #List
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        p = Product.objects.create(name='zapatos_2',price=1500.50,stock=10)
        test_order = {
            'date_time': datetime.now().date(),
            'details':[{
                "quantity": 2,
                "product": p.id
            }]
        }
        response = client.post(
            '/order/', 
            test_order,
            format='json'
        )
        test_order_2 = {
            'date_time': datetime.now().date(),
            'details':[{
                "quantity": 2,
                "product": p.id
            }]
        }
        response = client.post(
            '/order/', 
            test_order_2,
            format='json'
        )
        response = client.get('/order/')
        result = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result), 2)
        p = Product.objects.get(id=1)
        #Check restablecer product stock
        self.assertEqual(p.stock, 6)

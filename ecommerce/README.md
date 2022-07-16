# E-commerce-Django-REST
Simple ecommerce con DjangoREST

### Para correr local:

- Instalar requirements en entorno virtual: ```python3 -m venv <entorno>```, ```pip install -r requirements.txt```

- Correr: ```python manage.py makemigrations```, ```python manage.py migrate```,```python manage.py runserver localhost:8000```

- Ir a: ```http://localhost:8000/``` 

### Para visualizar los endpoints en la web (Heroku): 

- Ir a: https://frozen-reaches-24984.herokuapp.com/
    - ~/product
    - ~/order

### Autenticacion con JWT:
- Para obtener un token de acceso Ir a: https://frozen-reaches-24984.herokuapp.com/token
    - ```username:admin```, ```password:admin```

- Para refresco del token = https://frozen-reaches-24984.herokuapp.com/token/refresh

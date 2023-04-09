from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User

# Create your models here.




class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(
        max_length=14,
        validators=[RegexValidator(
            regex=r'^\+254\d{9}$',
            message='Enter a valid Kenyan phone number starting with "+254"',
            code='invalid_phone_number'
        )]
    )
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.store_name


class Collection(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    digital = models.BooleanField(default=False)
    image = models.ImageField(
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['png', 'jpeg', 'jpg'],
            message='Please upload a PNG, JPEG, or JPG file'
        )]
    )
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name="collection_product")
    posted_by = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_phone_number = models.CharField(
        max_length=14,
        validators=[RegexValidator(
            regex=r'^\+254\d{9}$',
            message='Enter a valid Kenyan phone number starting with "+254"',
            code='invalid_phone_number'
        )],
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url



class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField( auto_now_add=True)

    @property
    def get_total(self):
        if(self.quantity != 0):
            total = self.product.price * self.quantity
            return total
          
           
        else:
            return self.product.price


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

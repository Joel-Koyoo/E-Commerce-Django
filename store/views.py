from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from .models import *
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import logout

# Create your views here.
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignupForm, LoginForm, ProductForm
from .models import Customer
from django.contrib.auth.decorators import login_required
# from whatsapp_api import Client

# # def send_whatsapp_message(request, product_id):
# #     # Retrieve the customer's WhatsApp number from the database
# #     customer = Product.objects.get(id=product_id).posted_by
# #     whatsapp_number = customer.whatsapp_number

# #     # Construct the message
# #     product = Product.objects.get(id=product_id)
# #     message = f"Hi, {customer.store_name}! I'm interested in purchasing your {product.name} product. Can you send me more details and a link to purchase it?"

# #     # Initialize the WhatsApp API client
# #     client = Client()

# #     # Send the message
# #     response = client.send_message(whatsapp_number, message)


def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            store_name = form.cleaned_data['store_name']
            whatsapp_number = form.cleaned_data['whatsapp_number']
            password = form.cleaned_data['password']

            # Create new user and customer
            user = User.objects.create_user(
                username=store_name, password=password)
            customer = Customer.objects.create(
                user=user, store_name=store_name, whatsapp_number=whatsapp_number)

            # Redirect to success page or display success message
            messages.success(request, 'User created successfully!')
            return redirect('/')

    else:
        form = SignupForm()
    context = {'form': form}
    return render(request, 'store/signup.html', context)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'store/login.html', {'form': form})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # set the posted_by field to the current user
            product.posted_by = request.user.customer
            product.customer_phone_number = request.user.customer.whatsapp_number
            product.save()
            # or wherever you want to redirect after a successful submission
            return redirect('/')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    products = Product.objects.all()
    for product in products:
        product.collection_name = product.collection.name

    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def get_products_by_collection(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    products = Product.objects.filter(collection=collection)
    data = [{
        'id': p.id,
        'name': p.name,
        'imageURL': p.imageURL,
        'price': p.price
    } for p in products]
    return JsonResponse(data, safe=False)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        print(items)
        print(cartItems)
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productID']
    action = data['action']
    print('action', action)
    print('ProductId', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product
    )
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        total = float((data['form']['total']))
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

    else:
        print("User is not logged in")
    return JsonResponse('Payment submitted..', safe=False)

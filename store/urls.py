from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('', views.store, name="store"),
    path('register/', views.signup, name="register"),
    path('checkout/', views.checkout, name="checkout"),
    path('add_product/', views.add_product, name='add_product'),
    path('cart/', views.cart, name="cart"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    # path('send-whatsapp/<int:product_id>/', views.send_whatsapp_message, name='send_whatsapp_message'),

]

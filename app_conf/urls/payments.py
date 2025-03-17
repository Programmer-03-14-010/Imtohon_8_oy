from django.urls import path
from ..views import *

app_name = 'payments'

urlpatterns = [
    path('payments/months/', PaymentMonthAPIView.as_view(), name='payment_months_list'),
    path('payments/payment-type/', PaymentTypeAPIView.as_view(), name='payment_type_list'),
    path('payments/payment/', PaymentAPIView.as_view(), name='payment_list'),
]

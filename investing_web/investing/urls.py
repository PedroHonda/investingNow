from django.urls import path

from . import views

urlpatterns = [
    path('', views.mainPage_view, name='view-home'),
    path('settings/', views.settings_view, name='view-settings'),
    path('stock/', views.stock_view, name='view-stock'),
    path('stock/<str:ticker>', views.stock_by_ticker_view, name='view-ticker'),
    path('stock/summary/current', views.stock_summary_current_view, name='view-summary-current'),
    path('stock/summary/detail', views.stock_summary_detail_view, name='view-summary-detail'),
]

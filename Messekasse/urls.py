"""
URL configuration for Messekasse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    from django.contrib.auth.views import LogoutView
"""
from django.contrib import admin
from django.urls import path
from Users import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.user_list, name='login'),
    path('login/<str:user_id>/', views.login_pin, name='login_pin'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('add-to-basket/<int:article_id>/', views.add_to_basket, name='add_to_basket'),
    path('purchase/', views.purchase_basket, name='purchase_basket'),
    path('remove-from-basket/<int:bought_article_id>/', views.remove_from_basket, name='remove_from_basket'),
    path('add-special/<int:article_id>/', views.add_special_to_basket, name='add_special_to_basket'),
    path('management/', views.management, name='management'),
    path('marinerechnung/', views.marinerechnung, name='marinerechnung'),
    path('einzahlung/', views.einzahlung, name='einzahlung'),
    path('ueberblick/', views.ueberblick, name='ueberblick'),
    path('monatsuebersicht/', views.monatsuebersicht, name='monatsuebersicht'),
    path('basket/update/<int:bought_article_id>/', views.update_basket_quantity, name='update_basket_quantity'),
    path('nutzer-anlegen/', views.nutzer_anlegen, name='nutzer_anlegen'),
    path('saldo-erinnerung-senden/', views.sende_saldoerinnerung, name='sende_saldoerinnerung'),
    path('nutzer/deaktivieren/<int:user_id>/', views.deaktiviere_nutzer, name='deaktiviere_nutzer'),
    path('messebeitraege-buchen/', views.messebeitraege_buchen, name='messebeitraege_buchen'),




]

from django.urls import path
from rango import views

app_name = 'rango'
urlpatterns = [
    path('register_profile/', views.register_profile, name='register_profile'),
    path('profile/<username>/', views.profile, name='profile'),
    path('goto/<int:page_id>', views.goto_url2, name='goto2'),
    path('goto/', views.goto_url,name='goto'),
    path('search/', views.search, name='search'),
    path('', views.index, name='index'),
    path('category/<slug:category_name_url>/', views.show_category, name='show-category'),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<slug:category_name_slug>/add_page/', views.add_page, name='add_page'),
    path('about/', views.about, name='about'),

]

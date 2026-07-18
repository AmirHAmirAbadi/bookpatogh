from django.urls import path

from . import views

app_name = 'seo_pages'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('book/<str:slug>/', views.book_detail, name='book_detail'),
    path('authors/', views.authors_list, name='authors_list'),
    path('author/<str:slug>/', views.author_detail, name='author_detail'),
    path('workshops/', views.workshops, name='workshops'),
    path('library/', views.library, name='library'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<str:slug>/', views.blog_detail, name='blog_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
]

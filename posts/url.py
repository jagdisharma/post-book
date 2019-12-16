from django.urls import path
from . import views
urlpatterns = [
    path('create', views.create, name='create'),
    path('<int:post_id>', views.details, name='details'),
    path('like/<int:post_id>', views.like, name='like'),
    path('my-posts', views.myposts, name='myposts'),
]

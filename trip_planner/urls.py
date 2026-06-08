from django.urls import path

from . import views

app_name = 'trip_planner'

urlpatterns = [
    path('', views.plan_trip, name='plan_trip'),
    path('book/', views.book_trip, name='book_trip'),
    path('trip/<int:trip_id>/delete/', views.delete_booked_trip, name='delete_booked_trip'),
    path('destination/<int:destination_id>/upload-photo/', views.upload_destination_photo, name='upload_destination_photo'),
    path('destination/<int:destination_id>/delete/', views.delete_destination, name='delete_destination'),
    path('woody-chat/', views.woody_chat, name='woody_chat'),
    path('woody-chat/history/<str:destination>/', views.woody_chat_history, name='woody_chat_history'),
]

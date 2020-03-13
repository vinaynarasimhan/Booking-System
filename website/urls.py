from django.urls import path
from website import views

app_name = "website"

urlpatterns = [
	path('', views.index, name="index"),
	path('<int:is_user>', views.index, name="index"),
    path('login', views.user_login, name="login"),
    path('logout', views.user_logout, name="logout"),
    path('profile', views.add_or_edit_profile, name="profile"),
    path('slots', views.show_bookings, name="bookings"),
    path('add/slot/<int:resource_id>', views.book_slot, name="add_slot"),
    path('edit/slot/<int:slot_id>', views.edit_slot, name="edit_slot"),
]
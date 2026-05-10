from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/dars-jadvali/', views.dars_jadvali, name='dars_jadvali'),

    # O'qituvchilar sahifasi
    path('oqituvchilar/', views.oqituvchilar_list, name='oqituvchilar_list'),

    # O'qituvchi CRUD (mudir uchun)
    path('oqituvchi/qosh/', views.oqituvchi_create, name='oqituvchi_create'),
    path('oqituvchi/<int:pk>/tahrir/', views.oqituvchi_update, name='oqituvchi_update'),
    path('oqituvchi/<int:pk>/ochir/', views.oqituvchi_delete, name='oqituvchi_delete'),

    # Darslar
    path('darslar/', views.darslar_list, name='darslar_list'),
    path('dars/qosh/', views.dars_create, name='dars_create'),
    path('dars/<int:pk>/ochir/', views.dars_delete, name='dars_delete'),

    # Guruhlar
    path('guruhlar/', views.guruhlar_list, name='guruhlar_list'),
    path('guruh/qosh/', views.guruh_create, name='guruh_create'),
    path('guruh/<int:pk>/tahrir/', views.guruh_update, name='guruh_update'),
    path('guruh/<int:pk>/ochir/', views.guruh_delete, name='guruh_delete'),

    # Boshqa sahifalar
    path('statistika/', views.statistika, name='statistika'),
    path('planning/', views.planning, name='planning'),
    path('database/', views.database, name='database'),
    path('soat-kiritish/', views.soat_kiritish, name='soat_kiritish'),
    path('teacher/yuklama-jadvali/', views.yuklama_jadvali, name='yuklama_jadvali'),
    path('dars/<int:pk>/belgilash/', views.dars_belgilash, name='dars_belgilash'),
    path('tahlil/', views.tahlil, name='tahlil'),
    path('hisobot/', views.hisobot, name='hisobot'),
]

from django.urls import path
from django.contrib.auth import views as auth_views

import main.view.home as views 
import main.view.notes as note_views
import main.view.file as file
import main.view.login as login_view

loging = [
    path("login/", login_view.login_view, name="login"),
    path("logout/", login_view.logout_view, name="logout"),
    path("register/", login_view.register_view, name="register"),
]

notece = [
    # 🔒 OWNER + PUBLIC LIST
    path("notice/list/", note_views.notice_list_view, name="notice_list"),

    # 🔒 CREATE NOTICE
    path("notice/create/", note_views.notice_create_view, name="notice_create"),

    # 🌍 PUBLIC LINK (expire_date + limit + views + is_active)
    path("notice/public/<uuid:public_id>/", note_views.notice_public_view, name="notice_public"),
    
    # 🔒 DETAIL (faqat owner)
    path("notice/<int:notice_id>/", note_views.notice_detail_view, name="notice_detail"),

    # ✏️ EDIT (faqat owner)
    path("notice/<int:notice_id>/edit/", note_views.notice_edit_view, name="notice_edit"),

    # 🗑 DELETE (faqat owner)
    path("notice/<int:notice_id>/delete/", note_views.notice_delete_view, name="notice_delete"),
]

file = [
  # 📁 FILE LIST / CRUD
    path('file/', file.file_list_view, name='file_list'),
    path('file/create/', file.file_create_view, name='file_create'),
    path('file/<int:file_id>/', file.file_detail_view, name='file_detail'),
    path('file/<int:file_id>/edit/', file.file_edit_view, name='file_edit'),
    path('file/<int:file_id>/delete/', file.file_delete_view, name='file_delete'),

# 🔗 PUBLIC / PRIVATE LINK VIEW
    path('file/public/<uuid:public_id>/', file.file_public_view, name='file_public'),


    # ⬇️ DOWNLOAD (PRIVATE)
    path(
        'file/<int:file_id>/download/',
        file.file_download_view,
        name='file_download'
    ),

    # ⬇️ DOWNLOAD (PUBLIC LINK)
    path(
        'file/public/<uuid:public_id>/download/',
        file.public_file_download_view,
        name='file_public_download'
    ),
    path('file/public/<uuid:public_id>/', file.file_public_view, name='file_public')

]
urlpatterns = [
    path('', views.home),  
    path("account/", views.account),
] + notece + file + loging

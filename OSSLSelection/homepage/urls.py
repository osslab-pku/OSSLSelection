# 配置模板文件中静态文件路径
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import staticfiles

from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    path('',views.index,name='index'),
    path(r'about_license/',views.about_license,name='about_license'),
    path(r'license_list/',views.license_list,name='license_list'),
    path(r'license_list_details/',views.license_list_details,name='license_list_details'),
    path(r'license_compatibility/',views.license_compatibility,name='license_compatibility'),
    path(r'license_compatibility_judge/',views.license_compatibility_judge,name='license_compatibility_judge'),
    path(r'license_selection/', views.license_selection, name='license_selection'),
    path(r'license_trend/', views.license_trend, name='license_trend'),
    path(r'license_fqa/', views.license_fqa, name='license_fqa'),
    path(r'license_fqa_list/', views.license_fqa_list, name='license_fqa_list'),
    path(r'contact/', views.contact, name='contact'),
    path(r'fqa_bot/', views.license_bot, name='license_bot'),
    path(r'license_check/', views.license_check, name='license_check'),
    path(r'license_terms_choice/', views.license_terms_choice, name='license_terms_choice'),
    path(r'license_type_choice/', views.license_type_choice, name='license_type_choice'),
    path(r'business_model/', views.business_model, name='business_model'),
    path(r'license_feature/', views.license_feature, name='license_feature'),
    path(r'license_frame/', views.license_frame, name='license_frame'),
    path(r'license_compare/', views.license_compare, name='license_compare'),
    path(r'sort_license_popular/',views.sort_license_popular,name='sort_license_popular'),
    path(r'sort_license_comples/',views.sort_license_complex,name='sort_license_complex'),
    path(r'show_progress/',views.show_progress,name='show_progress'),
    path(r'draw_trend/',views.draw_trend,name='draw_trend'),
]

#设置静态文件路径
urlpatterns += staticfiles_urlpatterns()
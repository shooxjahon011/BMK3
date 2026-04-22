from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView  # To'g'irlandi: templates emas TemplateView

urlpatterns = [
path('', views.login, name='login_with_password'),
                  path('login/', views.login, name='login_with_password'),
                  path('BMK-asosiy/', views.home, name='home'),
                  path('sms-send/', views.vote_view, name='sms_send'),
                  path('verify/', views.verify_and_finish, name='verify_and_finish'),
                  path('loyha/', views.loyha, name='loyha'),  # / belgisi qo'shildi
                  path('vote/', views.vote_view, name='vote_page'),
                  path('xabarlar/', views.mahallauz, name='mahallauz'),
                  path('adminhomee/', views.adminhomeee, name='I'),
                  path('xabarlar1/', views.mahallauz2, name='mahallauz2'),
                  path('delete/<int:pk>/', views.delete_announcement, name='delete_announcement'),
                  path('register/', views.register, name='register'),

path('sw.js', TemplateView.as_view(template_name="sw.js", content_type='application/javascript'), name='sw.js'),
path('manifest.json', TemplateView.as_view(template_name="manifest.json", content_type='application/json'), name='manifest.json'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
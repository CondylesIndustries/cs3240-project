from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logout", views.logout_view, name="logout"),
    path("reporta", views.submit_anonymous_report, name="reporta"),
    path("reportu", views.submit_report, name="reportu"),
    path("report_success", views.report_success, name="report_success"),
    path("<int:report_id>/view_report", views.view_report, name="view_report"),
    path("report_list", views.report_list, name="report_list"),
    path("accounts/google/login/callback/", views.google_callback, name='google_callback'),
    # path("reportu/logout", views.logout_view),
    path("<int:report_id>/logout", views.logout_view),
]
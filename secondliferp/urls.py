from django.contrib import admin
from django.urls import path
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static
from matches.views import home_view, match_detail
from accounts.views import bet_history_view, balance_view, withdraw_view, cancel_withdrawal


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', accounts_views.register_view, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('profile/', accounts_views.profile_view, name='profile'),
    path('', home_view, name='home'),
    path('match/<int:match_id>/', match_detail, name='match_detail'),
    path('bet-history/', bet_history_view, name='bet_history'),
    path('balance/', accounts_views.balance_view, name='balance'),
    path('withdraw/', accounts_views.withdraw_view, name='withdraw'),
    path('withdrawals/cancel/<int:pk>/', accounts_views.cancel_withdrawal, name='cancel_withdrawal'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

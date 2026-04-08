from django.urls import path

from .views import BoardListCreateView, BoardDetailView

urlpatterns = [
    # Klärung später, ob für GET und POST eine oder zwei Views sinnvoll !
    path('', BoardListCreateView.as_view(), name='board-list'),
    
    # für <int:board_id>/ später klären ob GET, UPDATE und DELETE in einer View sinnvoll !
    path('<int:board_id>/', BoardDetailView.as_view(), name='board-detail'),
]
from django.urls import path, include
from django.conf import settings
from django.contrib.auth.views import LogoutView
from library.views import (
    homepage, logsin, LibrarianLoginView, librarian_signup, student_login, custom_logout,
    update_student_profile, student_dashboard, librarian_dashboard, student_issuing_history,
    add_book, edit_book, search_books, borrow_book, return_book, book_details, borrowed_books, upload_books,
    download_template, submit_feedback, view_feedbacks, rate_book, upload_books_excel, feedback_submitted,
)
from django.conf.urls import handler403
from django.conf.urls.static import static

handler403 = 'library.views.permission_denied_view'

urlpatterns = [
    path('', homepage, name='homepage'),
    path('logsin/', logsin, name='logsin'),
    path('librarian/login/', LibrarianLoginView.as_view(), name='librarian_login'),
    path('librarian/signup/', librarian_signup, name='librarian_signup'),    
    path('student/login/', student_login, name='student_login'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/update-profile/', update_student_profile, name='update_student_profile'),
    path('librarian/dashboard/', librarian_dashboard, name='librarian_dashboard'),
    path('books/add/', add_book, name='add_book'),
    path('books/edit/<int:pk>/', edit_book, name='edit_book'),
    path('books/search/', search_books, name='search_books'), 
    path('books/borrow/<int:pk>/', borrow_book, name='borrow_book'),
    path('books/return/<int:pk>/', return_book, name='return_book'),
    path('accounts/', include('allauth.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('leave/', custom_logout, name= 'leave'),
    path('books/<int:pk>/', book_details, name='book_details'),
    path('student/history/', student_issuing_history, name='student_history'),
    path('borrowed_books/', borrowed_books, name='borrowed_books'),
    path('upload_books/', upload_books, name='upload_books'),
    path('download_template/', download_template, name='download_template'),
    path('feedback/submit/', submit_feedback, name='submit_feedback'),
    path('feedbacks/', view_feedbacks, name='view_feedbacks'),
    path('book/<int:book_id>/rate/', rate_book, name='rate_book'),
    path('upload_books_excel/', upload_books_excel, name='upload_books_excel'),
    path('feedback/submitted/', feedback_submitted, name='feedback_submitted'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from .models import StudentProfile, LibrarianProfile, Book, BorrowRecord, BookRating, Feedback
from .forms import StudentProfileForm, LibrarianSignupForm, AddBookForm, FeedbackForm, LibrarianLoginForm, ExcelUploadForm, RatingForm
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone

def permission_denied_view(request, exception):
    return HttpResponseForbidden("You are not authorized to log in with this email domain.")

def upload_books(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        try:
            data = pd.read_excel(excel_file)
            for _, row in data.iterrows():
                Book.objects.create(
                    title=row['Title'],
                    author=row['Author'],
                    publisher=row['Publisher'],
                    isbn=row['ISBN'],
                    total_copies=row['Total Copies'],
                    available_copies=row['Available Copies'] or row['Total Copies'],
                )
            return HttpResponse("Books uploaded successfully!")
        except Exception as e:
            return HttpResponse(f"Error: {e}")
    return render(request, 'upload_books.html')

def download_template(request):
    template_data = {
        'Title': ['Sample Title'],
        'Author': ['Sample Author'],
        'Publisher': ['Sample Publisher'],
        'ISBN': ['1234567890123'],
        'Total Copies': [10],
        'Available Copies': [5],
    }
    df = pd.DataFrame(template_data)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Book_Upload_Template.xlsx"'
    df.to_excel(response, index=False)
    return response

def custom_logout(request):
    logout(request)
    return redirect('homepage')


@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if not hasattr(request.user, 'librarianprofile'):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = AddBookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_details', pk=book.pk)
    else:
        form = AddBookForm(instance=book)

    return render(request, 'edit_book.html', {'form': form, 'book': book})

def homepage(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'librarianprofile'):
            return redirect('librarian_dashboard')
        elif hasattr(request.user, 'studentprofile'):
            return redirect('student_dashboard')
    return render(request, 'homepage.html')

def logsin(request):
    return render(request, 'logsin.html')

# Views for Librarian Login and Signup
class LibrarianLoginView(FormView):
    template_name = 'librarian_login.html'
    form_class = LibrarianLoginForm
    success_url = reverse_lazy('librarian_dashboard')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, 'Invalid credentials')
            return self.form_invalid(form)


def librarian_signup(request):
    if request.method == "POST":
        form = LibrarianSignupForm(request.POST)
        
        if form.is_valid():
            user = form.save()  
            
            messages.success(request, "Librarian account created successfully!")
            return redirect('librarian_login')  
            
    else:
        form = LibrarianSignupForm()

    return render(request, 'librarian_signup.html', {'form': form})

def student_login(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'studentprofile'):
            return redirect('student_dashboard')
        return redirect('update_student_profile')
    return render(request, 'student_login.html')

@login_required
def student_dashboard(request):
    borrow_records = BorrowRecord.objects.filter(student=request.user.studentprofile)
    
    for record in borrow_records:
        record.due_date = record.borrow_date + timedelta(days=record.book.issue_period)
    
    return render(request, 'student_dashboard.html', {
        'borrow_records': borrow_records,
        'profile': request.user.studentprofile
    })

@login_required
def librarian_dashboard(request):
    librarian_profile = LibrarianProfile.objects.get(user=request.user)
    return render(request, 'librarian_dashboard.html', {'psrn': librarian_profile.psrn})

@login_required
def update_student_profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=profile)
    return render(request, 'update_profile.html', {'form': form})

@login_required
def add_book(request):
    if request.method == 'POST':
        form = AddBookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('librarian_dashboard')
    else:
        form = AddBookForm()
    return render(request, 'add_book.html', {'form': form})

@login_required
def upload_books_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.handle_uploaded_file(request.FILES['excel_file'])
            return redirect('librarian_dashboard')
    else:
        form = ExcelUploadForm()
    return render(request, 'upload_books_excel.html', {'form': form})

def download_excel_template(request):
    template_data = [
        ['Title', 'Author', 'Publisher', 'ISBN', 'Total Copies', 'Issue Period (Days)', 'Late Fee']
    ]
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="book_template.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in template_data:
        ws.append(row)
    wb.save(response)
    return response

@login_required
def search_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(title__icontains=query)
    return render(request, 'search_books.html', {'books': books, 'query': query})

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if book.is_available():
        record = BorrowRecord.objects.create(student=request.user.studentprofile, book=book)
        
        book.available_copies -= 1
        book.save()

        record.return_date = None
        record.save()

        return redirect('student_dashboard') 
    else:
        return HttpResponse("Book not available for borrowing") 

@login_required
def return_book(request, pk):
    record = get_object_or_404(BorrowRecord, pk=pk, student=request.user.studentprofile)
    book = record.book
    
    today = timezone.now().date()
    issue_date = record.borrow_date
    days_overdue = (today - issue_date).days - book.issue_period
    
    if days_overdue > 0:
        late_fee = days_overdue * book.late_fee
    else:
        late_fee = 0

    book.available_copies += 1
    book.save()

    record.return_date = today
    record.save()

    return render(request, 'return_book_confirmation.html', {'book': book, 'late_fee': late_fee})

@login_required
def feedback_submitted(request):
    return render(request, 'feedback_submitted.html')

@login_required
def book_details(request, pk):
    book = get_object_or_404(Book, pk=pk)

    is_librarian = hasattr(request.user, 'librarianprofile')

    if request.method == 'POST' and is_librarian:
        form = AddBookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_details', pk=book.pk)
    else:
        form = AddBookForm(instance=book)

    return render(request, 'book_details.html', {
        'book': book,
        'form': form,
        'is_librarian': is_librarian,
    })

@login_required
def borrowed_books(request):
    students = StudentProfile.objects.all()

    students_with_borrowed_books = []

    for student in students:
        borrow_records = BorrowRecord.objects.filter(student=student)

        students_with_borrowed_books.append({
            'student': student,
            'borrow_records': borrow_records
        })

    return render(request, 'borrowed_books.html', {'students_with_borrowed_books': students_with_borrowed_books})

@login_required
def student_issuing_history(request):
    student_profile = request.user.studentprofile
    borrow_records = BorrowRecord.objects.filter(student=student_profile)
    for record in borrow_records:
        record.due_date = record.borrow_date + timedelta(days=record.book.issue_period)
    return render(request, 'issuing_history.html', {'borrow_records': borrow_records})

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user.studentprofile
            feedback.save()
            return redirect('feedback_submitted')  # Redirect after submission
    else:
        form = FeedbackForm()
    return render(request, 'submit_feedback.html', {'form': form})

@login_required
def view_feedbacks(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'view_feedbacks.html', {'feedbacks': feedbacks})

@login_required
def rate_book(request, book_id):
    book = Book.objects.get(id=book_id)
    borrow_record = BorrowRecord.objects.filter(student=request.user.studentprofile, book=book)
    
    if not borrow_record.exists():
        return HttpResponse("You cannot rate this book because you have not borrowed it.")

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = BookRating.objects.get_or_create(
                student=request.user.studentprofile,
                book=book,
            )
            rating.rating = form.cleaned_data['rating']
            rating.save()
            return redirect('book_detail', book_id=book.id)
    else:
        form = RatingForm()

    return render(request, 'rate_book.html', {'form': form, 'book': book})
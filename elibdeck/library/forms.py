from django import forms
from .models import StudentProfile, LibrarianProfile, Book, Feedback, BookRating
from django.contrib.auth.models import User
import openpyxl

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['room', 'hostel']

class LibrarianLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class LibrarianSignupForm(forms.ModelForm):
    name = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    psrn = forms.CharField(max_length=10, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

            librarian_profile = LibrarianProfile.objects.create(
                user=user, 
                psrn=self.cleaned_data['psrn']
            )
        return user

class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'isbn', 'cover_image', 'total_copies', 'available_copies', 'issue_period', 'late_fee']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'body', 'image']

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()

    def handle_uploaded_file(self, file):
        wb = openpyxl.load_workbook(file)
        sheet = wb.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if len(row) < 5:
                raise ValueError(f"Row has insufficient columns: {row}")

            title = row[0]
            author = row[1]
            publisher = row[2]
            isbn = row[3]
            total_copies = row[4]
            issue_period = row[5] if len(row) > 5 else 14
            late_fee = row[6] if len(row) > 6 else 5.00

            if not title or not author or not isbn or not total_copies:
                raise ValueError(f"Missing required data in row: {row}")

            if Book.objects.filter(isbn=isbn).exists():
                raise ValueError(f"Book with ISBN {isbn} already exists.")

            Book.objects.create(
                title=title,
                author=author,
                publisher=publisher,
                isbn=isbn,
                total_copies=total_copies,
                available_copies=total_copies,
                issue_period=issue_period,
                late_fee=late_fee,
                cover_image='book_covers/dessert.jpg'
            )

class RatingForm(forms.Form):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # Rating range: 1 to 5
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)

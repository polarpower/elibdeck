from django import forms
from .models import StudentProfile, LibrarianProfile, Book, Complaint  
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

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'body', 'image']

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()

    def handle_uploaded_file(self, file):
        wb = openpyxl.load_workbook(file)
        sheet = wb.active
        for row in sheet.iter_rows(min_row=2, values_only=True):  
            title, author, publisher, isbn, total_copies, issue_period, late_fee = row
            if not isbn or not total_copies:
                raise ValidationError(f"Missing required data in row: {row}. ISBN and total copies are required.")
            
            if Book.objects.filter(isbn=isbn).exists():
                raise ValidationError(f"Book with ISBN {isbn} already exists.")
            
            issue_period = issue_period or 14  
            late_fee = late_fee or 5.00 
            
            Book.objects.create(
                title=title,
                author=author,
                publisher=publisher,
                isbn=isbn,
                total_copies=total_copies,
                available_copies=total_copies,
                issue_period=issue_period,
                late_fee=late_fee
            )
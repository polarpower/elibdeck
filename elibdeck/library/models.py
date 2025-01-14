from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room = models.CharField(max_length=10)
    hostel = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username

class LibrarianProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    psrn = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    cover_image = models.ImageField(
        upload_to='media/book_covers/', 
        blank=True, 
        null=True, 
        default='media/book_covers/dessert.jpg'
    )
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField(default=0)
    issue_period = models.PositiveIntegerField(default=14)  
    late_fee = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)  
    def is_available(self):
        return self.available_copies > 0

    def __str__(self):
        return self.title
 
    def get_average_rating(self):
        ratings = BookRating.objects.filter(book=self)
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0

    def get_rating_count(self):
        return BookRating.objects.filter(book=self).count()

class BorrowRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.book.title}"

class Feedback(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    image = models.ImageField(upload_to='feedback_images/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.student.user.username}: {self.subject}"

class BookRating(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])

    class Meta:
        unique_together = ('student', 'book')

    def __str__(self):
        return f"{self.student.user.username} - {self.book.title}: {self.rating}"

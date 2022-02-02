from django.contrib import admin

# Register your models here.
from .models import Author, Genre, Book, BookInstance,Language

# Define the admin class
# class AuthorAdmin(admin.ModelAdmin):
#     pass
admin.site.register(Genre)
admin.site.register(Language)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    
# Register the admin class with the associated model
admin.site.register(Author,AuthorAdmin)

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance


# Register the Admin Classes for Book Using The Decorator
@admin.register(Book)
# class BookAdmin(admin.ModelAdmin):
#     pass

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]
    def display_genre(self,obj):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in obj.genre.all()[:3])

    display_genre.short_description = 'Genre'



class BooksInstanceInline(admin.TabularInline):
    model = BookInstance



# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book','imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back','borrower')
        }),
    )

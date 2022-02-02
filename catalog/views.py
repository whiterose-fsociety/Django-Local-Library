from django.contrib.auth.mixins import PermissionRequiredMixin
from datetime import timedelta, date
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

from catalog.forms import RenewBookModelForm


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalog/index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 2


class AuthorListView(generic.ListView):
    model = Author


class AuthorDetailView(generic.DetailView):
    model = Author


class BookDetailView(generic.DetailView):
    model = Book


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


# Added as part of challenge!


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        # Check if the form is valid:
        if form.is_valid():
            # process the datain form.cleaned_data as required
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = date.today() + timedelta(weeks=3)
        form = RenewBookModelForm(
            initial={'renewal_date': proposed_renewal_date})
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'

# Classes created for the forms challenge


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'

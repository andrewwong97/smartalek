from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from .models import Course

# Create your views here.


class IndexView(generic.ListView):
    model = Course
    template_name = 'app/index.html'
    context_object_name = 'current_catalog'

    def get_queryset(self):
        return Course.objects.order_by('number')

class DetailView(generic.DetailView):
    model = Course
    template_name = 'app/detail.html'

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

from .models import SgAccess
from .forms import SgAccessForm


# Create your views here.
@csrf_exempt
def index(request):
    form = SgAccessForm(request.POST or None)
    allowed_sg_list = SgAccess.objects.order_by("-datetime_added")
    context = {
        'sg_access_form': form,
        'allowed_sg_list': allowed_sg_list
    }
    if form.is_valid():
        form.save(user=request.user, commit=False)
        return HttpResponseRedirect("sgman")

    return render(request, 'sgman/sg_list.html', context)

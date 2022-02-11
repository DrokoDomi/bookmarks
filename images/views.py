from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from common.decorators import ajax_required
from common.helpers import is_ajax
from .forms import ImageCreateForm
from .models import Image


@login_required
def image_create(request):
    if request.method == "POST":
        form = ImageCreateForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            messages.success(request, "Image added successfully")

            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreateForm(request.GET)

    return render(request, "images/image/create.html", {"section": "images", "form": form})


def image_detail(request, id_, slug):
    image = get_object_or_404(Image, id=id_, slug=slug)
    return render(request, "images/image/detail.html", {"section": "images", "image": image})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get("id")
    action = request.POST.get("action")
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == "like":
                image.users_like.add(request.user)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({"status": "ok"})
        except Exception:
            pass
    return JsonResponse({"status": "error"})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get("page")
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if is_ajax(request):
            return HttpResponse("")
        images = paginator.page(paginator.num_pages)
    render_arguments = {"section": "images", "images": images}
    if is_ajax(request):
        return render(request, "images/image/list_ajax.html", render_arguments)
    return render(request, "images/image/list.html", render_arguments)
from django.shortcuts import render

from .models import User


def test_view_hello(request):
    return render(request, "simple.html")


def test_view(request):
    return render(request, "index.html")


def test_query(request):
    user_name = request.POST['user_name']
    users = User.objects.raw(
        f"SELECT * from app_user WHERE user_name = \'{user_name}\'"  # '/
    )
    for item in users:
        print(item)
    return render(request, "index.html", {'users': users})

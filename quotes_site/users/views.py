from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomRegisterForm, LoginForm


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Log in successful")
            return redirect("quotes:root")
    else:
        form = LoginForm()

    return render(request, "users/login.html", context={"form": form})


def logout_view(request):
    logout(request)
    return redirect("quotes:root")


def sign_up_view(request):
    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successfully")
            return redirect("quotes:root")

        messages.error(request, "Please correct the errors below.")

    else:
        form = CustomRegisterForm()

    return render(request, "users/sign_up.html", context={"form": form})

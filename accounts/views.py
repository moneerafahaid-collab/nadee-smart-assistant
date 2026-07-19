from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import EmployeeLoginForm, EmployeeRegistrationForm


class EmployeeLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmployeeLoginForm
    redirect_authenticated_user = True


class EmployeeLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


def register(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:home")
    else:
        form = EmployeeRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})

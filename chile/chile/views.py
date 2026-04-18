from django.shortcuts import render


def name_form(request):
    return render(request, "name_form.html")

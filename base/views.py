from django.shortcuts import render


def error_403(request, exception):
    return render(request, 'error_403.html', status=403)


def error_404(request, exception):
    return render(request, 'error_404.html', status=404)


def error_500(request, exception):
    return render(request, 'error_500.html', status=500)


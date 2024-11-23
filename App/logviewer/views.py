# logviewer/views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .scanners.CSRF import csrf_scanner
from .scanners.sqli_detector import sql_injection_detector
from .scanners.XSS_Scanner import xss_scanner
from .scanners.CORScanner import cors_scan
from multiprocessing import Process
from .forms import URLInputForm


def log_view(request):
    return render(request, 'logviewer/log_view.html')


@csrf_exempt
def csrf_scan_view(request):
    return handle_scan(request, csrf_scanner.main)


@csrf_exempt
def sql_scan_view(request):
    return handle_scan(request, sql_injection_detector.main)


@csrf_exempt
def xss_scan_view(request):
    return handle_scan(request, xss_scanner.main)


@csrf_exempt
def cors_scan_view(request):
    return handle_scan(request, cors_scan.main)


def handle_scan(request, scanner_function):
    if request.method == "POST":
        form = URLInputForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            process = Process(target=scanner_function, args=(url,))
            process.start()
            result = f"Processed URL with {scanner_function.__name__}: {url}"

            return JsonResponse({
                "status": "success",
                "message": "URL processed successfully",
                "url": url,
                "result": result
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid URL",
                "errors": form.errors
            }, status=400)
    else:
        return JsonResponse({
            "status": "error",
            "message": "Only POST requests are allowed"
        }, status=405)

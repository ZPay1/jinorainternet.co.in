from django.conf import settings
from django.http import FileResponse, Http404
from pathlib import Path

class StaticMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.static_root = Path(settings.STATIC_ROOT)
        self.media_root = Path(settings.MEDIA_ROOT)

    def __call__(self, request):
        path = request.path

        # Serve static files
        if path.startswith(settings.STATIC_URL):
            file_path = self.static_root / path[len(settings.STATIC_URL):]
            return self.serve_file(file_path)

        # Serve media files
        if path.startswith(settings.MEDIA_URL):
            file_path = self.media_root / path[len(settings.MEDIA_URL):]
            return self.serve_file(file_path)

        return self.get_response(request)

    def serve_file(self, file_path):
        try:
            if file_path.is_file():
                return FileResponse(open(file_path, 'rb'))
            else:
                raise Http404("File not found")
        except Exception:
            raise Http404("Error serving file")

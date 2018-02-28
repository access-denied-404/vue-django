from bakery.views import BuildableTemplateView


class Error404View(BuildableTemplateView):
    build_path = '404.html'
    template_name = 'marer/static/error_404.html'


class Error500View(BuildableTemplateView):
    build_path = '500.html'
    template_name = 'marer/static/error_500.html'

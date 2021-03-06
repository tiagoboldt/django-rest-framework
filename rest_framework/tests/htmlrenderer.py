from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import TestCase
from django.template import TemplateDoesNotExist, Template
import django.template.loader
from rest_framework.compat import patterns, url
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def example(request):
    """
    A view that can returns an HTML representation.
    """
    data = {'object': 'foobar'}
    return Response(data, template_name='example.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def permission_denied(request):
    raise PermissionDenied()


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def not_found(request):
    raise Http404()


urlpatterns = patterns('',
    url(r'^$', example),
    url(r'^permission_denied$', permission_denied),
    url(r'^not_found$', not_found),
)


class TemplateHTMLRendererTests(TestCase):
    urls = 'rest_framework.tests.htmlrenderer'

    def setUp(self):
        """
        Monkeypatch get_template
        """
        self.get_template = django.template.loader.get_template

        def get_template(template_name):
            if template_name == 'example.html':
                return Template("example: {{ object }}")
            raise TemplateDoesNotExist(template_name)

        django.template.loader.get_template = get_template

    def tearDown(self):
        """
        Revert monkeypatching
        """
        django.template.loader.get_template = self.get_template

    def test_simple_html_view(self):
        response = self.client.get('/')
        self.assertContains(response, "example: foobar")
        self.assertEquals(response['Content-Type'], 'text/html')

    def test_not_found_html_view(self):
        response = self.client.get('/not_found')
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.content, "404 Not Found")
        self.assertEquals(response['Content-Type'], 'text/html')

    def test_permission_denied_html_view(self):
        response = self.client.get('/permission_denied')
        self.assertEquals(response.status_code, 403)
        self.assertEquals(response.content, "403 Forbidden")
        self.assertEquals(response['Content-Type'], 'text/html')


class TemplateHTMLRendererExceptionTests(TestCase):
    urls = 'rest_framework.tests.htmlrenderer'

    def setUp(self):
        """
        Monkeypatch get_template
        """
        self.get_template = django.template.loader.get_template

        def get_template(template_name):
            if template_name == '404.html':
                return Template("404: {{ detail }}")
            if template_name == '403.html':
                return Template("403: {{ detail }}")
            raise TemplateDoesNotExist(template_name)

        django.template.loader.get_template = get_template

    def tearDown(self):
        """
        Revert monkeypatching
        """
        django.template.loader.get_template = self.get_template

    def test_not_found_html_view_with_template(self):
        response = self.client.get('/not_found')
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.content, "404: Not found")
        self.assertEquals(response['Content-Type'], 'text/html')

    def test_permission_denied_html_view_with_template(self):
        response = self.client.get('/permission_denied')
        self.assertEquals(response.status_code, 403)
        self.assertEquals(response.content, "403: Permission denied")
        self.assertEquals(response['Content-Type'], 'text/html')

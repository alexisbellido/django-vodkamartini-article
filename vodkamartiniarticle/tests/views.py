from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db import IntegrityError
from django.contrib.auth.models import User
from vodkamartiniarticle.models import Article
import os
from django.core.files import File
from django.conf import settings

class ArticleHomeTest(TestCase):
    def setUp(self):
        """
        django.test.client.Client gets confused with templates when using the cache, that's why we need to clear it.
        """
        cache.clear()
        self.author = User.objects.create_user(username='joe', password='qwerty')
        self.teaser = "this is a teaser"
        self.body = "and this is the body"

    def testHome(self):
        """
        Creates one article and tests it's correctly returned
        """
        title = "First Live Article"
        status = Article.LIVE_STATUS

        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open("%s/media/image.png" % current_dir, "rb") as f:
            """ uses with statement to autoclose the file """
            image_file = File(f)
            article = Article(title=title, teaser=self.teaser, body=self.body, author=self.author, status=status, image=image_file)
            article.save()

        response = self.client.get(reverse('vodkamartiniarticle_articles_home'))
        os.remove("%s%s" % (settings.MEDIA_ROOT, article.image.name)) # remove file in MEDIA_ROOT to avoid leftovers

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vodkamartiniarticle/article_list.html')
        self.assertEqual(response.context['articles'].number, 1) # paginator page number should be 1 for one article
        self.assertEqual(response.context['object_list'][0].pk, article.pk) # first article in context is the one just created

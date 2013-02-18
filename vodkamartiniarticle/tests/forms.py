from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from vodkamartiniarticle.models import Article
from vodkamartinicategory.models import Category
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import os

# TODO create some articles, users, groups and permissions and check

class ArticleForms(TestCase):
    def setUp(self):
        """
        Create groups editor and author and their corresponding permissions.
        Create one editor, one author and one normal user without any special permission.
        The author will then create an article which he can edit.
        The editor can edit anything.
        The user without permissions can just view.
        """
        self.regular = User.objects.create_user(username='bill_normal', password='secret')
        self.author = User.objects.create_user(username='joe_author', password='secret')
        self.editor = User.objects.create_user(username='mark_editor', password='secret')

        self.perms = {
            'add_article': Permission.objects.get(codename='add_article', content_type__app_label='vodkamartiniarticle'),
            'change_article': Permission.objects.get(codename='change_article', content_type__app_label='vodkamartiniarticle'),
            'change_own_article': Permission.objects.get(codename='change_own_article', content_type__app_label='vodkamartiniarticle'),
            'delete_article': Permission.objects.get(codename='delete_article', content_type__app_label='vodkamartiniarticle'),
            'view_article': Permission.objects.get(codename='view_article', content_type__app_label='vodkamartiniarticle'),
        }

        self.group_author = Group.objects.create(name='author')
        self.group_author.permissions.add(
                                            self.perms['add_article'], 
                                            self.perms['change_own_article'],
                                         )

        self.group_editor = Group.objects.create(name='editor')
        self.group_editor.permissions.add(
                                            self.perms['add_article'], 
                                            self.perms['change_article'], 
                                            self.perms['change_own_article'], 
                                            self.perms['delete_article'],
                                         )

        self.author.groups.add(self.group_author)
        self.editor.groups.add(self.group_editor)

        title = "First Live Article"
        status = Article.LIVE_STATUS
        teaser = "The article teaser"
        body = "The article body"
        self.article = Article(title=title, teaser=teaser, body=body, author=self.author, status=status)
        self.article.save()

    def tearDown(self):
        self.client.logout()

    def testAddArticle(self):
        """
        There's a media directory below the tests directory where this file lives, and we use the file image.png there for posting an article.
        """
        logged_in = self.client.login(username='joe_author', password='secret')
        self.assertEqual(logged_in, True, 'The user was not logged in.')
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_file = open("%s/media/image.png" % current_dir, "rb")
        data = {'title': 'my title', 'teaser': 'my teaser', 'body': 'my body', 'image': image_file}
        response = self.client.post(reverse('vodkamartiniarticle_article_add'), data, follow=True)
        image_file.close()
        try:
            article = Article.objects.get(slug=slugify(data['title']))
        except Article.DoesNotExist:
            self.assertTrue(False, "The article was not created. Apparently the user did not have the correct permissions.")
        self.assertTemplateUsed(response, 'vodkamartiniarticle/article_detail.html')
        self.assertEqual(article.title, data['title'])

    #def testChangeArticle(self):
    #    """
    #    change_article allows users to edit any article, no matter who published it. Initially granted to the editor group.
    #    """
    #    pass

    def testChangeOwnArticle(self):
        """
        change_own_article allows users to edit only the articles they published. Initially granted to the author group.
        There's a media directory below the tests directory where this file lives, and we use the file image.png there for posting an article.
        """
        logged_in = self.client.login(username='joe_author', password='secret')
        self.assertEqual(logged_in, True, 'The user was not logged in.')
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_file = open("%s/media/image.png" % current_dir, "rb")
        data = {'title': 'edited title', 'teaser': 'edited teaser', 'body': 'edited body', 'image': image_file}
        response = self.client.post(reverse('vodkamartiniarticle_article_edit', args=[self.article.id]), data, follow=True)
        image_file.close()
        article = Article.objects.get(pk=self.article.id)
        self.assertTemplateUsed(response, 'vodkamartiniarticle/article_detail.html')
        self.assertEqual(article.title, data['title'], "The article was not edited, check the user has the change_own_article permission.")

    #def testViewArticle(self):
    #    pass

    #def testDeleteArticle(self):
    #    pass

    def testCantAddArticle(self):
        """
        The user is not authenticated, he shouldn't be able to add an article.
        Check that posting to the 'vodkamartiniarticle_article_add' view redirects to login.
        """
        data = {'title': 'my title', 'teaser': 'my teaser', 'body': 'my body'}
        response = self.client.post(reverse('vodkamartiniarticle_article_add'), data)
        self.assertRedirects(response, reverse('vodkamartiniauth_login') + '?next=' + reverse('vodkamartiniarticle_article_add'))

    #def testCantChangeArticle(self):
    #    pass

    def testCantChangeOwnArticle(self):
        """
        change_own_article allows users to edit only the articles they published. Initially granted to the author group.
        """
        logged_in = self.client.login(username='bill_normal', password='secret')
        self.assertEqual(logged_in, True, 'The user was not logged in.')
        data = {'title': 'edited title', 'teaser': 'edited teaser', 'body': 'edited body'}
        response = self.client.post(reverse('vodkamartiniarticle_article_edit', args=[self.article.id]), data, follow=True)
        article = Article.objects.get(pk=self.article.id)
        self.assertNotEqual(article.title, data['title'], "The article was edited, only a user with change_own_article permission should do this.")

    #def testCantViewArticle(self):
    #    pass

    #def testCantDeleteArticle(self):
    #    pass


#import datetime
#from django.contrib.auth.models import User
#from django.core.urlresolvers import reverse
#from django.db import close_connection
#from django.core import signals
#from django.core.handlers.wsgi import WSGIHandler
#from django.conf import settings
#import twill
#TWILL_TEST_HOST = 'twilltest'
#from StringIO import StringIO
#
#
#def reverse_for_twill(named_url):
#    return 'http://' + TWILL_TEST_HOST + reverse(named_url)
#
#
#class AdminTest(TestCase):
#    def setUp(self):
#        self.username = 'survey_admin'
#        self.pw = 'pwpwpw'
#        self.user = User.objects.create_user(self.username, '', self.pw)
#        self.user.is_staff = True
#        self.user.is_superuser = True
#        self.user.save()
#        self.assertTrue(self.client.login(username=self.username, password=self.pw), "Logging in user %s, pw %s failed." % (self.username, self.pw))
#
#
#class AdminSurveyTwillTest(AdminTest):
#    def setUp(self):
#        super(AdminSurveyTwillTest, self).setUp()
#        self.old_propagate = settings.DEBUG_PROPAGATE_EXCEPTIONS
#        settings.DEBUG_PROPAGATE_EXCEPTIONS = True
#        signals.request_finished.disconnect(close_connection)
#        twill.set_output(StringIO())
#        twill.add_wsgi_intercept(TWILL_TEST_HOST, 80, WSGIHandler)
#        self.browser = twill.get_browser()
#        self.browser.go(reverse_for_twill('admin:index'))
#        twill.commands.formvalue(1, 'username', self.username)
#        twill.commands.formvalue(1, 'password', self.pw)
#        self.browser.submit()
#        twill.commands.find('Welcome')
#
#    def tearDown(self):
#        self.browser.go(reverse_for_twill('admin:logout'))
#        twill.remove_wsgi_intercept(TWILL_TEST_HOST, 80)
#        signals.request_finished.connect(close_connection)
#        settings.DEBUG_PROPAGATE_EXCEPTIONS = self.old_propagate
#
#    def testAddSurveyError(self):
#        self.browser.go(reverse_for_twill('admin:survey_survey_add'))
#        twill.commands.formvalue(1, 'title', 'Time Traveling')
#        twill.commands.formvalue(1, 'opens', str(datetime.date.today()))
#        twill.commands.formvalue(1, 'closes', str(datetime.date.today() - datetime.timedelta(1)))
#        self.browser.submit()
#        twill.commands.url(reverse_for_twill('admin:survey_survey_add'))
#        twill.commands.find("Opens date cannot come after closes date.")
#
#    def testAddSurveyOK(self):
#        self.browser.go(reverse_for_twill('admin:survey_survey_add'))
#        twill.commands.formvalue(1, 'title', 'Not Time Traveling')
#        twill.commands.formvalue(1, 'opens', str(datetime.date.today()))
#        twill.commands.formvalue(1, 'closes', str(datetime.date.today()))
#        self.browser.submit()
#        twill.commands.url(reverse_for_twill('admin:survey_survey_changelist') + '$')

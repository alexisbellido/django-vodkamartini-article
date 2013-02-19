from django.db import models
from django.contrib.auth.models import User
import datetime
from markdown import markdown
from vodkamartiniarticle.helper import unique_slugify
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_will_be_posted
from django.conf import settings
from django.contrib.sites.models import Site
from akismet import Akismet
from akismet import AkismetError
from django.utils.encoding import smart_str
from django.contrib import messages
from django.core.mail import mail_managers

class LiveArticleManager(models.Manager):
    """
    Manager that returns articles with status = LIVE_STATUS.
    """
    def get_query_set(self):
        return super(LiveArticleManager, self).get_query_set().filter(status=self.model.LIVE_STATUS)

class BaseArticle(models.Model):
    """
    This is used by other content types to inherit. Never used to create an article.
    """
    LIVE_STATUS = 1
    DRAFT_STATUS = 2
    HIDDEN_STATUS = 3
    STATUS_CHOICES = (
        (LIVE_STATUS, 'Live'),
        (DRAFT_STATUS, 'Draft'),
        (HIDDEN_STATUS, 'Hidden'),
    )

    objects = models.Manager()
    live = LiveArticleManager()

    # Core
    title = models.CharField(max_length=200)
    teaser = models.TextField(blank=True)
    body = models.TextField()
    image = models.ImageField(upload_to='images/articles/%Y-%m', blank=True)
    created = models.DateTimeField(blank=True)
    updated = models.DateTimeField(auto_now=True)

    # Generated HTML
    teaser_html = models.TextField(editable=False, blank=True)
    body_html = models.TextField(editable=False, blank=True)

    # Metadata
    slug = models.SlugField(unique=True, max_length=128)
    author = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT_STATUS)

    enable_comments = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    # Categorization
    # https://docs.djangoproject.com/en/dev/ref/models/fields/#recursive-relationships
    # To refer to models defined in another application, you can explicitly specify a model with the full application label
    # Do not use this to avoid circular import in Article: models.ManyToManyField(Category)
    categories = models.ManyToManyField('vodkamartinicategory.Category', blank=True)

    class Meta:
        ordering = ["-created"]
        abstract = True

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Convert teaser and body from markdown to HTML.
        """

	#import pdb; pdb.set_trace()
        if not self.pk and not self.slug:
            unique_slugify(self, self.title)
        if not self.pk and not self.created:
            self.created = datetime.datetime.now()
        self.body_html = markdown(self.body.replace('<p>', '').replace('</p>', ''), safe_mode="replace", html_replacement_text="")
        if self.teaser:
            self.teaser_html = markdown(self.teaser.replace('<p>', '').replace('</p>', ''), safe_mode="replace", html_replacement_text="")
        else:
            self.teaser_html = ''
        super(BaseArticle, self).save(*args, **kwargs)

class Article(BaseArticle):
    class Meta(BaseArticle.Meta):
        """
        If there's need to override super class Meta, abstract is not inherited
        """
        ordering = ["-created"]

        permissions = (
                ('change_own_article', 'Can change own article'),
                ('view_article', 'View article'),
        )

    @models.permalink
    def get_absolute_url(self):
        return ('vodkamartiniarticle_article_detail', (), {'slug': self.slug})


def moderate_comment(sender, comment, request, **kwargs):
    """
    Test Akismet spam with 'viagra-test-123'
    """
    if not comment.id:
        akismet_api = Akismet(key=settings.AKISMET_API_KEY, blog_url="http://%s/" % Site.objects.get_current().domain)
        if akismet_api.verify_key():
            akismet_data = {
                    'comment_type' : 'comment',
                    'referrer': request.META['HTTP_REFERER'],
                    'user_ip': comment.ip_address,
                    'user_agent': request.META['HTTP_USER_AGENT'],
                   }
            try:
                if akismet_api.comment_check(smart_str(comment.comment), akismet_data, build_data=True):
                    comment.is_public = False
                    messages.info(request, 'Your comment was marked as spam.')
                else:
                    content_type = comment.content_object.__class__.__name__.lower()
                    if content_type == 'article':
                        messages.info(request, 'Your comment has been published.')

            except AkismetError:
                """ This exception can be raised when Akismet is down or some parameter in the call is missing. See akismet.py """
                pass

comment_will_be_posted.connect(moderate_comment, sender=Comment)

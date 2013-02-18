from vodkamartiniarticle.models import Article
from vodkamartiniarticle.forms import ArticleForm
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.contrib import messages
#import json

def articles_index(request, page=1):
    """ list on articles home"""

    # only needed if no other object that bypasses the lazy loading is being called on the view or template
    bypass_lazyload = request.user.is_authenticated()

    articles_list = Article.live.all()
    paginate_by = 4
    paginator = Paginator(articles_list, paginate_by)

    try:        
        # TODO get it from request.GET
        page = int(page)
    except ValueError:
        page = 1

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page.
        articles = paginator.page(paginator.num_pages)

    return render_to_response('vodkamartiniarticle/article_list.html',
                              {'object_list': articles.object_list,
                               'articles': articles,
                              },
                              RequestContext(request))

def article_detail(request, slug):
    """
    Article detail view

    Templates: ``<app_label>/<model_name>_detail.html``
    Context:
        object:
            the object to be detailed
        can_edit:
            boolean to decide if the edit link is displayed
    """

    # TODO just show live object
    bypass_lazyload = request.user.is_authenticated()

    # TODO what to do if there are more than one article with the same slug?, for now redirecting to listing but we should avoid this on save
    try:
        object = get_object_or_404(Article, slug=slug)
    except Article.DoesNotExist:
        return HttpResponseRedirect(reverse('vodkamartiniarticle_articles_home'))

    # TODO what to do with articles which are not live? changing the template to not show the content for now
    # but we could redirect to another page
    can_edit = False
    if request.user.has_perm('vodkamartiniarticle.change_own_article', obj=object):
        can_edit = True

    if object.status == Article.LIVE_STATUS:
        object_is_live = True
    else:
        object_is_live = False

    return render_to_response('vodkamartiniarticle/article_detail.html',
                              {'object': object,
                               'can_edit': can_edit,
                               'object_is_live': object_is_live,
                              },
                              RequestContext(request))

@login_required
def article_edit(request, pk):
    object = get_object_or_404(Article, pk=pk)

    if not request.user.has_perm('vodkamartiniarticle.change_own_article', obj=object):
        # no need for the extra reverse when I can use use get_absolute_url for the object
        #return HttpResponseRedirect(reverse('vodkamartiniarticle_article_detail', kwargs={'slug': object.slug}))
        return HttpResponseRedirect(object.get_absolute_url())

    if request.method == 'POST':
        form = ArticleForm(author=request.user, article_id=object.id, data=request.POST, files=request.FILES)
        if form.is_valid():
            object = form.save()
            # Change the messages level to ensure the debug message is added.
            #messages.set_level(request, messages.DEBUG)
            messages.info(request, 'Your article has been updated.')
            #messages.debug(request, 'debug for article updated.')
            return HttpResponseRedirect(object.get_absolute_url())
    else:
        data = {'title': object.title, 'teaser': object.teaser, 'body': object.body}
        form = ArticleForm(author=request.user, article_id=object.id, data=data)

    return render_to_response('vodkamartiniarticle/article_form.html',
                              {
                               'object': object,
                               'form': form,
                              },
                              RequestContext(request))

@permission_required('vodkamartiniarticle.add_article')
def article_add(request):
    """
    @permission_required will check for permission and ask for login, there's no need for extra @login_required.
    """
    if request.method == 'POST':
        form = ArticleForm(author=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            article = form.save()
            #import pdb; pdb.set_trace()
            messages.add_message(request, messages.INFO, 'Your article has been published.')
            #return HttpResponseRedirect(reverse('vodkamartiniarticle_article_detail', kwargs={'slug': article.slug}))
            return HttpResponseRedirect(article.get_absolute_url())
    else:
        form = ArticleForm(author=request.user)

    return render_to_response('vodkamartiniarticle/article_form.html',
                              {
                               'form': form,
                              },
                              RequestContext(request))

def article_probe_ok(request):
    return HttpResponse('ok')

#def article_ajax_test(request):
#    return HttpResponse('some text content here')

#def article_json_test(request):
#    to_json = { "key1": "value1", "key2": "value2" }
#    return HttpResponse(json.dumps(to_json), mimetype='application/json')

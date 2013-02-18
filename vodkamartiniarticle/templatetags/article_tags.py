from django import template
from vodkamartiniarticle.models import Article
from django.db.models import get_model

register = template.Library()

@register.tag(name='get_latest_articles')
def do_latest_articles(parser, token):
    """
    Simple tag to create a new template variable latest_articles which contains the latest five Article objects.
    """
    return LatestArticlesNode()

class LatestArticlesNode(template.Node):
    def render(self, context):
        context['latest_articles'] = Article.live.all()[:5]
        return ''

@register.tag(name='get_latest_content')
def do_latest_content(parser, token):
    """
    Flexible tag to create a new template variable with latest X objects.
    Use like this: {% get_latest_content vodkamartini.article 5 as latest_articles %}
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, appmodel, num, discard_this, varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly four arguments" % token.contents.split()[0])

    model_args = appmodel.split('.')
    if len(model_args) != 2:
        raise template.TemplateSyntaxError("The first argument to 'get_latest_content' needs to be an string like 'appname.model_name'.")
    model = get_model(*model_args)
    if model is None:
        raise template.TemplateSyntaxError("'get_latest_content' got an invalid model %s" % appmodel)

    return LatestContentNode(model, num, varname)

class LatestContentNode(template.Node):
    def __init__(self, model, num, varname):
        self.model = model
        self.num = int(num)
        self.varname = varname

    def render(self, context):
        context[self.varname] = self.model.live.all()[:self.num]
        return ''

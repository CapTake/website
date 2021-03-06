from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView, CreateView, View, ListView
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render_to_response, RequestContext
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib import messages
from website.models import *
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from updown.views import AddRatingFromModel
import json
from django_comments.models import Comment
from django.db.models import Q
from django.db.models import Count
import django_tables2 as tables
from django_filters import FilterSet
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import RequestConfig
from django.utils.html import format_html
from django.template.defaultfilters import slugify
import requests
from datetime import datetime, timedelta

def comment_posted( request ):
    if request.GET['c']:
        comment_id = request.GET['c'] 
        comment = Comment.objects.get( pk=comment_id )
        project = Project.objects.get(id=comment.object_pk) 

        if project:
            messages.success(request, 'Comment Posted!')
            return HttpResponseRedirect( project.get_absolute_url() )

    return HttpResponseRedirect( "/" )

def index(request, template="index.html"):
    projects = Project.objects.all().order_by('-order')
    context = {
        'project_count': projects.count(),
        'projects': projects[0:15],
        'user_count': User.objects.all().count(),
        'grant_count': Grant.objects.all().count(),
        'cryptocurrencies_count': Cryptocurrency.objects.all().count(),
    }
    return render_to_response(template, context, context_instance=RequestContext(request))

class ProjectListView(ListView):
    model = Project
    template_name = 'list.html'  
    context_object_name = "projects"    
    paginate_by = 21 

    def dispatch(self, request, *args, **kwargs):
        sort = self.request.GET.get('sort','-order')
        if sort not in ['-created','-rating_likes','-public_views','-order','-comment_count']:
            messages.error(self.request, 'invalid sort option')
            return HttpResponseRedirect("/list")
        return super(ProjectListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.GET.get('sort') == "-comment_count":
            projects_by_score = Comment.objects.values('object_pk').annotate(
                score=Count('id')).order_by('-score')
            project_ids = [int(obj['object_pk']) for obj in projects_by_score]  
            object_list = Project.objects.filter(id__in=project_ids)
        else:
            object_list  = Project.objects.order_by(self.request.GET.get('sort','-order'))
        if self.request.GET.get('q'):
            object_list = object_list.filter(Q(name__icontains=self.request.GET.get('q')) | Q(description__icontains=self.request.GET.get('q')) | Q(tags__icontains=self.request.GET.get('q')) )
        return object_list


class CryptocurrencyFilter(FilterSet):
    class Meta:
        model = Cryptocurrency
        fields = ['symbol', 'name']


class CryptoTable(tables.Table):
    class Meta:
        model = Cryptocurrency
        exclude = ['id','slug','symbol','description']

        name = tables.Column()

    def render_name(self, value):
        return format_html('<div class="s-s-{} currency-logo-sprite"></div><span><a href="/cryptocurrency/{}">{}</a></span>', slugify(value), slugify(value), value )

class FlyEyeView(ListView):
    model = Cryptocurrency
    template_name = 'fly_eye.html'  


class CryptocurrencyListView(SingleTableMixin, FilterView):
    model = Cryptocurrency
    template_name = 'cryptocurrency_list.html'
    context_object_name = "cryptocurrencies"
    paginate_by = 100 
    table_class = CryptoTable
    filterset_class = CryptocurrencyFilter
    

    def get_context_data(self, **kwargs):
            context = super(CryptocurrencyListView, self).get_context_data(**kwargs)
            table = CryptoTable(Cryptocurrency.objects.all(), order_by="-market_cap")
            RequestConfig(self.request).configure(table)
            table.paginate(page=self.request.GET.get('page', 1), per_page=100)
            context['table'] = table     
            return context

class CryptocurrencyDetailView(DetailView):
    model = Cryptocurrency
    slug_field = "slug"     
    context_object_name = "cryptocurrency"     
    template_name = "cryptocurrency_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super(CryptocurrencyDetailView, self).get_context_data(**kwargs)

        for goal in Goal.objects.filter(cryptocurrency=self.object).exclude(result="Complete"):
            time_threshold = datetime.now() - timedelta(seconds=goal.target_cryptocurrency.block_time_seconds)
            if time_threshold > goal.updated:

                url = goal.target_cryptocurrency.block_explorer_balance_api % goal.wallet_address
                r1=requests.get(url)
                goal.current_amount = 0

                if goal.target_cryptocurrency.name == 'Dotcoin':
                    try:
                       
                        goal.current_amount = int(r1.json()['result']['tokens']['DOT'])
                    except:
                        goal.current_amount = 0
                else:
                    try:
                        if goal.target_cryptocurrency.block_explorer_balance_in_satoshis:
                            goal.current_amount = int(r1.text) * .00000001
                        else:
                            goal.current_amount = r1.text 
                    except:
                        goal.current_amount = 0

                goal.updated = datetime.now()
                goal.save()



        return context




class GrantListView(ListView):
    model = Grant
    queryset = Grant.objects.order_by('-deadline')      
    template_name = 'grants.html'  
    context_object_name = "grants"    
    paginate_by = 100 

class GrantDetailView(DetailView):
    model = Grant
    slug_field = "id"     
    context_object_name = "grant"     
    template_name = "grant.html"
    
    def get_context_data(self, **kwargs):
            context = super(GrantDetailView, self).get_context_data(**kwargs)
            context['matches'] = Match.objects.filter(grant=self.get_object()).order_by('-score')   
            return context

def profile(request):
    try:
        return redirect('/profile/' + request.user.username)
    except Exception:
        return redirect('/')

class AddRating(View):
  
    def post(self, request, *args, **kwargs):
        params = {
            'app_label': 'website',
            'model': 'project',
            'field_name': 'rating'
        }
        params.update(kwargs)
        response = AddRatingFromModel()(request, **params)
        print response 
        if response.status_code == 200:

            return HttpResponse(Project.objects.get(id=kwargs['object_id']).rating.likes)
        return HttpResponse(json.dumps({'error': 9, 'message': response.content}))
  
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)



class UserProfileDetailView(DetailView):
    model = get_user_model()
    slug_field = "username"
    template_name = "profile.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(self.request, 'That user was not found.')
            return redirect("/")
        return super(UserProfileDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        user = super(UserProfileDetailView, self).get_object(queryset)
        return user

    def get_context_data(self, **kwargs):
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)
        return context



class ProjectDetailView(DetailView):
    model = Project
    slug_field = "slug"
    template_name = "project.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
           return HttpResponseNotFound('<h1>Page not found</h1>')
        if request.user.is_authenticated():
            self.object.private_views = self.object.private_views + 1
        else:
            self.object.public_views = self.object.public_views + 1
        self.object.save()
        return super(ProjectDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
            context = super(ProjectDetailView, self).get_context_data(**kwargs)
            context['matches'] = Match.objects.filter(project=self.get_object()).order_by('-score')   
            return context


class ProjectCreate(CreateView):
    model = Project
    fields = ['name','description','image','slug']
    template_name = "add_project.html"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        messages.success(self.request, 'Project added!')
        return HttpResponseRedirect("/"+obj.slug) 

class AddResource(View):
  
    def post(self, request, *args, **kwargs):
        project = Project.objects.get(id=self.request.POST.get('project_id'))
        
        Resource.objects.create(user=self.request.user, project=project, link=self.request.POST.get('link'), icon=self.request.POST.get('icon'))
        messages.success(request, 'Resource Added!')
        return HttpResponseRedirect("/"+project.slug) 
  
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     context = super(ProjectCreate, self).get_context_data(**kwargs)
    #     return context

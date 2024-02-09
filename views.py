from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Post, Comment, UserProfile, Notification
from .forms import PostForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect


# Create your views here.

class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        # https://youtu.be/HHCRqjyPoCY?t=583 explains what's put in the filter
        # allows us to only show posts from user's the user follows
        posts = Post.objects.filter(author__profile__followers__in=[logged_in_user.id]).order_by('-created_on')
        form = PostForm()

        context = {
            'post_list':posts,
            'form':form,
        }
        
        return render(request, 'social/post_list.html', context)

    def post(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm(request.POST)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            
        context = {
            'post_list':posts,
            'form':form,
        }
        
        return render(request, 'social/post_list.html', context)

class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by('-created_on') # -created_on makes new posts appear first

        context=  {'post':post, 'form':form, 'comments':comments}
        return render(request, 'social/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

        comments = Comment.objects.filter(post=post).order_by('-created_on') # -created_on makes new posts appear first

        # from models.py, 2 stands for comment  
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author, post=post)

        context=  {'post':post, 'form':form, 'comments':comments}
        return render(request, 'social/post_detail.html', context)

class CommentReplyView(LoginRequiredMixin, View):
    # pk is comment's pk    
    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            # the author of the comment will be the user who wants to right the reply
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        # from models.py, 2 stands for comment  
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)

        return redirect('post-detail', pk=post_pk)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk':pk})

    #built in var of UserPassesTestMixin
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
        

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('post-list')

    #built in var of UserPassesTestMixin
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk':pk})

    #built in var of UserPassesTestMixin
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author 

class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['comment']
    template_name = 'social/comment_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['post_pk']

        return reverse_lazy('post-detail', kwargs={'pk':pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author 

class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-created_on')

        followers = profile.followers.all()


        if len(followers) == 0:
            is_following = False

        for follower in followers:
            # since everything in list is user object, これはへいきです
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers = len(followers)


        context = {
            'user':user,
            'profile':profile,
            'posts':posts,
            'number_of_followers':number_of_followers,
            'is_following':is_following,
        }

        return render(request, 'social/profile.html', context)

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['username', '自己紹介', '誕生日', '写真', '国', 'サイト', '言語']
    template_name = 'social/profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk':pk})

    def test_func(self):
        profile = self.get_object() # get object we are working on
        return self.request.user == profile.user

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)

        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)

        return redirect('profile', pk=profile.pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        return redirect('profile', pk=profile.pk)

class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
         
        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            post.dislikes.remove(request.user)


        # will be set false from beginning, since users don't have posts liked befoer liking them themselves.
        is_like = False
    
        for like in post.likes.all():
            # if user has already liked post
            if like == request.user:
                is_like = True
                break
            
        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author, post=post)

        else:
            post.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddCommentLike(LoginRequiredMixin, View):
    # the names of the function should still be post
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
         
        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)


        # will be set false from beginning, since users don't have posts liked befoer liking them themselves.
        is_like = False

        for like in comment.likes.all():
            # if user has already liked post
            if like == request.user:
                is_like = True
                break
            
        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=profile.user, comment=comment)            
        else:
            comment.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddCommentDislike(LoginRequiredMixin, View):
    # the names of the function will be post
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
         
        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)


        # will be set false from beginning, since users don't have posts liked befoer liking them themselves.
        is_like = False

        for like in comment.likes.all():
            # if user has already liked post
            if like == request.user:
                is_like = True
                break
            
        if not is_like:
            comment.likes.add(request.user)
        else:
            comment.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        # will be set false from beginning, since users don't have posts liked befoer liking them themselves.
        is_like = False

        for like in post.likes.all():
            # if user has already liked post
            if like == request.user:
                is_like = True
                break

        if is_like:
            post.likes.remove(request.user)

        is_dislike = False

        

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        
        if is_like:
            post

        if not is_dislike:
            post.dislikes.add(request.user)
        else:
            post.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class UserSearch(View):
    # parameters for search will be in url, so get method is good
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
                                                 # if anything in username is in the query, show it in results.
                                                # Q functions allows this to happen, really is just called Q
        profile_list = UserProfile.objects.filter(Q(user__username__icontains=query))
        context = {
            'profile_list' : profile_list,
        }

        return render(request, 'social/search.html', context)

class ListFollowers(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        # returns list of users that follow a user
        followers = profile.followers.all()
        context = {'profile':profile, 'followers':followers}
        return render(request, 'social/followers_list.html', context)

class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('post-detail', pk=post_pk)

class FollowNotification(View):
    # profile_pk because it will direct to the profile who followed 
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', pk=profile_pk)

from django.urls import path
from .views import *

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/<int:pk>/reply', CommentReplyView.as_view(), name='comment-reply'),
    path('post/<int:post_pk>/comment/delete/<int:pk>', CommentDeleteView.as_view(), name='comment-delete'), # for this specific one, 'post_pk' is the pk used for the other urls. 'pk' is the comment's pk
    path('post/<int:post_pk>/comment/<int:pk>/like', AddCommentLike.as_view(), name='comment-like'), # for this specific one, 'post_pk' is the pk used for the other urls. 'pk' is the comment's pk
    path('post/<int:post_pk>/comment/<int:pk>/dislike', AddCommentDislike.as_view(), name='comment-dislike'), # for this specific one, 'post_pk' is the pk used for the other urls. 'pk' is the comment's pk
    path('post/<int:post_pk>/comment/edit/<int:pk>', CommentEditView.as_view(), name='comment-edit'), # for this specific one, 'post_pk' is the pk used for the other urls. 'pk' is the comment's pk
    path('post/<int:pk>/like', AddLike.as_view(), name="like"),
    path('post/<int:pk>/dislike', AddDislike.as_view(), name="dislike"),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'), 
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/', ListFollowers.as_view(), name='list-followers'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove', RemoveFollower.as_view(), name='remove-follower'),
    path('search/', UserSearch.as_view(), name="profile-search"),
    path('notification/<int:notification_pk>/post/<int:post_pk>', PostNotification.as_view(), name="post-notification"),
    path('notification/<int:notification_pk>/profile/<int:profile_pk>', FollowNotification.as_view(), name="follow-notification"),


]


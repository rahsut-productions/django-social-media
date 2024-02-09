from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Post(models.Model):
    body = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='dislikes')

class Comment(models.Model):
    comment = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes')
    # self is comment model itself
    # "related_name='+'" removes reverse mapping that's unneeded
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')

    # decorators (marked by @ sign) help add extra function to the function that can't be done in function, or won't
    # allow other things to work without it.
    # Will allow us to easily access
    @property
    # get the replies to the comment or "children" of the comment
    def children(self):
        return Comment.objects.filter(parent=self).order_by('-created_on').all()

    @property
    # will determine if comment is a child/reply or a parent/normal comment
    def is_parent(self):
        # if not a parent, if not showing it is parent
        if self.parent is None:
            return True
        return False
class UserProfile(models.Model):
    countries = (
        ('アメリカ','アメリカ'),
        ('インド', 'インド'),
        ('メキシコ',  'メキシコ'),
        ('ドイツ', 'ドイツ'),
        ('韓国', '韓国'),
        ('北朝鮮', '北朝鮮'),
        ('台湾', '台湾'),
        ('日本', '日本'), 
    )

    languages = (
        ('日本語', '日本語'),
        ('English','English'),
        ('ਪੰਜਾਬੀ',  'ਪੰਜਾਬੀ'),
    )

    # creates relationship between UserProfile model and the user model 
    # primary_key will set it to primary_key set/used by user
    # verbose_name is another name the "User" model goes by/the other name to access "User" model
    # related_name: user profile is stored on user object on name of profile, so we can access that name later
    # on_delete: if user is deleted, profile is deleted as well.
    #OneToOneField means one user can have one profile and one profile can have one user. (一user＝一プロファイル)

    user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True, null=True) # blank means not required, null means it's fine to be empty in database
    自己紹介 = models.TextField(max_length=300, blank=True, null=True)
    誕生日 = models.DateField(blank=True, null=True)
    国 = models.CharField(max_length=6, choices=countries, blank=True, null=True)
    # upload_to: where images will be stored
    # default: if no profile picture used, it will use the default picture. For that reason, null is not necessary.
    # the "media" folder/root is not necessary in upload_to or default because it was established in settings.py 
    写真 = models.ImageField(upload_to='uploads/profile_pictures/', default='uploads/profile_pictures/default.png', blank=True)
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    サイト = models.URLField(max_length=900, blank=True, null=True)
    言語 = models.CharField(max_length=900, choices=languages, default=languages[1])


# sender - model that sends signal
# instance - model that's saved in database
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Notification(models.Model):
    # 1 - いい, 2 - コメント, 3 - フォロー
    notification_type = models.IntegerField()
    to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE, null=True)
    from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE, null=True)
    # related name there because we don't want reverse mapping
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    user_has_seen = models.BooleanField(default=False)


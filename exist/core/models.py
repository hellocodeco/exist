from django.db import models
from .json_field import JSONField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.utils.datastructures import SortedDict
from django.contrib import admin
import datetime, re, hashlib, math


class User(AbstractUser):
    """
    Using 1.5's ability to override the User model.
    We will add fields here as necessary.
    """ 
    timezone = models.CharField(max_length=80,null=True,blank=False,db_index=True)
    avatar = models.ImageField(null=True,blank=True)
    last_seen_activity = models.DateTimeField(null=True,blank=True) #date last visited activity, so we know how many to show
    bio = models.CharField(max_length=160, blank=True, null=True)
    url = models.URLField(max_length=250, blank=True, null=True, verbose_name='Website')
    private = models.BooleanField(default=True,help_text='Only logged-in users will be able to see your profile.')
    imperial_units = models.BooleanField(default=False)
    stripe_customer = models.CharField(max_length=250,null=True,blank=True)
    country = models.CharField(max_length=150,null=True,blank=True)
    weekly_email = models.BooleanField(default=True)
    delinquent = models.BooleanField(default=False)
    trial = models.BooleanField(default=True)
    
    def is_authenticated(self):
        if self.is_active:
            return True
        return False
    
    @property
    def attribute_types(self):
        return [a.attribute for a in self.attributes.all().prefetch_related()]
    
    def auth_hash(self,fieldname):
        return hashlib.sha1("[%s]/%s::%s" % (settings.SECRET_KEY,self.id,fieldname)).hexdigest()
    
    class Meta:
        ordering = ['username']
        unique_together=(('email',),)

User._meta.get_field('username').validators = [ validators.RegexValidator(re.compile('^[\w]+$'), 'Enter a valid username.', 'invalid') ]


class Attribute(models.Model):
    
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    PERIOD = 3
    TIMEOFDAY_MIDNIGHT = 4
    PERCENTAGE = 5
    TIMEOFDAY_MIDDAY = 6
    
    VALUE_TYPES = (
        (INTEGER,'Integer'),
        (FLOAT,'Float'),
        (STRING,'String'),
        (PERIOD,'Period (min)'),
        (TIMEOFDAY_MIDNIGHT,'Time of day (min from midnight)'),
        (PERCENTAGE, 'Percentage'),
        (TIMEOFDAY_MIDDAY,'Time of day (min from midday)'),
        )
    
    name = models.CharField(max_length=40)
    label = models.CharField(max_length=40)
    priority = models.IntegerField(default=2)
    value_type = models.SmallIntegerField(default=0,choices=VALUE_TYPES)
    group = models.ForeignKey('AttributeGroup',related_name='attributes',null=True,blank=True)
    private_default = models.BooleanField(default=False)
    correlation_offset = models.SmallIntegerField(default=0)
    correlation_positive = models.CharField(max_length=160,null=True,blank=True)
    correlation_negative = models.CharField(max_length=160,null=True,blank=True)
    correlation_priority = models.IntegerField(default=0,
                                               help_text="Higher = everything else follows this, eg. the weather. You can't control the weather.")
    
    def __str__(self):
        return self.label

    class Meta:
        ordering = ['priority','label']
    

class AttributeGroup(models.Model):
    name = models.CharField(max_length=40)
    label = models.CharField(max_length=40)
    priority = models.IntegerField(default=2)
    
    def __str__(self):
        return self.label

    class Meta:
        ordering = ['priority','label']
    

class UserAttributeManager(models.Manager):
    use_for_related_fields = True
    
    def score(self):
        atts = self.high_priority()
        scores = [att.value for att in atts if att.value is not None]
        return sum(scores)
    
    def high_priority(self):
        if not getattr(self,'_high_priority',None):
            self._high_priority = self.get_query_set().filter(
                attribute__priority__lte=9,active=True).exclude(
                attribute__value_type=Attribute.STRING).order_by('attribute__group__priority','attribute__priority').prefetch_related()
        
        return self._high_priority
    
    def public_high_priority(self):
        qs = self.high_priority().filter(private=False)
        return qs
    
    def active(self):
        if not getattr(self,'_active',None):
            self._active = self.get_query_set().filter(active=True).prefetch_related()
        
        return self._active
    
    
    def by_name(self):    
        if not getattr(self,'_attributes',None):
            result = self.get_query_set().filter(active=True).select_related()
            self._attributes = dict([(a.attribute.name, a) for a in result])
        
        return self._attributes
    
    def public_by_name(self):    
        if not getattr(self,'_public_attributes',None):
            result = self.get_query_set().filter(active=True,private=False).select_related()
            self._public_attributes = dict([(a.attribute.name, a) for a in result])
        
        return self._public_attributes
    
    def by_group(self):
        # get all attributes
        # find which have groups
        # return a dict of attribute groups
        
        result = self.get_query_set().filter(active=True).order_by('attribute__priority').prefetch_related()
        used_groups = [g.attribute.group.id for g in result if g.attribute.group is not None]
        
        _groups = AttributeGroup.objects.filter(id__in=used_groups).order_by('priority','name')
        grouped = SortedDict([(g.name,{'priority':g.priority,'label':g.label,'attributes':[]}) for g in _groups])
        
        ungrouped = {'attributes':[]}
        
        for att in result:
            if att.attribute.group is not None:
                grouped[att.attribute.group.name]['attributes'].insert(att.priority,att)
            else:
                ungrouped['attributes'].append(att)
        
        if len(ungrouped['attributes']) > 0:
            grouped.update({'ungrouped':ungrouped})
        return grouped
    
    def by_group_all(self):
        # this one includes inactive
        # get all attributes
        # find which have groups
        # return a dict of attribute groups
        
        result = self.get_query_set().order_by('attribute__priority').prefetch_related()
        used_groups = [g.attribute.group.id for g in result if g.attribute.group is not None]
        
        _groups = AttributeGroup.objects.filter(id__in=used_groups).order_by('priority','name')
        grouped = SortedDict([(g.name,{'priority':g.priority,'label':g.label,'attributes':[]}) for g in _groups])
        
        ungrouped = {'attributes':[]}
        
        for att in result:
            if att.attribute.group is not None:
                grouped[att.attribute.group.name]['attributes'].insert(att.priority,att)
            else:
                ungrouped['attributes'].append(att)
        
        if len(ungrouped['attributes']) > 0:
            grouped.update({'ungrouped':ungrouped})
        return grouped    

    
class UserAttribute(models.Model):
    user = models.ForeignKey('User',related_name='attributes')
    attribute = models.ForeignKey('Attribute',related_name='users')
    service = models.ForeignKey('Service',related_name='user_attributes', null=True, blank=True)
    objects = UserAttributeManager()
    active = models.BooleanField(default=True,verbose_name='Enabled')
    private = models.BooleanField(default=False,verbose_name='Private')

    def __str__(self):
        return "%s for %s" % (self.attribute.label, self.user.username)

    @property
    def label(self):
        return self.attribute.label
    
    @property
    def name(self):
        return self.attribute.name
    
    @property
    def priority(self):
        return self.attribute.priority
    
    @property
    def value_type(self):
        return self.attribute.value_type
    
    @property
    def value_type_description(self):
        return Attribute.VALUE_TYPES[self.attribute.value_type][1]
    
    @property
    def value(self):
        data = self.data.all()
        if data.count() > 0:
            data = data[0]
            return data.value
        return None
    
    @property
    def group(self):
        
        if self.attribute.group is not None:
            return self.attribute.group
        else:
            return None
    
    @property
    def available_services(self):
        if not getattr(self,'_available_services',None):
        
            self._available_services = Service.objects.filter(id__in=[profile.service.id for profile in self.user.profiles.all()],
                                                              attributes=self.attribute).order_by('name')
        return self._available_services
    
    class Meta:
        ordering = ['attribute__group__priority','attribute__priority','attribute__name']


class UserAttributeData(models.Model):
    user_attribute = models.ForeignKey('UserAttribute',related_name='data')
    created = models.DateTimeField(auto_now_add=True)
    time = models.DateField()
    value_type = models.SmallIntegerField(default=0)
    int_value = models.IntegerField(null=True, blank=True)
    string_value = models.CharField(null=True,max_length=250, blank=True)
    float_value = models.DecimalField(max_digits=16,decimal_places=4, null=True, blank=True)
    
    @property
    def value(self):
        """
        Return the appropriate value type.
        """
        if self.value_type == 0:
            return self.int_value
        if self.value_type == 1:
            return self.float_value
        if self.value_type == 2:
            return self.string_value
        if self.value_type == 3:
            return self.int_value
        if self.value_type == 4:
            return self.int_value
        if self.value_type == 5:
            return self.float_value
        if self.value_type == 6:
            return self.int_value
        
    def set_value(self,value):
        if self.value_type == 0:
            self.int_value = value
        if self.value_type == 1:
            self.float_value = value
        if self.value_type == 2:
            self.string_value = value
        if self.value_type == 3:
            self.int_value = value
        if self.value_type == 4:
            self.int_value = value
        if self.value_type == 5:
            self.float_value = value
        if self.value_type == 6:
            self.int_value = value

    def __str__(self):
        return "%s: %s: %s" % (self.user_attribute.user.username, self.user_attribute.attribute.label, unicode(self.value))

    class Meta:
        ordering = ['-time']
        unique_together=('user_attribute','time')




class Service(models.Model):
    """
    An external service we collect data from.
    """
    name = models.CharField(max_length=60,db_index=True)
    slug = models.SlugField(max_length=60)
    description = models.TextField(blank=True,null=True)
    provides = models.TextField(blank=True,null=True)
    requirements = models.TextField(blank=True,null=True)
    attributes = models.ManyToManyField('Attribute',related_name='services',blank=True)
    settings = models.BooleanField(default=False)
    external = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    
    @property
    def types(self):
        try:
            return self._types
        except:
            self._types = set([s.type for s in self.streams.all()])
        return self._types
    
    def create_profile(self, user):
        p, c = Profile.objects.get_or_create(user=user,service=self)
        p.save()
        return p


class Profile(models.Model):
    """
    A relationship between a user and a service.
    This should be inherited by the concrete service class
    and overridden with details like auth tokens etc
    """
    user = models.ForeignKey('User',related_name='profiles')
    service = models.ForeignKey('Service',related_name='users')
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return "%s on %s" % (self.user.username, self.service.name)

    class Meta:
        unique_together = (("user","service"),)
        ordering = ['service__name']
        
    @property
    def concrete_model(self):
        try:
            return self._service_model
        except:
            slug = self.service.slug
            mod = __import__('services.%s.models' % slug,
                             fromlist=['%sProfile' % (slug.title())])
            self._service_model = getattr(mod,'%sProfile' % (slug.title()))
        return self._service_model
    
    @property
    def concrete(self):
        return getattr(self,'%sprofile' % (self.service.slug))
    
    @staticmethod
    def type_sort(profile):
        #stream_ids = [s.type.id for s in profile.service.streams.all()]
        return 1 #min(stream_ids) if stream_ids else 1


class Event(models.Model):
    user = models.ForeignKey('User',related_name='events')
    attribute = models.ForeignKey('Attribute',related_name='events')
    created = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField()
    value = models.DecimalField(null=True,blank=True,max_digits=16,decimal_places=4)
    value_type = models.SmallIntegerField()
    meta = JSONField(null=True, default={})
    
    def __str__(self):
        return "[%s] %s: %s" % (self.created.strftime("%Y-%m-%d %H:%M:%S"), self.user.username, self.attribute.name)

    class Meta:
        unique_together = (("user","attribute","time"),)


class UserLogManager(models.Manager):
    
    def most_active_in_period(self, days_ago_start, days_ago_end=0, limit=20):
        """
        A list of most active users, with their log count annotated.
        Leaving the end delta empty uses today's date.
        """
        
        date_start = datetime.date.today() - datetime.timedelta(days=days_ago_start)
        date_end = datetime.date.today() + datetime.timedelta(days=1) - datetime.timedelta(days=days_ago_end)
        
        return User.objects.raw("""
                                 SELECT core_user.*, COUNT(core_userlog.id) AS log_count
                                 FROM core_userlog
                                 RIGHT JOIN (core_user) ON (core_userlog.user_id = core_user.id)
                                 WHERE core_userlog.created >= %s AND core_userlog.created <= %s
                                 GROUP BY core_userlog.user_id
                                 ORDER BY log_count DESC
                                 LIMIT 0, %s
                                 """,[date_start, date_end, limit])
    
    def most_active_days(self, days_ago_start, days_ago_end=0, limit=20):
        """
        Ranking of users by number of days they've made logs in period
        """
        date_start = datetime.date.today() - datetime.timedelta(days=days_ago_start)
        date_end = datetime.date.today() + datetime.timedelta(days=1) - datetime.timedelta(days=days_ago_end)
        
        return User.objects.raw("""
                                 SELECT core_user.*, COUNT(DISTINCT DATE(core_userlog.created)) AS log_count
                                 FROM core_user
                                 RIGHT JOIN (core_userlog) ON ( core_userlog.user_id = core_user.id )
                                 WHERE core_userlog.created >= %s AND core_userlog.created <= %s
                                 GROUP BY core_user.id
                                 ORDER BY log_count DESC
                                 LIMIT 0, %s
                                 """, [date_start, date_end, limit])
        
    
    def most_popular_in_period(self, days_ago_start, days_ago_end=0, limit=20):
        """
        Ranking of page/action combos by popularity
        """
        date_start = datetime.date.today() - datetime.timedelta(days=days_ago_start)
        date_end = datetime.date.today() - datetime.timedelta(days=days_ago_end)
        
        return self.raw("""
                        SELECT core_userlog.*, COUNT(*) AS log_count FROM core_userlog
                        WHERE core_userlog.created >= %s AND core_userlog.created <= %s
                        GROUP BY core_userlog.page, core_userlog.action, core_userlog.args
                        ORDER BY log_count DESC
                        LIMIT 0, %s
                        """,[date_start, date_end, limit])
    
    
    def viewed_delete_in_period(self, days_ago_start, days_ago_end=0):
        """
        All users with an `account_delete.view` log in period.
        """
        date_start = datetime.date.today() - datetime.timedelta(days=days_ago_start)
        date_end = datetime.date.today() + datetime.timedelta(days=1) - datetime.timedelta(days=days_ago_end)
        
        return User.objects.raw("""
                                 SELECT core_user.*, core_userlog.created AS log_date
                                 FROM core_userlog
                                 RIGHT JOIN (core_user) ON (core_userlog.user_id = core_user.id)
                                 WHERE core_userlog.created >= %s AND core_userlog.created <= %s
                                 AND core_userlog.page = 'account_delete'
                                 AND core_userlog.action = 'view'
                                 AND core_user.is_active = 1
                                 GROUP BY core_userlog.user_id
                                 ORDER BY created DESC
                                 """,[date_start, date_end])


class UserLog(models.Model):
    user =          models.ForeignKey(User,related_name='logs')
    created =       models.DateTimeField(auto_now_add=True)
    page =          models.CharField(max_length=128, db_index=True)
    action =        models.CharField(max_length=128)
    args =          models.TextField(null=True,blank=True)
    objects =       UserLogManager()
    
    def __str__(self):
        return "%s: %s.%s" % (self.user.username, self.page, self.action)

    class Meta:
        ordering = ['-created']

    

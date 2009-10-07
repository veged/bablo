# -*- coding: utf-8 -*-

from django.db import models
import datetime
from django.contrib.auth.models import User

class Bitem(models.Model):
    user = models.ForeignKey(User, related_name='bitem_set', editable=False, blank=True, null=True, db_index=True)
    title = models.CharField('Название', maxlength=100)
    description = models.CharField('Описание', maxlength=200, blank=True, null=True)
    amount = models.DecimalField('Величина', default=0, max_digits=8, decimal_places=2)
    is_deposit = models.BooleanField('Является получением', default=False, editable=False)
    time = models.DateTimeField('Дата и время', blank=True, null=True)
    created = models.DateTimeField('Дата и время сохранения', editable=False)
    modified = models.DateTimeField('Дата и время редактирования', editable=False)
    parents = models.ManyToManyField('self', related_name='children', symmetrical=False, blank=True, verbose_name='Обобщения')

    def save(self):
        if not self.id:
            self.created = datetime.datetime.now()
        self.modified = datetime.datetime.now()
        super(Bitem, self).save()

    @classmethod
    def form_save(cls, oldsave):
        def BitemForm_save(self, user, action=False, rbitem=False):
            bitem = oldsave(self)
            bitem.user = user
            cleaned_data = self.cleaned_data
            if cleaned_data.has_key('children'):
                bitem.children = cleaned_data.get('children', [])
            if rbitem:
                if action == 'generalize':
                    bitem.children = [rbitem]
                if action == 'specify':
                    bitem.parents = [rbitem]
                rbitem.save() # для изменения modified
            for pbitem in bitem.parents.all():
                pbitem.amount = max([pbitem.amount - bitem.amount, 0])
                pbitem.save()
            bitem.save()
            return bitem
        return BitemForm_save


    def __unicode__(self):
        return '%s' % self.title

    def signed_amount(self):
        return self.amount
        # if self.is_deposit or self.amount == 0:
        #     return self.amount
        # else:
        #     return (- self.amount)

    def total_subamount(self):
        descendants = self.descendants()
        total_subamount = 0
        for bitem in descendants.values():
            total_subamount = total_subamount + bitem.signed_amount()
        return total_subamount

    def total_amount(self):
        return self.total_subamount() + self.signed_amount()

    def descendants(self, descendants=None):
        if descendants is None:
            descendants = {}
        for bitem in self.children.all():
            if not(descendants.has_key(bitem.id)):
                descendants[bitem.id] = bitem
            descendants = bitem.descendants(descendants)
        return descendants

    @classmethod
    def mains(cls, user):
        return user.bitem_set.filter(parents__isnull=True)

    @classmethod
    def main_pluses(cls, user):
        return cls.mains(user).filter(is_deposit=True)

    @classmethod
    def main_minuses(cls, user):
        return cls.mains(user).filter(is_deposit=False)

    @classmethod
    def balance(cls, user):
        return sum([x.signed_amount() for x in user.bitem_set.all()])

    class Admin:
        list_display   = ('title', 'description', 'amount', 'is_deposit', 'time', 'modified', 'created')
        list_filter    = ('title', 'description')
        ordering       = ('title',)
        search_fields  = ('title', 'description')

    class Meta():
        verbose_name = 'Деньги'
        verbose_name_plural = 'Деньги'

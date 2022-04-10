from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

# 重新更改字段需要删除migrations文件夹中的除__init__.py以外的文件，并重新运行数据迁移
class LicenseTerms(models.Model):
    license = models.CharField(max_length=250)
    info = models.BooleanField()
    preamble = models.BooleanField()
    define = models.BooleanField()
    copyright = models.IntegerField()  # 0为模糊授予，1为明确授予，-1为放弃版权
    patent = models.IntegerField() # 0为未提及，1为明确授予，-1为明确不授予
    trademark = models.BooleanField()  # 0为未提及，1为明确不授予
    copyleft = models.IntegerField()  # 分发限制性，无限制为0，文件级限制为1，库级限制为2，强限制为3
    interaction = models.BooleanField()
    modification = models.BooleanField()
    retain_attr = models.BooleanField()
    enhance_attr = models.BooleanField()
    acceptance = models.BooleanField()
    patent_term = models.BooleanField()  # 0为未提及，1为明确不授予
    vio_term = models.BooleanField()
    disclaimer = models.BooleanField()
    law_info = models.CharField(max_length=250,default='0')
    instructions = models.BooleanField()
    compatible_version  = models.CharField(max_length=2500, default='0')
    secondary_license = models.CharField(max_length=5000, default='0')

    class Meta:
        ordering = ('license',)

    def __str__(self):
        return self.license


class BusinessModel(models.Model):
    id = models.IntegerField(primary_key=True)
    company = models.CharField(max_length=250)
    project = models.CharField(max_length=250)
    domain = models.CharField(max_length=1000)
    source = models.CharField(max_length=250)
    business_model = models.CharField(max_length=250)
    license = models.CharField(max_length=250)
    license_type = models.CharField(max_length=250)

    class Meta:
        ordering = ('company',)

    def __str__(self):
        return self.company
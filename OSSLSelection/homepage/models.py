from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

class LicenseList(models.Model):
    # 开源许可证的基本信息及常用链接、正文
    licensename = models.CharField(max_length=250)
    spdx = models.CharField(max_length=250)
    # published = models.DateField(blank=True,null=True)  # blank=0是为空“”的字段值；blank=0，null=0，是为None的字段值;
    # 重新更改字段需要删除migrations文件夹中的除__init__.py以外的文件，并重新运行数据迁移
    category = models.CharField(max_length=250)
    # 许可证正文
    license_info = RichTextUploadingField(null=True,blank=True)
    # 许可证是否通过官方认证，认证为1，未认证为0
    OSIapproved = models.BooleanField()
    FSFapproved = models.BooleanField()

    class Meta:
        ordering = ('licensename',)

    def __str__(self):
        return self.licensename

    def get_absolute_url(self):
        return reverse('homepage:license_list',
                       args=[self.licensename])


class FQAList(models.Model):
    spdx = models.CharField(max_length=250)
    question = models.TextField()
    answer = models.CharField(max_length=20000)

    class Meta:
        ordering = ('spdx',)

    def __str__(self):
        return self.spdx




class LicenseTerms(models.Model):
    spdx = models.CharField(max_length=250)
    license_info = models.BooleanField()
    preamble = models.BooleanField()
    definitions = models.BooleanField()
    instructions = models.BooleanField()
    disclaimer = models.BooleanField()
    copyright_l = models.BooleanField() # 0为模糊授予，1为明确授予
    trademark_l = models.BooleanField() # 0为未提及，1为明确不授予
    termination_authorization = models.BooleanField()
    law = models.IntegerField()
    copyleft = models.IntegerField()  # 分发限制性，无限制为0，文件级限制为1，模块级限制为2，库级限制为3，限制为4
    attribution = models.BooleanField()
    Strengthen_attribution = models.BooleanField()
    modification = models.BooleanField()
    internet_action = models.BooleanField()
    patent_lice = models.BooleanField() # 0为未提及，1为明确授予
    patent_anti = models.BooleanField() # 0为未提及，1为明确授予
    patent_cant = models.BooleanField() # 0为未提及，1为明确不授予
    acceptance = models.BooleanField()
    law_info = models.CharField(max_length=250,default='无')

    class Meta:
        ordering = ('spdx',)

    def __str__(self):
        return self.spdx




class AboutLicense(models.Model):
    alicense_title = models.CharField(max_length=250)
    alicense_description = models.CharField(max_length=2500,null=True,blank=True)
    alicense_body = RichTextUploadingField(null=True,blank=True)

    class Meta:
        ordering = ('alicense_title',)

    def __str__(self):
        return self.alicense_title


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
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from .models import LicenseList,FQAList,LicenseTerms,BusinessModel
from django.views.decorators.http import require_POST,require_GET
from django.http import HttpResponseBadRequest,JsonResponse
from django.forms.models import model_to_dict
from django.template.defaulttags import register
import subprocess
import zipfile
import rarfile
import os
import shutil
import pandas as pd
from pathlib import Path
import json


# 1、首页
def index(request):
    # licenses = LicenseList.objects.all()
    return render(request,
                  'homepage/templates/index.html',
                  )

# 2、开源许可证介绍页
def about_license(request):
    return render(request,
                  'homepage/templates/about-license.html',
                  )

# 3、许可证条款特征页
def license_feature(request):
    licenses_terms = LicenseTerms.objects.all()
    df = pd.read_excel('E:\\OSSLSelection\\OSSLSelection\\homepage\\compatibility.xls', index_col=0)
    oss_license_list = df.index.tolist()
    oss_license_list.remove('AGPL-3.0+')
    oss_license_list.remove('GPL-2.0+')
    oss_license_list.remove('GPL-3.0+')
    oss_license_list.remove('LGPL-2.1+')
    oss_license_list.remove('LGPL-3.0+')
    return render(request,
                  'homepage/templates/license-feature.html',
                  {
                   'licenses_terms':licenses_terms,
                   'oss_license_list': oss_license_list,
                   }
                  )

# 4、许可证列表页
def license_list(request):
    df = pd.read_excel('E:\\OSSLSelection\\OSSLSelection\\homepage\\compatibility.xls', index_col=0)
    oss_license_list = df.index.tolist()
    f = open('E:\\OSSLSelection\\OSSLSelection\\homepage\\static\\doc\\license\\Apache-2.0.txt',encoding='utf-8-sig')
    license_info = f.read()
    f.close()
    return render(request,
                  'homepage/templates/license-list.html',
                  {'oss_license_list':oss_license_list,
                   'license_info':license_info,
                   }
                  )

# 4、许可证列表页___许可证详情
def license_list_details(request):
    licensespdx = request.POST.get('license')
    # print('+++++'+licensespdx)
    f = open('E:\\OSSLSelection\\OSSLSelection\\homepage\\static\\doc\\license\\'+licensespdx+'.txt',encoding='utf-8-sig')
    license_info = f.read()
    # license_detail = LicenseList.objects.filter(spdx=licensespdx)
    # license_info = license_detail['license_info']
    return JsonResponse({"license_info": license_info,
                        })


# 5、许可证兼容性判断工具页
def license_compatibility(request):
    all_licenses = list(LicenseList.objects.values_list('spdx', flat=True).order_by('spdx'))
    df = pd.read_excel('E:\\OSSLSelection\\OSSLSelection\\homepage\\compatibility.xls', index_col=0)
    judge_licenses = df.index.tolist()
    return render(request,
                  'homepage/templates/license-compatibility.html',
                  {
                      'licenses':judge_licenses,
                  },
                  )

# 5、许可证兼容性判断工具页___许可证兼容性判断
def license_compatibility_judge(request):
    licenseA = request.POST.get('licenseA')
    licenseB = request.POST.get('licenseB')
    compatibility_result = compatibility_judge(licenseA,licenseB)
    iscompatibility = " "
    if licenseA == licenseB:
        iscompatibility = licenseA + "兼容" + licenseB + "。"
    else:
        if compatibility_result == '0':
            iscompatibility = licenseA + "不兼容" + licenseB + "。" + license_uncompatibility_reason(licenseA, licenseB)
        elif compatibility_result == '1':
            iscompatibility = licenseA + "兼容" + licenseB + "。" + licenseA + "授权的作品经过修改，所产生的衍生作品可以使用" + licenseB + "重新授权。" + "然而，" + licenseA + "不能组合兼容" + licenseB + "，因为" + licenseB + "的copyleft属性将传染" + licenseA + "授权的代码。"
        elif compatibility_result == '2':
            iscompatibility = licenseA + "兼容" + licenseB + "。" + licenseB + "是" + licenseA + "的后续版本，（初始开发者指定或默认情况下）" + licenseA + "授权的作品经过修改，所产生的衍生作品可以使用" + licenseB + "重新授权。"
        elif compatibility_result == '3':
            iscompatibility = licenseA + "组合兼容" + licenseB + "。" + licenseA + "授权的作品可以与" + licenseB + "授权的作品进行组合，且组合作品的整体使用" + licenseB + "授权。" + "然而，" + licenseA + "授权的作品经过修改，所产生的衍生作品不能使用" + licenseB + "重新授权，因为" + license_uncompatibility_reason(
                licenseA, licenseB)
        elif compatibility_result == '4':
            iscompatibility = licenseA + "兼容" + licenseB + "。" + licenseA + "的兼容许可证列表包含" + licenseB + "，" + licenseA + "授权的作品经过修改，所产生的衍生作品可以使用" + licenseB + "重新授权。"
        elif compatibility_result == '4+':
            iscompatibility = licenseA + "不兼容" + licenseB + "。" + license_uncompatibility_reason(licenseA,
                                                                                                 licenseB) + "但是，" + licenseA + "授权的作品可以通过多次重新授权的方式（A兼容C，C兼容B），变更为" + licenseB + "授权。"
        elif compatibility_result == '1、3':
            iscompatibility = licenseA + "兼容且组合兼容" + licenseB + "。" + licenseA + "授权的作品经过修改，所产生的衍生作品可以使用" + licenseB + "重新授权；且" + licenseA + "授权的作品可以与" + licenseB + "授权的作品进行组合，组合作品的整体使用" + licenseB + "授权。"
        elif compatibility_result == '3、4':
            iscompatibility = licenseA + "兼容且组合兼容" + licenseB + "。" + licenseA + "的兼容许可证列表包含" + licenseB + "，即" + licenseA + "授权的作品经过修改，所产生的衍生作品可以使用" + licenseB + "重新授权；且" + licenseA + "授权的作品可以与" + licenseB + "授权的作品进行组合，组合作品的整体使用" + licenseB + "授权。"
        elif compatibility_result == '3、4+':
            iscompatibility = licenseA + "组合兼容" + licenseB + "。" + licenseA + "授权的作品可以与" + licenseB + "授权的作品进行组合，组合作品的整体使用" + licenseB + "授权。" + licenseA + "授权的作品经过修改，不能直接使用" + licenseB + "重新授权，因为" + license_uncompatibility_reason(
                licenseA, licenseB) + "；但可以通过多次重新授权的方式（A兼容C，C兼容B），使得" + licenseA + "授权的作品可以变更为" + licenseB + "授权。"
    return JsonResponse({"licenseA": licenseA,
                         "licenseB": licenseB,
                         "iscompatibility":iscompatibility,
                         })

# 5、许可证兼容性判断
def compatibility_judge(licenseA,licenseB):
    df = pd.read_excel('E:\\OSSLSelection\\OSSLSelection\\homepage\\compatibility_0.1.xls', index_col=0)
    compatibility_result = str(df.loc[licenseA, licenseB])
    return compatibility_result

# 5、许可证兼容性判断工具页___许可证不兼容原因判断
def license_uncompatibility_reason(licenseA,licenseB):
    reason = ''
    licenseA_terms = LicenseTerms.objects.filter(spdx=licenseA)[0]
    licenseB_terms = LicenseTerms.objects.filter(spdx=licenseB)[0]
    restrictiveA = set()
    restrictiveB = set()
    if licenseA_terms.attribution == 1:
        restrictiveA.add('保留归属')
    if licenseA_terms.Strengthen_attribution == 1:
        restrictiveA.add('增强归属')
    if licenseA_terms.modification == 1:
        restrictiveA.add('添加修改说明')
    if licenseA_terms.internet_action == 1:
        restrictiveA.add('网络交互视为分发')
    if licenseA_terms.patent_anti == 1:
        restrictiveA.add('反专利诉讼')
    if licenseA_terms.acceptance == 1:
        restrictiveA.add('获得接受者对许可证条款的明确同意')
    if licenseA_terms.law_info != 0:
        restrictiveA.add(licenseA_terms.law_info)
    if licenseB_terms.attribution == 1:
        restrictiveB.add('保留归属')
    if licenseB_terms.Strengthen_attribution == 1:
        restrictiveB.add('增强归属')
    if licenseB_terms.modification == 1:
        restrictiveB.add('添加修改说明')
    if licenseB_terms.internet_action == 1:
        restrictiveB.add('网络交互视为分发')
    if licenseB_terms.patent_anti == 1:
        restrictiveB.add('反专利诉讼')
    if licenseB_terms.acceptance == 1:
        restrictiveB.add('获得接受者对许可证条款的明确同意')
    if licenseB_terms.law_info != 0:
        restrictiveB.add(licenseB_terms.law_info)
    if licenseA_terms.copyleft == 0 and licenseB_terms.copyleft == 4:
        reason = "因为" + licenseA + "包含" + str(restrictiveA.difference(restrictiveB)) + "等要求，而" + licenseB + "中未包含此等要求，若需变更许可证，须要征得所有贡献者的同意。"
    elif (licenseA_terms.copyleft == 1 or licenseA_terms.copyleft == 2 or licenseA_terms.copyleft == 3) and licenseB_terms.copyleft == 4:
        reason = "因为" + licenseA + "是弱限制型开源许可证，而" + licenseB + "是强限制型开源许可证，弱copyleft的特性与强copyleft不兼容；且" + licenseB + "不是" + licenseA + "的后续版本，也不是其例外兼容许可证，若需变更许可证，须要征得所有贡献者的同意。"
    elif licenseA_terms.copyleft == 4 and licenseB_terms.copyleft != 0:
        reason = "因为" + licenseA + "是强限制型开源许可证，且" + licenseB + "不是" + licenseA + "的后续版本，也不是其例外兼容许可证，若需变更许可证，须要征得所有贡献者的同意。"
    elif licenseA_terms.copyleft == 4 and licenseB_terms.copyleft == 0:
        reason = "因为" + licenseA + "是强限制型开源许可证，而" + licenseB + "是宽松型开源许可证，因此" + licenseA + "不兼容" + licenseB + "，若需变更许可证，须要征得所有贡献者的同意。"
    elif licenseA_terms.copyleft == 0 and (licenseB_terms.copyleft == 0 or licenseB_terms.copyleft == 1 or licenseB_terms == 2 or licenseB_terms.copyleft == 3):
        reason = "因为" + licenseA + "包含" + str(restrictiveA.difference(restrictiveB)) + "等要求，而" + licenseB + "中未包含此等要求，若需变更许可证，须要征得所有贡献者的同意。"
    elif (licenseA_terms.copyleft == 1 or licenseA_terms.copyleft == 2 or licenseA_terms.copyleft == 3) and licenseB_terms.copyleft == 0:
        reason = "因为" + licenseA + "是弱限制型开源许可证，而" + licenseB + "是宽松型开源许可证，若需变更许可证，须要征得所有贡献者的同意。"
    elif (licenseA_terms.copyleft == 1 or licenseA_terms.copyleft == 2 or licenseA_terms.copyleft == 3) and licenseB_terms.copyleft != 0 and licenseB_terms.copyleft != 4:
        reason = "因为" + licenseA + "和" + licenseB + "都是弱限制型开源许可证，且" + licenseB + "不是" + licenseA + "的后续版本，也不是其例外兼容许可证，若需变更许可证，须要征得所有贡献者的同意。"
    return reason

@register.filter
def get_licensename(dict,key):
    return dict.get(key)

# 6、许可证选择工具页
def license_selection(request):
    # licenses = list(LicenseTerms.objects.values_list('spdx', flat=True).order_by('spdx'))
    df = pd.read_csv('E:\\OSSLSelection\\OSSLSelection\\homepage\\github_license_usage.csv')
    popular_dict = {}
    for _, row in df.iterrows():
        popular_dict[row['license']] = row['count']
    recommand_licenses = df['license'].tolist()
    return render(request,
                  'homepage/templates/license-selection.html',
                  {'licenses':recommand_licenses,
                   'popular_dict':popular_dict,}
                  )

# 6、许可证选择工具页__许可证识别及兼容性检测
num_progress = 1
def license_check(request):
    upload_file = request.FILES.get("FILE")
    if upload_file == None:
        return JsonResponse({"in_licenses": "error",})
    else:
        if os.path.exists(r"E:\oss_license_selection_analyze\temp_files")==False:
            os.makedirs(r"E:\oss_license_selection_analyze\temp_files")
        with open("E:\\oss_license_selection_analyze\\temp_files\\"+upload_file.name, 'wb+') as save_file:
            for chunk in upload_file.chunks():
                save_file.write(chunk)
        uploadfile_path = "E:\\oss_license_selection_analyze\\temp_files\\"+upload_file.name
        temp_path = "E:\\oss_license_selection_analyze\\temp_files\\zziprar"
        results = {}
        in_licenses = set()
        global num_progress
        if ".zip" in uploadfile_path:
            z = zipfile.ZipFile(uploadfile_path, "r")
            z.extractall(temp_path)
            z.close()
            filepath_list = show_files(Path(temp_path), [])
            filepathlist_len = len(filepath_list)
            for i,one_file in enumerate(filepath_list):
                file_license_list, in_licenses, results = license_detection_file(one_file,results,in_licenses)
                num_progress2 = i * 100 / filepathlist_len
                if num_progress2 >= 1:
                    num_progress = num_progress2
        elif ".rar" in uploadfile_path:
            z = rarfile.RarFile(uploadfile_path, "r")
            z.extractall(temp_path)
            z.close()
            filepath_list, filesname_list, treestr_list = show_files(Path(temp_path), [], [], [], 0)
            filepathlist_len = len(filepath_list)
            for i,one_file in enumerate(filepath_list):
                file_license_list, in_licenses, results = license_detection_file(one_file,results,in_licenses)
                num_progress2 = i * 100 / filepathlist_len
                if num_progress2 >= 1:
                    num_progress = num_progress2
        else:
            file_license_list, in_licenses, results = license_detection_file(uploadfile_path)
        num_progress = 100
        dependencies = depend_detection(temp_path)
        confilct_copyleft_dir, confilct_depend_dict= conflict_dection(results,dependencies)
        json_list = tree_json(Path(temp_path), results, confilct_copyleft_dir, confilct_depend_dict, pi=0, fi=0, json_list=[])
        shutil.rmtree("E:\\oss_license_selection_analyze\\temp_files\\")
        llist, checked_list, compatible_licenses, compatible_1_2_3_4_list, compatible_1_2_4_list, compatible_3_list = license_compatibility_filter(in_licenses)
        num_progress = 1
        return JsonResponse({"in_licenses": llist,
                             'checked_list':checked_list,
                             'licenselist_recommended':compatible_licenses,
                             'compatible_1_2_3_4_list': compatible_1_2_3_4_list,
                             'compatible_1_2_4_list':compatible_1_2_4_list,
                             'compatible_3_list': compatible_3_list,
                             "files_license_detail": results,
                             "json_list":json_list,
                             })

# 6、许可证选择工具页__许可证识别__显示进度
def show_progress(request):
    # print('show_progress----------'+str(num_progress))
    num_progress_2 = round(num_progress,2)
    return JsonResponse(num_progress_2, safe=False)

# 6、许可证选择工具页__许可证识别__遍历文件
def show_files(pathname, files_path):
    file_path = str(pathname.parent) + '\\' + pathname.name
    if pathname.is_file():
        files_path.append(file_path)
    elif pathname.is_dir():
        for cp in pathname.iterdir():
            show_files(cp, files_path)
    return files_path

def tree_json(pathname,results, confilct_copyleft_dict, confilct_depend_dict, pi,fi,json_list):
    file_path = str(pathname.parent) + '\\' + pathname.name
    if pathname.is_file():
        if file_path in results:
            file_name = pathname.name + '-' * (150 - len(str(pathname.name)) - len(str(results[file_path]))) + str(results[file_path])
        else:
            file_name = pathname.name
        if file_path in confilct_depend_dict.keys():
            json_list.append({"id":fi,"Pid":pi,"name":file_name,"t":confilct_depend_dict[file_path],"font":{'color':'red'}})
        else:
            json_list.append({"id": fi, "Pid": pi, "name": file_name,"t":'ok'})
    elif pathname.is_dir():
        if file_path in confilct_copyleft_dict.keys():
            json_list.append({"id": fi, "Pid": pi, "name": pathname.name, "open": 'true',"t":confilct_copyleft_dict[file_path],"font":{'color':'red'}})
        else:
            json_list.append({"id": fi, "Pid": pi, "name": pathname.name, "open": 'true'})
        pi = fi
        for cp in pathname.iterdir():
            fi += 1
            tree_json(cp,results, confilct_copyleft_dict, confilct_depend_dict, pi,fi,json_list)
    return json_list


# 6、许可证选择工具页__许可证识别__Ninka识别文件
def license_detection_file(one_file,results,in_licenses):
    Other_Licenses = ['SeeFile', 'UNKNOWN']
    try:
        pipe = subprocess.Popen(
            ["perl", r"E:\oss_license_selection_analyze\ninka-tool\ninka-master\bin\ninka.pl", one_file],
            stdout=subprocess.PIPE)
        file_license_list = str(pipe.stdout.read()).split(";")
        file_licenses = file_license_list[1].split(',')
        init_file_name = file_license_list[0].replace(r"b'", '',1)
        init_file_name = init_file_name.replace(r"\\", '\\')
        results[init_file_name] = file_licenses
        dual_licenses_str = ''
        dual_licenses = set()
        for li in file_licenses:
            if li in Other_Licenses:
                in_licenses.add('Other')
            elif "NONE" in li:
                in_licenses.add('')
            else:
                if li not in dual_licenses:
                    dual_licenses_str = dual_licenses_str + li + ' or '
                    dual_licenses.add(li)
        in_licenses.add(dual_licenses_str[:-4])
        in_licenses.discard('')
    except:
        init_file_name = one_file.replace(r"b'", '', 1)
        init_file_name = init_file_name.replace(r"\\", '\\')
        results[init_file_name] = 'UNKOWN'
        in_licenses.add('Other')
    return file_license_list,in_licenses,results

def depend_detection(src_path):
    output_depend_path = "E:\\oss_license_selection_analyze\\temp_files\\output_depend"
    if os.path.exists(output_depend_path) == False:
        os.makedirs(output_depend_path)
    surport_lang = ["python","java","cpp","ruby","pom"]
    dependencies = {}
    for lang in surport_lang:
        proc = subprocess.Popen(
            "java -jar "+"E:\\oss_license_selection_analyze\\depends-tool\\depends-0.9.6-package\\depends-0.9.6\\depends.jar "+"-d="+output_depend_path+" "+lang +" "+src_path+" "+lang+'depend')
        proc.communicate()
        proc.wait()
        if os.path.exists("E:\\oss_license_selection_analyze\\temp_files\\output_depend\\"+lang+"depend.json"):
            with open("E:\\oss_license_selection_analyze\\temp_files\\output_depend\\"+lang+"depend.json", 'r') as f:
                data = json.load(f)
                file_path_list = data['variables']
                dependencies_list = data['cells']
                for one_denpendence in dependencies_list:
                    src_index = one_denpendence['src']
                    dest_index = one_denpendence['dest']
                    src_file = file_path_list[src_index]
                    dest_file = file_path_list[dest_index]
                    dependencies[dest_file] = src_file
    return dependencies

# 6、许可证选择工具页__许可证识别__冲突检测
def conflict_dection(results,dependencies):
    temp_path = "E:\\oss_license_selection_analyze\\temp_files\\zziprar"
    df1 = pd.read_excel(r'E:\OSSLSelection\OSSLSelection\homepage\compatibility_0.1.xls', index_col=0)
    check_license_list = df1.index.tolist()
    confilct_copyleft_dict = {}
    confilct_depend_dict = {}
    for src_file in dependencies.keys():
        dest_file = dependencies[src_file]
        iscompatibility = 0
        for licenseA in results[src_file]:
            for licenseB in results[dest_file]:
                compatibility_result = compatibility_judge(licenseA, licenseB)
            if compatibility_result != '0':
                iscompatibility = 1
        if iscompatibility == 0:
            confilct_depend_dict[dest_file] = src_file.replace(temp_path,'')+'的许可证'+licenseA+'不兼容'+dest_file.replace(temp_path,'')+'的许可证'+licenseB
    have_check = []
    for fileA in results.keys():
        for fileB in results.keys():
            if [fileA,fileB] in have_check:
                pass
            else:
                have_check.append([fileA, fileB])
                have_check.append([fileB, fileA])
                licenseAs = results[fileA]
                licenseBs = results[fileB]
                if set(licenseAs).issubset(set(check_license_list)) and set(licenseBs).issubset(set(check_license_list)):
                    iscompatibility = 0
                    lA = ''
                    lB = ''
                    for licenseA in licenseAs:
                        for licenseB in licenseBs:
                            lA = licenseA
                            lB = licenseB
                            if licenseA in check_license_list and licenseB in check_license_list:
                                compatibility_result_ab = compatibility_judge(licenseA, licenseB)
                                compatibility_result_ba = compatibility_judge(licenseB, licenseA)
                                if compatibility_result_ab != '0' or compatibility_result_ba != '0':
                                    iscompatibility = 1
                    if iscompatibility == 0:
                        confilct_copyleft_dict[longestCommonDir(fileA, fileB)] = fileA.replace(temp_path,'') + "的许可证" + lA + "和" + fileB.replace(temp_path,'') + "的许可证" + lB +"互不兼容。"
    return confilct_copyleft_dict,confilct_depend_dict


def longestCommonDir(fileA,fileB):
    pathname = Path(fileA).parent
    while str(pathname) not in fileB:
        if str(pathname) in fileB:
            break
        pathname = pathname.parent
    return str(pathname)

# 6、许可证选择工具页__许可证识别__兼容许可证筛选
def license_compatibility_filter(in_licenses):
    df = pd.read_csv(r'E:\OSSLSelection\OSSLSelection\homepage\github_license_usage.csv')
    all_licenses = df['license'].tolist()
    compatible_licenses = df['license'].tolist()
    df1 = pd.read_excel(r'E:\OSSLSelection\OSSLSelection\homepage\compatibility_0.1.xls', index_col=0)
    check_license_list = df1.index.tolist()
    checked_list = []
    compatible_1_2_3_4_list = df['license'].tolist()
    compatible_1_2_4_list = df['license'].tolist()
    compatible_3_list = df['license'].tolist()
    for licenseA in list(in_licenses):
        if 'or' not in licenseA:
            if licenseA in check_license_list:
                checked_list.append(licenseA)
                for licenseB in all_licenses:
                    compatibility_result = str(df1.loc[licenseA, licenseB])
                    if compatibility_result == '0':
                        if licenseB in compatible_licenses:
                            compatible_licenses.remove(licenseB)
                    if compatibility_result != '1、3' and compatibility_result != '3、4':
                        if licenseB in compatible_1_2_3_4_list:
                            compatible_1_2_3_4_list.remove(licenseB)
                    if '1' not in compatibility_result and '2' not in compatibility_result and '4' not in compatibility_result:
                        if licenseB in compatible_1_2_4_list:
                            compatible_1_2_4_list.remove(licenseB)
                    if '3' not in compatibility_result:
                        if licenseB in compatible_3_list:
                            compatible_3_list.remove(licenseB)
        else:
            checked_list.append(licenseA)
            for licenseB in all_licenses:
                dual_licenses = licenseA.split(' or ')
                is_remove = 1
                for sub_license in dual_licenses:
                    if sub_license in check_license_list:
                        compatibility_result = str(df1.loc[sub_license, licenseB])
                    if compatibility_result != '0':
                        is_remove = 0
                if is_remove and licenseB in compatible_licenses:
                    compatible_licenses.remove(licenseB)
    llist = list(in_licenses)
    llist = sorted(llist)
    if 'Other' in llist:
        llist.append('Other')
        llist.remove('Other')
    return llist, checked_list, compatible_licenses, compatible_1_2_3_4_list, compatible_1_2_4_list, compatible_3_list


# 6、许可证选择工具页__许可证类型推荐
def license_type_choice(request):
    return render(request,
                  'homepage/templates/license-type-choice.html',
                  )

# 6、许可证选择工具页__开源商业模式
def business_model(request):
    business_terms = BusinessModel.objects.all()
    return render(request,
                  'homepage/templates/business_model.html',
                  {'business_terms':business_terms,}
                  )



# 6、许可证选择工具页__许可证条款分析
def license_terms_choice(request):
    question1_val = request.POST.get('question1_val')
    question2_val = request.POST.get('question2_val')
    question3_val = request.POST.get('question3_val')
    question4_val = request.POST.get('question4_val')
    question5_val = request.POST.get('question5_val')
    question6_val = request.POST.get('question6_val')
    question7_val = request.POST.get('question7_val')
    cur_question = int(request.POST.get('cur_question'))
    init_licenselist = request.POST.getlist('init_licenselist')
    licenses_spdx = list(LicenseTerms.objects.values_list('spdx', flat=True).order_by('spdx'))
    licenses_copyleft = list(LicenseTerms.objects.values_list('copyleft', flat=True).order_by('spdx'))
    licenses_modification = list(LicenseTerms.objects.values_list('modification', flat=True).order_by('spdx'))
    licenses_internet_action = list(LicenseTerms.objects.values_list('internet_action', flat=True).order_by('spdx'))
    licenses_patent_lice = list(LicenseTerms.objects.values_list('patent_lice', flat=True).order_by('spdx'))
    licenses_patent_anti = list(LicenseTerms.objects.values_list('patent_anti', flat=True).order_by('spdx'))
    licenses_patent_cant = list(LicenseTerms.objects.values_list('patent_cant', flat=True).order_by('spdx'))
    licenses_trademark_l = list(LicenseTerms.objects.values_list('trademark_l', flat=True).order_by('spdx'))
    # 初始化推荐列表
    licenselist_recommended = init_licenselist
    # 满足各个条款的列表的列表
    rr_license = []
    # 已选择的条款选项
    rr_question_var = []
    # 是否显示问题2
    q2_show = 1
    if question1_val != None:
        # 满足该条款的许可证列表
        license_ok = []
        if question1_val == '宽松型开源许可证':
            q2_show = 0
            for i, x in enumerate(licenses_copyleft):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        elif question1_val == '限制型开源许可证':
            for i, x in enumerate(licenses_copyleft):
                if x > 0:
                    license_ok.append(licenses_spdx[i])
        elif question1_val == '公共领域许可证':
            q2_show = 0
            for i, x in enumerate(licenses_copyleft):
                if x == -1:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
        rr_question_var.append(question1_val)
    else:
        rr_license.append(init_licenselist)
        rr_question_var.append(question1_val)
    if question2_val != None:
        # 满足该条款的许可证列表
        license_ok = []
        if question2_val == '文件级__弱限制型开源许可证':
            for i, x in enumerate(licenses_copyleft):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        elif question2_val == '模块级__弱限制型开源许可证':
            for i, x in enumerate(licenses_copyleft):
                if x == 2:
                    license_ok.append(licenses_spdx[i])
        elif question2_val == '库级__弱限制型开源许可证':
            for i, x in enumerate(licenses_copyleft):
                if x == 3:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_copyleft):
                if x == 4:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
        rr_question_var.append(question2_val)
    else:
        rr_license.append(init_licenselist)
        rr_question_var.append(question2_val)
    if question3_val != None:
        # 满足该条款的许可证列表
        license_ok = []
        if question3_val == '不提及专利权':
            for i, x in enumerate(licenses_patent_lice):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        elif question3_val == '明确授予专利权':
            for i, x in enumerate(licenses_patent_lice):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_patent_cant):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
        rr_question_var.append(question3_val)
    else:
        rr_license.append(init_licenselist)
        rr_question_var.append(question3_val)
    if question4_val != None:
        # 满足该条款的许可证列表
        license_ok = []
        if question4_val == '包含反专利诉讼条款':
            for i, x in enumerate(licenses_patent_anti):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_patent_anti):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
        rr_question_var.append(question4_val)
    else:
        rr_license.append(init_licenselist)
        rr_question_var.append(question4_val)
    if question5_val != None:
        # 满足该条款的许可证列表
        license_ok = []
        if question5_val == '不提及商标权':
            for i, x in enumerate(licenses_trademark_l):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_trademark_l):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
        rr_question_var.append(question5_val)
    else:
        rr_license.append(init_licenselist)
        rr_question_var.append(question5_val)
    if question6_val != None:
        # 满足该条款的许可证列表
        license_ok = []
        if question6_val == '网络部署视为分发':
            for i, x in enumerate(licenses_internet_action):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_internet_action):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
        rr_question_var.append(question6_val)
    else:
        rr_license.append(init_licenselist)
        rr_question_var.append(question6_val)
    if question7_val != None:
        # 满足该条款的许可证列表
        license_ok = []
        if question7_val == '包含修改说明条款':
            for i, x in enumerate(licenses_modification):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_modification):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        rr_license.append(license_ok)
        rr_question_var.append(question7_val)
    else:
        rr_license.append(init_licenselist)
        rr_question_var.append(question7_val)

    terms_choice = []
    for i in range(7):
        licenselist_recommended = sorted(list(set(licenselist_recommended) & set(rr_license[i])))
        terms_choice.append(rr_question_var[i])
    return JsonResponse({"terms_choice": terms_choice,
                         "licenselist_recommended":licenselist_recommended,
                         "q2_show":q2_show,
                         })


# 6、许可证选择工具页__许可证细节对比
def license_compare(request):
    compare_licenselist = request.POST.getlist('compare_licenselist')
    compared_licenselist = []
    for cl in compare_licenselist:
        license_terms = LicenseTerms.objects.get(spdx=cl)
        license_dict = model_to_dict(license_terms)
        compared_licenselist.append(license_dict)
    return JsonResponse({"compared_licenselist": compared_licenselist,
                         })


# 6、许可证选择工具页__许可证推荐排序——流行度
def sort_license_popular(request):
    license_popular_asc = request.POST.get('license_popular_asc')
    df = pd.read_csv('E:\\OSSLSelection\\OSSLSelection\\homepage\\github_license_usage.csv')
    popular_dict = {}
    for _,row in df.iterrows():
        popular_dict[row['license']] = row['count']
    return JsonResponse({"popular_dict": popular_dict,
                         "license_popular_asc":license_popular_asc,
                         })


# 6、许可证选择工具页__许可证推荐排序——可读性
def sort_license_complex(request):
    license_complex_asc = request.POST.get('license_complex_asc')
    df = pd.read_csv('E:\\OSSLSelection\\OSSLSelection\\homepage\\license_readability.csv')
    complex_dict = {}
    for _,row in df.iterrows():
        complex_dict[row['license']] = int(row['mean'])
    return JsonResponse({"complex_dict": complex_dict,
                         "license_complex_asc":license_complex_asc,
                         })


# 7、许可证使用详情页
def license_trend(request):
    df = pd.read_csv('E:\\OSSLSelection\\OSSLSelection\\homepage\\github_repos_info_removeother.csv')
    github_topics_count = df['topic'].value_counts()
    github_languages_count = df['language'].value_counts()
    github_licenses_count = df['license'].value_counts()
    github_topics = github_topics_count[:27].index.tolist()
    github_languages = github_languages_count[:30].index.tolist()
    github_licenses = github_licenses_count[:10].index.tolist()
    return render(request,
                  'homepage/templates/license-trend.html',
                  {   'github_topics':github_topics,
                      'github_languages':github_languages,
                      "github_licenses":github_licenses,})

# 7、许可证使用详情页__画图
def draw_trend(request):
    selected_data_source = request.POST.get('selected_data_source')
    selected_topics = request.POST.getlist('selected_topics')
    selected_languages = request.POST.getlist('selected_languages')
    selected_licenses = request.POST.getlist('selected_licenses')
    minstar = request.POST.get('minstar')
    maxstar = request.POST.get('maxstar')
    datalist = []
    datadict = {}
    datelist = ['2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021']
    df = pd.read_csv('E:\\OSSLSelection\\OSSLSelection\\homepage\\github_license_usage.csv')
    recommand_licenses = df['license'].tolist()
    if selected_data_source == "github":
        df = pd.read_csv('E:\\OSSLSelection\\OSSLSelection\\homepage\\github_repos_info_removeother.csv')
        if selected_topics[0] != 'all':
            df = df.query('topic in '+str(selected_topics))
        if selected_languages[0] != 'all':
            df = df.query('language in '+str(selected_languages))
        if minstar != None and minstar.isdigit():
            df = df[df['stars'] > float(minstar)]
        if maxstar != None and maxstar.isdigit():
            df = df[df['stars'] < float(maxstar)]
        if selected_licenses[0] != 'all':
            df = df.query('license in '+str(selected_licenses))
        else:
            df = df.query('license in ' + str(recommand_licenses))
        df['date'] = pd.to_datetime(df['created_at'])
        df1 = df.groupby([df['date'].dt.year,df['license']])['repo_name'].agg({'count'})
        df2 = df.groupby([df['license']])['repo_name'].agg({'count'})
        for i,r in df1.iterrows():
            if r.name[1] not in datadict.keys():
                datadict[r.name[1]] = [0.0] * 14
                datadict[r.name[1]][datelist.index(str(r.name[0]))] = float(r['count'])
            else:
                datadict[r.name[1]][datelist.index(str(r.name[0]))] = float(r['count'])
        sorted(datadict)
        for i in datadict.keys():
            one_data = {}
            one_data['name'] = i
            one_data['data'] = datadict[i]
            datalist.append(one_data)
        distribut_dic = []
        for i,r in df2.iterrows():
            distribut_dic.append([r.name, float(r['count'])])
    return JsonResponse({"datalist":datalist,
                         "datelist":datelist,
                         "distribut_dict":distribut_dic,
                         })


# 8、许可证常见问答页
def license_fqa(request):
    f = open('E:\\OSSLSelection\\OSSLSelection\\homepage\\static\\doc\\FQA\\0BSD.txt',encoding='utf-8-sig')
    fqas = f.read()
    return render(request,
                      'homepage/templates/license_fqa.html',
                      {
                         'fqa':fqas,
                      },
                  )
# 8、许可证常见问答页
def license_fqa_list(request):
    spdx = request.POST.get('spdx')
    f = open('E:\\OSSLSelection\\OSSLSelection\\homepage\\static\\doc\\FQA\\'+spdx+'.txt',encoding='utf-8-sig')
    fqas = f.read()
    return JsonResponse({"fqa": fqas,})

# 8、许可证常见问答机器人
def license_bot(request):
    return render(request,
                  'homepage/templates/fqa-bot.html',
                  )

# 9、开源许可证框架页
def license_frame(request):
    return render(request,
                  'homepage/templates/license-frame.html',
                  )


# 10、联系我们
def contact(request):
    return render(request,
                  'homepage/templates/contact.html',
                  )

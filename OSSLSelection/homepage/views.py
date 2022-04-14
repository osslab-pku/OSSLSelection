from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from .models import LicenseTerms,BusinessModel
from django.views.decorators.http import require_POST,require_GET
from django.http import HttpResponseBadRequest,JsonResponse
from django.forms.models import model_to_dict
from django.template.defaulttags import register
from OSSLSelection.settings import BASE_DIR
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

# 2、许可证兼容性判断工具页
def license_compatibility(request):
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\compatibility_63.csv'), index_col=0)
    judge_licenses = df.index.tolist()
    return render(request,
                  'homepage/templates/license-compatibility.html',
                  {'licenses':sorted(judge_licenses),},)

# 2、许可证兼容性判断工具页___许可证兼容性判断结果
def license_compatibility_judge(request):
    licenseA = request.POST.get('licenseA')
    licenseB = request.POST.get('licenseB')
    compatibility_result = compatibility_judge(licenseA,licenseB)
    iscompatibility = ""
    how_to_use = ""
    why_or_why_not = ""
    compatibility_terms = []
    if licenseA == licenseB:
        iscompatibility = licenseA + "兼容" + licenseB + "。"
        why_or_why_not = "您选择了两个相同的许可证。"
    else:
        if compatibility_result == '0':
            iscompatibility = licenseA + "不兼容" + licenseB + "。"
            how_to_use = "您不能在" + licenseB + "授权的作品中使用（包括但不限于链接、复制粘贴等方式）" + licenseA + "授权的作品。"
            why_or_why_not,compatibility_terms = license_uncompatibility1_reason(licenseA, licenseB)
            why_or_why_not = "(1)" + why_or_why_not + "(2)" +license_uncompatibility2_reason(licenseA, licenseB)
        elif compatibility_result == '1':
            iscompatibility = licenseA + "次级兼容" + licenseB + "。"
            how_to_use = license_compatibility3_reason(licenseA,licenseB) + "您可以修改或使用（包括但不限于链接、复制粘贴等方式）" + licenseA + "授权的作品，所产生的衍生作品可以采用" + licenseB + "授权，" \
                         + "衍生作品的整体及其部分（包括原" + licenseA + "授权的部分）都将受" + licenseB + "的约束，请注意许可证信息的管理。"
            why_or_why_not = license_uncompatibility2_reason(licenseA, licenseB)
        elif compatibility_result == '2':
            iscompatibility = licenseA + "组合兼容" + licenseB + "。"
            how_to_use = license_compatibility3_reason(licenseA,licenseB) + "您可以修改或使用（包括但不限于链接、复制粘贴等方式）" + licenseA + "授权的作品，所产生的衍生作品的整体可以采用" + licenseB + "授权，" \
                         + "但须确保该衍生作品中原" + licenseA + "授权的部分及其修改仍然受" + licenseA + "的约束，而" + licenseB + "约束除" + licenseA + "授权部分的其他部分。"
            why_or_why_not,compatibility_terms =  license_uncompatibility1_reason(licenseA, licenseB)
        elif compatibility_result == '1,2':
            iscompatibility = licenseA + "次级兼容且组合兼容" + licenseB + "。"
            how_to_use = license_compatibility3_reason(licenseA,licenseB) + "您可以任选一种兼容性场景进行许可证管理。（1）若您选择次级兼容，则" + "您可以修改或使用（包括但不限于链接、复制粘贴等方式）" \
                         + licenseA + "授权的作品，所产生的衍生作品可以采用" + licenseB + "授权，" + "衍生作品的整体及其部分（包括原" + licenseA \
                         + "授权的部分）都将受" + licenseB + "的约束，请注意许可证信息的管理；（2）若您选择组合兼容，则" + "您可以修改或使用（包括但不限于链接、复制粘贴等方式）" \
                         + licenseA + "授权的作品，所产生的衍生作品的整体可以采用" + licenseB + "授权，" + "但须确保该衍生作品中原" + licenseA \
                         + "授权的部分及其修改仍然受" + licenseA + "的约束，而" + licenseB + "约束除" + licenseA + "授权部分的其他部分。"
            why_or_why_not = ""
    return JsonResponse({"licenseA": licenseA,
                         "licenseB": licenseB,
                         "iscompatibility":iscompatibility,
                         "how_to_use":how_to_use,
                         "why_or_why_not":why_or_why_not,
                         "compatibility_terms":compatibility_terms,
                         })

# 2、许可证兼容性判断
def compatibility_judge(licenseA,licenseB):
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\compatibility_63.csv'), index_col=0)
    compatibility_result = str(df.loc[licenseA, licenseB])
    return compatibility_result

# 2、因版本兼容、次级许可证兼容、gpl组合兼容的原因
def license_compatibility3_reason(licenseA,licenseB):
    reason = ''
    versionA = []
    secondaryA = []
    combineA = []
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\licenses_terms_63.csv'))
    licenseA_terms = df[df['license'] == licenseA].to_dict(orient='records')[0]
    if licenseA_terms['compatible_version'] != '0':
        versionA = licenseA_terms['compatible_version'].split(',')
    if licenseA_terms['secondary_license'] != '0':
        secondaryA = licenseA_terms['secondary_license'].split(',')
    if licenseA_terms['gpl_combine'] != '0':
        combineA = licenseA_terms['gpl_combine'].split(',')
    if licenseB in versionA:
        reason = reason + licenseB + '是' + licenseA + '的次级兼容的后续版本。'
    if licenseB in secondaryA:
        reason = reason + licenseB + '在' + licenseA + '包含的次级许可证列表中，允许' + licenseA + '次级兼容' + licenseB + '。'
    if licenseB in combineA:
        reason = reason + licenseA + '与' + licenseB + '满足GPL系列许可证的组合兼容条件。'
    return reason


# 2、许可证兼容性判断工具页___许可证不次级兼容原因判断
def license_uncompatibility1_reason(licenseA,licenseB):
    reason = '不能次级兼容的原因是，'
    compatibility_terms = []
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\licenses_terms_63.csv'))
    licenseA_terms = df[df['license']==licenseA].to_dict(orient='records')[0]
    licenseB_terms = df[df['license']==licenseB].to_dict(orient='records')[0]
    restrictiveA = set()
    restrictiveB = set()
    if licenseA_terms['retain_attr'] == 1:
        restrictiveA.add('保留归属')
    if licenseA_terms['enhance_attr'] == 1:
        restrictiveA.add('增强归属')
    if licenseA_terms['modification'] == 1:
        restrictiveA.add('添加修改说明')
    if licenseA_terms['interaction'] == 1:
        restrictiveA.add('网络交互视为分发')
    if licenseA_terms['patent_term'] == 1:
        restrictiveA.add('反专利诉讼')
    if licenseA_terms['acceptance'] == 1:
        restrictiveA.add('获得接受者对许可证条款的明确同意')
    if licenseB_terms['retain_attr'] == 1:
        restrictiveB.add('保留归属')
    if licenseB_terms['enhance_attr'] == 1:
        restrictiveB.add('增强归属')
    if licenseB_terms['modification'] == 1:
        restrictiveB.add('添加修改说明')
    if licenseB_terms['interaction'] == 1:
        restrictiveB.add('网络交互视为分发')
    if licenseB_terms['patent_term'] == 1:
        restrictiveB.add('反专利诉讼')
    if licenseB_terms['acceptance'] == 1:
        restrictiveB.add('获得接受者对许可证条款的明确同意')
    if licenseA_terms['copyleft'] == 0 and licenseB_terms['copyleft'] != 0:
        reason = reason + licenseB + "是限制型开源许可证，如果使用（包括但不限于链接、复制粘贴等方式）了" + licenseA + "授权的作品，要求" + licenseA \
                 + "授权的作品将受" + licenseB + "的约束，而" + licenseA + "包含如下影响次级兼容的条款（" + licenseB + "中没有此等要求）" +"，使其不能变更为" + licenseB + "授权。"
        compatibility_terms = list(restrictiveA.difference(restrictiveB))
    elif licenseA_terms['copyleft'] == 0 and licenseB_terms['copyleft'] == 0 :
        reason = reason + licenseA + "和" + licenseB + "都是宽松型开源许可证，但" + licenseA + "包含如下影响次级兼容的条款（" + licenseB + "中没有此等要求）" + "，使其不能变更为" + licenseB + "授权。"
        compatibility_terms = list(restrictiveA.difference(restrictiveB))
    elif licenseA_terms['copyleft'] != 0 and licenseB_terms['copyleft'] != 0:
        reason = reason + licenseA + "和" + licenseB + "都是限制型开源许可证，它们都包含copyleft的特性，且" + licenseB \
                 + "不是" + licenseA +"的兼容后续版本，也不是其兼容次级许可证，使" + licenseA + "无法变更为" +licenseB + \
                 "，进而无法满足" + licenseB + "的copyleft要求。"
    elif licenseA_terms['copyleft'] != 0 and licenseB_terms['copyleft'] == 0:
        reason = reason + licenseA + "是限制型开源许可证，而" + licenseB + "是宽松型开源许可证，修改或使用（包括但不限于链接、复制粘贴等方式）了" \
                 + licenseA + "授权的作品，所产生的衍生作品须遵循" + licenseA + "的copyleft要求，无法采用" + licenseB + "授权。"
    return reason,compatibility_terms

# 2、许可证兼容性判断工具页___许可证不组合兼容原因判断
def license_uncompatibility2_reason(licenseA,licenseB):
    reason = '不能组合兼容的原因是，'
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\licenses_terms_63.csv'))
    licenseA_terms = df[df['license'] == licenseA].to_dict(orient='records')[0]
    licenseB_terms = df[df['license'] == licenseB].to_dict(orient='records')[0]
    if licenseA_terms['copyleft'] != 3 and licenseB_terms['copyleft'] == 2 :
        reason = reason + licenseB + "是库级弱限制型开源许可证，不限制通过接口调用该许可证授权作品的其他作品，但要求其约束部分（包括但不限于其包含的文件、其调用的组件等）都遵循其copyleft特性，若使用（包括但不限于调用、复制粘贴等方式）了" \
                 + licenseA + "授权的作品，" + licenseA + "授权的部分须遵循" + licenseB + "，因此无法满足组合兼容的场景。"
    elif licenseA_terms['copyleft'] != 3 and licenseB_terms['copyleft'] == 3 :
        reason = reason + licenseB + "是强限制型开源许可证，要求其授权作品的整体及其部分都遵循其copyleft特性，若使用（包括但不限于调用、复制粘贴等方式）了" \
                 + licenseA + "授权的作品，" + licenseA + "授权的部分须遵循" + licenseB + "，因此无法满足组合兼容的场景。"
    elif licenseA_terms['copyleft'] == 3:
        reason = reason + licenseA + "是强限制型开源许可证，要求其授权作品的整体及其部分都遵循其copyleft特性，因此无法满足组合兼容的场景。"
    return reason

@register.filter
def get_licensename(dict,key):
    return dict.get(key)

# 3、许可证选择工具页
def license_selection(request):
    # licenses = list(LicenseTerms.objects.values_list('spdx', flat=True).order_by('spdx'))
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\github_license_usage.csv'))
    popular_dict = {}
    for _, row in df.iterrows():
        popular_dict[row['license']] = row['count']
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\license_recommended.csv'))
    recommand_licenses = df['license'].tolist()
    return render(request,
                  'homepage/templates/license-selection.html',
                  {'licenses':recommand_licenses,
                   'popular_dict':popular_dict,}
                  )

# 3、许可证选择工具页__许可证识别及兼容性检测
num_progress = 1
def license_check(request):
    upload_file = request.FILES.get("FILE")
    if upload_file == None:
        return JsonResponse({"in_licenses": "error",})
    else:
        temp_path = os.path.join(BASE_DIR, 'temp_files')
        if os.path.exists(temp_path)==False:
            os.makedirs(temp_path)
        with open(os.path.join(temp_path,upload_file.name), 'wb+') as save_file:
            for chunk in upload_file.chunks():
                save_file.write(chunk)
        uploadfile_path = temp_path + '\\' +upload_file.name
        unzip_path = temp_path + '\\' + "unzip"
        results = {}
        in_licenses = set()
        global num_progress
        if ".zip" in uploadfile_path:
            z = zipfile.ZipFile(uploadfile_path, "r")
            z.extractall(unzip_path)
            z.close()
            filepath_list = show_files(Path(unzip_path), [])
            filepathlist_len = len(filepath_list)
            for i,one_file in enumerate(filepath_list):
                in_licenses, results = license_detection_file(one_file,results,in_licenses)
                num_progress2 = i * 100 / filepathlist_len
                if num_progress2 >= 1:
                    num_progress = num_progress2
        elif ".rar" in uploadfile_path:
            z = rarfile.RarFile(uploadfile_path, "r")
            z.extractall(unzip_path)
            z.close()
            filepath_list = show_files(Path(unzip_path), [])
            filepathlist_len = len(filepath_list)
            for i,one_file in enumerate(filepath_list):
                in_licenses, results = license_detection_file(one_file,results,in_licenses)
                num_progress2 = i * 100 / filepathlist_len
                if num_progress2 >= 1:
                    num_progress = num_progress2
        else:
            return JsonResponse({"in_licenses": "error2",})
        num_progress = 100
        show_in_licenses, checked_list, compatible_licenses, compatible_both_list, compatible_secondary_list, compatible_combine_list, dual_no_checked = license_compatibility_filter(in_licenses)
        dependencies = depend_detection(unzip_path,temp_path)
        confilct_copyleft_list, confilct_depend_dict = conflict_dection(results, dependencies,checked_list,unzip_path)
        json_list = tree_json(Path(unzip_path), results,confilct_depend_dict, pi=0,
                              json_list=[])
        shutil.rmtree(temp_path)
        num_progress = 1
        return JsonResponse({"in_licenses": show_in_licenses,
                             'checked_list':checked_list,
                             'licenselist_recommended':compatible_licenses,
                             'compatible_both_list': compatible_both_list,
                             'compatible_secondary_list':compatible_secondary_list,
                             'compatible_combine_list': compatible_combine_list,
                             "files_license_detail": results,
                             "json_list":json_list,
                             "dual_no_checked":dual_no_checked,
                             "conflict_copyleft_list":confilct_copyleft_list,
                             })

# 3、许可证选择工具页__许可证识别__显示进度
def show_progress(request):
    num_progress_2 = round(num_progress,2)
    return JsonResponse(num_progress_2, safe=False)

# 3、许可证选择工具页__许可证识别__遍历文件
def show_files(pathname, files_path):
    file_path = str(pathname.parent) + '\\' + pathname.name
    if pathname.is_file():
        files_path.append(file_path)
    elif pathname.is_dir():
        for cp in pathname.iterdir():
            show_files(cp, files_path)
    return files_path

# 3、许可证选择工具页__许可证识别__文件树标记
file_dir_id = 0
def tree_json(pathname,results, confilct_depend_dict, pi,json_list):
    file_path = str(pathname.parent) + '\\' + pathname.name
    global file_dir_id
    if pathname.is_file():
        file_dir_id += 1
        if file_path in results:
            file_name = pathname.name + '-' * (150 - len(str(pathname.name)) - len(str(results[file_path]))) + str(results[file_path])
        else:
            file_name = pathname.name
        if file_path in confilct_depend_dict.keys():
            json_list.append({"id":file_dir_id,"Pid":pi,"name":file_name,"t":confilct_depend_dict[file_path],"font":{'color':'red'}})
        else:
            json_list.append({"id": file_dir_id, "Pid": pi, "name": file_name,"t":'ok'})
    elif pathname.is_dir():
        file_dir_id += 1
        json_list.append({"id": file_dir_id, "Pid": pi, "name": pathname.name, "open": 'true'})
        pi = file_dir_id
        for cp in pathname.iterdir():
            tree_json(cp,results, confilct_depend_dict, pi,json_list)
    return json_list


# 3、许可证选择工具页__许可证识别__Ninka识别文件
def license_detection_file(one_file,results,in_licenses):
    Other_Licenses = ['SeeFile', 'UNKNOWN']
    try:
        pipe = subprocess.Popen(
            ["perl", BASE_DIR + "\\ninka-tool\\ninka-master\\bin\\ninka.pl", one_file],
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
    return in_licenses,results

# 3、许可证选择工具页__依赖识别
def depend_detection(src_path,temp_path):
    output_depend_path = temp_path + "\\output_depend"
    if os.path.exists(output_depend_path) == False:
        os.makedirs(output_depend_path)
    surport_lang = ["python","java","cpp","ruby","pom"]
    dependencies = {}
    for lang in surport_lang:
        proc = subprocess.Popen(
            "java -jar " + BASE_DIR + "\\depends-tool\\depends-0.9.6-package\\depends-0.9.6\\depends.jar " + "-d=" + output_depend_path + " " + lang + " " + src_path + " " + lang + 'depend')
        proc.communicate()
        proc.wait()
        if os.path.exists(output_depend_path + "\\" + lang + "depend.json"):
            with open(output_depend_path + "\\" + lang + "depend.json", 'r') as f:
                data = json.load(f)
                file_path_list = data['variables']
                dependencies_list = data['cells']
                for one_denpendence in dependencies_list:
                    src_index = one_denpendence['src']
                    dest_index = one_denpendence['dest']
                    src_file = file_path_list[src_index]
                    dest_file = file_path_list[dest_index]
                    dependencies[dest_file] = src_file
    print("依赖识别完成………………")
    return dependencies

# 3、许可证选择工具页__依赖识别__冲突检测
def conflict_dection(file_license_results,dependencies,checked_license_list,unzip_path):
    df1 = pd.read_csv(os.path.join(BASE_DIR, 'csv\compatibility_63.csv'), index_col=0)
    check_license_list = df1.index.tolist()
    confilct_copyleft_set= set()
    confilct_depend_dict = {}
    compatibility_result_ab = ''
    for src_file in dependencies.keys():
        dest_file = dependencies[src_file]
        iscompatibility = 0
        ischeck = 0
        for licenseA in file_license_results[src_file]:
            for licenseB in file_license_results[dest_file]:
                if licenseA in check_license_list and licenseB in check_license_list:
                    ischeck = 1
                    compatibility_result_ab = compatibility_judge(licenseA, licenseB)
                if compatibility_result_ab != '0':
                    iscompatibility = 1
        if iscompatibility == 0 and ischeck == 1:
            confilct_depend_dict[dest_file] = src_file.replace(unzip_path,'')+'的许可证'+licenseA+'不兼容'+dest_file.replace(unzip_path,'')+'的许可证'+licenseB

    for licenseA in checked_license_list:
        for licenseB in checked_license_list:
            if 'or' not in licenseA:
                iscompatibility = 0
                ischeck = 0
                if 'or' not in licenseB:
                    ischeck = 1
                    compatibility_result_ab = compatibility_judge(licenseA, licenseB)
                    compatibility_result_ba = compatibility_judge(licenseB, licenseA)
                    if compatibility_result_ab != '0' or compatibility_result_ba != '0':
                        iscompatibility = 1
                    if iscompatibility == 0 and ischeck == 1:
                        confilct_copyleft_set.add(licenseA + "和" + licenseB + "互不兼容。")
                else:
                    licenseBs = licenseB.split(' or ')
                    for lB in licenseBs:
                        if lB in check_license_list:
                            ischeck = 1
                            compatibility_result_ab = compatibility_judge(licenseA, lB)
                            compatibility_result_ba = compatibility_judge(lB, licenseA)
                            if compatibility_result_ab != '0' or compatibility_result_ba != '0':
                                iscompatibility = 1
                    if iscompatibility == 0 and ischeck == 1:
                        confilct_copyleft_set.add(licenseA + "和" + licenseB + "互不兼容。")
            else:
                iscompatibility == 0
                ischeck = 0
                licenseAs = licenseA.split(' or ')
                if 'or' not in licenseB:
                    for lA in licenseAs:
                        if lA in check_license_list:
                            ischeck = 1
                            compatibility_result_ab = compatibility_judge(lA, licenseB)
                            compatibility_result_ba = compatibility_judge(licenseB, lA)
                            if compatibility_result_ab != '0' or compatibility_result_ba != '0':
                                iscompatibility = 1
                    if iscompatibility == 0 and ischeck == 1:
                        confilct_copyleft_set.add(licenseA + "和" + licenseB + "互不兼容。")
                else:
                    licenseBs = licenseB.split(' or ')
                    for lA in licenseAs:
                        for lB in licenseBs:
                            if lA in check_license_list and lB in check_license_list:
                                ischeck = 1
                                compatibility_result_ab = compatibility_judge(lA, lB)
                                compatibility_result_ba = compatibility_judge(lB, lA)
                                if compatibility_result_ab != '0' or compatibility_result_ba != '0':
                                    iscompatibility = 1
                    if iscompatibility == 0 and ischeck == 1:
                        confilct_copyleft_set.add(licenseA + "和" + licenseB + "互不兼容。")

    print("互不兼容检查完毕")
    return list(confilct_copyleft_set),confilct_depend_dict

# 3、许可证选择工具页__依赖识别__共同目录
def longestCommonDir(fileA,fileB):
    pathname = Path(fileA).parent
    while str(pathname) not in fileB:
        if str(pathname) in fileB:
            break
        pathname = pathname.parent
    return str(pathname)

# 3、许可证选择工具页__许可证识别__兼容许可证筛选
def license_compatibility_filter(in_licenses):
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\license_recommended.csv'))
    all_licenses = df['license'].tolist()
    compatible_licenses = df['license'].tolist()
    compatible_both_list = df['license'].tolist()
    compatible_secondary_list = df['license'].tolist()
    compatible_combine_list = df['license'].tolist()
    df1 = pd.read_csv(os.path.join(BASE_DIR, 'csv\compatibility_63.csv'), index_col=0)
    check_license_list = df1.index.tolist()
    checked_list = []
    dual_no_checked_license = set()
    for licenseA in list(in_licenses):
        if 'or' not in licenseA:
            if licenseA in check_license_list:
                checked_list.append(licenseA)
                for licenseB in all_licenses:
                    compatibility_result = str(df1.loc[licenseA, licenseB])
                    if compatibility_result == '0':
                        if licenseB in compatible_licenses:
                            compatible_licenses.remove(licenseB)
                    if compatibility_result != '1,2':
                        if licenseB in compatible_both_list:
                            compatible_both_list.remove(licenseB)
                    if compatibility_result != '1' and compatibility_result != '1,2':
                        if licenseB in compatible_secondary_list:
                            compatible_secondary_list.remove(licenseB)
                    if compatibility_result != '2' and compatibility_result != '1,2':
                        if licenseB in compatible_combine_list:
                            compatible_combine_list.remove(licenseB)
        else:
            dual_checked = 0
            for licenseB in all_licenses:
                dual_licenses = licenseA.split(' or ')
                is_remove = 1
                is_remove_both = 1
                is_remove_combine = 1
                is_remove_secondary = 1
                for sub_license in dual_licenses:
                    if sub_license in check_license_list:
                        compatibility_result = str(df1.loc[sub_license, licenseB])
                        dual_checked = 1
                    else:
                        dual_no_checked_license.add(sub_license)
                    if compatibility_result != '0':
                        is_remove = 0
                    if compatibility_result == '1,2':
                        is_remove_both = 0
                    if compatibility_result == '1' or compatibility_result == '1,2':
                        is_remove_secondary = 0
                    if compatibility_result == '2' or compatibility_result == '1,2':
                        is_remove_combine = 0
                if is_remove and licenseB in compatible_licenses:
                    compatible_licenses.remove(licenseB)
                if is_remove_both and licenseB in compatible_both_list:
                    compatible_both_list.remove(licenseB)
                if is_remove_secondary and licenseB in compatible_secondary_list:
                    compatible_secondary_list.remove(licenseB)
                if is_remove_combine and licenseB in compatible_combine_list:
                    compatible_combine_list.remove(licenseB)
            if dual_checked == 1:
                checked_list.append(licenseA)
    llist = list(in_licenses)
    llist = sorted(llist)
    if 'Other' in llist:
        llist.append('Other')
        llist.remove('Other')
    return llist, checked_list, compatible_licenses, compatible_both_list, compatible_secondary_list, compatible_combine_list,list(dual_no_checked_license)


# 3、许可证选择工具页__许可证类型推荐
def license_type_choice(request):
    return render(request,
                  'homepage/templates/license-type-choice.html',
                  )

# 3、许可证选择工具页__开源商业模式
def business_model(request):
    business_terms = BusinessModel.objects.all()
    return render(request,
                  'homepage/templates/business_model.html',
                  {'business_terms':business_terms,}
                  )



# 3、许可证选择工具页__交互式条款选择
def license_terms_choice(request):
    question1_val = request.POST.get('question1_val')
    question2_val = request.POST.get('question2_val')
    question3_val = request.POST.get('question3_val')
    question4_val = request.POST.get('question4_val')
    question5_val = request.POST.get('question5_val')
    question6_val = request.POST.get('question6_val')
    question7_val = request.POST.get('question7_val')
    init_licenselist = request.POST.getlist('init_licenselist')
    cur_question = int(request.POST.get('cur_question'))
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\licenses_terms_63.csv'))
    licenses_spdx = df['license'].tolist()
    licenses_copyleft = df['copyleft'].tolist()
    licenses_copyright = df['copyright'].tolist()
    licenses_patent = df['patent'].tolist()
    licenses_patent_term = df['patent_term'].tolist()
    licenses_trademark = df['trademark'].tolist()
    licenses_interaction = df['interaction'].tolist()
    licenses_modification = df['modification'].tolist()
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
                if x == 0 and licenses_copyright[i] != -1:
                    license_ok.append(licenses_spdx[i])
        elif question1_val == '限制型开源许可证':
            for i, x in enumerate(licenses_copyleft):
                if x > 0:
                    license_ok.append(licenses_spdx[i])
        elif question1_val == '公共领域许可证':
            q2_show = 0
            for i, x in enumerate(licenses_copyright):
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
        elif question2_val == '库级__弱限制型开源许可证':
            for i, x in enumerate(licenses_copyleft):
                if x == 2:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_copyleft):
                if x == 3:
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
            for i, x in enumerate(licenses_patent):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        elif question3_val == '明确授予专利权':
            for i, x in enumerate(licenses_patent):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_patent):
                if x == -1:
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
            for i, x in enumerate(licenses_patent_term):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_patent_term):
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
            for i, x in enumerate(licenses_trademark):
                if x == 0:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_trademark):
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
        if question6_val == '网络部署公开源码':
            for i, x in enumerate(licenses_interaction):
                if x == 1:
                    license_ok.append(licenses_spdx[i])
        else:
            for i, x in enumerate(licenses_interaction):
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
        if rr_question_var[i] != None:
            terms_choice.append(rr_question_var[i])


    return JsonResponse({"terms_choice": terms_choice,
                         "licenselist_recommended":licenselist_recommended,
                         "q2_show":q2_show,
                         })


# 3、许可证选择工具页__许可证要素对比
def license_compare(request):
    compare_licenselist = request.POST.getlist('compare_licenselist')
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\licenses_terms_63.csv'))
    df = df.query('license in '+str(compare_licenselist))
    result_list = df.to_dict(orient='records')
    return JsonResponse({"compared_licenselist": result_list,
                         })


# 3、许可证选择工具页__许可证推荐排序
def sort_license(request):
    sort_val = request.POST.get('sort_val')
    if sort_val == 'complex_desc' or sort_val == 'complex_asc':
        df = pd.read_csv(os.path.join(BASE_DIR, 'csv\license_readability.csv'))
        complex_dict = {}
        for _,row in df.iterrows():
            complex_dict[row['license']] = int(row['mean'])
        return JsonResponse({"sort_dict": complex_dict,
                             })
    else:
        df = pd.read_csv(os.path.join(BASE_DIR, 'csv\github_license_usage.csv'))
        popular_dict = {}
        for _, row in df.iterrows():
            popular_dict[row['license']] = int(row['count'])
        return JsonResponse({"sort_dict": popular_dict,
                             })


# 4、许可证使用数据展示页
def license_trend(request):
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\github_repos_removenulllang.csv'))
    github_topics_count = df['topic'].value_counts()
    github_languages_count = df['language'].value_counts()
    github_topics = github_topics_count.index.tolist()
    github_topics_10 = github_topics_count.index[:10].tolist()
    github_languages = github_languages_count.index.tolist()
    github_languages_10 = github_languages_count[:10].index.tolist()
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\license_recommended.csv'))
    recommand_licenses = df['license'].tolist()
    return render(request,
                  'homepage/templates/license-trend.html',
                  {   'github_topics':github_topics,
                      'github_topics_10':github_topics_10,
                      'github_languages':github_languages,
                      'github_languages_10':github_languages_10,
                      "github_licenses":recommand_licenses,
                      })

# 4、许可证使用数据展示页__画图
def draw_trend(request):
    selected_topics = request.POST.getlist('selected_topics')
    selected_languages = request.POST.getlist('selected_languages')
    selected_licenses = request.POST.getlist('selected_licenses')
    minstar = request.POST.get('minstar')
    maxstar = request.POST.get('maxstar')
    df = pd.read_csv(os.path.join(BASE_DIR, 'csv\github_repos_removenulllang.csv'))
    df = df.query('topic in '+str(selected_topics))
    df = df.query('language in '+str(selected_languages))
    if minstar != None and minstar.isdigit():
        df = df[df['stars'] > float(minstar)]
    if maxstar != None and maxstar.isdigit():
        df = df[df['stars'] < float(maxstar)]
    df = df.query('license in '+str(selected_licenses))
    datelist, datalist, distribut_dic = draw_trend_data(df)
    return JsonResponse({"datalist":datalist,
                         "datelist":datelist,
                         "distribut_dict":distribut_dic,
                         })

def draw_trend_data(df):
    datalist = []
    datadict = {}
    df['date'] = pd.to_datetime(df['created_at'])
    df1 = df.groupby([df['date'].dt.year, df['license']])['repo_name'].agg({'count'})
    df2 = df.groupby([df['license']])['repo_name'].agg({'count'})
    datelist = ['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020',
                '2021']
    for i, r in df1.iterrows():
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
    for i, r in df2.iterrows():
        distribut_dic.append([r.name, float(r['count'])])
    return datelist,datalist,distribut_dic
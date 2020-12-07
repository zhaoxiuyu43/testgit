# -*- coding: utf-8 -*-
import re
import os
import chardet

key = ['s0001', 's0002', 's0003', 's0004','s0005', 's0006', 's0007', 's0008','s0009','s0010']
key_2 = ['01', '02', '03', '04', '05', '06','07','08','09','10']
fail = dict([(i, dict([(i, [])for i in key_2]))for i in key])
data_str_name = ('void', 'int', 'short', 'long', 'float', 'double','bool', 'char', 'static', 'enum', 'extern',
                  'int8_t', 'int16_t', 'int32_t', 'int64_t', 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t')
out_str = ('static', 'extern')


def check_show_part(data, i, j, kuo_hao):
    global fail
    for k in range(len(data[i+j])):
        if data[i+j][k] == '{':
            kuo_hao.append('{')
        if data[i + j][k] == '}' and kuo_hao != []:
            kuo_hao.pop()
        elif data[i + j][k] == '}' and kuo_hao == []:
            fail['s0002']['01'].append('函数的大括号数量错误,line:%d到%d' % (i + 1, i + j + 1))
    return fail


def check_show(data, i, kuo_hao):
    global fail
    j = 1
    while j < len(data) - i - 2:
        # 某行不存在{}，j+=1
        if data[i + j].strip(' ').startswith(('//', '/*', '/*')):
            j+=1
            # continue
        if data[i + j].find('{') == -1 and data[i + j].find('}') == -1 and \
                not data[i + j].startswith(data_str_name) and i + j < len(data) - 1:
            if len(data[i+j]) >= 120:
                fail['s0010']['01'].append('按照惯例,每一行代码字符数不超过120,line:%d' % (i + j+ 1))
            j += 1
        if not data[i + j].startswith(data_str_name) and (data[i + j].find('{') != -1 or data[i + j].find('}') != -1)\
            and i + j < len(data) - 1 :
            if len(data[i + j]) >= 120:
                fail['s0010']['01'].append('按照惯例,每一行代码字符数不超过120,line:%d' % (i + j + 1))
            for k in range(len(data[i + j])):
                if data[i + j][k] == '{':
                    kuo_hao.append('{')
                if data[i + j][k] == '}' and kuo_hao != []:
                    kuo_hao.pop()
                elif data[i + j][k] == '}' and kuo_hao == []:
                    fail['s0002']['01'].append('函数的大括号数量错误,line:%d到%d' % (i + 1, i + j+1))
                    return fail
            j += 1
        if data[i + j].startswith(data_str_name) and i + j < len(data) - 1:
            if not kuo_hao == []:
                fail['s0002']['01'].append('函数的大括号数量错误,line:%d到%d' % (i + 1, i + j))
                break
            return fail
        if i + j == len(data) - 1:
            if data[i + j].find('{') == -1 and data[i + j].find('}') == -1:
                return fail
            if data[i + j].find('{') != -1 or data[i + j].find('}') != -1:
                check_show_part(data, i, j, kuo_hao)
                if not kuo_hao == []:
                    fail['s0002']['01'].append('函数的大括号数量错误,line:%d到%d' % (i + 1, i + j))
                    break
                return fail

def test_big_kuohao(data,i):
    if data[i].endswith('{'):
        kuohao = ['{']
        check_show(data, i, kuohao)
    if not data[i].endswith('{'):
        kuohao = []
        check_show(data, i, kuohao)


def test_var_name(name,i):
    global fail
    for j in name:
        if j.find('[') != -1:
            j = re.findall(r'(.*?)\[', j)
            j = ''.join(j)
            test_var_name_part(j,i)
        else:
            test_var_name_part(j,i)

def judian(sstr,i):
    global fail
    for j in range(len(sstr)):
        if sstr[j] == '-' and sstr[j+1] == '>':
            pattern2 = re.findall(r'[\s][-]', sstr[j - 2:j + 3])
            pattern3 = re.findall(r'[>][\s]', sstr[j - 2:j + 3])
            if pattern2 != [] or pattern3 != []:
                fail['s0004']['01'].append('句点或箭头前后不要有空格,line:%d' % (i + 1))
    return fail


def test_judian(data):
    global fail
    for i in range(len(data)):
        if data[i].find('.') != -1 and data[i].find('...') == -1:
            if data[i].find('"') != -1 and re.findall(r'\"(.*?)\.(.*?)\"', data[i]) != []:
                pass
            else:
                pattern0 = re.findall(r'[\s][.]', data[i])
                pattern1 = re.findall(r'[.][\s]', data[i])
                if pattern0 != [] or pattern1 != []:
                    fail['s0004']['01'].append('句点或箭头前后不要有空格,line:%d' % (i + 1))
        if data[i].find('->') != -1:
            judian(data[i], i)
        pattern_san1 = re.compile(r'(\S)\s\?\s(\S)')
        pattern_san2 = re.compile(r'(\S)\s:\s(\S)')
        if data[i].find('?') != -1 and data[i].find(':') != -1:
            if re.search(pattern_san1, data[i]) is None or re.search(pattern_san2, data[i]) is None:
                fail['s0003']['02'].append('三目运算符缺少空格,line:%d' % (i + 1))
    return fail

def if_ink(data,data_kong, i, j):
    global fail
    fill = True
    while fill:
        if data[i + j].startswith(('#', '/*', '*/')):
            j += 1
        if len(data[i + j]) >= 1:
            if data_kong[i + j].index(list(data[i + j])[0]) > data_kong[i].index(list(data[i])[0]):
                j += 1
            elif data_kong[i + j].index(list(data[i + j])[0]) == data_kong[i].index(list(data[i])[0]):
                if data_kong[i + j].find('}') == -1:
                    fail['s0002']['03'].append('if/else/while/for/switch的右大括号缺失,line:%d' % ( i + j))
                    fill = False
                else:
                    if data[i+j] != '}':
                        fail['s0002']['05'].append('if/else/while/for/switch的右大括号应单独一行,line:%d' % (i + j+1))
                    fill = False
            elif data_kong[i + j].index(list(data[i + j])[0]) < data_kong[i].index(list(data[i])[0]):
                fail['s0002']['03'].append('if/else/while/for/switch的右大括号缺失,line:%d' % (i + j))
                fill = False
        else:
            j += 1
    return fail


def test_if_else(data_1,data):
    data_function_str = ('if', 'switch', 'while', 'for','else', '}else')
    pattern = re.compile(r'[if|for|switch|while] \(')
    for i in range(len(data)):
        global fail
        function_str = re.findall('[^|}]\w+', data_1[i])
        if function_str:
            function_str = function_str[0]
            if data_1[i].startswith(data_function_str) and function_str in data_function_str:
                if re.search(pattern,data[i]) is None:
                    fail['s0002']['06'].append('if/while/for/switch等与左圆括号之间一定要有一个空格,line:%d' % (i + 1))
                if data_1[i].find('{') == -1 and data_1[i + 1].find('{') == -1:
                    fail['s0002']['02'].append('if/else/while/for/switch的左大括号缺失,line:%d' % (i + 1))
                    j = 1
                    if_ink(data_1, data, i, j)
                if data_1[i].find('{') == -1 and data_1[i + 1].find('{') != -1:
                    j = 2
                    if_ink(data_1, data, i, j)
                if data_1[i].find('{') != -1:
                    fail['s0002']['04'].append('if/else/while/for/switch的左大括号应单独一行,line:%d' % (i + 1))
                    j = 1
                    if_ink(data_1, data, i, j)
    return fail

def show_note(data_1):
    global fail
    i = 0
    pattern = re.compile(r'http://+(.*?)')
    while i < len(data_1) - 1:
        if data_1[i].startswith(('#include', '//')):
            if data_1[i].startswith('//'):
                if data_1[i].find('/*') != -1 or data_1[i].find('*/') != -1:
                    fail['s0010']['04'].append('注释应统一, 单行注释中不要使用块注释,line:%d' % (i + 1))
            i += 1
        elif data_1[i].startswith('/*'):
            if data_1[i].find('*/') != -1:
                i += 1
            else:
                j = 0
                while True:
                    if data_1[i + j].find('*/') != -1:
                        i = i + j + 1
                        break
                    else:
                        if data_1[i+j].find('//') != -1:
                            fail['s0010']['04'].append('注释应统一, 块注释中不要使用单行注释,line:%d' % (i + j + 1))
                        j += 1
        elif re.search(pattern,data_1[i]) is not None:
            i += 1
        else:
            i += 1


def show_tab(data_df):
    global fail
    data_original = [i.strip(' ') for i in data_df]
    for i in range(len(data_original)):
        if data_original[i].startswith('\t'):
            fail['s0010']['02'].append('使用4个空格缩进，不要在代码中使用制表符，可以设置编辑器将制表符转为空格,line:%d'%(i+1))


def test_var_name_part(j,i):
    global fail
    quen_suo = ('n', 's', 'i', 'j', 'k', 'T', 'id')
    zi_mu = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    key_name = ('auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern','float' ,\
                'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof',' static', 'struct', 'switch', 'typedef',\
                'union', 'unsigned', 'void', 'volatile', 'while', 'inline', 'restrict')
    if len(j) <= 2 and j not in quen_suo:
        fail['s0005']['01'].append('变量名称过短,应该>=3,line:%d'%(i+1))
        # print (j, i)
    if j.islower() is False:
        fail['s0005']['02'].append('变量名不规范,应全为小写,line:%d'%(i+1))
        # print(j, i)
    if j.find('_') == -1 and len(j) > 2:
        jj = j.lower()
        di_zeng = zi_mu[zi_mu.index(jj[0]):zi_mu.index(jj[0])+len(j)]
        di_zeng = ''.join(di_zeng)
        di_jian_part = zi_mu[zi_mu.index(jj[0])-len(j)+1:zi_mu.index(jj[0])+1]
        di_jian_part.reverse()
        di_jian = di_jian_part;di_jian = ''.join(di_jian)
        if jj == di_zeng or jj == di_jian:
            fail['s0005']['03'].append('变量名不规范,不应递增或递减,line:%d'%(i+1))
    dan_ci = re.compile(r'\W+')
    if re.search(dan_ci,j) is not None:
        fail['s0005']['04'].append('变量名不规范,应由下划线连接,line:%d' % (i + 1))
    if j in key_name:
        fail['s0005']['05'].append('变量名不规范,关键字不能作为变量,line:%d' % (i + 1))


def test_file_name(name,i):
    global fail
    file_name = re.findall(r'#include .(.*?)\.',name)
    file_name = ''.join(file_name)
    if file_name.islower() is False:
        fail['s0006']['01'].append('文件名应全部小写,line:%d' % (i+1))
    dan_ci = re.compile(r'\W+')
    if re.search(dan_ci, file_name) is not None:
        fail['s0006']['02'].append('文件名应由下划线连接,line:%d' % (i+1))
    if file_name.startswith('_'):
        fail['s0006']['03'].append('文件名不能以下划线开头,line:%d' % (i + 1))


def test_function_name(name,i):
    global fail
    if name.islower() is False:
        fail['s0007']['01'].append('函数名应全部小写,line:%d' % (i+1))
    dan_ci = re.compile(r'\W+')
    pattern = re.compile(r'^\D(\S+).$')
    if name.endswith(' '):
        fail['s0001']['05'].append('函数名和左圆括号间应没有空格,line:%d' % (i + 1))
    part_name = name.strip(' ')
    if re.search(dan_ci, part_name) is not None:
        fail['s0007']['02'].append('函数名应由下划线连接,line:%d' % (i + 1))
    if re.match(pattern, name) is None:
        fail['s0007']['03'].append('函数名命名不规范,line:%d' % (i + 1))



def test_hong_name(name,i):
    global fail
    file_name = re.findall(r'#define (.*?)[ |(]',name)
    file_name = ''.join(file_name)
    if file_name.isupper() is False:
        fail['s0008']['01'].append('宏命名应全部大写,line:%d' % (i+1))
    dan_ci = re.compile(r'\W+')
    if re.search(dan_ci, file_name) is not None:
        fail['s0008']['02'].append('宏命名应由下划线连接,line:%d' % (i+1))


def test_return_type_part(name):
    return_part = re.findall(r'struct (\S+)', name)
    return_part = ''.join(return_part)
    if len(return_part) >= 1:
        return_type = ''.join(return_part)
        if return_type.endswith('{'):
            return_type = return_type.replace('{','')
        return return_type


def test_return_type_t(name,i):
    global fail
    dan_ci = re.compile(r'\W')
    if re.search(dan_ci, name) is not None:
        fail['s0009']['01'].append('返回类型名应由下划线连接,line:%d' % (i + 1))
    if not name.endswith('_t'):
        fail['s0009']['02'].append('返回类型应由_t结尾,line:%d' % (i + 1))


def test_return_type(data,i):
    if data[i].startswith('struct'):
        return_type = test_return_type_part(data[i])
        if return_type:
            test_return_type_t(return_type, i)
    if data[i].startswith('typedef'):
        return_type = test_return_type_part(data[i])
        if return_type:
            test_return_type_t(return_type, i)
        j = 1
        while True:
            if data[i + j].find('}') == -1:
                j += 1
            else:
                return_type_two = re.findall(r'(\S.*?);',data[i+j])
                return_type_two = [i.strip('}').strip(' ') for i in return_type_two]
                return_type_two = ''.join(return_type_two)
                test_return_type_t(return_type_two, i+j)
                break


def test_can(variable_name,i):
    variable1_name = re.findall(r' ([a-z|*]\S+)[,|)]', variable_name)
    variable2_name = [i.strip('*') for i in variable1_name]
    test_var_name(variable2_name, i)


def test_upper(st3_name,data_num,i):
    st3_name = ''.join(st3_name)
    pattern = re.compile(r'(.*?) ')
    if re.match(pattern, st3_name) is not None:
        st3_name = st3_name.strip(' ').strip('*')
        st4_first_name = re.findall(r' (.\S.*?)[;| =]', data_num)
        if st4_first_name:
            st4_name = st4_first_name[0].strip(' ').strip('*')
            pattern = re.compile(r'\W')
            if re.search(pattern,st4_name) is None:
                test_return_type_t(st3_name,i)
                st5_name = re.findall(r'%s (.\S+), (\S+)[;]' % st3_name, data_num)
                st5_name = [i.strip('*') for i in st5_name]
                if st5_name:
                    st_num = list(st5_name[0])
                else:
                    st_num = [st4_name]
                variable_sum_name = [i.strip(' ').strip('*') for i in st_num]
                test_var_name(variable_sum_name, i)


def test_inside(str_name,i):
    if str_name.find('(') == -1 and str_name.find(')') != -1:
        pass
    else:
        st0_name = re.findall(r' (.\S.*?)[ =|;]', str_name)
        if st0_name:
            variable_name = [st0_name[0].strip(' ').strip('*').strip(';')]
            test_var_name(variable_name, i)


def test_var(var_name,i):
    if var_name.find('(') != -1:
        pass
    else:
        if var_name.find('=') != -1:
            var_num = [var_name.strip('*').split('=')[0]]
            test_var_name(var_num, i)
        else:
            variable_sum_name = [var_name.strip('*')]
            test_var_name(variable_sum_name, i)


def show_name(data,data_1):
    global fail
    for i in range(len(data)):
        global fail
        # 函数定义内部变量
        par = re.findall(r'^(.*?) ',data_1[i])
        partt = ''.join(par)
        if data_1[i].startswith(data_str_name) and partt in data_str_name and data[i].startswith(' '):
            test_inside(data_1[i], i)
        if data_1[i].startswith('struct') and data[i].startswith(' '):
            st1_name = re.findall(r'struct \S+ (.\S+)[ =|;]', data_1[i])
            variable_name = [i.strip('*') for i in st1_name]
            test_var_name(variable_name, i)
        # 返回类型为结构体命名
        st3_name = re.findall(r'(^[A-Z]\S.*?[-| |(|:|.])', data_1[i])
        if st3_name:
            test_upper(st3_name, data_1[i], i)
        if data[i].startswith(data_str_name) and data[i].endswith(';') and not data[i].startswith(out_str):
            var_name = data[i].split(' ')[1].strip(';')
            test_var(var_name, i)
        # 搜索文件名并检测
        if data[i].startswith('#include'):
            test_file_name(data[i], i)
        # 搜索宏名称并检测
        if data[i].startswith('#define'):
            test_hong_name(data[i], i)
        if data[i].startswith(('struct','typedef')):
            test_return_type(data, i)
    return fail
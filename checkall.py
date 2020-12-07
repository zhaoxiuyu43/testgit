# -*- coding: utf-8 -*-
import re
import os
import chardet
import check_name
# 检验函数名称和参数是否存在且形式正确

key = ['s0001', 's0002', 's0003', 's0004','s0005', 's0006', 's0007', 's0008','s0009','s0010']
key_2 = ['01', '02', '03', '04', '05', '06','07','08','09','10']
fail = dict([(i, dict([(i, [])for i in key_2]))for i in key])
data_str_name = ('void', 'int', 'short', 'long', 'float', 'double','bool', 'char', 'static', 'enum', 'extern',
                  'int8_t', 'int16_t', 'int32_t', 'int64_t', 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t')
out_str = ('static', 'extern','const')
full = []

def test_function_kongge(data_str_one,data_str_two,a,b):
    pattern_one = re.compile(r'\(\s')
    pattern_two = re.compile(r'\s\)')
    if re.search(pattern_one, data_str_one) is not None:
        fail['s0001']['07'].append('圆括号与参数间应没有空格,line:%d' % a)
    if re.search(pattern_two, data_str_two) is not None:
        fail['s0001']['07'].append('圆括号与参数间应没有空格,line:%d' % b)


def test_function_kuohao(data,i):
    j = 1
    while j < len(data) - 1:
        if data[i + j] != '}' and not data[i + j].startswith(data_str_name):
            j += 1
        if data[i + j] == '}':
            break
        if data[i + j].startswith(data_str_name) or i + j == len(data) - 1:
            fail['s0001']['08'].append('函数的左大括号和右大括号应单独一行,line:%d' % (i + j))
            break


def xingcan(f,data,i):
    global fail
    if data[i].find('(') != -1 and data[i].find(')') == -1 and data[i + 1].find(')') != -1:
        if data[i+1].endswith('{'):
            fail['s0001']['08'].append('函数的左大括号和右大括号应单独一行,line:%d' % (i + 1))
        test_function_kuohao(data, i+1)
        name_two = re.findall(r'(\S.*?)[)]', data[i + 1])
        if name_two:
            test_function_kongge(data[i], data[i+1], i+1, i+2)
            name_two_first = name_two[0]
            if data[i].index('(') + 1 != f[i + 1].index(list(name_two_first)[0]):
                fail['s0001']['03'].append('形参分行时,所有形参应尽可能对齐,line:%d' % (i + 1))
                fail.update(fail)
    if data[i].find('(') != -1 and data[i].find(')') != -1:
        if data[i].endswith('{'):
            fail['s0001']['08'].append('函数的左大括号和右大括号应单独一行,line:%d' % (i + 1))
        test_function_kuohao(data, i)
        test_function_kongge(data[i], data[i], i + 1, i + 1)


def num(data_s):
    suct_name = []
    bianame = []
    data_part_name = ('struct', 'union', 'static', 'extern','const')
    for i in range(len(data_s)):
        if data_s[i].startswith('typedef'):
            j = 1
            while True:
                if data_s[i + j].find('}') == -1:
                    j += 1
                else:
                    suct_name.append(data_s[i + j])
                    break

        if data_s[i].startswith(data_part_name):
            pattern_9 = re.findall(r'[ ](\w+.)[ ]', data_s[i])
            pattern_9 = ''.join(pattern_9)
            stt_name = re.findall(r'[ ](\w+.)[;|=]', data_s[i])
            stt_name = ''.join(stt_name)
            bianame.append(pattern_9)
            suct_name.append(pattern_9)
            suct_name.append(stt_name)

    suct_name = [i.replace('}','') for i in suct_name]
    suct_name = [i.replace(';','') for i in suct_name]
    return suct_name, bianame


def test_dizhi(data,i):
    global fail
    if data[i].find('&&') != -1:
        fan_1 = re.findall(r' &', data[i])
        fan_2 = re.findall(r'& ', data[i])
        if fan_1 == [] or fan_2 == []:
            fail['s0003']['01'].append('双目运算符缺少空格,line:%d' % (i + 1))

    pattern8 = re.findall(r'(\S.[&].[^\s+])', data[i])
    pattern6 = re.findall(r'(\w+\s[&]\s\S+)', data[i])
    pattern7 = re.findall(r'[&][\s]', data[i])
    pattern8 = [i.strip(' ').split('&') for i in pattern8]
    pattern8 = [i for item in pattern8 for i in item]
    if data[i].find('&&') == -1:
        if pattern6 == [] and pattern7 != []:
            dizhifu = re.findall(r'\w+', pattern8[0])
            dizhifu = ''.join(dizhifu)
            dizhifu1 = re.findall(r'[A-Z]', pattern8[0])
            dizhifu2 = re.findall(r'[A-Z]', pattern8[1])
            dizhifu3 = re.findall(r'.(~|!)', pattern8[1])
            dizhifu4 = re.findall(r'\s\d', pattern8[-1])
            if pattern8[0].find(')') != -1:
                pass
            elif dizhifu == pattern8[0]:
                if dizhifu4 != []:
                    fail['s0004']['03'].append('地址操作符后不要有空格,line:%d' % (i + 1))
                if dizhifu1 != [] or dizhifu2 != [] or dizhifu3 != []:
                    fail['s0003']['01'].append('双目运算符缺少空格,line:%d' % (i + 1))
            elif dizhifu != pattern8[0]:
                fail['s0004']['03'].append('地址操作符后不要有空格,line:%d' % (i + 1))
    return fail


def zhizhen(sstre, i):
    global fail
    pattern = re.findall(r'[*][\s]', sstre)
    if pattern != []:
        fail['s0004']['02'].append('指针后不要有空格,line:%d' % (i + 1))
    return fail


def file(file_full_path, filename):
    global fail
    lis = []
    videos = os.listdir(file_full_path)
    for im_video in videos:
        if im_video in filename:
            filepath = os.path.join(file_full_path,im_video)
            with open(filepath, encoding='utf-8') as f:
                struct_name = []
                data_df = f.readlines()
                data_s = [i.strip('\n\t\r') for i in data_df]
                for i in range(len(data_s)):
                    if data_s[i].startswith(('//','#')):
                        continue
                    if data_s[i].startswith('typedef'):
                        j = 1
                        while True:
                            if data_s[i + j].find('}') == -1:
                                file_name = re.findall(r'(\w+) ', data_s[i+j])
                                if file_name:
                                    lis.extend(file_name)
                                j += 1
                            else:
                                struct_name.append(data_s[i + j])
                                break
                    if not data_s[i].startswith(data_str_name) and data_s[i].endswith(';') \
                            and not data_s[i].startswith('typedef'):
                        file_name = re.findall(r'^\w+[ ]', data_s[i])
                        if file_name:
                            file_name = ''.join(file_name)
                            struct_name.append(file_name)
                struct_name = [i.replace('}','') for i in struct_name]
                struct_name = [i.replace(';','') for i in struct_name]
                lis.extend(struct_name)

    return lis


def canshu_two(data):
    l = []
    for i in range(len(data)):
        global fail
        if data[i].startswith(data_str_name) and data[i].find('(') != -1 and data[i].find(')') != -1:
            function_coffecient = re.findall(r'[(](.*?)[)]', data[i])
            function_canshu = ''.join(function_coffecient)
            function_ss = re.findall(r' (.\w+)', function_canshu)
            if function_ss:
                for j in function_ss:
                    if j.startswith('*'):
                        l.append(j[1:])
                    else:
                        l.append(j)
    return l


def filename(data):
    global fail
    file_j = []
    for i in range(len(data)):
        if data[i].startswith('#include'):
            file_name = re.findall(r'["](.*?)["]', data[i])
            file_name = ''.join(file_name)
            if file_name:
                file_j.append(file_name)
            else:
                pass
    return file_j


def num_str(data_file):
    global fail
    lie = []
    data_str_name = ('struct', 'union', 'enum', 'static', 'extern','int8_t', 'int16_t', 'int32_t','char',
                      'int64_t', 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t','static', 'enum', 'extern')
    for i in range(len(data_file)):
        if data_file[i].startswith(data_str_name) and not data_file[i].endswith(';'):
            st_name = re.findall(r'\(\S+ (.\w+)', data_file[i])
            if st_name:
                st0_name = [i.strip('*') for i in st_name]
                lie.extend(st0_name)
        if data_file[i].startswith(data_str_name) and data_file[i].endswith(';'):
            stt_name = re.findall(r'[ ](.\w+.)[;|=|\[|(]', data_file[i])
            if stt_name:
                stt_name = stt_name[0].strip(' ')
                if stt_name.startswith('*'):
                    lie.append(stt_name[1:])
                else:
                    lie.append(stt_name)
        pattern = re.compile(r'^[A-Z]')
        pattern_oo = re.compile(r'\W')
        oo = data_file[i].split(' ')[0]
        if re.match(pattern,data_file[i]) is not None or oo.endswith('_t'):
            if oo not in data_str_name and re.search(pattern_oo,oo) is None:
                function_ss = re.findall(r' (.\w+)', data_file[i])[0].strip('*')
                lie.append(function_ss)
    return lie


def canshu(data):
    l = []
    g = []
    for i in range(len(data)):
        global fail
        if data[i].startswith(data_str_name) and data[i].find('(') != -1 and data[i].find(')') != -1:
            function_coffecient = re.findall(r'[(](.*?)[)]', data[i])
            function_canshu = ''.join(function_coffecient)
            function_ss = re.findall(r' (.\w+)', function_canshu)
            l.extend(function_ss)
            for j in l:
                if j.startswith('*'):
                    g.append(j[1:])
                else:
                    g.append(j)

    return g


def struct_part(data,data_file):
    global fail
    number_one = ['void', 'int', 'char', 'short', 'long', 'float', 'double','sizeof',
                  'int8_t', 'int16_t', 'int32_t', 'int64_t', 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t']
    filepath_01 = r'D:\zhaoxiuyu\桌面\aa'
    file_name = filename(data_file)
    number_two = file(filepath_01,file_name)
    number_two = list(filter(None,number_two))
    number_two = [number_two[i].strip(' ') for i in range(len(number_two))]
    number_str = number_two+number_one
    number_strsum = tuple(number_str)
    lie = num_str(data_file)
    lie_two = canshu_two(data)
    lie_two = list(filter(None,lie_two))
    lie_three = canshu(data)
    lie_three = [i.strip() for i in lie_three]
    lie = lie + number_str + lie_two + lie_three
    lie = [i.strip() for i in lie]
    for i in range(len(data_file)):
        if data_file[i].startswith(('//', '/*', '#')):
            continue
        if data_file[i].find('&') != -1 and data_file[i].find('&&') == -1 \
                and not data_file[i].startswith(('if','else if')):
            st_name = re.findall(r'[&](\D\w+)', data_file[i])
            st_name = [i.strip(' ') for i in st_name]
            pattern = re.compile(r'\d|\W')
            pattern_two = re.compile(r'^[A-Z]')
            pattern_three = re.compile(r'\W')
            for j in range(len(st_name)):
                if st_name[j] not in lie and re.search(pattern,st_name[j]) is None and st_name != [] \
                        and re.search(pattern_two,st_name[j]) is None:
                    fail['s0004']['04'].append('指针或地址后需跟函数或变量名,line:%d' % (i + 1))
    return lie,number_strsum


def shuangmu(data_sql,i,m):
    global fail
    pattern_1 = re.findall(r'[,][.*]', data_sql)
    pattern_2 = re.findall(r'[(][.*]', data_sql)
    pattern_4 = re.findall(r'[*][)]', data_sql)
    if pattern_1 != [] or pattern_2 != [] or pattern_4 != []:
        pattern = re.findall(r'[*][\s]', data_sql)
        if pattern != []:
            fail['s0004']['02'].append('指针后不要有空格,line:%d' % (i + m + 1))

    if pattern_1 == [] and pattern_2 == [] and pattern_4 == []:
        if data_sql.find('sizeof') == -1:
            pattern_01 = re.findall(r'[*][\s]', data_sql)
            pattern_02 = re.findall(r'[\s][*]', data_sql)
            if pattern_01 == [] or pattern_02 == []:
                fail['s0003']['01'].append('双目运算符缺少空格,line:%d' % (i + m + 1))
    return fail


def test_zhizhen(data,i,sts):
    global fail
    m = 1
    # 按行查询指针空格情况
    while m < len(data) - i - 1:
        if data[i + m].find('*') == -1 and data[i + m] != '}':
            m += 1
        if data[i + m].find('/*') != -1 or data[i + m].find('*/') != -1 or data[i + m].find('//') != -1:
            m += 1
        if data[i + m] == '}' or data[i + m].startswith(sts):
            break
        if data[i + m].find('*') != -1 and data[i + m].find('=') == -1:
            data_sql = data[i + m].strip(' ')
            data_se = re.findall(r'(\w+.\*.)', data_sql)
            data_se = ''.join(data_se)
            pattern_1 = re.findall(r'[*][\s]', data_se)
            if data_se.startswith(sts) or data_se.endswith(')'):
                if pattern_1 != []:
                    fail['s0004']['02'].append('指针后不要有空格,line:%d' % (i + m + 1))
                    continue
            else:
                shuangmu(data_sql, i, m)
            m += 1
        if data[i + m].find('*') != -1 and data[i + m].find('=') != -1:
            data_spl = data[i + m].split('=')
            data_spl = [i.strip(' ') for i in data_spl]
            pattern = re.compile(r'[A-Z]')
            if data_spl[0].find('*') != -1:
                pattern_1 = re.findall(r'[*][\s]', data_spl[0])
                pattern_2 = re.findall(r'[\s][*]', data_spl[0])
                if data_spl[0].startswith(sts) and pattern_1 != []:
                    fail['s0004']['02'].append('指针后不要有空格,line:%d' % (i + m + 1))
                elif re.match(pattern,data_spl[0]) is not None and pattern_1 != []:
                    fail['s0004']['02'].append('指针后不要有空格,line:%d' % (i + m + 1))
                if data_spl[0].startswith('*') and pattern_1 != []:
                    fail['s0004']['02'].append('指针后不要有空格,line:%d' % (i + m + 1))
                if re.match(pattern,data_spl[0]) is None and pattern_2 == [] and not data_spl[0].startswith(sts) \
                        and not data_spl[0].startswith('*') and data_spl[0].find('(*') == -1:
                    fail['s0003']['01'].append('双目运算符缺少空格,line:%d' % (i + m + 1))
            if data_spl[-1].find('*') != -1:
                if data_spl[-1].startswith('*'):
                    pattern_1 = re.findall(r'[*][\s]', data_spl[-1])
                    if pattern_1 != []:
                        fail['s0004']['02'].append('指针后不要有空格,line:%d' % (i + m + 1))
                        break
                else:
                    shuangmu(data_spl[-1], i, m)
            m += 1
    return fail


def struct_show(data, data_file):
    global fail
    number_one = ['void', 'int', 'char', 'short', 'long', 'float', 'double', 'sizeof','extern','static',
                  'int8_t', 'int16_t', 'int32_t', 'int64_t', 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t']
    sp, s_part = num(data)
    data_full, bian_name = struct_part(data,data_file)
    s_part.append(bian_name)
    sp.extend(data_full); sp.extend(number_one)
    sp = list(filter(None, sp))
    sp = set(sp); sts = tuple(sp)
    # hi = xingc(data)
    # ts(data,hi)
    fu_hao = ( '+', '-', '/','+=', '-=', '/=', '*=', '<<=', '>>+', '|=', '^=', '<', '>','|=',
               '<=', '>=', '!=', '||', '!', '^', '<<', '>>')
    for i in range(len(data)):
        if data[i].find('//') != -1 or data[i].find('/*') != -1 or data[i].find('*/') != -1 or data[i].find('#') != -1:
            continue
        for j in fu_hao:
            pattern = re.compile(r'[ ]+(\W+)[ ]')
            pattern1 = re.compile(r'(\S)+[\+\+]|[--]+[;|)]')
            pattern2 = re.compile(r'[~]|[!](\w+)')
            pattern3 = re.compile(r'\-\d+')
            pattern4 = re.findall(r'"(.*?)"',data[i])
            if data[i].find('->') != -1 or data[i].find('*') != -1 or data[i].find('&') != -1:
                continue
            if data[i].find(j) != -1 and data[i].find('---') == -1:
                if re.search(pattern1, data[i]) is not None or re.search(pattern2, data[i]) is not None or re.search(pattern3, data[i]) is not None:
                    continue
                elif re.search(pattern, data[i][data[i].index(j) - 1:data[i].index(j) + 3]) is None:
                    if pattern4:
                        if data[i][data[i].index(j) - 1:data[i].index(j) + 1] not in pattern4[0]:
                            fail['s0003']['01'].append('双目运算符缺少空格,line:%d' % (i + 1))
                            break
                    else:
                        fail['s0003']['01'].append('双目运算符缺少空格,line:%d' % (i + 1))
                        break
        # 地址运算符&
        if data[i].find('&') != -1:
            test_dizhi(data,i)
        # 查询函数定义首行的指针空格情况
        if data[i].startswith(sts) and not data[i].endswith(';') and data[i].find('(') != -1 and data[i].find('/*') == -1:
            if data[i].find('*') != -1:
                zhizhen(data[i], i)
            test_zhizhen(data, i, sts)
        # 查询函数声明的指针情况
        if data[i].startswith(sts) and data[i].endswith(';'):
            zhizhen(data[i], i)
        if data[i].startswith(('typedef', 'struct')) and not data[i].endswith(';'):
            j = 1
            while True:
                if data[i + j].find('*') == -1 or data[i + j].find('}') == -1 or data[i+j].find('/*') != -1:
                    j += 1
                if data[i + j].find('*') != -1 and data[i+j].find('/*')  == -1:
                    pattern = re.findall(r'[*][\s]', data[i + j])
                    if pattern != []:
                        fail['s0004']['02'].append('指针后不要有空格,line:%d' % (i + j + 1))
                        break
                if data[i + j].find('}') != -1:
                    break


def test_fenhang(data,data_1,i,j,a):
    if data[i + j].find(')') != -1:
        data_sum = data_1[a:i + j + 1]
        data_sum = [data[i]] + [''.join(data_sum)]
        data_full = ' '.join(data_sum)
        sum_name_first(data_full, i + 1)
    else:
        data_sum = data_1[a:i + j + 2]
        data_sum = [data[i]] + [''.join(data_sum)]
        data_full = ' '.join(data_sum)
        sum_name_first(data_full, i + 1)
    return data_full


def test_suojin(data_str,i):
    if data_str.index('(') != 0:
        fail['s0001']['09'].append('如果返回类型与函数声明或定义分行了,不要缩进,line:%d' % (i + 1))


def sum_name_first(data_str,i):
    variable_name = re.findall(r'\((.*?\))', data_str)
    variable_name = ''.join(variable_name)
    function_name = re.findall(r' (\S+.)\(', data_str)
    function_name = [i.strip('*') for i in function_name]
    function_name = ''.join(function_name)
    check_name.test_function_name(function_name, i)
    if variable_name:
        check_name.test_can(variable_name, i)


def test_normal_part(data,data_1,data_df,i,k):
    global full
    if len(data[i].split(' ')) == k:
        fail['s0001']['01'].append('返回类型和函数名不在同一行,line:%d' % (i + 1))
        if data[i + 1].find('(') == -1:
            test_suojin(data[i + 2], i + 2)
            xingcan(data_df, data, i + 2)
            fail['s0001']['06'].append('左圆括号应和函数名在同一行,line:%d' % (i + 2))
            full_part = test_fenhang(data, data_1, i, 2, i+1)
            full.append(full_part)
        else:
            xingcan(data_df, data, i + 1)
            full_part = test_fenhang(data, data_1, i, 1, i+1)
            full.append(full_part)
    # 检验左圆括号是否与函数名称在同一行
    if len(data[i].split(' ')) > k and data[i].find('(') == -1 and data[i].find(')') == -1 and data[i + 1].find('(') != -1:
        fail['s0001']['06'].append('左圆括号应和函数名在同一行,line:%d' % (i + 1))
        test_suojin(data[i + 1], i + 1)
        xingcan(data_df, data, i + 1)
        full_part = test_fenhang(data, data_1, i, 1, i)
        full.append(full_part)
    # 检验形参分行
    if len(data[i].split(' ')) > k and data[i].find('(') != -1 and not data[i].endswith(';'):
        if len(data[i]) > 120:
            fail['s0001']['02'].append('如果返回类型和函数名在一行放不下超过120个字符,分行,line:%d' % (i + 1))
        if data[i].find(')') != -1:
            sum_name_first(data[i], i)
            full.append(data[i])
        if data[i].find(')') == -1 and data[i + 1].find(')') != -1:
            data_sum_part = data[i] + data_1[i + 1]
            full.append(data_sum_part)
            sum_name_first(data_sum_part, i)
        xingcan(data_df, data, i)
        # 检验函数大括号数量是否正确
    check_name.test_big_kuohao(data, i)

def full_short_xingcan():
    global fail
    global full
    hi = {}
    for i in full:
        func_part = i.split('(')
        function_name = re.findall(r' (\S+.)$', func_part[0])
        function_name = ''.join(function_name)
        func_cofficient = re.findall(r'(.*?)\)', func_part[1])
        if func_cofficient == ['']:
            hi[function_name] = 0
        func_cofficient = ''.join(func_cofficient)
        if func_cofficient.find('void')  != -1:
            hi[function_name] = func_cofficient.count(',') + 1 - func_cofficient.count('void')
        if func_cofficient.find('=') != -1:
            lst = []
            first = func_cofficient.count(',') + 1 - func_cofficient.count('=')
            two = func_cofficient.count(',') + 1
            lst.append(first)
            lst.append(two)
            hi[function_name] = lst
        if func_cofficient != '' and func_cofficient.find('void')  == -1 and func_cofficient.find('=') == -1:
            hi[function_name] = func_cofficient.count(',') + 1
    return hi


def test_short_coff_part(data,i,hi,p):
    functi_name = re.findall(r'(%s)[;|)|(]' % p, data[i])
    if functi_name:
        func_cofficient = re.findall(r'%s\((.*?)\)'%p, data[i])
        func_cofficient = ''.join(func_cofficient)
        if func_cofficient == ')' or len(func_cofficient) == 0:
            if isinstance(hi[p], int):
                if hi[p] >= 1:
                    fail['s0001']['04'].append('缺少形参错误,line:%d' % (i + 1))
            if isinstance(hi[p], list):
                j = min(hi[p])
                if j >= 1:
                    fail['s0001']['04'].append('缺少形参错误,line:%d' % (i + 1))
        if func_cofficient != ')' and len(func_cofficient) >= 1:
            if isinstance(hi[p], int):
                if func_cofficient.count(',') + 1 != hi[p]:
                    fail['s0001']['04'].append('缺少形参错误,line:%d' % (i + 1))
            if isinstance(hi[p], list):
                if func_cofficient.count(',') + 1 not in hi[p]:
                    fail['s0001']['04'].append('缺少形参错误,line:%d' % (i + 1))



def test_short_cofficient(data,hi):
    for i in range(len(data)):
        for p,q in hi.items():
            if data[i].find(p) != -1 and data[i].startswith(' ') and data[i].find('//') ==-1 \
                    and data[i].find('/*') ==-1:
                drop_fucntion = re.findall(r'"(.*?)"',data[i])
                drop_fucntion = ''.join(drop_fucntion)
                if p not in drop_fucntion:
                    test_short_coff_part(data, i, hi, p)


def show(file_full_path):
    global fail
    with open(file_full_path, encoding='utf-8') as f:
        encoding_full = chardet.detect(open(file_full_path, 'rb').read())['encoding']
        if encoding_full != 'utf-8':
            fail['s0010']['03'].append('文本编码统一为UTF-8,避免乱码')
        data_df = f.readlines()
        data_1 = [i.strip('\n\t\r ') for i in data_df]
        data = [i.strip('\n\t\r') for i in data_df]
        check_name.show_note(data_1)
        check_name.show_tab(data_df)
        fail = check_name.show_name(data, data_1)
        fail.update()
        paee = re.compile('^[A-Z].*?')
        # c语言数据类型
        for i in range(len(data)):
            if data[i].find('//') != -1 or data[i].find('/*') != -1 or data[i].find('*/') != -1:
                continue
            #  检验函数类型和函数名是否在同一行
            if data[i].startswith(data_str_name) or re.match(paee,data[i]) is not None:
                if not data[i].endswith(';') and not data[i].startswith(out_str):
                    test_normal_part(data, data_1, data_df, i, 1)
            if data[i].startswith(out_str) and not data[i].endswith(';'):
                test_normal_part(data, data_1, data_df, i, 2)
        # if/else/while/for/switch等必须都包含一对大括号，与左圆括号之间有空格
        check_name.test_if_else(data_1, data)
        # 确定点和句点 的空格情况
        check_name.test_judian(data)
        # 赋值符号,双目或者三目运算符前后都要有一个空格
        struct_show(data, data_1)
        hi = full_short_xingcan()
        test_short_cofficient(data,hi)
        return fail


def xunhuan(file_full_path):
    videos = os.listdir(file_full_path)
    listaa = []
    for im_video in videos:
        if im_video.endswith('.c'):
            filepath = os.path.join(file_full_path, im_video)
            listaa.append(filepath)
    return listaa


def spae(c_show):
    for i, v in c_show.items():
        print(i)
        for n, m in v.items():
            if len(m) >= 2:
                first = m.pop(0)
                last = []
                last.append(first)
                for k in range(len(m)):
                    num = re.findall(r'[:](.*)', m[k])
                    num = ''.join(num)
                    last.append(num)
                last = ','.join(last)
                print(n + '\t' + last)
                m.insert(0, first)
            else:
                for r in m:
                    print(n + '\t' + r)


if __name__ == '__main__':
    filepath = r'D:\zhaoxiuyu\桌面\aa\ds_adapter.c'
    c_show = show(filepath)
    spae(c_show)





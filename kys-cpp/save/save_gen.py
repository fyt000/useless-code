import yaml


def indent(num, s):
    return num*4*' ' + s

def type_decl(t, eng, chn, size = 0):
    if t == 0:
        return 'int {0}; // {1}'.format(eng, chn)
    elif t == 1:
        return 'char {0}[{1}]; // {2}'.format(eng, size, chn)
    elif t == 2:
        return 'int {0}[{1}]; // {2}'.format(eng, size, chn)

def gen_struct_h(root_node):
    result = []
    result.append('#pragma once')
    # result.append('#include "yaml-cpp\\yaml.h"')
    
    result.append('')

    for ynode in root_node['数据描述']:
        result.append('// {0}'.format(ynode['数据类型'][1]))
        result.append('struct {0} {{'.format(ynode['数据类型'][0]))
        for item in ynode['字段']:
            item_type = item.get('类型', 0)
            size = item.get('长度', 0)
            result.append(indent(1, type_decl(item_type, item['描述'][0], item['描述'][1], size)))
        result.append('')

        result.append('};')
    
    result.append('class NewSave {')
    result.append('public:')
    for ynode in root_node['数据描述']:
        type_name_eng = ynode['数据类型'][0]
        type_name_chn = ynode['数据类型'][1]
        result.append('// {0}'.format(type_name_chn))
        if '扩展类' in ynode:
            extended_type = ynode['扩展类']
            result.append('static void Save::NewSave::SaveToCSV{0} (const std::vector<{1}>& data, int record);'.format(type_name_eng, extended_type))
        else:
            result.append('static void Save::NewSave::SaveToCSV{0} ({1}* data, int length, int record);'.format(type_name_eng, type_name_eng))
        if '扩展类' in ynode:
            extended_type = ynode['扩展类']
            result.append('static void Save::NewSave::LoadFromCSV{0} (std::vector<{1}>& data, int record);'.format(type_name_eng, extended_type))
        else:
            result.append('static void Save::NewSave::LoadFromCSV{0} ({1}* data, int length, int record);'.format(type_name_eng, type_name_eng))
        if '扩展类' in ynode:
            result.append('static void Save::NewSave::Insert{0}At(std::vector<{0}>& data, int idx);'.format(ynode["扩展类"]))
    result.append('};')
    
    return result

def get_full_field_names(item, lang = 1):
    item_len = item.get('长度', 0)
    item_type = item.get('类型', 0)
    field = item['描述'][lang]
    result = []
    if item_len == 0 or item_type == 1:
        result.append(field)
    else:
        for i in range(item_len):
            if lang == 1:
                result.append('{0}{1}'.format(field, i + 1))
            else:
                result.append('{0}[{1}]'.format(field, i))
    return result


def gen_save_function(root_node):
    result = []
    # result.append('#include "NewSave.h"')
    # result.append('#include <fstream>')
    for ynode in root_node['数据描述']:
        type_name_eng = ynode['数据类型'][0]
        type_name_chn = ynode['数据类型'][1]
        result.append('// {0}'.format(type_name_chn))
        # 这里用arr+length是因为有基础物品200这个愚蠢的设计
        if '扩展类' in ynode:
            extended_type = ynode['扩展类']
            result.append('void Save::NewSave::SaveToCSV{0} (const std::vector<{1}>& data, int record) {{'.format(type_name_eng, extended_type))
        else:
            result.append('void Save::NewSave::SaveToCSV{0} ({1}* data, int length, int record) {{'.format(type_name_eng, type_name_eng))
        result.append(indent(1,'std::ofstream fout("../game/save/csv/" + std::to_string(record) + "_{0}.csv");'.format(type_name_chn)))

        # 还是可以有空格的
        sub_result = []
        total_fields = len(ynode['字段'])
        for item in ynode['字段']:
            item_len = item.get('长度', 0)
            item_type = item.get('类型', 0)
            field_eng = item['描述'][0]
            all_fields = get_full_field_names(item)
            
            for field_real_chn in all_fields:
                sub_result.append(indent(1, 'fout << \"{0}\";'.format(field_real_chn))) 
        result.append('\n    fout << ",";'.join(sub_result))
            

        result.append(indent(1, 'fout << std::endl;'))
        
        # 输出单个
        fields = 0
        if '扩展类' in ynode:
            result.append(indent(1, 'int length = data.size();'))
        result.append(indent(1, 'for (int i = 0; i < length; i++) {'))
        for item in ynode['字段']:
            item_len = item.get('长度', 0)
            item_type = item.get('类型', 0)
            field_eng = item['描述'][0]
            field_chn = item['描述'][1]
            if item_len == 0 or item_type == 1:
                # 整数直接输出，字符串""
                if item_type == 0:
                    result.append(indent(2, 'fout << data[i].{0};'.format(field_eng)))
                else:
                    result.append(indent(2, 'fout << \'"\' << data[i].{0} << \'"\';'.format(field_eng)))
            else:
                result.append(indent(2, 'for (int j = 0; j < {0}; j++) {{').format(item_len))
                result.append(indent(3, 'fout << data[i].{0}[j];'.format(field_eng)))
                result.append(indent(3, 'if (j != {0} - 1) fout << ",";'.format(item_len)))
                result.append(indent(2, '}'))
            if fields !=  total_fields - 1:
                result.append(indent(2, 'fout << ",";')) 
            fields += 1
        result.append(indent(2, 'fout << std::endl;'))
        result.append(indent(1, '}'))
        result.append('}')
    return result

def gen_load_function(root_node):
    result = []
    for ynode in root_node['数据描述']:
        type_name_eng = ynode['数据类型'][0]
        type_name_chn = ynode['数据类型'][1]
        result.append('// {0}'.format(type_name_chn))
        new_type = type_name_eng
        if '扩展类' in ynode:
            extended_type = ynode['扩展类']
            new_type = extended_type
            result.append('void Save::NewSave::LoadFromCSV{0} (std::vector<{1}>& data, int record) {{'.format(type_name_eng, extended_type))
        else:
            result.append('void Save::NewSave::LoadFromCSV{0} ({1}* data, int length, int record) {{'.format(type_name_eng, type_name_eng))

        if '扩展类' in ynode:
            result.append(indent(1, "data.clear();"))

        all_fields = []
        for item in ynode['字段']:
            fields = get_full_field_names(item)
            fields = [ '"{0}"'.format(x) for x in fields ]
            all_fields.extend(fields)
        col_names = ',\n        '.join(all_fields)

        length = len(all_fields)

        result.append(indent(1, 'io::CSVReader<{0}, io::trim_chars<' '>, io::double_quote_escape<\',\',\'\\\"\'>> in("../game/save/csv/" + std::to_string(record) + "_{1}.csv");'.format(length, type_name_chn)))

        # 无视多余和缺省的 ignore_missing_column | ignore_extra_column
        result.append(indent(1, 'in.read_header(io::ignore_missing_column | io::ignore_extra_column, '))
        result.append(indent(2, col_names))
        result.append(indent(1, ');'))
        result.append(indent(1, 'auto getDefault = []() {'))
        result.append(indent(2, '{0} nextLineData;'.format(new_type)))

        for item in ynode['字段']:
            item_len = item.get('长度', 0)
            item_type = item.get('类型', 0)
            field_eng = item['描述'][0]
            if item_len == 0 or item_type == 1:
                if item_type == 0:
                    default_val = item.get('默认', 0)
                    result.append(indent(2, 'nextLineData.{0} = {1};'.format(field_eng, default_val)))
                else:
                    result.append(indent(2, 'memset(nextLineData.{0}, \'\\0\', sizeof(nextLineData.{1}));'.format(field_eng, field_eng)))
            else:
                default_val = item.get('默认', 0)
                result.append(indent(2, 'for (int j = 0; j < {0}; j++) {{').format(item_len))
                result.append(indent(3, 'nextLineData.{0}[j] = {1};'.format(field_eng, default_val)))
                result.append(indent(2, '}'))
        result.append(indent(2, 'return nextLineData;'))
        result.append(indent(1, '};'))


        # 这里所有字符串因为是char x[y]，所以必须给额外的char*来读取指针
        # 因为我要兼容机器猫的原结构，这里操作不能用std::string很让人捉急
        str_ptr = set()
        for item in ynode['字段']:
            item_len = item.get('长度', 0)
            item_type = item.get('类型', 0)
            field_eng = item['描述'][0]
            if item_type == 1:
                str_ptr.add(field_eng)
                result.append(indent(1, 'char * {0}__;'.format(field_eng)))

        result.append(indent(1, 'int lines = 0;'))
        result.append(indent(1, 'auto nextLineData = getDefault();'))
        result.append(indent(1, 'while(in.read_row('))

        all_fields = []
        for item in ynode['字段']:
            fields = get_full_field_names(item, 0)
            all_fields.extend(fields)

        all_fields = [ 'nextLineData.{0}'.format(x) if not (x in str_ptr) else '{0}__'.format(x) for x in all_fields ]
        col_names = ',\n        '.join(all_fields)
        result.append(indent(2, col_names))
        result.append(indent(1, ')) {'))
        # 复制回来，令人窒息的操作
        for str_name in str_ptr:
            # 我已经保证'\0'结尾，现在长度-1即可
            result.append(indent(2, "strncpy(nextLineData.{0}, {0}__, sizeof(nextLineData.{0})-1);".format(str_name)))
        if '扩展类' in ynode:
            result.append(indent(2, "data.push_back(nextLineData);"))
        else:
            result.append(indent(2, "data[lines] = nextLineData;"))
            result.append(indent(2, "if (lines + 1 == length) break;"))
        result.append(indent(2, 'lines++;'))
        result.append(indent(2, 'nextLineData = getDefault();'))
        result.append(indent(1, '}'))     
        result.append('}')
    return result

def depending_items_graph(root_node):
    # 先生成图
    G = {}
    for ynode in root_node['数据描述']:
        type_name = ynode['数据类型'][1]
        for item in ynode['字段']:
            if '引用' in item:
                item_type = item.get('类型', 0)
                item_len = item.get('长度', 0)
                if item_type == 2:
                    for i in range(item_len):
                        G.setdefault(item['引用'], {}).setdefault(type_name, []).append('{0}[{1}]'.format(item["描述"][0], i))
                else:
                    G.setdefault(item['引用'], {}).setdefault(type_name, []).append(item["描述"][0])
    return G


# 这个函数 硬着写的，因为很难搞
def get_all_vec_func_name(dtype):
    if dtype == '人物':
        return 'Save::getInstance()->getRoles()'
    elif dtype == '基本':
        # 这个怎么搞得出来，手写
        return 'Save::getInstance()'
    elif dtype == '背包':
        # 这个更是不可能，手写
        return 'Save::getInstance()->Items'
    elif dtype == '物品':
        return 'Save::getInstance()->getItems()'
    elif dtype == '武功':
        return 'Save::getInstance()->getMagics()'
    elif dtype == '场景':
        return 'Save::getInstance()->getSubMapInfoSaves()'
    elif dtype == '商店':
        return 'Save::getInstance()->getShops()'

def gen_insert_function(root_node):
    result = []
    # 仅支持 有扩展类的 （即vector搞出来的）
    G = depending_items_graph(root_node)
    print(G)
    for ynode in root_node['数据描述']:
        type_name = ynode['数据类型'][1]
        if '扩展类' in ynode:
            result.append('void Save::NewSave::Insert{0}At(std::vector<{0}>& data, int idx) {{'.format(ynode["扩展类"]))
            result.append(indent(1, 'auto newCopy = data[idx];'))
            result.append(indent(1, 'data.insert(data.begin() + idx, newCopy);'))
            result.append(indent(1, 'for (int i = 0; i < data.size(); i++) {'))
            result.append(indent(2, 'data[i].ID = i;'))
            result.append(indent(1, '}'))
            result.append(indent(1, 'Save::getInstance()->updateAllPtrVector();'))
            for dependency_type, fields in G.setdefault(type_name, {}).items():
                # 获取所有基于他的数据类型
                result.append(indent(1, 'for (auto& p : {0}) {{'.format(get_all_vec_func_name(dependency_type))))
                # 所有相关字段
                for update in fields:
                    result.append(indent(2, 'if (p->{0} >= idx) p->{0} += 1;'.format(update)))
                result.append(indent(1, '}'))
            
            result.append('}')
    return result
                    



with open('saveconfig.yaml', encoding='utf-8') as fp:
    saveconfig = yaml.load(fp)

with open('NewSaveGenerated.h', 'w', encoding='gbk') as gen:
    gen.write('\n'.join(gen_struct_h(saveconfig)))

with open('NewSaveGenerated.cpp', 'w', encoding='gbk') as gen:
    gen.write('\n'.join(gen_save_function(saveconfig)))
    gen.write('\n')
    gen.write('\n'.join(gen_load_function(saveconfig)))
    gen.write('\n')
    gen.write('\n'.join(gen_insert_function(saveconfig)))



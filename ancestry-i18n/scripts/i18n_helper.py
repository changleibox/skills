#!/usr/bin/env python3
"""
Ancestry项目国际化处理辅助脚本
用于识别中文字符串、生成键名、更新ARB文件等核心功能
"""

import re
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import hashlib

class TranslationService:
    """翻译服务"""
    
    def __init__(self):
        # 常见业务术语的精确翻译映射
        self.business_translations = {
            # 账户相关
            "登录": "Login",
            "注册": "Register",
            "注销": "Logout",
            "账户": "Account",
            "用户名": "Username",
            "密码": "Password",
            "验证码": "Verification Code",
            "手机号": "Phone Number",
            "邮箱": "Email",
            
            # 单据相关
            "单据": "Document",
            "订单": "Order",
            "销售单": "Sales Order",
            "采购单": "Purchase Order",
            "退货单": "Return Order",
            "入库单": "Stock In",
            "出库单": "Stock Out",
            "盘点单": "Inventory Check",
            
            # 商品相关
            "商品": "Product",
            "货物": "Goods",
            "库存": "Inventory",
            "价格": "Price",
            "数量": "Quantity",
            "单位": "Unit",
            "规格": "Specification",
            
            # 客户供应商
            "客户": "Customer",
            "供应商": "Supplier",
            "联系人": "Contact",
            "地址": "Address",
            "电话": "Phone",
            
            # 报表统计
            "报表": "Report",
            "统计": "Statistics",
            "分析": "Analysis",
            "图表": "Chart",
            "数据": "Data",
            "记录": "Record",
            
            # 系统操作
            "保存": "Save",
            "删除": "Delete",
            "编辑": "Edit",
            "新建": "New",
            "搜索": "Search",
            "查询": "Query",
            "刷新": "Refresh",
            "导出": "Export",
            "打印": "Print",
            "取消": "Cancel",
            "确定": "Confirm",
            "提交": "Submit",
            "审核": "Review",
            "发布": "Publish",
            
            # 状态提示
            "成功": "Success",
            "失败": "Failed",
            "错误": "Error",
            "警告": "Warning",
            "提示": "Notice",
            "加载中": "Loading",
            "处理中": "Processing",
            "暂无数据": "No Data Available",
            
            # 通用词汇
            "系统": "System",
            "设置": "Settings",
            "配置": "Configuration",
            "管理": "Management",
            "中心": "Center",
            "首页": "Home",
            "个人": "Personal",
            "消息": "Message",
            "通知": "Notification",
            "帮助": "Help",
            "关于": "About"
        }
        
        # 月份和星期的翻译
        self.time_translations = {
            "一月": "January", "二月": "February", "三月": "March",
            "四月": "April", "五月": "May", "六月": "June",
            "七月": "July", "八月": "August", "九月": "September",
            "十月": "October", "十一月": "November", "十二月": "December",
            "周一": "Monday", "周二": "Tuesday", "周三": "Wednesday",
            "周四": "Thursday", "周五": "Friday", "周六": "Saturday", "周日": "Sunday"
        }
    
    def translate(self, chinese_text: str) -> str:
        """翻译中文到英文"""
        # 处理带变量的字符串
        if '${' in chinese_text:
            # 提取变量名
            var_matches = re.findall(r'\$\{(\w+)\}', chinese_text)
            base_text = re.sub(r'\$\{[^}]+\}', '{}', chinese_text)
            
            # 翻译基础文本
            translated_base = self._translate_simple(base_text)
            
            # 恢复变量占位符
            for i, var_name in enumerate(var_matches):
                translated_base = translated_base.replace('{}', '{' + var_name + '}', 1)
            
            return translated_base
        
        # 处理普通文本
        return self._translate_simple(chinese_text)
    
    def _translate_simple(self, text: str) -> str:
        """简单文本翻译"""
        # 直接映射
        if text in self.business_translations:
            return self.business_translations[text]
        
        if text in self.time_translations:
            return self.time_translations[text]
        
        # 处理复合词（包含多个已知词汇）
        words = re.findall(r'[\u4e00-\u9fff]+', text)
        if len(words) > 1:
            translated_parts = []
            remaining_text = text
            
            # 按优先级匹配长词组
            sorted_terms = sorted(
                list(self.business_translations.keys()) + list(self.time_translations.keys()),
                key=len, reverse=True
            )
            
            for term in sorted_terms:
                if term in remaining_text:
                    translated_term = self.business_translations.get(term) or self.time_translations.get(term)
                    translated_parts.append(translated_term)
                    remaining_text = remaining_text.replace(term, '', 1)
            
            if translated_parts:
                # 简单连接翻译结果
                return ' '.join(translated_parts)
        
        # 基础翻译（这里可以集成在线翻译API）
        # 目前返回原文的拼音化处理作为后备
        return self._fallback_translation(text)
    
    def _fallback_translation(self, text: str) -> str:
        """后备翻译方法"""
        # 简单的音译或意译规则
        fallback_map = {
            "请选择": "Please select",
            "请输入": "Please enter",
            "不能为空": "cannot be empty",
            "已经": "already",
            "可以": "can",
            "需要": "need",
            "必须": "must",
            "应该": "should",
            "将会": "will",
            "正在": "is",
            "完成": "completed",
            "处理": "process",
            "操作": "operation",
            "功能": "function",
            "页面": "page",
            "模块": "module",
            "系统": "system",
            "管理": "management",
            "控制": "control",
            "查看": "view",
            "显示": "display",
            "隐藏": "hide",
            "启用": "enable",
            "禁用": "disable",
            "开启": "open",
            "关闭": "close",
            "添加": "add",
            "移除": "remove",
            "更新": "update",
            "修改": "modify",
            "复制": "copy",
            "粘贴": "paste",
            "剪切": "cut",
            "全选": "select all",
            "反选": "invert selection",
            "清空": "clear",
            "重置": "reset",
            "恢复": "restore",
            "备份": "backup",
            "导入": "import",
            "导出": "export",
            "上传": "upload",
            "下载": "download",
            "预览": "preview",
            "打印": "print",
            "分享": "share",
            "收藏": "favorite",
            "关注": "follow",
            "取消关注": "unfollow",
            "点赞": "like",
            "评论": "comment",
            "回复": "reply",
            "转发": "forward",
            "举报": "report",
            "屏蔽": "block",
            "解除": "remove",
            "绑定": "bind",
            "解绑": "unbind",
            "关联": "associate",
            "取消关联": "disassociate",
            "同步": "sync",
            "异步": "async",
            "立即": "immediately",
            "稍后": "later",
            "定时": "scheduled",
            "自动": "automatic",
            "手动": "manual",
            "批量": "batch",
            "单个": "single",
            "全部": "all",
            "部分": "partial",
            "详细": "detail",
            "简要": "brief",
            "高级": "advanced",
            "基础": "basic",
            "专业": "professional",
            "简易": "simple",
            "复杂": "complex",
            "简单": "simple",
            "困难": "difficult",
            "容易": "easy",
            "困难": "hard",
            "快速": "fast",
            "慢速": "slow",
            "高效": "efficient",
            "低效": "inefficient",
            "稳定": "stable",
            "不稳定": "unstable",
            "安全": "secure",
            "危险": "dangerous",
            "公开": "public",
            "私有": "private",
            "内部": "internal",
            "外部": "external",
            "本地": "local",
            "远程": "remote",
            "在线": "online",
            "离线": "offline",
            "实时": "real-time",
            "延迟": "delayed",
            "即时": "instant",
            "定期": "periodic",
            "临时": "temporary",
            "永久": "permanent",
            "临时": "temporary",
            "长期": "long-term",
            "短期": "short-term",
            "中期": "medium-term"
        }
        
        # 查找匹配的短语
        for chinese_phrase, english_phrase in fallback_map.items():
            if chinese_phrase in text:
                # 替换并处理剩余部分
                remaining = text.replace(chinese_phrase, '')
                if remaining.strip():
                    return english_phrase + ' ' + self._fallback_translation(remaining.strip())
                return english_phrase
        
        # 如果没有匹配项，返回原文（这在实际使用中应该调用翻译API）
        return text

class ChineseStringExtractor:
    """中文字符串提取器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
    def extract_chinese_strings(self, file_path: Path) -> List[Tuple[str, int, str]]:
        """
        从Dart文件中提取中文字符串
        
        返回: [(字符串内容, 行号, 上下文)]
        """
        chinese_strings = []
        chinese_pattern = re.compile(r"['\"]([^'\"]*[\\u4e00-\\u9fff]+[^'\"]*)['\"]")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                matches = chinese_pattern.findall(line)
                for match in matches:
                    # 过滤掉纯数字和特殊字符
                    if re.search(r'[\\u4e00-\\u9fff]', match):
                        context = self._get_context(lines, line_num)
                        chinese_strings.append((match, line_num, context))
                        
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            
        return chinese_strings
    
    def _get_context(self, lines: List[str], line_num: int, context_lines: int = 2) -> str:
        """获取字符串周围的上下文"""
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        context_lines = lines[start:end]
        return ''.join(context_lines).strip()

class KeyGenerator:
    """国际化键名生成器"""
    
    def __init__(self):
        self.used_keys = set()
        
    def generate_key(self, chinese_text: str, context: str = "", max_length: int = 50) -> str:
        """
        生成唯一的国际化键名
        
        策略:
        1. 使用英文翻译作为基础
        2. 添加上下文前缀
        3. 确保唯一性
        """
        # 获取英文翻译作为键名基础
        translator = TranslationService()
        english_text = translator.translate(chinese_text)
        
        # 转换为camelCase
        key = self._to_camel_case(english_text)
        
        # 添加上下文前缀
        if context:
            prefix = self._extract_context_prefix(context)
            if prefix:
                key = f"{prefix}{key[0].upper()}{key[1:]}" if key else prefix
        
        # 确保唯一性
        original_key = key
        counter = 1
        while key in self.used_keys or len(key) > max_length:
            if len(key) > max_length:
                # 截断并添加哈希后缀
                hash_suffix = hashlib.md5(chinese_text.encode()).hexdigest()[:6]
                key = f"{original_key[:max_length-7]}_{hash_suffix}"
            else:
                key = f"{original_key}_{counter}"
                counter += 1
                
        self.used_keys.add(key)
        return key
    
    def _to_camel_case(self, text: str) -> str:
        """转换为camelCase"""
        # 移除标点符号，分割单词
        words = re.findall(r'[a-zA-Z]+', text.lower())
        if not words:
            return "key"
        
        # 第一个单词小写，其余首字母大写
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    
    def _extract_context_prefix(self, context: str) -> str:
        """从上下文提取前缀"""
        # 基于常见的业务词汇提取前缀
        prefixes = {
            'login': ['登录', '登陆', 'signin', 'login'],
            'register': ['注册', 'signup', 'register'],
            'user': ['用户', 'user', 'profile'],
            'order': ['订单', 'order', 'bill'],
            'product': ['商品', '产品', 'product', 'goods'],
            'customer': ['客户', '顾客', 'customer'],
            'report': ['报表', '报告', 'report'],
            'setting': ['设置', '配置', 'setting', 'config'],
            'message': ['消息', '通知', 'message', 'notification'],
            'error': ['错误', '失败', 'error', 'fail'],
            'success': ['成功', '完成', 'success', 'complete'],
            'validation': ['验证', '校验', '检查', 'validate', 'check'],
            'navigation': ['导航', '菜单', '页面', 'nav', 'menu', 'page'],
            'account': ['账户', '账号', 'account'],
            'bill': ['单据', '账单', 'bill'],
            'inventory': ['库存', '盘点', 'inventory'],
            'supplier': ['供应商', 'supplier'],
            'purchase': ['采购', '进货', 'purchase'],
            'sales': ['销售', '出售', 'sales'],
            'finance': ['财务', '金融', 'finance'],
            'system': ['系统', 'system']
        }
        
        context_lower = context.lower()
        for prefix, keywords in prefixes.items():
            if any(keyword in context_lower for keyword in keywords):
                return prefix
        
        return ""

class ARBFileManager:
    """ARB文件管理器"""
    
    def __init__(self, arb_directory: str):
        self.arb_directory = Path(arb_directory)
        self.zh_arb_path = self.arb_directory / "app_zh.arb"
        self.en_arb_path = self.arb_directory / "app_en.arb"
        self.translator = TranslationService()
        
    def load_arb_files(self) -> Tuple[Dict, Dict]:
        """加载现有的ARB文件，保持字段顺序"""
        zh_data = self._load_arb_file(self.zh_arb_path)
        en_data = self._load_arb_file(self.en_arb_path)
        return zh_data, en_data
    
    def _load_arb_file(self, file_path: Path) -> Dict:
        """加载单个ARB文件，保持原有字段顺序"""
        if not file_path.exists():
            return {"@@locale": "zh" if "zh" in file_path.name else "en"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 使用object_pairs_hook保持顺序
                return json.load(f, object_pairs_hook=lambda pairs: {k: v for k, v in pairs})
        except Exception as e:
            print(f"加载ARB文件失败 {file_path}: {e}")
            return {"@@locale": "zh" if "zh" in file_path.name else "en"}
    
    def save_arb_files(self, zh_data: Dict, en_data: Dict):
        """保存ARB文件，确保字段顺序一致且新增字段在末尾"""
        # 确保两个文件具有相同的键顺序
        ordered_keys = self._get_consistent_key_order(zh_data, en_data)
        
        # 重新排列字典顺序
        zh_ordered = self._reorder_dict(zh_data, ordered_keys)
        en_ordered = self._reorder_dict(en_data, ordered_keys)
        
        self._save_arb_file(self.zh_arb_path, zh_ordered)
        self._save_arb_file(self.en_arb_path, en_ordered)
    
    def _get_consistent_key_order(self, zh_data: Dict, en_data: Dict) -> List[str]:
        """获取一致的键顺序，确保新增字段在末尾"""
        # 获取所有键
        all_keys = set(zh_data.keys()) | set(en_data.keys())
        
        # 分离元数据键和普通键
        meta_keys = [key for key in all_keys if key.startswith('@@')]
        regular_keys = [key for key in all_keys if not key.startswith('@@')]
        
        # 按原有顺序排列普通键，新键放在末尾
        existing_keys_zh = [key for key in zh_data.keys() if not key.startswith('@@') and key in regular_keys]
        existing_keys_en = [key for key in en_data.keys() if not key.startswith('@@') and key in regular_keys]
        
        # 合并现有键，保持相对顺序
        merged_existing = []
        zh_index = 0
        en_index = 0
        
        while zh_index < len(existing_keys_zh) or en_index < len(existing_keys_en):
            if zh_index < len(existing_keys_zh):
                key = existing_keys_zh[zh_index]
                if key not in merged_existing:
                    merged_existing.append(key)
                zh_index += 1
            
            if en_index < len(existing_keys_en):
                key = existing_keys_en[en_index]
                if key not in merged_existing:
                    merged_existing.append(key)
                en_index += 1
        
        # 新键按字母顺序排列后添加到末尾
        new_keys = [key for key in regular_keys if key not in merged_existing]
        new_keys.sort()
        
        # 组合最终顺序：元数据键 + 现有键 + 新键
        return meta_keys + merged_existing + new_keys
    
    def _reorder_dict(self, data: Dict, ordered_keys: List[str]) -> Dict:
        """按指定顺序重新排列字典"""
        reordered = {}
        # 先添加有序的键
        for key in ordered_keys:
            if key in data:
                reordered[key] = data[key]
        # 添加可能遗漏的键（理论上不应该有）
        for key, value in data.items():
            if key not in reordered:
                reordered[key] = value
        return reordered
    
    def _save_arb_file(self, file_path: Path, data: Dict):
        """保存单个ARB文件，保持字段顺序"""
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用自定义序列化确保顺序
            with open(file_path, 'w', encoding='utf-8') as f:
                # 手动构建JSON字符串以确保顺序
                json_str = self._dict_to_json_string(data)
                f.write(json_str)
        except Exception as e:
            print(f"保存ARB文件失败 {file_path}: {e}")
    
    def _dict_to_json_string(self, data: Dict) -> str:
        """将字典转换为格式化的JSON字符串，保持键顺序"""
        lines = ["{"]
        
        # 分离元数据和普通字段
        meta_items = [(k, v) for k, v in data.items() if k.startswith('@@')]
        regular_items = [(k, v) for k, v in data.items() if not k.startswith('@@')]
        
        # 先处理元数据字段
        for i, (key, value) in enumerate(meta_items):
            if isinstance(value, str):
                line = f'  "{key}": "{value}"'
            else:
                line = f'  "{key}": {json.dumps(value, ensure_ascii=False)}'
            
            if i < len(meta_items) - 1 or regular_items:
                line += ","
            lines.append(line)
        
        # 处理普通字段
        for i, (key, value) in enumerate(regular_items):
            if isinstance(value, str):
                line = f'  "{key}": "{value}"'
            else:
                line = f'  "{key}": {json.dumps(value, ensure_ascii=False)}'
            
            if i < len(regular_items) - 1:
                line += ","
            lines.append(line)
        
        lines.append("}")
        return '\n'.join(lines) + '\n'
    
    def add_translations(self, new_entries: Dict) -> Tuple[Dict, Dict]:
        """
        添加新的翻译条目到ARB文件
        
        Args:
            new_entries: {key: chinese_value} 字典
            
        Returns:
            (updated_zh_data, updated_en_data)
        """
        zh_data, en_data = self.load_arb_files()
        
        # 添加中文条目
        for key, chinese_value in new_entries.items():
            zh_data[key] = chinese_value
            
            # 生成英文翻译
            english_value = self.translator.translate(chinese_value)
            en_data[key] = english_value
            
            print(f"添加翻译: {chinese_value} -> {english_value}")
        
        return zh_data, en_data

class CodeReplacer:
    """代码替换器"""
    
    def replace_chinese_strings(self, file_path: Path, replacements: List[Tuple[str, str, str]]) -> bool:
        """
        替换文件中的中文字符串
        
        replacements: [(原文, 键名, 参数列表)]
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for original_text, key_name, params in replacements:
                # 构造替换后的字符串
                if params:
                    # 提取参数名，构造正确的调用格式
                    param_names = [param.split(':')[0].strip() for param in params.split(',')]
                    replacement = f"S.strings.{key_name}({', '.join(param_names)})"
                else:
                    replacement = f"S.strings.{key_name}"
                
                # 转义特殊字符
                escaped_text = re.escape(original_text)
                # 处理字符串中的引号
                if "'" in original_text and '"' not in original_text:
                    pattern = f"'{escaped_text}'"
                elif '"' in original_text and "'" not in original_text:
                    pattern = f'"{escaped_text}"'
                else:
                    # 如果同时包含单双引号，需要更复杂的处理
                    pattern = f"(?:'{escaped_text}'|\"{escaped_text}\")"
                
                content = re.sub(pattern, replacement, content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"替换文件内容失败 {file_path}: {e}")
            return False
        
        return False

def main():
    """主函数 - 演示如何使用这些工具"""
    if len(sys.argv) < 2:
        print("用法: python ancestry_i18n_helper.py <file_path>")
        return
    
    file_path = Path(sys.argv[1])
    project_root = "/Volumes/Samsung/AndroidStudioWorkspace/ishops/packages/ancestry"
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return
    
    # 初始化工具
    extractor = ChineseStringExtractor(project_root)
    keygen = KeyGenerator()
    arb_manager = ARBFileManager(f"{project_root}/lib/src/l10n")
    replacer = CodeReplacer()
    
    # 提取中文字符串
    chinese_strings = extractor.extract_chinese_strings(file_path)
    
    if not chinese_strings:
        print("未找到中文字符串")
        return
    
    print(f"找到 {len(chinese_strings)} 个中文字符串:")
    for text, line_num, context in chinese_strings[:5]:  # 只显示前5个
        print(f"  行 {line_num}: '{text}'")
    
    # 生成键名和翻译映射
    key_mapping = {}
    replacements = []
    
    for chinese_text, line_num, context in chinese_strings[:5]:  # 处理前5个
        key_name = keygen.generate_key(chinese_text, context)
        
        # 处理参数
        params = ""
        if '${' in chinese_text:
            var_matches = re.findall(r'\$\{(\w+)\}', chinese_text)
            params = ", ".join([f"{var}: {var}" for var in var_matches])
        
        replacements.append((chinese_text, key_name, params))
        key_mapping[key_name] = chinese_text
    
    # 同步更新ARB文件（中英文）
    zh_data, en_data = arb_manager.add_translations(key_mapping)
    arb_manager.save_arb_files(zh_data, en_data)
    
    # 替换代码中的字符串
    if replacer.replace_chinese_strings(file_path, replacements):
        print("代码替换完成")
        print("\n处理摘要:")
        print(f"- 处理文件: {file_path}")
        print(f"- 识别中文字符串: {len(chinese_strings)} 个")
        print(f"- 实际处理: {len(replacements)} 个")
        print(f"- 更新ARB条目: {len(key_mapping)} 个")
        print("- 中英文同步完成")
    else:
        print("代码替换失败")

if __name__ == "__main__":
    main()
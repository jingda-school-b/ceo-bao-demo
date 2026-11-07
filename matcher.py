# -*- coding: utf-8 -*-
"""演示用的名称匹配：只展示「归一化 + 二元组 Dice 相似度」这条主线。

说明：真实系统里还有多候选召回、地址门牌三态校验、唯一线路兜底等规则，
属于业务核心，不在演示范围内。本文件刻意保持简单，方便对照论文理解思路。
"""
import re

# 行政区与常见后缀，归一化时剥掉，避免「河南省郑州市」「郑州市」被当成不一致
ADMIN = re.compile(
    r'(?:[\u4e00-\u9fa5]{2,8}(?:省|自治区|特别行政区))?'
    r'(?:[\u4e00-\u9fa5]{2,8}市)?'
    r'(?:[\u4e00-\u9fa5]{2,8}(?:区|县|旗))?'
)
NOISE = re.compile(r'[\s\-—·（）()【】\[\]，,。.、/\\]+')


def normalize(s):
    """只保留中文与数字，去掉行政区前缀和标点。"""
    if not s:
        return ''
    s = NOISE.sub('', str(s))
    m = ADMIN.match(s)
    if m:
        s = s[m.end():]
    return s


def bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else {s}


def dice(a, b):
    """Dice 系数：2|A∩B| / (|A|+|B|)，对短文本比编辑距离更稳。"""
    if not a or not b:
        return 0.0
    A, B = bigrams(a), bigrams(b)
    return 2.0 * len(A & B) / (len(A) + len(B))


def extract_house_no(s):
    """抽取「路名 + 门牌号」，用于演示门牌一致性校验。"""
    m = re.search(r'([\u4e00-\u9fa5]{1,10}?(?:大道|大街|路|街|道|巷))\s*(\d{1,5})\s*号?', s or '')
    return (m.group(1), int(m.group(2))) if m else (None, None)


def score(query, title):
    """返回 0~1 的名称匹配分。"""
    q, t = normalize(query), normalize(title)
    if not q or not t:
        return 0.0
    if t in q:
        return 1.0
    return round(dice(q, t), 3)

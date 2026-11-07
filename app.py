# -*- coding: utf-8 -*-
"""演示服务：输入一个地址，返回候选地点各自落在哪个围栏里。

只做两件事：
  1. 名称归一化 + 相似度打分（matcher.py）
  2. 射线法判断坐标落在哪个围栏（fence.py）

不接任何地图 API，不读写数据库，数据全部来自 data/ 下的虚构样例。
启动：pip install flask && python app.py   然后打开 http://127.0.0.1:5000
"""
import json
import os

from flask import Flask, jsonify, render_template, request

from fence import distance_to_ring, point_in_polygon_fast
from matcher import extract_house_no, score

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

with open(os.path.join(BASE, 'data', 'fences.json'), encoding='utf-8') as f:
    FENCES = json.load(f)
with open(os.path.join(BASE, 'data', 'pois.json'), encoding='utf-8') as f:
    POIS = json.load(f)


def locate(lng, lat):
    hits = []
    for fc in FENCES:
        if point_in_polygon_fast(lng, lat, fc['ring']):
            hits.append(fc['name'])
    return hits


@app.route('/')
def index():
    return render_template('index.html',
                           fences=FENCES, pois=POIS)


@app.route('/api/parse')
def parse():
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify({'code': 1, 'msg': '请输入地址'})

    road, no = extract_house_no(q)
    results = []
    for p in POIS:
        s = score(q, p['title'])
        if s < 0.3:
            continue
        routes = locate(p['lng'], p['lat'])
        edge = min(distance_to_ring(p['lng'], p['lat'], fc['ring']) for fc in FENCES)
        results.append({
            'title': p['title'],
            'address': p['address'],
            'lng': p['lng'],
            'lat': p['lat'],
            'score': s,
            'routes': routes,
            'edge_distance_m': round(edge * 111000, 1),
            'name_in_query': p['title'] in q,
            'house_no_match': bool(road and no and p['address'].find('%s%d' % (road, no)) >= 0),
        })
    results.sort(key=lambda r: (-r['score'], not r['routes']))
    return jsonify({'code': 0, 'query': q, 'count': len(results),
                    'results': results[:5]})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)), debug=True)

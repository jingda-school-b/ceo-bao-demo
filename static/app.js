/* 演示前端：提交地址 → 调 /api/parse → 卡片列表 + 画布标点。
 * 坐标换算只是把经纬度线性映射到画布，不涉及任何地图服务。 */
(function () {
  var data = JSON.parse(document.getElementById('bootstrap').textContent);
  var cv = document.getElementById('cv');
  var ctx = cv.getContext('2d');
  var out = document.getElementById('out');
  var input = document.getElementById('q');

  // 用所有围栏 + 点算出一个刚好装下的范围
  var pts = [];
  data.fences.forEach(function (f) { pts = pts.concat(f.ring); });
  data.pois.forEach(function (p) { pts.push([p.lng, p.lat]); });
  var xs = pts.map(function (p) { return p[0]; });
  var ys = pts.map(function (p) { return p[1]; });
  var pad = 0.006;
  var box = [Math.min.apply(null, xs) - pad, Math.min.apply(null, ys) - pad,
             Math.max.apply(null, xs) + pad, Math.max.apply(null, ys) + pad];

  function X(lng) { return (lng - box[0]) / (box[2] - box[0]) * cv.width; }
  function Y(lat) { return cv.height - (lat - box[1]) / (box[3] - box[1]) * cv.height; }

  function draw(hits) {
    ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.fillStyle = '#fbfcfe';
    ctx.fillRect(0, 0, cv.width, cv.height);

    data.fences.forEach(function (f) {
      ctx.beginPath();
      f.ring.forEach(function (p, i) {
        i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1]));
      });
      ctx.closePath();
      ctx.fillStyle = f.color + '14';
      ctx.fill();
      ctx.strokeStyle = f.color;
      ctx.lineWidth = 1.6;
      ctx.stroke();
      ctx.fillStyle = f.color;
      ctx.font = '13px sans-serif';
      ctx.fillText(f.name, X(f.ring[0][0]) + 8, Y(f.ring[0][1]) + 18);
    });

    data.pois.forEach(function (p) {
      var hit = hits.indexOf(p.title) >= 0;
      ctx.beginPath();
      ctx.arc(X(p.lng), Y(p.lat), hit ? 5.5 : 3.5, 0, Math.PI * 2);
      ctx.fillStyle = hit ? '#111827' : '#9ca3af';
      ctx.fill();
      if (hit) {
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    });
  }

  function render(res) {
    if (!res.count) {
      out.innerHTML = '<p class="empty">没有匹配到候选地点，换个写法试试。</p>';
      return;
    }
    out.innerHTML = res.results.map(function (r) {
      var routes = r.routes.length
        ? r.routes.map(function (n) { return '<span class="tag">' + n + '</span>'; }).join('')
        : '<span class="tag warn">围栏外</span>';
      return '<div class="card">' +
        '<div class="t">' + r.title + '</div>' +
        '<div class="a">' + r.address + '</div>' +
        '<div class="m">' + routes +
        '<span class="tag gray">名称相似度 ' + r.score.toFixed(2) + '</span>' +
        (r.name_in_query ? '<span class="tag gray">逐字命中</span>' : '') +
        (r.house_no_match ? '<span class="tag gray">门牌一致</span>' : '') +
        '</div></div>';
    }).join('');
  }

  function ask(q) {
    if (!q) return;
    out.innerHTML = '<p class="empty">解析中…</p>';
    fetch('/api/parse?q=' + encodeURIComponent(q))
      .then(function (r) { return r.json(); })
      .then(function (res) {
        render(res);
        draw((res.results || []).filter(function (r) { return r.routes.length; })
                                .map(function (r) { return r.title; }));
      });
  }

  document.getElementById('f').addEventListener('submit', function (e) {
    e.preventDefault();
    ask(input.value.trim());
  });
  Array.prototype.forEach.call(document.querySelectorAll('.examples a'), function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      input.value = a.dataset.q;
      ask(a.dataset.q);
    });
  });

  document.getElementById('legend').innerHTML = data.fences.map(function (f) {
    return '<span><i style="background:' + f.color + '"></i>' + f.name + '</span>';
  }).join('');

  draw([]);
})();

import os
from datetime import date, datetime, timedelta
from flask import Flask, jsonify, render_template_string, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

# Interfaz incluida en este mismo archivo para facilitar la subida desde celular.
HTML_PAGE = '<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8"/>\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>\n<title>Dulces Momentos — Vitrina compartida</title>\n<style>\n:root{--bg:#fff8fb;--card:#fff;--ink:#2b2230;--muted:#7f7484;--accent:#d65a8a;--ok:#2f9e66;--warn:#d49a16;--high:#e46b45;--bad:#c43b4f;--line:#eee2e8;--shadow:0 10px 30px rgba(89,50,70,.09)}\n*{box-sizing:border-box} body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;background:var(--bg);color:var(--ink)}\nheader{position:sticky;top:0;z-index:20;background:rgba(255,248,251,.94);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}\n.wrap{max-width:1180px;margin:auto;padding:16px}.brand{display:flex;align-items:center;gap:12px}.logo{width:42px;height:42px;border-radius:14px;background:linear-gradient(145deg,#f7b8cf,#d65a8a);display:grid;place-items:center;box-shadow:var(--shadow);font-size:24px}h1{font-size:20px;margin:0}.sub{font-size:12px;color:var(--muted)}\n.sync{margin-left:auto;font-size:11px;padding:7px 10px;border-radius:999px;background:#e7f6ee;color:var(--ok);font-weight:800}\nnav{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}button{border:0;border-radius:12px;padding:11px 14px;font-weight:700;cursor:pointer;background:#f4eaf0;color:var(--ink)}button.primary{background:var(--accent);color:#fff}nav button.active{background:var(--accent);color:#fff}.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px;box-shadow:var(--shadow)}.metric .label{font-size:12px;color:var(--muted)}.metric .value{font-size:28px;font-weight:800;margin-top:5px}.mini,.small{font-size:12px;color:var(--muted)}.warn{color:var(--warn)}.bad{color:var(--bad)}.section-title{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:16px 0 10px}.section-title h2{font-size:18px;margin:0}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:16px;background:#fff}table{width:100%;border-collapse:collapse;min-width:900px}th,td{padding:12px 10px;border-bottom:1px solid var(--line);text-align:left;font-size:13px;vertical-align:middle}th{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;background:#fffafd}.product{display:flex;align-items:center;gap:10px}.thumb{width:44px;height:44px;border-radius:12px;background:#fae5ee;display:grid;place-items:center;font-size:23px}.badge{display:inline-flex;align-items:center;border-radius:999px;padding:6px 9px;font-size:11px;font-weight:800}.b-ok{background:#e7f6ee;color:var(--ok)}.b-warn{background:#fff5d9;color:#a06a00}.b-high{background:#ffe8df;color:#b84f2d}.b-today{background:#ffe1e6;color:var(--bad)}.b-expired{background:#f1e6e8;color:#842635}.two{display:grid;grid-template-columns:1fr 1fr;gap:14px}form{display:grid;gap:12px}label{font-size:12px;font-weight:700;color:#5f5364}input,select{width:100%;padding:12px;border:1px solid #dfd1d8;border-radius:12px;background:#fff;font:inherit}.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.notice{padding:12px 14px;border-radius:14px;background:#fff4d8;border:1px solid #f4dda1;color:#755200;font-size:13px;margin:12px 0}.alert{padding:12px;border-radius:14px;border:1px solid var(--line);background:#fff;margin-bottom:8px}.hidden{display:none!important}.empty{padding:32px;text-align:center;color:var(--muted)}.toast{position:fixed;right:16px;bottom:20px;background:#2b2230;color:white;padding:12px 16px;border-radius:12px;box-shadow:var(--shadow);z-index:50;max-width:320px}.error{background:#8f2f3f}.cloud-note{padding:10px 12px;background:#eef7ff;border:1px solid #cfe5f7;border-radius:13px;font-size:12px;color:#34546a;margin-top:14px}footer{padding:30px 0 50px;color:var(--muted);font-size:12px;text-align:center}\n@media(max-width:820px){.grid4{grid-template-columns:1fr 1fr}.two,.row{grid-template-columns:1fr}.wrap{padding:12px}nav{overflow:auto;flex-wrap:nowrap}nav button{white-space:nowrap}.sync{display:none}}@media(max-width:480px){.metric .value{font-size:22px}}\n</style>\n</head>\n<body>\n<header><div class="wrap"><div class="brand"><div class="logo">🧁</div><div><h1>Dulces Momentos</h1><div class="sub">Control compartido de vitrina y vencimientos</div></div><div class="sync">☁️ Datos compartidos</div></div><nav><button class="active" data-tab="inicio">Inicio</button><button data-tab="entrada">Nueva entrada</button><button data-tab="salida">Registrar salida</button><button data-tab="productos">Productos</button><button data-tab="alertas">Alertas</button></nav></div></header>\n<main class="wrap">\n<section id="inicio" class="tab"><div class="grid4"><div class="card metric"><div class="label">Unidades en vitrina</div><div id="mStock" class="value">0</div><div class="mini">Disponibles ahora</div></div><div class="card metric"><div class="label">Por vencer</div><div id="mWarn" class="value warn">0</div><div class="mini">2 días o menos</div></div><div class="card metric"><div class="label">Vencidos</div><div id="mExpired" class="value bad">0</div><div class="mini">Retirar de vitrina</div></div><div class="card metric"><div class="label">Valor en vitrina</div><div id="mValue" class="value">S/ 0.00</div><div class="mini">Cantidad × precio</div></div></div><div id="mainNotice" class="notice hidden"></div><div class="section-title"><h2>Inventario de vitrina</h2><button class="primary" onclick="go(\'entrada\')">+ Nueva entrada</button></div><div class="table-wrap"><table><thead><tr><th>Producto</th><th>Lote</th><th>Cantidad</th><th>Ingreso</th><th>Vence</th><th>Días</th><th>Estado</th><th>Precio</th><th>Valor</th></tr></thead><tbody id="inventoryBody"></tbody></table></div><div class="cloud-note">Esta versión obtiene los datos del servidor. Cuando se publique en la nube, cualquier teléfono con el enlace verá el mismo inventario.</div></section>\n<section id="entrada" class="tab hidden"><div class="section-title"><h2>Registrar nueva entrada</h2></div><div class="two"><div class="card"><form id="entryForm"><div><label>Producto</label><select id="entryProduct" required></select></div><div class="row"><div><label>Cantidad</label><input id="entryQty" type="number" min="1" value="1" required></div><div><label>Fecha de ingreso</label><input id="entryDate" type="date" required></div></div><div id="entryPreview" class="notice"></div><button class="primary" type="submit">Guardar entrada</button></form></div><div class="card"><h3 style="margin-top:0">Regla de vencimiento</h3><p class="small">El día de ingreso cuenta como día 1. El vencimiento se calcula con la vida útil de cada producto.</p><div class="alert"><b>3+ días</b><br><span class="small">Vigente</span></div><div class="alert"><b>2 días</b><br><span class="small">Por vencer</span></div><div class="alert"><b>1 día</b><br><span class="small">Prioridad alta</span></div><div class="alert"><b>0 días</b><br><span class="small">Vence hoy</span></div></div></div></section>\n<section id="salida" class="tab hidden"><div class="section-title"><h2>Registrar salida</h2></div><div class="card"><form id="exitForm"><div><label>Lote / producto</label><select id="exitLot" required></select></div><div class="row"><div><label>Cantidad</label><input id="exitQty" type="number" min="1" value="1" required></div><div><label>Motivo</label><select id="exitReason"><option>Venta</option><option>Merma</option><option>Retiro por vencimiento</option><option>Ajuste</option></select></div></div><button class="primary" type="submit">Registrar salida</button></form></div></section>\n<section id="productos" class="tab hidden"><div class="section-title"><h2>Productos</h2></div><div class="two"><div class="card"><form id="productForm"><div><label>Nombre</label><input id="pName" required placeholder="Ej. Cheesecake de fresa"></div><div class="row"><div><label>Precio (S/)</label><input id="pPrice" type="number" min="0" step="0.10" required></div><div><label>Vida útil (días)</label><input id="pLife" type="number" min="1" max="30" required></div></div><button class="primary" type="submit">Agregar producto</button></form></div><div class="card"><div id="productList"></div></div></div></section>\n<section id="alertas" class="tab hidden"><div class="section-title"><h2>Alertas de vencimiento</h2></div><div id="alertsList"></div></section>\n</main><footer>Dulces Momentos · Versión nube V2 · Base de datos central</footer><div id="toast" class="toast hidden"></div>\n<script>\nconst $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)]; let products=[],lots=[],dashboard={alerts:[]};\nconst todayISO=()=>new Date().toISOString().slice(0,10), money=n=>"S/ "+Number(n||0).toFixed(2), fmt=d=>new Date(d+"T12:00:00").toLocaleDateString("es-PE",{day:"2-digit",month:"2-digit",year:"numeric"});\nfunction toast(msg,error=false){const t=$("#toast");t.textContent=msg;t.className="toast"+(error?" error":"");setTimeout(()=>t.classList.add("hidden"),2600)}\nasync function api(url,opts={}){const r=await fetch(url,{headers:{"Content-Type":"application/json"},...opts});let data={};try{data=await r.json()}catch{}if(!r.ok)throw new Error(data.error||"No se pudo completar la operación.");return data}\nfunction go(id){$$(\'.tab\').forEach(x=>x.classList.add(\'hidden\'));$(\'#\'+id).classList.remove(\'hidden\');$$(\'nav button\').forEach(b=>b.classList.toggle(\'active\',b.dataset.tab===id));refresh()}\n$$(\'nav button\').forEach(b=>b.onclick=()=>go(b.dataset.tab));\nfunction badge(l){return l===\'ok\'?\'b-ok\':l===\'warn\'?\'b-warn\':l===\'high\'?\'b-high\':l===\'today\'?\'b-today\':\'b-expired\'}\nasync function refresh(){try{[products,lots,dashboard]=await Promise.all([api(\'/api/products\'),api(\'/api/lots\'),api(\'/api/dashboard\')]);render()}catch(e){toast(e.message,true)}}\nfunction render(){\n $(\'#mStock\').textContent=dashboard.stock||0;$(\'#mWarn\').textContent=dashboard.warn||0;$(\'#mExpired\').textContent=dashboard.expired||0;$(\'#mValue\').textContent=money(dashboard.value);\n const n=$(\'#mainNotice\');if(dashboard.expired>0){n.classList.remove(\'hidden\');n.innerHTML=`⚠️ Tienes <b>${dashboard.expired}</b> unidad(es) vencida(s).`}else if(dashboard.warn>0){n.classList.remove(\'hidden\');n.innerHTML=`⏰ Tienes <b>${dashboard.warn}</b> unidad(es) con 2 días o menos antes de vencer.`}else n.classList.add(\'hidden\');\n $(\'#inventoryBody\').innerHTML=lots.length?lots.map(l=>`<tr><td><div class="product"><div class="thumb">${l.product.emoji}</div><div><b>${l.product.name}</b><div class="small">${l.product.shelf_life_days} días de vida útil</div></div></div></td><td>${l.code}</td><td><b>${l.stock}</b></td><td>${fmt(l.entry_date)}</td><td>${fmt(l.expiry_date)}</td><td>${l.days_left<0?Math.abs(l.days_left)+\' vencido\':l.days_left}</td><td><span class="badge ${badge(l.level)}">${l.status}</span></td><td>${money(l.product.price)}</td><td>${money(l.value)}</td></tr>`).join(\'\'):`<tr><td colspan="9" class="empty">Aún no hay productos en vitrina.</td></tr>`;\n $(\'#entryProduct\').innerHTML=products.map(p=>`<option value="${p.id}">${p.name} · ${money(p.price)} · ${p.shelf_life_days} días</option>`).join(\'\');\n $(\'#productList\').innerHTML=products.map(p=>`<div class="alert"><b>${p.emoji} ${p.name}</b><div class="small">${money(p.price)} · vida útil ${p.shelf_life_days} días</div></div>`).join(\'\')||\'<div class="empty">Sin productos.</div>\';\n $(\'#exitLot\').innerHTML=lots.map(l=>`<option value="${l.id}">${l.code} · ${l.product.name} · stock ${l.stock} · vence ${fmt(l.expiry_date)}</option>`).join(\'\')||\'<option value="">No hay stock disponible</option>\';\n $(\'#alertsList\').innerHTML=(dashboard.alerts||[]).length?dashboard.alerts.map(l=>`<div class="alert"><b>${l.product.name}</b> · ${l.code}<br><span class="badge ${badge(l.level)}">${l.status}</span> <span class="small">· ${l.stock} unidad(es) · vence ${fmt(l.expiry_date)}</span></div>`).join(\'\'):\'<div class="card empty">No tienes alertas por vencimiento.</div>\';\n updatePreview();\n}\nfunction updatePreview(){const p=products.find(x=>x.id===Number($(\'#entryProduct\').value));const d=$(\'#entryDate\').value||todayISO();if(!p){$(\'#entryPreview\').textContent=\'Agrega un producto primero.\';return}const dt=new Date(d+\'T12:00:00\');dt.setDate(dt.getDate()+p.shelf_life_days-1);$(\'#entryPreview\').innerHTML=`Vida útil: <b>${p.shelf_life_days} días</b> · Vencimiento calculado: <b>${dt.toLocaleDateString(\'es-PE\')}</b>`}\n$(\'#entryDate\').value=todayISO();$(\'#entryProduct\').addEventListener(\'change\',updatePreview);$(\'#entryDate\').addEventListener(\'change\',updatePreview);\n$(\'#entryForm\').addEventListener(\'submit\',async e=>{e.preventDefault();try{await api(\'/api/entries\',{method:\'POST\',body:JSON.stringify({product_id:Number($(\'#entryProduct\').value),qty:Number($(\'#entryQty\').value),entry_date:$(\'#entryDate\').value})});$(\'#entryQty\').value=1;toast(\'Entrada guardada para todos los usuarios.\');go(\'inicio\')}catch(err){toast(err.message,true)}});\n$(\'#exitForm\').addEventListener(\'submit\',async e=>{e.preventDefault();try{await api(\'/api/exits\',{method:\'POST\',body:JSON.stringify({lot_id:Number($(\'#exitLot\').value),qty:Number($(\'#exitQty\').value),reason:$(\'#exitReason\').value})});$(\'#exitQty\').value=1;toast(\'Salida registrada.\');go(\'inicio\')}catch(err){toast(err.message,true)}});\n$(\'#productForm\').addEventListener(\'submit\',async e=>{e.preventDefault();try{await api(\'/api/products\',{method:\'POST\',body:JSON.stringify({name:$(\'#pName\').value.trim(),price:Number($(\'#pPrice\').value),shelf_life_days:Number($(\'#pLife\').value)})});e.target.reset();toast(\'Producto agregado.\');await refresh()}catch(err){toast(err.message,true)}});\nrefresh(); setInterval(refresh,30000);\n</script></body></html>\n'

raw_db_url = os.getenv("DATABASE_URL", "sqlite:///dulces_momentos.db")
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif raw_db_url.startswith("postgresql://") and "+psycopg" not in raw_db_url:
    raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shelf_life_days = db.Column(db.Integer, nullable=False, default=1)
    emoji = db.Column(db.String(8), nullable=False, default="🍰")
    active = db.Column(db.Boolean, nullable=False, default=True)

class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False, unique=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    qty_in = db.Column(db.Integer, nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    product = db.relationship("Product")

class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("lot.id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(60), nullable=False)
    movement_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    lot = db.relationship("Lot")


def iso(d):
    return d.isoformat() if d else None


def stock_for_lot(lot_id):
    lot = db.session.get(Lot, lot_id)
    if not lot:
        return 0
    out = db.session.query(func.coalesce(func.sum(Movement.qty), 0)).filter(Movement.lot_id == lot_id).scalar() or 0
    return int(lot.qty_in) - int(out)


def status_for(expiry_date):
    days = (expiry_date - date.today()).days
    if days < 0:
        return days, "Vencido", "expired"
    if days == 0:
        return days, "Vence hoy", "today"
    if days == 1:
        return days, "Prioridad alta", "high"
    if days == 2:
        return days, "Por vencer", "warn"
    return days, "Vigente", "ok"


def product_payload(p):
    return {
        "id": p.id,
        "name": p.name,
        "price": float(p.price),
        "shelf_life_days": p.shelf_life_days,
        "emoji": p.emoji,
        "active": p.active,
    }


def lot_payload(l):
    stock = stock_for_lot(l.id)
    days, status, level = status_for(l.expiry_date)
    return {
        "id": l.id,
        "code": l.code,
        "product": product_payload(l.product),
        "qty_in": l.qty_in,
        "stock": stock,
        "entry_date": iso(l.entry_date),
        "expiry_date": iso(l.expiry_date),
        "days_left": days,
        "status": status,
        "level": level,
        "value": round(stock * float(l.product.price), 2),
    }


def seed_defaults():
    if Product.query.count() == 0:
        defaults = [
            Product(name="Pay de manzana", price=4, shelf_life_days=5, emoji="🥧"),
            Product(name="Torta de chocolate", price=5, shelf_life_days=5, emoji="🍫"),
            Product(name="Torta de durazno", price=5, shelf_life_days=5, emoji="🍑"),
            Product(name="Cheesecake de Oreo", price=6, shelf_life_days=7, emoji="🍰"),
        ]
        db.session.add_all(defaults)
        db.session.commit()


@app.get("/")
def index():
    return render_template_string(HTML_PAGE)


@app.get("/api/products")
def get_products():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    return jsonify([product_payload(p) for p in products])


@app.post("/api/products")
def create_product():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    price = data.get("price")
    life = data.get("shelf_life_days")
    if not name or price is None or not life or int(life) < 1:
        return jsonify({"error": "Completa nombre, precio y vida útil."}), 400
    if Product.query.filter(func.lower(Product.name) == name.lower()).first():
        return jsonify({"error": "Ya existe un producto con ese nombre."}), 409
    p = Product(name=name, price=float(price), shelf_life_days=int(life), emoji=(data.get("emoji") or "🍰")[:8])
    db.session.add(p)
    db.session.commit()
    return jsonify(product_payload(p)), 201


@app.get("/api/lots")
def get_lots():
    lots = Lot.query.order_by(Lot.expiry_date.asc(), Lot.created_at.asc()).all()
    return jsonify([lot_payload(l) for l in lots if stock_for_lot(l.id) > 0])


@app.post("/api/entries")
def create_entry():
    data = request.get_json(force=True)
    try:
        product_id = int(data.get("product_id"))
        qty = int(data.get("qty"))
        entry_date = datetime.strptime(data.get("entry_date"), "%Y-%m-%d").date()
    except Exception:
        return jsonify({"error": "Datos de entrada inválidos."}), 400
    product = db.session.get(Product, product_id)
    if not product or qty < 1:
        return jsonify({"error": "Producto o cantidad inválidos."}), 400
    expiry = entry_date + timedelta(days=product.shelf_life_days - 1)
    next_num = (db.session.query(func.max(Lot.id)).scalar() or 0) + 1
    code = f"DM-{next_num:04d}"
    lot = Lot(code=code, product_id=product.id, qty_in=qty, entry_date=entry_date, expiry_date=expiry)
    db.session.add(lot)
    db.session.commit()
    return jsonify(lot_payload(lot)), 201


@app.post("/api/exits")
def create_exit():
    data = request.get_json(force=True)
    try:
        lot_id = int(data.get("lot_id"))
        qty = int(data.get("qty"))
    except Exception:
        return jsonify({"error": "Datos de salida inválidos."}), 400
    lot = db.session.get(Lot, lot_id)
    if not lot or qty < 1:
        return jsonify({"error": "Lote o cantidad inválidos."}), 400
    available = stock_for_lot(lot.id)
    if qty > available:
        return jsonify({"error": f"Solo hay {available} unidad(es) disponibles en este lote."}), 400
    reason = (data.get("reason") or "Venta").strip()
    movement = Movement(lot_id=lot.id, qty=qty, reason=reason, movement_date=date.today())
    db.session.add(movement)
    db.session.commit()
    return jsonify({"ok": True, "stock_remaining": stock_for_lot(lot.id)}), 201


@app.get("/api/dashboard")
def dashboard():
    lots = Lot.query.all()
    stock = warn = expired = 0
    total_value = 0.0
    alerts = []
    for lot in lots:
        qty = stock_for_lot(lot.id)
        if qty <= 0:
            continue
        days, status, level = status_for(lot.expiry_date)
        stock += qty
        total_value += qty * float(lot.product.price)
        if days < 0:
            expired += qty
        elif days <= 2:
            warn += qty
        if days <= 2:
            alerts.append(lot_payload(lot))
    alerts.sort(key=lambda x: (x["days_left"], x["expiry_date"]))
    return jsonify({
        "stock": stock,
        "warn": warn,
        "expired": expired,
        "value": round(total_value, 2),
        "alerts": alerts,
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


with app.app_context():
    db.create_all()
    seed_defaults()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("FLASK_DEBUG") == "1")

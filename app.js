(() => {
  const cfg = window.DM_CONFIG || {};
  const loginScreen = document.getElementById("loginScreen");
  const appShell = document.getElementById("appShell");
  const loginMsg = document.getElementById("loginMsg");

  if (!window.supabase || !cfg.SUPABASE_URL || cfg.SUPABASE_URL.includes("PEGA_AQUI")) {
    loginMsg.innerHTML = '<span class="error">Primero completa config.js con la URL y la clave pública de Supabase.</span>';
    return;
  }

  const sb = window.supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_KEY);
  let products = [], batches = [], sales = [];

  const $ = id => document.getElementById(id);
  const money = n => `S/ ${Number(n || 0).toFixed(2)}`;
  const isoToday = () => new Date().toLocaleDateString("en-CA");
  const fmt = s => s ? new Date(`${s}T00:00:00`).toLocaleDateString("es-PE") : "";
  const esc = s => String(s ?? "").replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

  function daysRemaining(dateStr){
    const a = new Date(`${isoToday()}T00:00:00`);
    const b = new Date(`${dateStr}T00:00:00`);
    return Math.ceil((b-a)/86400000);
  }
  function statusFor(b){
    if (Number(b.qty_available) <= 0) return ["Agotado","agotado"];
    const d = daysRemaining(b.expires_at);
    if (d < 0) return ["Vencido","vencido"];
    if (d <= 1) return ["Por vencer","vence"];
    return ["Vigente","vigente"];
  }
  function productName(id){ return products.find(p => Number(p.id) === Number(id))?.name || "Producto"; }
  function productPrice(id){ return Number(products.find(p => Number(p.id) === Number(id))?.sale_price || 0); }

  window.goSection = function(section){
    document.querySelectorAll(".section").forEach(x => x.classList.toggle("active", x.id === section));
    document.querySelectorAll("[data-section]").forEach(x => x.classList.toggle("active", x.dataset.section === section));
    const names = {inicio:"Inicio",entradas:"Entradas",ventas:"Ventas",inventario:"Inventario",productos:"Productos",reportes:"Reportes",config:"Configuración"};
    $("pageTitle").textContent = names[section] || "Dulces Momentos";
    if(section === "reportes") renderReports();
  };

  document.querySelectorAll("[data-section]").forEach(btn => btn.addEventListener("click", () => goSection(btn.dataset.section)));

  $("todayText").textContent = new Intl.DateTimeFormat("es-PE", {weekday:"long",year:"numeric",month:"long",day:"numeric"}).format(new Date());
  $("inDate").value = isoToday();

  $("loginBtn").addEventListener("click", async () => {
    loginMsg.textContent = "Ingresando...";
    const email = $("loginEmail").value.trim();
    const password = $("loginPassword").value;
    const { error } = await sb.auth.signInWithPassword({ email, password });
    if(error) loginMsg.innerHTML = `<span class="error">${esc(error.message)}</span>`;
  });
  $("loginPassword").addEventListener("keydown", e => { if(e.key === "Enter") $("loginBtn").click(); });
  $("logoutBtn").addEventListener("click", () => sb.auth.signOut());

  async function refreshAll(){
    const [pRes,bRes,sRes] = await Promise.all([
      sb.from("products").select("*").eq("active", true).order("name"),
      sb.from("inventory_batches").select("*").order("expires_at"),
      sb.from("sales").select("*").order("sold_at",{ascending:false}).limit(250)
    ]);
    const err = pRes.error || bRes.error || sRes.error;
    if(err){ alert("No se pudieron cargar los datos: " + err.message); return; }
    products = pRes.data || []; batches = bRes.data || []; sales = sRes.data || [];
    renderAll();
  }

  function renderAll(){
    renderProductOptions();
    renderBatchOptions();
    renderDashboard();
    renderInventory();
    renderProducts();
    renderReports();
  }

  function renderProductOptions(){
    const opts = ['<option value="">Selecciona...</option>', ...products.map(p => `<option value="${p.id}">${esc(p.name)}</option>`)].join("");
    $("inProduct").innerHTML = opts;
  }
  function renderBatchOptions(){
    const available = batches.filter(b => Number(b.qty_available) > 0 && daysRemaining(b.expires_at) >= 0);
    $("saleBatch").innerHTML = ['<option value="">Selecciona...</option>', ...available.map(b => `<option value="${b.id}" data-product="${b.product_id}">${esc(productName(b.product_id))} · lote ${esc(b.lot_code)} · disp. ${b.qty_available}</option>`)].join("");
  }
  $("saleBatch").addEventListener("change", () => {
    const b = batches.find(x => Number(x.id) === Number($("saleBatch").value));
    if(b) $("salePrice").value = productPrice(b.product_id).toFixed(2);
  });

  function rowsFor(list){
    return `<thead><tr><th>Producto</th><th>Lote</th><th>Cantidad</th><th>Ingreso</th><th>Vencimiento</th><th>Días</th><th>Estado</th><th>Precio</th><th>Valor</th></tr></thead><tbody>` +
      list.map(b => {
        const [st,cls] = statusFor(b), d = daysRemaining(b.expires_at), price = productPrice(b.product_id);
        return `<tr><td>${esc(productName(b.product_id))}</td><td>${esc(b.lot_code)}</td><td>${b.qty_available}</td><td>${fmt(b.entered_at)}</td><td>${fmt(b.expires_at)}</td><td>${d}</td><td><span class="badge ${cls}">${st}</span></td><td>${money(price)}</td><td>${money(price*Number(b.qty_available))}</td></tr>`;
      }).join("") + `</tbody>`;
  }
  function renderDashboard(){
    const avail = batches.filter(b => Number(b.qty_available) > 0);
    $("mUnits").textContent = avail.reduce((a,b) => a + Number(b.qty_available), 0);
    $("mSoon").textContent = avail.filter(b => daysRemaining(b.expires_at) >= 0 && daysRemaining(b.expires_at) <= 1).reduce((a,b)=>a+Number(b.qty_available),0);
    $("mExpired").textContent = avail.filter(b => daysRemaining(b.expires_at) < 0).reduce((a,b)=>a+Number(b.qty_available),0);
    $("mValue").textContent = money(avail.reduce((a,b)=>a + productPrice(b.product_id)*Number(b.qty_available),0));
    $("homeTable").innerHTML = rowsFor(avail.slice(0,30));
  }
  function renderInventory(){
    const q = ($("searchInv").value || "").toLowerCase();
    const list = batches.filter(b => !q || productName(b.product_id).toLowerCase().includes(q) || String(b.lot_code).toLowerCase().includes(q));
    $("inventoryTable").innerHTML = rowsFor(list);
  }
  $("searchInv").addEventListener("input", renderInventory);
  $("refreshBtn").addEventListener("click", refreshAll);

  function renderProducts(){
    $("productsTable").innerHTML = `<thead><tr><th>Producto</th><th>Categoría</th><th>Precio venta</th><th>Activo</th></tr></thead><tbody>` +
      products.map(p => `<tr><td>${esc(p.name)}</td><td>${esc(p.category||"")}</td><td>${money(p.sale_price)}</td><td>Sí</td></tr>`).join("") + "</tbody>";
  }
  function renderReports(){
    const today = isoToday();
    const ym = today.slice(0,7);
    const todaySales = sales.filter(s => String(s.sold_at).slice(0,10) === today);
    const monthSales = sales.filter(s => String(s.sold_at).slice(0,7) === ym);
    const total = xs => xs.reduce((a,s)=>a + Number(s.qty)*Number(s.unit_price),0);
    const qty = xs => xs.reduce((a,s)=>a + Number(s.qty),0);
    $("rToday").textContent = money(total(todaySales)); $("rTodayQty").textContent = `${qty(todaySales)} unidades`;
    $("rMonth").textContent = money(total(monthSales)); $("rMonthQty").textContent = `${qty(monthSales)} unidades`;
    $("salesTable").innerHTML = `<thead><tr><th>Fecha</th><th>Producto</th><th>Lote</th><th>Cantidad</th><th>Precio</th><th>Total</th></tr></thead><tbody>` +
      sales.slice(0,100).map(s => {
        const b = batches.find(x => Number(x.id)===Number(s.batch_id));
        return `<tr><td>${new Date(s.sold_at).toLocaleString("es-PE")}</td><td>${esc(productName(s.product_id))}</td><td>${esc(b?.lot_code||"")}</td><td>${s.qty}</td><td>${money(s.unit_price)}</td><td>${money(Number(s.qty)*Number(s.unit_price))}</td></tr>`;
      }).join("") + "</tbody>";
  }

  $("saveProductBtn").addEventListener("click", async () => {
    const name=$("pName").value.trim(), category=$("pCategory").value.trim(), price=Number($("pPrice").value);
    const msg=$("productMsg"); msg.textContent="";
    if(!name || !Number.isFinite(price) || price<0){ msg.innerHTML='<span class="error">Completa nombre y precio.</span>'; return; }
    const {error}=await sb.from("products").insert({name,category,sale_price:price});
    if(error){ msg.innerHTML=`<span class="error">${esc(error.message)}</span>`; return; }
    $("pName").value=""; $("pCategory").value=""; $("pPrice").value="";
    msg.innerHTML='<span class="ok">Producto guardado.</span>'; await refreshAll();
  });

  $("saveEntryBtn").addEventListener("click", async () => {
    const product_id=Number($("inProduct").value), lot_code=$("inLot").value.trim(), qty=Number($("inQty").value),
      unit_cost=$("inCost").value ? Number($("inCost").value) : null, entered_at=$("inDate").value, expires_at=$("inExpiry").value,
      note=$("inNote").value.trim(), msg=$("entryMsg");
    msg.textContent="";
    if(!product_id || !lot_code || !Number.isFinite(qty) || qty<=0 || !entered_at || !expires_at){ msg.innerHTML='<span class="error">Completa producto, lote, cantidad y fechas.</span>'; return; }
    if(expires_at < entered_at){ msg.innerHTML='<span class="error">El vencimiento no puede ser anterior al ingreso.</span>'; return; }
    const {data:{user}}=await sb.auth.getUser();
    const {error}=await sb.from("inventory_batches").insert({product_id,lot_code,qty_initial:qty,qty_available:qty,unit_cost,entered_at,expires_at,note,created_by:user?.id});
    if(error){ msg.innerHTML=`<span class="error">${esc(error.message)}</span>`; return; }
    $("inLot").value=""; $("inQty").value=""; $("inCost").value=""; $("inExpiry").value=""; $("inNote").value="";
    msg.innerHTML='<span class="ok">Entrada guardada.</span>'; await refreshAll();
  });

  $("saveSaleBtn").addEventListener("click", async () => {
    const batch_id=Number($("saleBatch").value), qty=Number($("saleQty").value), unit_price=Number($("salePrice").value), msg=$("saleMsg");
    msg.textContent="";
    if(!batch_id || !Number.isFinite(qty) || qty<=0 || !Number.isFinite(unit_price) || unit_price<0){ msg.innerHTML='<span class="error">Completa lote, cantidad y precio.</span>'; return; }
    const b=batches.find(x => Number(x.id)===batch_id);
    if(!b || qty>Number(b.qty_available)){ msg.innerHTML='<span class="error">La cantidad supera el stock disponible.</span>'; return; }
    const {error}=await sb.rpc("register_sale",{p_batch_id:batch_id,p_qty:qty,p_unit_price:unit_price});
    if(error){ msg.innerHTML=`<span class="error">${esc(error.message)}</span>`; return; }
    $("saleQty").value=""; msg.innerHTML='<span class="ok">Venta registrada y stock descontado.</span>'; await refreshAll();
  });

  sb.auth.onAuthStateChange(async (_event, session) => {
    if(session?.user){
      loginScreen.classList.add("hidden"); appShell.classList.remove("hidden");
      $("userEmail").textContent=session.user.email || "";
      await refreshAll();
    }else{
      appShell.classList.add("hidden"); loginScreen.classList.remove("hidden");
    }
  });

  sb.auth.getSession().then(({data}) => {
    if(!data.session){ loginScreen.classList.remove("hidden"); }
  });
})();

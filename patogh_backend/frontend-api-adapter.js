/* ==========================================================================
   آداپتور اتصال فرانت‌اند «بوک پاتوق» به بک‌اند جنگو
   این بلوک را در book_patogh.html جایگزین توابع هم‌نامش کن:
   loadData, saveBook, deleteBookRemote, savePost, deletePostRemote,
   saveAuthor, deleteAuthorRemote, saveRequest, deleteRequestRemote,
   saveOrder, submitAuth, logoutUser
   و کد ورودِ ادمین در renderAdmin (پایین توضیح داده شده).
   ========================================================================== */

const API_BASE = 'http://127.0.0.1:8000/api'; // آدرس سرور جنگو را اینجا تنظیم کن

function authToken(){ return localStorage.getItem('patough_token'); }
function authHeaders(extra){
  const token = authToken();
  return Object.assign({'Content-Type':'application/json'}, token?{'Authorization':'Token '+token}:{}, extra||{});
}
async function apiFetch(path, options={}){
  const res = await fetch(API_BASE+path, Object.assign({}, options, {
    headers: authHeaders(options.headers),
  }));
  if(!res.ok){
    const body = await res.json().catch(()=>({}));
    throw new Error(body.detail || 'خطا در ارتباط با سرور');
  }
  if(res.status===204) return null;
  return res.json();
}

/* ---------- بارگذاری اولیه‌ی داده‌ها ---------- */
async function loadData(){
  const [books, posts, authors] = await Promise.all([
    apiFetch('/books/'),
    apiFetch('/posts/'),
    apiFetch('/authors/'),
  ]);
  DATA.books = books;
  DATA.posts = posts;
  DATA.authors = authors;
  // درخواست‌ها فقط برای ادمین قابل‌مشاهده‌اند؛ اگر واردشده و ادمین هستیم بگیرشان
  if(authToken() && isAdminAuthed()){
    try { DATA.requests = await apiFetch('/requests/'); } catch(e){ DATA.requests = []; }
  } else {
    DATA.requests = [];
  }
}

/* ---------- کتاب‌ها ---------- */
async function saveBook(book){
  const payload = {
    title: book.title, author: book.author, price: book.price, discount: book.discount,
    category: book.category, category2: book.category2, emoji: book.emoji,
    images: book.images||[], featured: book.featured, description: book.description||'',
  };
  const isNew = !DATA.books.some(b=>b.id===book.id);
  const saved = isNew
    ? await apiFetch('/books/', {method:'POST', body: JSON.stringify(payload)})
    : await apiFetch(`/books/${book.id}/`, {method:'PUT', body: JSON.stringify(payload)});
  Object.assign(book, saved); // مهم: id واقعی ساخته‌شده توسط سرور را برگردان
}
async function deleteBookRemote(id){
  await apiFetch(`/books/${id}/`, {method:'DELETE'});
}

/* ---------- نویسندگان ---------- */
async function saveAuthor(author){
  const payload = {name: author.name, bio: author.bio||''};
  const isNew = !DATA.authors.some(a=>a.id===author.id);
  const saved = isNew
    ? await apiFetch('/authors/', {method:'POST', body: JSON.stringify(payload)})
    : await apiFetch(`/authors/${author.id}/`, {method:'PUT', body: JSON.stringify(payload)});
  Object.assign(author, saved);
}
async function deleteAuthorRemote(id){
  await apiFetch(`/authors/${id}/`, {method:'DELETE'});
}

/* ---------- وبلاگ ---------- */
async function savePost(post){
  const payload = {title: post.title, content: post.content};
  const isNew = !DATA.posts.some(p=>p.id===post.id);
  const saved = isNew
    ? await apiFetch('/posts/', {method:'POST', body: JSON.stringify(payload)})
    : await apiFetch(`/posts/${post.id}/`, {method:'PUT', body: JSON.stringify(payload)});
  Object.assign(post, saved);
}
async function deletePostRemote(id){
  await apiFetch(`/posts/${id}/`, {method:'DELETE'});
}

/* ---------- درخواست‌ها ---------- */
async function saveRequest(req){
  // ثبت درخواست جدید برای همه باز است (نیاز به ورود ندارد)
  const isNew = !DATA.requests.some(r=>r.id===req.id);
  const saved = isNew
    ? await apiFetch('/requests/', {method:'POST', body: JSON.stringify({name:req.name, text:req.text})})
    : await apiFetch(`/requests/${req.id}/`, {method:'PUT', body: JSON.stringify(req)});
  Object.assign(req, saved);
}
async function deleteRequestRemote(id){
  await apiFetch(`/requests/${id}/`, {method:'DELETE'});
}

/* ---------- سفارش‌ها ---------- */
async function saveOrder(order){
  const payload = {
    customer_name: order.customer_name, phone: order.phone,
    postal_code: order.postal_code, address: order.address,
    gateway: 'zarinpal', // آی‌دی درگاه، نه برچسب فارسی‌اش
    total: order.total,
    items: order.items.map(i=>({id: i.id, title: i.title, price: i.price, emoji: i.emoji, qty: i.qty})),
  };
  const saved = await apiFetch('/orders/', {method:'POST', body: JSON.stringify(payload)});
  order.id = saved.id; // شماره سفارش واقعی که سرور ساخته (مثل PB482913)
  return saved;
}

/* ---------- احراز هویت مشتری ---------- */
async function submitAuth(tab){
  const phone = document.getElementById('authEmail').value.trim();
  const pass = document.getElementById('authPass').value.trim();
  const nameInput = document.getElementById('authName');
  const name = nameInput ? nameInput.value.trim() : '';
  if(!phone || !pass){ showToast('لطفاً همه فیلدها را پر کنید'); return; }
  if(tab==='signup' && !name){ showToast('لطفاً نام و نام خانوادگی را وارد کنید'); return; }

  try{
    const data = tab==='signup'
      ? await apiFetch('/auth/signup/', {method:'POST', body: JSON.stringify({name, phone, password: pass})})
      : await apiFetch('/auth/login/', {method:'POST', body: JSON.stringify({phone, password: pass})});
    localStorage.setItem('patough_token', data.token);
    localStorage.setItem('patough_is_staff', data.is_staff ? '1' : '');
    currentUser = data.name;
    closeModal();
    showToast(tab==='signup' ? 'حساب کاربری با موفقیت ساخته شد' : 'با موفقیت وارد شدید');
  }catch(e){
    showToast(tab==='signup' ? 'این شماره قبلاً ثبت‌نام کرده است' : 'شماره یا رمز عبور اشتباه است');
  }
}
function logoutUser(){
  apiFetch('/auth/logout/', {method:'POST'}).catch(()=>{});
  localStorage.removeItem('patough_token');
  localStorage.removeItem('patough_is_staff');
  currentUser = null;
  closeModal();
  showToast('از حساب کاربری خارج شدید');
}

/* ---------- ورود پنل ادمین ----------
   در تابع renderAdmin، بلوک زیر را:

     document.getElementById('loginBtn').onclick = async ()=>{
       const val = document.getElementById('adminPass').value;
       const valHash = await hashPassword(val);
       if(valHash === DATA.passwordHash){ _sessionFlag = true; renderAdmin(hash); }
       else showToast('رمز عبور اشتباه است');
     };

   با این جایگزین کن (رمز را دیگر مرورگر می‌سازد؛ حساب ادمین واقعی روی
   سرور با `python manage.py createsuperuser` ساخته می‌شود؛ به‌عنوان
   «شماره موبایل» همان نام‌کاربری‌ای را بده که به createsuperuser دادی): */
function isAdminAuthed(){ return !!localStorage.getItem('patough_is_staff'); }
/*
   document.getElementById('loginBtn').onclick = async ()=>{
     const phone = document.getElementById('adminPass').value; // این ورودی را به «نام کاربری ادمین» تغییر بده
     try{
       const data = await apiFetch('/auth/login/', {method:'POST', body: JSON.stringify({phone, password: '...'})});
       // بهتر: یک اینپوت جدا برای رمز عبور هم به فرم اضافه کن
       if(!data.is_staff){ showToast('این حساب دسترسی ادمین ندارد'); return; }
       localStorage.setItem('patough_token', data.token);
       localStorage.setItem('patough_is_staff', '1');
       _sessionFlag = true;
       await loadData();
       renderAdmin(hash);
     }catch(e){ showToast('نام کاربری یا رمز عبور اشتباه است'); }
   };
*/

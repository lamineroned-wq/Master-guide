import streamlit as st
import datetime
import pandas as pd
import google.generativeai as genai

# =========================================================================
# 1. طبقة الأمان وحظر النسخ والتحديد (Anti-Copy)
# =========================================================================
st.markdown(
    """
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.keyCode == 123 || 
            (e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 74 || e.keyCode == 67)) || 
            (e.ctrlKey && (e.keyCode == 85 || e.keyCode == 67 || e.keyCode == 83))) {
            return false;
        }
    }
    </script>
    <style>
    body, div, p, span, a, table, h1, h2, h3 {
        -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none;
        direction: rtl; text-align: right;
    }
    @media print { body { display: none; } }
    .stButton>button {
        background-color: #008751 !important; color: white !important;
        border-radius: 8px !important; border: none !important; font-weight: bold !important; width: 100% !important;
    }
    .stButton>button:hover { background-color: #005f38 !important; }
    .store-card { background-color: #f8f9fa; border-right: 5px solid #D21034; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .phone-btn { display: inline-block; background-color: #e6f3ed; color: #008751 !important; padding: 8px 15px; border-radius: 5px; text-decoration: none !important; font-weight: bold; }
    
    /* تصميم بطاقة العضوية الرقمية الاحترافي */
    .id-card { width: 100%; max-width: 400px; background: linear-gradient(135deg, #1e3a8a 0%, #0d1b2a 100%); color: white; border-radius: 15px; padding: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.2); margin: 20px auto; border: 2px solid #008751; }
    .id-header { text-align: center; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; margin-bottom: 15px; }
    .id-title { color: #008751; font-size: 18px; font-weight: bold; margin: 0; }
    .id-field { margin-bottom: 8px; font-size: 14px; }
    .id-label { color: #94a3b8; }
    .id-value { font-weight: bold; color: #f8fafc; }
    .id-footer { margin-top: 15px; text-align: center; background: white; padding: 10px; border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 2. بوابة تسجيل الدخول بالتحقق من ملف users.csv
# =========================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_data"] = {}

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: center; color: #D21034;'>🔐 تسجيل الدخول إلى الدليل الرقمي</h2>", unsafe_allow_html=True)
    input_user = st.text_input("اسم المستخدم (Username):")
    input_pass = st.text_input("كلمة المرور (Password):", type="password")
    
    if st.button("دخول"):
        try:
            # قراءة ملف المشتركين المحدث
            users_df = pd.read_csv("users.csv")
            # التحقق من مطابقة الحساب
            match = users_df[(users_df["username"] == input_user) & (users_df["password"] == input_pass)]
            
            if not match.empty:
                user_info = match.iloc[0]
                expiry_date = datetime.datetime.strptime(user_info["expiry_date"], "%Y-%m-%d").date()
                
                # التحقق من صلاحية اشتراك هذا المستخدم بالتحديد
                if datetime.date.today() > expiry_date:
                    st.error("❌ عذراً، انتهت صلاحية اشتراكك في هذا الدليل. يرجى التواصل مع الإدارة للتجديد.")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["user_data"] = user_info.to_dict()
                    st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")
        except Exception as e:
            st.error("خطأ في نظام الحسابات، يرجى التأكد من رفع ملف users.csv")
    st.stop()

# البيانات الخاصة بالمشترك الحالي بعد نجاح الدخول
current_user = st.session_state["user_data"]

# =========================================================================
# 3. واجهة الدليل بعد الدخول الناجح (تحديث: إضافة الشعار وصورة الواجهة)
# =========================================================================
st.set_page_config(page_title="Master 3 Algérie", layout="wide")

# إنشاء عمودين في الأعلى: واحد للشعار وواحد لعنوان التطبيق
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        # عرض الشعار في زاوية الشاشة بشكل دائري وأنيق
        st.image("logo.png", width=100)
    except:
        pass # في حال لم يتم رفع الصورة بعد، يتخطى الكود الخطأ تلقائياً

with col_title:
    st.markdown(
        f"""
        <div style='text-align: right; padding-top: 10px;'>
            <h1 style='color: #008751; margin: 0; font-size: 28px;'>📱 دليل Master 3 Algérie الرقمي</h1>
            <p style='color: #555; margin: 5px 0 0 0;'>مرحباً بك: {current_user['full_name']} | المركبة الموثقة: {current_user['car_type']}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# عرض صورة الواجهة العريضة (Banner) كفاصل إعلاني فخم تحت الترويسة
try:
    st.image("banner.png", use_container_width=True)
except:
    pass

st.write("---")

    unsafe_allow_html=True
)

# تفعيل محرك الذكاء الاصطناعي (Gemini) - تأكد من إدراج مفتاح الـ API الحر والصحيح هنا
GOOGLE_API_KEY = "AQ.Ab8RN6Ix5-y9wkHP6wTz1Uuwe_rb00L30Z-wGZKOmuo9qPYDiw" 
genai.configure(api_key=GOOGLE_API_KEY)

# =========================================================================
# 4. توليد بطاقة العضوية التلقائية الآمنة (قراءة آلية لبيانات الزبون)
# =========================================================================
st.write("---")
st.write("### 🪪 بطاقة العضوية الرقمية الخاصة بك")
if st.button("إظهار بطاقتي الرسمية الموثقة"):
    member_code = f"M3A-{current_user['username'].upper()}"
    barcode_url = f"https://metafloor.com{member_code}&scale=3&rotate=N&includetext=true"

    st.markdown(
        f"""
        <div class="id-card">
            <div class="id-header">
                <p class="id-title">بطاقة عضوية رقمية موثقة</p>
                <p class="id-subtitle">MASTER 3 ALGÉRIE CLUB</p>
            </div>
            <div class="id-field"><span class="id-label">اسم العضو:</span> <span class="id-value">{current_user['full_name']}</span></div>
            <div class="id-field"><span class="id-label">نوع المركبة:</span> <span class="id-value">{current_user['car_type']}</span></div>
            <div class="id-field"><span class="id-label">رقم العضوية:</span> <span class="id-value" style="color:#008751;">{member_code}</span></div>
            <div class="id-field"><span class="id-label">تاريخ نهاية الاشتراك:</span> <span class="id-value" style="color:#D21034;">{current_user['expiry_date']}</span></div>
            <div class="id-footer">
                <img src="{barcode_url}" style="max-width:100%;">
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================================
# 5. عرض قائمة المحلات والأرقام التفاعلية من ملف stores.csv الخارجي
# =========================================================================
st.write("---")
st.write("### 📍 محطات الخدمات والمحلات التجارية المعتمدة")
try:
    df = pd.read_csv("stores.csv")
    search_query = st.selectbox("اختر الولاية لتصفية المحلات:", ["الكل"] + list(df["الولاية"].unique()))
    
    if search_query != "الكل":
        filtered_df = df[df["الولاية"] == search_query]
    else:
        filtered_df = df

    for index, row in filtered_df.iterrows():
        st.markdown(
            f"""
            <div class="store-card">
                <h3 style="color: #008751; margin-top: 0;">🏢 {row['الاسم']}</h3>
                <p style="color: #333; margin: 5px 0;">📍 <b>الولاية:</b> {row['الولاية']}</p>
                <p style="color: #333; margin: 5px 0;">📞 <b>رقم الهاتف:</b> <a class="phone-btn" href="tel:{row['Telephone']}">📱 {row['Telephone']}</a></p>
                <p style="margin-top: 10px;">🗺️ <b><a href="{row['Location']}" target="_blank" style="color: #D21034; text-decoration: underline;">فتح الموقع على خرائط Google Maps</a></b></p>
            </div>
            """, 
            unsafe_allow_html=True
        )
except Exception as e:
    st.info("جاري تحديث قاعدة بيانات المحلات والأرقام حالياً...")

# =========================================================================
# 6. قسم المستشار الذكي
# =========================================================================
st.write("---")
st.write("### 🤖 استفسار تفاعلي ذكي")
user_query = st.text_input("اسأل المساعد الذكي للدليل عن أي تفاصيل:")
if st.button("إرسال الاستشارة"):
    if user_query:
        with st.spinner("جاري مراجعة الدليل..."):
            try:
                system_instruction = "أنت المساعد الذكي لدليل Master 3 Algérie. أجب باحترافية واختصار حول الخدمات المتاحة فقط."
                model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=system_instruction)
                response = model.generate_content(user_query)
                st.info(response.text)
            except Exception as e:
                st.error("خطأ في الاتصال، يرجى تفقّد مفتاح الـ API الخاص بك.")

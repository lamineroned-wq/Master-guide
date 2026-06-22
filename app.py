import streamlit as st
import datetime
import pandas as pd
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
import os

# =========================================================================
# 1. تأمين المحتوى وحظر النسخ والتحديد (Anti-Copy CSS)
# =========================================================================
st.markdown(
    """
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.keyCode == 123 || (e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 74))) return false;
    }
    </script>
    <style>
    body, div, p, span, a, table, h1, h2, h3, h4 {
        -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none;
        direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    @media print { body { display: none; } }
    .stButton>button {
        background: linear-gradient(135deg, #D21034 0%, #990011 100%) !important;
        color: white !important; border-radius: 30px !important; border: none !important;
        font-weight: bold !important; font-size: 18px !important; padding: 12px 0 !important; width: 100% !important;
    }
    .provider-card {
        background-color: #ffffff; border-right: 6px solid #008751; padding: 15px;
        border-radius: 12px; margin-bottom: 15px; border: 1px solid #eef0f2;
    }
    .phone-link {
        display: inline-block; background-color: #008751; color: white !important;
        padding: 8px 20px; border-radius: 25px; text-decoration: none !important; font-weight: bold; margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 2. إعدادات واجهة التطبيق القياسية
# =========================================================================
st.set_page_config(
    page_title="SOS Road Assistance", 
    page_icon="🚨", 
    layout="wide"
)

# =========================================================================
# 3. بوابة الدخول الآمنة بالتحقق من ملف users.csv
# =========================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_data"] = {}

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: center; color: #111;'>⚠️ SOS Road Assistance</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>الرجاء تسجيل الدخول لتفعيل نظام الاستغاثة الحية</p>", unsafe_allow_html=True)
    input_user = st.text_input("اسم المستخدم (Username):")
    input_pass = st.text_input("كلمة المرور (Password):", type="password")
    
    if st.button("تفعيل النظام الآمن"):
        try:
            users_df = pd.read_csv("users.csv")
            match = users_df[(users_df["username"] == input_user) & (users_df["password"] == input_pass)]
            if not match.empty:
                user_info = match.iloc[0]
                expiry_date = datetime.datetime.strptime(user_info["expiry_date"], "%Y-%m-%d").date()
                if datetime.date.today() > expiry_date:
                    st.error("❌ انتهت صلاحية اشتراكك الفني في نظام الاستغاثة.")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["user_data"] = user_info.to_dict()
                    st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة!")
        except:
            st.error("خطأ في الاتصال بقاعدة البيانات، تأكد من وجود ملف users.csv")
    st.stop()

current_user = st.session_state["user_data"]

# =========================================================================
# 4. تفعيل العداد التلقائي للحماية (30 ثانية)
# =========================================================================
refresh_count = st_autorefresh(interval=30000, key="sos_autorefresh")
if refresh_count > 0:
    st.toast("🔄 تم تحديث الرادار الحركي ومواقع شاحنات السحب...", icon="📡")

# =========================================================================
# 5. الشريط الجانبي الفخم لإدارة العضوية وزر الخروج
# =========================================================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #D21034;'>⚙️ لوحة التحكم</h2>", unsafe_allow_html=True)
    st.write(f"**👤 العضو:** {current_user['full_name']}")
    st.write(f"**🚗 المركبة:** {current_user['car_type']}")
    st.write(f"**📅 نهاية التغطية:** {current_user['expiry_date']}")
    st.write("---")
    
    if st.button("🪪 إظهار بطاقة العضوية الرقمية"):
        member_code = f"SOS-{current_user['username'].upper()}"
        barcode_url = f"https://metafloor.com{member_code}&scale=3&rotate=N&includetext=true"
        
        # عرض بطاقة العضوية مقسمة برمجياً لتفادي أخطاء النصوص المفتوحة
        st.info("💳 بطاقة عضوية رقمية موثقة")
        st.write(f"**رقم الحساب:** {member_code}")
        st.image(barcode_url, caption="باركود التحقق الفني المسحي")
    
    st.write("---")
    if st.button("🚪 تسجيل الخروج من النظام"):
        st.session_state["authenticated"] = False
        st.session_state["user_data"] = {}
        st.rerun()

# =========================================================================
# 6. الواجهة الرئيسية وعرض الخريطة التفاعلية الرادارية
# =========================================================================
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.markdown("<h2 style='color: #111; margin:0;'>📡 رادار الإغاثة الحية بالطرقات</h2>", unsafe_allow_html=True)
    st.write("يقوم النظام بمزامنة أقرب شاحنات السحب (الـ Dépannage) والميكانيكيين المتنقلين تلقائياً.")
with col_logo:
    if os.path.exists("Wallpaper_01.png"):
        st.image("Wallpaper_01.png", width=80)

if os.path.exists("p042391jpg"):
    with open("p042391jpg", "rb") as file:
        st.image(file.read(), use_container_width=True)

user_lat, user_lon = 36.7528, 3.0420

try:
    df = pd.read_csv("stores.csv")
    sos_providers = df[df["الصنف"].isin(["محطة خدمات", "ميكانيك وصيانة", "شاحنة سحب"])]
    
    m = folium.Map(location=[user_lat, user_lon], zoom_start=10, tiles="cartodbpositron")
    
    folium.Marker(
        location=[user_lat, user_lon],
        popup=f"مركبة العضو: {current_user['full_name']}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    
    for index, row in sos_providers.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"🚨 {row['الاسم']} - هاتف: {row['Telephone']}",
            icon=folium.Icon(color="green", icon="wrench")
        ).add_to(m)
        
    st_folium(m, width="100%", height=400, returned_objects=[])
except:
    st.warning("⚠️ جاري مزامنة إحداثيات الأقمار الصناعية للخرائط الحية...")

# =========================================================================
# 7. أزرار الطوارئ وعرض بطاقات مزودي الخدمة المفلترة
# =========================================================================
st.write("---")
if st.button("🔴 اضغط هنا لطلب نجدة عاجلة فوراً"):
    st.error(f"🚨 تم إرسال نداء استغاثة باسم العضو ({current_user['full_name']}) وموقعك الجغرافي لأقرب الدوريات.")

st.write("### 🛠️ مراكز الإنقاذ المتوفرة في نطاقك الجغرافي:")

try:
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sel_state = st.selectbox("تصفية بالولاية:", ["كل الولايات"] + list(df["الولاية"].unique()))
    with col_s2:
        categories = [c for c in df["الصنف"].dropna().unique() if str(c).strip() != ""]
        sel_cat = st.selectbox("نوع المساعدة المطلوبة:", ["كل الأصناف"] + list(categories))
        
    f_df = df.copy()
    if sel_state != "كل الولايات": f_df = f_df[f_df["الولاية"] == sel_state]
    if sel_cat != "كل الأصناف": f_df = f_df[f_df["الصنف"] == sel_cat]
    
    for index, row in f_df.iterrows():
        st.markdown(
            f"""
            <div class="provider-card">
                <h3 style="color: #111; margin: 0; font-size: 18px;">🚨 {row['الاسم']}</h3>
                <p style="color: #666; margin: 8px 0 0 0; font-size: 14px;">📍 <b>النطاق:</b> {row['الولاية']} | 🛠️ <b>الخدمة:</b> {row['الصنف']}</p>
                <a class="phone-link" href="tel:{row['Telephone']}">📞 اتصل فوراً لطلب النجدة</a>
            </div>
            """, 
            unsafe_allow_html=True
        )
except:
    pass

# =========================================================================
# 8. مستشار الطوارئ الذكي (AI Mechanic)
# =========================================================================
st.write("---")
GOOGLE_API_KEY = "ضع_مفتاح_API_الخاص_بك_هنا"  # استبدله بمفتاحك المبتدئ بـ AIzaSy
genai.configure(api_key=GOOGLE_API_KEY)

st.write("### 🤖 مساعد ميكانيكي ذكي للاستشارة السريعة")
user_query = st.text_input("اكتب العطل الذي تلاحظه في سيارتك حالياً:")
if st.button("تحليل العطل الذكي"):
    if user_query:
        with st.spinner("جاري فحص العطل الفني وتقديم نصائح السلامة..."):
            try:
                system_instruction = "أنت المساعد الميكانيكي الخبير لتطبيق SOS Road Assistance. قدم نصائح سلامة وإصلاح سريعة وبنقاط واضحة لحماية السائق."
                model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=system_instruction)
                response = model.generate_content(user_query)
                st.info(response.text)
            except:
                st.error("مفتاح الـ API الحالي غير مفعل في الكود، يرجى كتابة مفتاحك الصحيح.")



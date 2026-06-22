import streamlit as st
import datetime
import pandas as pd
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# =========================================================================
# 1. الهوية البصرية الاحترافية للـ SOS وتأمين المحتوى (CSS & Anti-Copy)
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
    
    /* أزرار الطوارئ الفخمة */
    .stButton>button {
        background: linear-gradient(135deg, #D21034 0%, #990011 100%) !important;
        color: white !important; border-radius: 30px !important; border: none !important;
        font-weight: bold !important; font-size: 18px !important; padding: 12px 0 !important;
        box-shadow: 0px 5px 15px rgba(210, 16, 52, 0.4) !important; width: 100% !important; transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0px 8px 20px rgba(210, 16, 52, 0.6) !important;
    }
    
    /* بطاقات مزودي الخدمة الاحترافية */
    .provider-card {
        background-color: #ffffff; border-right: 6px solid #008751; padding: 18px;
        border-radius: 12px; margin-bottom: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #eef0f2;
    }
    .badge-status {
        background-color: #e6f3ed; color: #008751; padding: 4px 10px;
        border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block;
    }
    .phone-link {
        display: inline-block; background-color: #008751; color: white !important;
        padding: 8px 20px; border-radius: 25px; text-decoration: none !important;
        font-weight: bold; font-size: 14px; margin-top: 10px; box-shadow: 0px 3px 8px rgba(0, 135, 81, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 2. بوابة الدخول الذكية والآمنة (users.csv)
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
            st.error("خطأ في الاتصال بقاعدة البيانات.")
    st.stop()

current_user = st.session_state["user_data"]

# =========================================================================
# 3. إعداد العداد التلقائي (Auto-Refresh) كل 30 ثانية للنسخة الاحترافية
# =========================================================================
refresh_count = st_autorefresh(interval=30000, key="sos_autorefresh")
if refresh_count > 0:
    st.toast("🔄 تم تحديث الرادار الحركي ومواقع شاحنات السحب...", icon="📡")

# =========================================================================
# 4. الشريط الجانبي (Sidebar) لإدارة العضوية والبطاقة الذكية
# =========================================================================
with st.sidebar:
    st.markdown(f"### 👤 الملف الشخصي")
    st.write(f"**العضو:** {current_user['full_name']}")
    st.write(f"**المركبة:** {current_user['car_type']}")
    st.write(f"**نهاية التغطية:** {current_user['expiry_date']}")
    st.write("---")
    
    # ميزة استخراج بطاقة العضوية الإلكترونية داخل الشريط الجانبي الفخم
    if st.button("🪪 إظهار بطاقة العضوية الرقمية"):
        member_code = f"SOS-{current_user['username'].upper()}"
        barcode_url = f"https://metafloor.com{member_code}&scale=3&rotate=N&includetext=true"
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #111 0%, #222 100%); color: white; padding: 15px; border-radius: 12px; border: 1px solid #D21034; text-align: center;">
                <p style="color: #D21034; font-weight: bold; margin:0;">SOS MEMBER CARD</p>
                <p style="font-size: 13px; margin: 5px 0;">{current_user['full_name']}</p>
                <p style="font-size: 11px; color: #aaa; margin: 0;">{current_user['car_type']}</p>
                <div style="background: white; padding: 5px; border-radius: 5px; margin-top: 10px;">
                    <img src="{barcode_url}" style="max-width:100%;">
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================================
# 5. الواجهة الرئيسية: خريطة التتبع الرادارية الكبرى (SOS Map)
# =========================================================================
st.markdown("<h2 style='color: #111; margin:0;'>📡 رادار الإغاثة الحية بالطرقات</h2>", unsafe_allow_html=True)
st.write("يقوم النظام بفحص موقعك ومزامنة أقرب شاحنات السحب (الـ Dépannage) والميكانيكيين المتنقلين تلقائياً.")

# إحداثيات موقع السائق الافتراضية
user_lat, user_lon = 36.7528, 3.0420

try:
    df = pd.read_csv("stores.csv")
    # فرز مقدمي خدمات الإنقاذ الفوري فقط
    sos_providers = df[df["الصنف"].isin(["محطة خدمات", "ميكانيك وصيانة", "شاحنة سحب"])]
    
    # بناء الخريطة التفاعلية الفخمة
    m = folium.Map(location=[user_lat, user_lon], zoom_start=10, tiles="cartodbpositron")
    
    # دبوس السائق (المستغيث) باللون الأحمر التنبيهي
    folium.Marker(
        location=[user_lat, user_lon],
        popup=f"<b>مركبة تعطلت: {current_user['full_name']}</b>",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    
    # دبابيس مقدمي الإغاثة باللون الأخضر
    for index, row in sos_providers.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"<b>🚨 {row['الاسم']}</b><br>📞 {row['Telephone']}<br>🛠️ {row['الصنف']}",
            icon=folium.Icon(color="green", icon="wrench")
        ).add_to(m)
        
    # عرض الخريطة لتملأ شاشة السائق
    st_folium(m, width="100%", height=400, returned_objects=[])

except:
    st.warning("⚠️ جاري مزامنة إحداثيات الأقمار الصناعية للخرائط الحية...")

# =========================================================================
# 6. زر الاستغاثة السريع وجدول التواصل المحمي للإنقاذ الفوري
# =========================================================================
st.write("---")
if st.button("🔴 اضغط هنا لطلب نجدة عاجلة فوراً"):
    st.error(f"🚨 تم إرسال نداء استغاثة باسم العضو ({current_user['full_name']}) وموقعك الجغرافي الحالي لأقرب الدوريات المتوفرة.")

st.write("### 🛠️ مراكز الإنقاذ المتوفرة في نطاقك الجغرافي:")

try:
    # قائمة اختيار مزدوجة سريعة وسلسة للبحث أثناء الطوارئ
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sel_state = st.selectbox("تصفية بالولاية:", ["كل الولايات"] + list(df["الولاية"].unique()))
    with col_s2:
        categories = [c for c in df["الصنف"].dropna().unique() if str(c).strip() != ""]
        sel_cat = st.selectbox("نوع المساعدة المطلوبة:", ["كل الأصناف"] + list(categories))
        
    f_df = df.copy()
    if sel_state != "كل الولايات": f_df = f_df[f_df["الولاية"] == sel_state]
    if sel_cat != "كل الأصناف": f_df = f_df[f_df["الصنف"] == sel_cat]
    
    # عرض بطاقات مزودي الخدمة بتصميم تطبيقات التتبع الحديثة
    for index, row in f_df.iterrows():
        st.markdown(
            f"""
            <div class="provider-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: #111; margin: 0; font-size: 18px;">🚨 {row['الاسم']}</h3>
                    <span class="badge-status">🟢 متوفر للإنقاذ</span>
                </div>
                <p style="color: #666; margin: 8px 0 0 0; font-size: 14px;">📍 <b>النطاق:</b> {row['الولاية']} | 🛠️ <b>الخدمة:</b> {row['الصنف']}</p>
                <a class="phone-link" href="tel:{row['Telephone']}">📞 اتصل فوراً لطلب النجدة</a>
            </div>
            """, 
            unsafe_allow_html=True
        )
except:
    pass

# =========================================================================
# 7. مستشار الطوارئ الذكي (مساعد ميكانيكي مدعوم بالذكاء الاصطناعي)
# =========================================================================
st.write("---")
st.write("### 🤖 مساعد ميكانيكي ذكي للاستشارة السريعة")
user_query = st.text_input("اكتب العطل الذي تلاحظه في سيارتك حالياً (مثال: ارتفاع حرارة المحرك، دخان أبيض):")
if st.button("تحليل العطل الذكي"):


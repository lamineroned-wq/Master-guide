import streamlit as st
import datetime
import pandas as pd
import google.generativeai as genai
import os

# =========================================================================
# 🔴 ضع مفتاح الـ API الخاص بك هنا في أول الكود ليعمل فوراً ومباشرة
# =========================================================================
GOOGLE_API_KEY = "AQ.Ab8RN6K4rQpTHGLPsO-LhokGwNY7-HYQZtEgRo-9JSBspOHrXQ"  # امسح العبارة العربية والصق مفتاحك المبتدئ بـ AIzaSy

# تفعيل محرك الذكاء الاصطناعي الرئيسي
if GOOGLE_API_KEY and GOOGLE_API_KEY != "AQ.Ab8RN6K4rQpTHGLPsO-LhokGwNY7-HYQZtEgRo-9JSBspOHrXQ":
    genai.configure(api_key=GOOGLE_API_KEY)

# =========================================================================
# 1. تأمين واجهة التطبيق وحظر النسخ والتحديد
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

# إعدادات واجهة التطبيق
st.set_page_config(page_title="SOS Road Assistance", page_icon="🚨", layout="wide")

# =========================================================================
# 2. بوابة الدخول الآمنة بالتحقق من ملف users.csv
# =========================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_data"] = {}

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: center;'>⚠️ SOS Road Assistance Map</h2>", unsafe_allow_html=True)
    input_user = st.text_input("اسم المستخدم (Username):", key="login_user")
    input_pass = st.text_input("كلمة المرور (Password):", type="password", key="login_pass")
    
    if st.button("تفعيل رادار الخريطة"):
        try:
            users_df = pd.read_csv("users.csv")
            match = users_df[(users_df["username"] == input_user) & (users_df["password"] == input_pass)]
            if not match.empty:
                st.session_state["authenticated"] = True
                st.session_state["user_data"] = match.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة!")
        except:
            st.error("خطأ في نظام الحسابات.")
    st.stop()

current_user = st.session_state["user_data"]

# =========================================================================
# 3. لوحة التحكم الجانبية (Sidebar)
# =========================================================================
with st.sidebar:
    st.markdown("<h3 style='color: #D21034;'>⚙️ لوحة التتبع</h3>", unsafe_allow_html=True)
    st.write(f"**👤 المستغيث:** {current_user['full_name']}")
    st.write(f"**🚗 المركبة:** {current_user['car_type']}")
    st.write("---")
    
    if st.button("🪪 بطاقة العضوية الرقمية"):
        member_code = f"SOS-{str(current_user['username']).upper()}"
        barcode_url = f"https://metafloor.com{member_code}&scale=3"
        st.info(f"رقم الحساب: {member_code}")
        st.image(barcode_url)

    if st.button("🚪 تسجيل الخروج"):
        st.session_state["authenticated"] = False
        st.session_state["user_data"] = {}
        st.rerun()

# =========================================================================
# 4. الواجهة الرئيسية وعرض الخرائط الرقمية لـ Streamlit
# =========================================================================
st.markdown("<h2 style='color: #111; margin:0;'>📡 رادار الإغاثة الحية بالطرقات (SOS Map)</h2>", unsafe_allow_html=True)

try:
    df = pd.read_csv("stores.csv")
    sel_state = st.selectbox("اختر الولاية لتركيز الرادار الجغرافي:", list(df["الولاية"].unique()))
    f_df = df[df["الولاية"] == sel_state]
    
    if not f_df.empty:
        lat_clean = pd.to_numeric(f_df['latitude'], errors='coerce')
        lon_clean = pd.to_numeric(f_df['longitude'], errors='coerce')
        map_data = pd.DataFrame({'latitude': lat_clean, 'longitude': lon_clean}).dropna()
        st.map(map_data, zoom=10, use_container_width=True)
        st.success("📍 تظهر أمامك الآن نقاط وتمركز طواقم الإنقاذ المتاحة في هذه الولاية.")
    else:
        st.warning("⚠️ لا توجد طواقم مسجلة في هذه الولاية حالياً.")
        
    st.markdown("<div class='provider-card'><h4>🛠️ طواقم الإنقاذ وشاحنات السحب المتوفرة في هذا النطاق:</h4></div>", unsafe_allow_html=True)
    
    for index, row in f_df.iterrows():
        with st.expander(f"🚨 {row['الاسم']} ({row['الصنف']})", expanded=True):
            st.write(f"📞 **رقم الاتصال السريع:** {row['Telephone']}")
            st.markdown(f"<a href='tel:{row['Telephone']}' style='background-color:#008751; color:white; padding:8px 25px; border-radius:20px; text-decoration:none; font-weight:bold; display:inline-block;'>📞 اطلب النجدة فوراً</a>", unsafe_allow_html=True)
            st.markdown(f"[🗺️ فتح في تطبيق الخرائط الخارجي (Google Maps)]({row['Location']})")

except Exception as e:
    st.info("جاري مزامنة رادار الخرائط الرقمية...")

# =========================================================================
# 5. مستشار الطوارئ الفني (AI Mechanic)
# =========================================================================
st.write("---")
st.write("### 🤖 مساعد ميكانيكي ذكي للاستشارة السريعة على الطريق")
user_query = st.text_input("اكتب العطل الفني لمركبتك حالياً:")
if st.button("تحليل العطل"):
    if user_query:
        if GOOGLE_API_KEY == "AQ.Ab8RN6K4rQpTHGLPsO-LhokGwNY7-HYQZtEgRo-9JSBspOHrXQ":
            st.error("يرجى وضع مفتاح الـ API الحقيقي في أول سطر داخل الكود البرمجي ليعمل المستشار.")
        else:
            with st.spinner("جاري مراجعة كتيب السلامة الفني..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"أنت خبير ميكانيكي لتطبيق SOS Road Assistance. قدم نصائح سلامة وإصلاح سريعة ومختصرة جداً بنقاط لعطل السيارة التالي: {user_query}")
                    st.info(response.text)
                except Exception as e:
                    st.error(f"فشل الاتصال بالخادم السحابي: {e}. تأكد من صلاحية المفتاح.")







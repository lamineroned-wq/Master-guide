import streamlit as st
import datetime
import pandas as pd
import google.generativeai as genai

# =========================================================================
# 1. تخصيص الواجهة لتصبح على شكل خريطة كبرى (Full-Screen Map Style)
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
    
    /* جعل حاوية الخريطة تمتد بكامل الأبعاد المتاحة */
    .map-container {
        position: relative;
        width: 100%;
        height: 500px;
        border-radius: 15px;
        overflow: hidden;
        border: 2px solid #D21034;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 20px;
    }
    
    /* تصميم بطاقات الطوارئ العائمة */
    .emergency-panel {
        background: linear-gradient(135deg, #111 0%, #222 100%);
        color: white; padding: 15px; border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0px 5px 15px rgba(210, 16, 52, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# إعدادات الصفحة القياسية المستقرة
st.set_page_config(page_title="SOS Radar Map", page_icon="🚨", layout="wide")

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
    if st.button("🚪 تسجيل الخروج"):
        st.session_state["authenticated"] = False
        st.session_state["user_data"] = {}
        st.rerun()

# =========================================================================
# 4. الواجهة الرئيسية: خريطة رادار الطوارئ الكبرى المدمجة
# =========================================================================
st.markdown("<h2 style='color: #111; margin:0;'>📡 رادار الإغاثة الحية بالطرقات (SOS Map View)</h2>", unsafe_allow_html=True)

# قراءة البيانات لتغذية الخريطة المشتركة بالدبابيس
try:
    df = pd.read_csv("stores.csv")
    
    # فلترة سريعة لتحديد النطاق الجغرافي لعرضه على الخريطة الكبرى
    sel_state = st.selectbox("اختر الولاية لتركيز الرادار الجغرافي:", list(df["الولاية"].unique()))
    f_df = df[df["الولاية"] == sel_state]
    
    # جلب إحداثيات أول محل في الولاية المحددة لتركيز خريطة جوجل عليها تلقائياً
    if not f_df.empty:
        center_lat = f_df.iloc[0]['latitude']
        center_lon = f_df.iloc[0]['longitude']
    else:
        center_lat, center_lon = 36.7528, 3.0420 # الجزائر العاصمة كمركز افتراضي

    # توليد رابط الدمج القياسي لخرائط جوجل الكبرى (تظهر كل المحلات في النطاق)
    google_embed_url = f"https://google.com{center_lat},{center_lon}&z=10&output=embed"
    
    # حقن الخريطة التفاعلية الكبرى لتشغل الواجهة بالكامل بصرياً
    st.markdown(
        f"""
        <div class="map-container">
            <iframe src="{google_embed_url}" width="100%" height="500" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # عرض لوحة عائمة أسفل الخريطة بأسماء وأرقام الهواتف التفاعلية لسرعة الاتصال
    st.markdown("<div class='emergency-panel'><h4>🛠️ طواقم الإنقاذ وشاحنات السحب المتوفرة في هذا النطاق:</h4></div>", unsafe_allow_html=True)
    
    for index, row in f_df.iterrows():
        with st.expander(f"🚨 {row['الاسم']} ({row['الصنف']})", expanded=True):
            st.write(f"📞 **رقم الاتصال السريع:** {row['Telephone']}")
            st.markdown(f"<a href='tel:{row['Telephone']}' style='background-color:#008751; color:white; padding:8px 25px; border-radius:20px; text-decoration:none; font-weight:bold; display:inline-block;'>📞 اطلب النجدة فوراً</a>", unsafe_allow_html=True)

except Exception as e:
    st.info("جاري مزامنة رادار الخرائط الرقمية حالياً...")

# =========================================================================
# 5. مستشار الطوارئ الفني (AI Mechanic)
# =========================================================================
st.write("---")
GOOGLE_API_KEY = "ضع_مفتاح_API_الخاص_بك_هنا"  # ضع مفتاح الـ API الحقيقي هنا ليعمل المستشار الذكي
genai.configure(api_key=GOOGLE_API_KEY)

st.write("### 🤖 مساعد ميكانيكي ذكي للاستشارة السريعة على الطريق")
user_query = st.text_input("اكتب العطل الفني لمركبتك حالياً:")
if st.button("تحليل العطل"):
    if user_query:
        with st.spinner("جاري مراجعة كتيب السلامة الفني..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"قدم نصائح إصلاح وسلامة سريعة ومختصرة جداً بنقاط لعطل السيارة التالي: {user_query}")
                st.info(response.text)
            except:
                st.error("يرجى التأكد من كتابة مفتاح الـ API بشكل صحيح.")






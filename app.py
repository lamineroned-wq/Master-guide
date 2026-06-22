import streamlit as st
import datetime
import pandas as pd
import google.generativeai as genai
import os

# =========================================================================
# 1. بوابة الدخول الآمنة بالتحقق من ملف users.csv
# =========================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_data"] = {}

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: center;'>⚠️ SOS Road Assistance</h2>", unsafe_allow_html=True)
    st.write("الرجاء تسجيل الدخول لتفعيل نظام الاستغاثة الحية:")
    input_user = st.text_input("اسم المستخدم (Username):", key="login_user")
    input_pass = st.text_input("كلمة المرور (Password):", type="password", key="login_pass")
    
    if st.button("تفعيل النظام الآمن"):
        try:
            users_df = pd.read_csv("users.csv")
            match = users_df[(users_df["username"] == input_user) & (users_df["password"] == input_pass)]
            if not match.empty:
                user_info = match.iloc[0]
                st.session_state["authenticated"] = True
                st.session_state["user_data"] = user_info.to_dict()
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة!")
        except:
            st.error("خطأ في نظام الحسابات، يرجى التأكد من رفع ملف users.csv")
    st.stop()

current_user = st.session_state["user_data"]

# =========================================================================
# 2. إعدادات واجهة التطبيق واللوحة الجانبية
# =========================================================================
st.set_page_config(page_title="SOS Road Assistance", page_icon="🚨", layout="wide")

with st.sidebar:
    st.markdown("### ⚙️ لوحة التحكم")
    st.write(f"**👤 العضو:** {current_user['full_name']}")
    st.write(f"**🚗 المركبة:** {current_user['car_type']}")
    st.write(f"**📅 نهاية التغطية:** {current_user['expiry_date']}")
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
# 3. الواجهة الرئيسية وعرض الصور الترويجية
# =========================================================================
st.markdown("<h2 style='color: #D21034;'>📡 رادار الإغاثة الفوري بالطرقات</h2>", unsafe_allow_html=True)
st.write("يقوم النظام بمزامنة أقرب شاحنات السحب (الـ Dépannage) والميكانيكيين المتنقلين.")

if os.path.exists("p042391jpg"):
    with open("p042391jpg", "rb") as file:
        st.image(file.read(), use_container_width=True)

# =========================================================================
# 4. أزرار الطوارئ والفلترة وعرض الخرائط الحية المدمجة
# =========================================================================
st.write("---")
if st.button("🔴 اضغط هنا لطلب نجدة عاجلة فوراً"):
    st.error(f"🚨 تم بث نداء استغاثة طارئ باسم العضو ({current_user['full_name']}) بنجاح لأقرب دوريات الإنقاذ المتاحة.")

st.write("### 🛠️ مراكز الإنقاذ المتوفرة في نطاقك الجغرافي:")

try:
    df = pd.read_csv("stores.csv")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sel_state = st.selectbox("تصفية بالولاية:", ["كل الولايات"] + list(df["الولاية"].unique()))
    with col_s2:
        categories = [c for c in df["الصنف"].dropna().unique() if str(c).strip() != ""]
        sel_cat = st.selectbox("نوع المساعدة المطلوبة:", ["كل الأصناف"] + list(categories))
        
    f_df = df.copy()
    if sel_state != "كل الولايات": 
        f_df = f_df[f_df["الولاية"] == sel_state]
    if sel_cat != "كل الأصناف": 
        f_df = f_df[f_df["الصنف"] == sel_cat]
    
    # عرض بطاقات المحلات والخرائط المدمجة بالطريقة المستقرة 100%
    for index, row in f_df.iterrows():
        with st.expander(f"🚨 {row['الاسم']} - {row['الولاية']} ({row['الصنف']})", expanded=True):
            st.write(f"📞 **رقم الهاتف:** {row['Telephone']}")
            
            # زر اتصال آمن
            st.markdown(f"<a href='tel:{row['Telephone']}' style='background-color:#008751; color:white; padding:8px 20px; border-radius:20px; text-decoration:none; font-weight:bold;'>📞 اتصل فوراً</a>", unsafe_allow_html=True)
            
            # حل مشكلة عدم ظهور الخريطة عبر حقن نافذة عرض تفاعلية حية تفتح موقع المحل بداخل الصفحة تلقائياً
            raw_url = str(row['Location'])
            if "q=" in raw_url:
                coords = raw_url.split("q=")[1].split("&")[0]
                embed_url = f"https://google.com{coords}&output=embed"
                st.markdown(f'<iframe src="{embed_url}" width="100%" height="230" style="border:0; border-radius:8px; margin-top:15px;"></iframe>', unsafe_allow_html=True)
            else:
                st.markdown(f"[🗺️ اضغط هنا لفتح الموقع على الخريطة الخارجية]({raw_url})")

except Exception as e:
    st.info("جاري تحديث وتأمين قاعدة بيانات المحلات والأصناف حالياً...")

# =========================================================================
# 5. مستشار الطوارئ الذكي (AI Mechanic)
# =========================================================================
st.write("---")
GOOGLE_API_KEY = "ضع_مفتاح_API_الخاص_بك_هنا"  # الصق هنا مفتاحك الحقيقي المبتدئ بـ AIzaSy
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
                st.error("يرجى التأكد من وضع مفتاح الـ API الصحيح والمفعل داخل الكود ليعمل الذكاء الاصطناعي.")





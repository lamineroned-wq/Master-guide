import streamlit as st
import datetime
import google.generativeai as genai

# 1. إعدادات الأمان: تاريخ انتهاء الدليل الرقمي لحمايتك
EXPIRATION_DATE = datetime.date(2026, 9, 1) 
current_date = datetime.date.today()

if current_date > EXPIRATION_DATE:
    st.error("❌ عذراً، انتهت فترة صلاحية هذا الدليل الرقمي. يرجى التواصل مع المطور لتجديد الترخيص.")
    st.stop() 

# 2. نظام التحقق وبوابة الدخول لمنع الزبون من مشاركته عشوائياً
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: right; direction: rtl;'>🔐 بوابة الدخول الآمنة للدليل الرقمي</h2>", unsafe_allow_html=True)
    password = st.text_input("أدخل كلمة المرور الخاصة بك للوصول:", type="password")

    if st.button("تسجيل الدخول"):
        if password == "Master3_Algerie_Pass": 
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("خطأ! كلمة المرور غير صحيحة.")
    st.stop()

# 3. إعدادات واجهة الدليل بعد تجاوز بوابة الأمان بنجاح
st.set_page_config(page_title="Master 3 Algérie", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>📱 دليل Master 3 Algérie الرقمي والتفاعلي</h1>", unsafe_allow_html=True)
# 4. ربط وتفعيل محرك الذكاء الاصطناعي (Gemini) المخصص والمقيد
GOOGLE_API_KEY = "AQ.Ab8RN6LkDDFiSlYUOipi9r8rhMvTNYsjsxAwB_JteVox6nQYaQ"
genai.configure(api_key=GOOGLE_API_KEY)

st.write("---")
user_query = st.text_input("اسأل الدليل الرقمي الذكي عن أي معلومة تحتاجها:")

if st.button("استشارة ذكية"):
    if user_query:
        with st.spinner("جاري جلب المعلومات من الدليل..."):
            try:
                # تخصيص تصرف الذكاء الاصطناعي ليكون دليلاً رسمياً فقط لـ Master 3 Algérie
                system_instruction = (
                    "أنت المساعد الذكي الرسمي والخاص بالدليل الرقمي 'Master 3 Algérie'. "
                    "مهمتك هي الإجابة على الأسئلة المتعلقة بالتعليم والتوجيه في الجزائر ومحتويات هذا الدليل فقط. "
                    "أجب بأسلوب احترافي، واضح، وباللغة العربية. "
                    "إذا سألك المستخدم عن مواضيع عامة أو أكواد برمجية أو طبخ أو سياسة أو أي شيء خارج نطاق التعليم والدليل في الجزائر، "
                    "أخبره بلطف: 'عذراً، أنا مبرمج للإجابة على استفسارات دليل Master 3 Algérie التعليمي فقط.'"
                )
                
                # تشغيل النموذج مع التعليمات المخصصة
                model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash', # الإصدار الأحدث والأسرع لتطبيقات الويب
                    system_instruction=system_instruction
                )
                
                response = model.generate_content(user_query)
                st.info(response.text)
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال: {e}")
    else:
        st.warning("الرجاء كتابة استفسارك أولاً.")


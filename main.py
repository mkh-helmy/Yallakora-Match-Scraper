import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# 1. دالة للتحقق من صحة إدخال التاريخ
def validate_date(date_str):
    try:
        valid_date = datetime.strptime(date_str, "%m/%d/%Y")
        return valid_date.strftime("%m/%d/%Y")
    except ValueError:
        return None

# 2. دالة لجلب محتوى الصفحة بأمان
def get_html_content(date):
    url = f"https://www.yallakora.com/match-center/?date={date}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"❌ حدث خطأ أثناء الاتصال: {e}")
        return None

# 3. دالة لاستخراج بيانات المباريات
def extract_matches_data(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    matches_details = []
    
    # البحث عن كل البطولات
    championships = soup.find_all("div", class_="matchCard")
    
    for championship in championships:
        try:
            # استخراج اسم البطولة
            title_tag = championship.find("h2")
            championship_title = title_tag.text.strip() if title_tag else "بطولة غير معروفة"
            
            # جلب كل المباريات داخل البطولة
            all_matches = championship.find_all("div", class_="liItem")
            
            for match in all_matches:
                # أسماء الفرق
                team_a_tag = match.find("div", class_="teamA")
                team_a = team_a_tag.find("p").text.strip() if team_a_tag and team_a_tag.find("p") else "غير معروف"
                
                team_b_tag = match.find("div", class_="teamB")
                team_b = team_b_tag.find("p").text.strip() if team_b_tag and team_b_tag.find("p") else "غير معروف"
                
                # النتيجة (تم استبدال علامة - بعلامة | لتجنب مشكلة التاريخ في الإكسيل)
                match_result = match.find("div", class_="MResult")
                if match_result:
                    scores = match_result.find_all("span", class_="score")
                    score = f"{scores[0].text.strip()} | {scores[1].text.strip()}" if len(scores) >= 2 else "لم تبدأ"
                else:
                    score = "لم تبدأ"
                
                # الميعاد
                time_tag = match.find("span", class_="time")
                match_time = time_tag.text.strip() if time_tag else "غير محدد"
                
                # إضافة البيانات للقائمة كـ Dictionary
                matches_details.append({
                    "نوع البطولة": championship_title,
                    "الفريق الأول": team_a,
                    "الفريق الثاني": team_b,
                    "ميعاد المباراة": match_time,
                    "النتيجة": score
                })
        except Exception as e:
            continue # تخطي أي مباراة بها أخطاء هيكلية وإكمال الباقي

    return matches_details

# 4. دالة لحفظ البيانات في ملف CSV (على شكل جدول)
def save_to_csv(matches_details, filename="matches.csv"):
    if not matches_details:
        print("ℹ️ لا توجد مباريات لحفظها في هذا التاريخ.")
        return
        
    # استخراج أسماء الأعمدة (Headers) من القاموس الأول
    keys = matches_details[0].keys()
    
    try:
        # إنشاء ملف CSV بصلاحية الكتابة 
        with open(filename, "w", encoding="utf-8-sig", newline="") as output_file:
            # استخدام DictWriter لإنشاء الجدول مع فاصلة منقوطة لتوافق الإكسيل العربي
            dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
            
            # كتابة صف العناوين في الأعلى 
            dict_writer.writeheader()
            
            # كتابة باقي الصفوف الخاصة بالبيانات 
            dict_writer.writerows(matches_details)
            
            print(f"🎉 تم استخراج البيانات بنجاح في شكل جدول داخل ملف: {filename}")
    except IOError as e:
        print(f"❌ خطأ أثناء حفظ الملف: {e}")

# 5. الدالة الرئيسية لتشغيل السكريبت
def main():
    while True:
        date_input = input("أدخل التاريخ بصيغة MM/DD/YYYY (مثال 11/23/2022): ")
        valid_date = validate_date(date_input)
        if valid_date:
            break
        print("❌ صيغة خاطئة! يرجى إدخال التاريخ بالصيغة الصحيحة.\n")
        
    html_content = get_html_content(valid_date)
    
    if html_content:
        matches_data = extract_matches_data(html_content)
        save_to_csv(matches_data)

# تشغيل البرنامج
if __name__ == "__main__":
    main()
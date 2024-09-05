from flask import Flask, jsonify,render_template, request
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import google.generativeai as genai


app = Flask(__name__)

scraped_data = {}

@app.route('/')
def firstpage():
    return render_template("frontpage.html")

@app.route('/dashboard')
def dashboard():
    return render_template('home.html',content="welcome")

def friends_problems(username):
    url_main = f"https://www.geeksforgeeks.org/user/{username}/"
    response_main = requests.get(url_main)
    soup_main = BeautifulSoup(response_main.content, "html.parser")
    tot = soup_main.find_all('div',class_ = 'scoreCard_head_left--score__oSi_x')
    p = []
    for e in tot:
        p.append(e.text)
    return p[1]

@app.route('/add-friend', methods=['POST'])
def add_friend():
    data = request.get_json()
    username = data.get('username')

    problems_solved = friends_problems(username)
    if problems_solved:
        return jsonify({
            'success': True,
            'username': username,
            'problems_solved': problems_solved
        })
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404


def scrape_website_data(username):
    url_main = f"https://www.geeksforgeeks.org/user/{username}/"
    response_main = requests.get(url_main)
    soup_main = BeautifulSoup(response_main.content, "html.parser")
    #all q
    res = {"total" :0,"MCS":0,"S":0,"B":0,"E":0,"M":0,"H":0}
    tot = soup_main.find_all('div',class_ = 'scoreCard_head_left--score__oSi_x')
    p = []
    for e in tot:
        p.append(e.text)
    res['total'] = int(p[1])
    if(p[2]=='__'):
        res['MCS'] = p[2]
    easy = soup_main.find_all('div','problemNavbar_head_nav--text__UaGCx')
    d=[]
    for e in easy:
        numbers = re.findall('\d+\.\d+|\d+', e.text)
        d.append(numbers[0])
    res['S'] = int(d[0])
    res['B'] = int(d[1])
    res['E'] = int(d[2])
    res['M'] = int(d[3])
    res['H'] = int(d[4])
    profilename = soup_main.find('div', class_='profilePicSection_head_userHandle__oOfFy').get_text(strip=True)
    #cont
    driver = webdriver.Chrome()
    driver.get("https://www.geeksforgeeks.org/events?itm_source=geeksforgeeks&itm_medium=main_header&itm_campaign=contests")
    driver.implicitly_wait(10)
    html = driver.page_source
    soup_cont = BeautifulSoup(html, 'html.parser')
    main_div = soup_cont.find('div', class_='ui stackable three column grid')
    links=[]
    text =[]
    combined_text = []
    if main_div:
        sections = main_div.find_all('div', class_='five wide computer five wide large screen eight wide mobile seven wide tablet five wide widescreen column')
        for section in sections:
            anchors = section.find_all('a')
            for anchor in anchors:
                links.append(anchor.get('href'))
            for p_tag in soup_cont.find_all('p', class_='sofia-pro eventsLanding_eventCardTitle__byiHw'):
                key = p_tag.get_text(strip=True)
                text.append(key)
            ex = soup_cont.find_all('p', class_='sofia-pro')
            p1_text = ex[1].get_text()
            p2_text = soup_cont.find('p', class_='sofia-pro g-opacity-50').text.strip()
            combined_text.append(p1_text + ' ' + p2_text)
        combined_dict = {links[i]: {text[i]: combined_text[i]} for i in range(len(links))}
    #recent ques
    anchor_dict = {}
    ques_links = []
    for anchor in soup_main.find_all('a', class_='problemList_head_list_item_link__dhmtd'):
        anchor_text = anchor.get_text(strip=True)  # Extract the text
        anchor_link = anchor['href']  # Extract the href link
        ques_links.append(anchor_link)
        anchor_dict[anchor_text] = anchor_link
    #scraped_data
    global scraped_data
    scraped_data = {
        "username":username,
        "val": res,
        "profilename" : profilename,
        "pod" : "https://www.geeksforgeeks.org/problem-of-the-day?itm_source=geeksforgeeks&itm_medium=main_header&itm_campaign=practice_header",
        "cont" : combined_dict,
        "recentques" : anchor_dict
    }
    
    return scraped_data

@app.route('/get_content', methods=['POST'])
def get_content():
    section_id = request.form.get('section_id')
    username = request.form.get('username')

    scrape_data = scrape_website_data(username)

    content = render_template(f'{section_id}.html', username=username,scraped_data=scrape_data)
    
    return jsonify({'content': content})

@app.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    global scraped_data
    API_KEY = 'AIzaSyDmPwXlv1x8P0_yjhJWoqveUf-yN7ueGMg'
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(
        f"The dictionary {scraped_data['val']} contains total questions solved of School(S), Basic(B), Easy(E), Medium(M), Hard(H) levels and a monthly coding score(MCS) meaning no.of submissions in the last month."
        f"This is the list of questions solved by the user: '{scraped_data['recentques']}'."
        "By going through each question, identify which topics of data structure and algorithms they belong to, and find what topic they have a grip on, which topics they need to practice, and what new topics they should move on to next."
        "Provide suggestions for improving their skills.provide text in the format grip on , need practice on , new topics to explore and suggest some resources for the new topics to explore and suggestions for improvement"
    )
    suggestions = response.text
    return jsonify({"suggestions": suggestions})

if __name__ == '__main__':
    app.run(debug=True)


import re, time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def stage_list(StagesSoup) -> list:
    stageList = []
    stagesTable = StagesSoup.find_all(name="table")
    stagesTable = stagesTable[1].find_all(name="tr")
    for stages in stagesTable:
        stage = stages.find_next("td")
        if stage.find_next("td") and stage.find_next("td").getText() == "Review":
            stage = stage.getText()
            stageList.append(stage.strip())
    return stageList

def calc_points(alphas:int, charlies:int, deltas:int, mikes:int, ns:int, proc:int, isMajor) -> int:
    if isMajor:
        charliePoints = 4
        deltaPoints = 2
    else:
        charliePoints = 3
        deltaPoints = 1
    points = int(alphas) * 5 + int(charlies) * charliePoints + int(deltas) * deltaPoints - ((int(mikes) + int(ns) + int(proc)) * 10)
    if points < 0:
        return 0
    return points

def total_points(alphas:int, charlies:int, deltas:int, mikes:int) -> int:
    points = (int(alphas) + int(charlies) + int(deltas) + int(mikes)) * 5
    if points == 0:
        return 1
    return points

def marcel_print(place:int, percent:float, stage:str, time:float, alphas:int, charlies:int, deltas:int, mikes:int, npm:int, ns:int, proc:int, hf:float, division:str) -> None:
    place = int(place)
    if place == 1:
        printString = "Stage Win"
    elif place == 2:
        printString = f"2nd {division} {percent}%"
    elif place == 3:
        printString = f"3rd {division} {percent}%"
    else:
        printString = f"{place}th {division} {percent}%"
    printString += f" - Stage {stage}\nTime: {time}s, {alphas}A, "
    if int(charlies) > 0:
        printString += f"{charlies}C, "
    if int(deltas) > 0:
        printString += f"{deltas}D, "
    if int(mikes) > 0:
        printString += f"{mikes}M, "
    if int(npm) > 0:
        printString += f"{npm}NPM, "
    if int(ns) > 0:
        printString += f"{ns}NS, "
    if int(proc) > 0:
        printString += f"{proc}PROC, "
    printString += f"{float(hf):.4f}HF"
    print (printString)

def find_name(name, results):
    for result in results:
        if name.lower() in result.getText().lower():
            return result
    

url =  input("URL? > ")
firstName = "Marcel"
lastName = "Englmaier"
isMarcel = True
splitURL = url.split("?")
url = splitURL[0].strip()
if isMarcel == "true":
    isMarcel = True
else:
    isMarcel = False

name = f"{lastName}, {firstName}"
# options = Options()
# options.headless = True
#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver = webdriver.Firefox()
options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.get(url)
html = driver.page_source
MySoup = BeautifulSoup(html, "html.parser")
results = MySoup.find_all(name="a", class_="shooterLink")

ShooterID = find_name(name, results)['shooterid']
results = MySoup.find(name="a", shooterid=ShooterID)
overallPlace = re.sub('\D', '', results.getText())
rawLastPlace = MySoup.find_all("a", class_="shooterLink")[-1]
lastPlace = re.sub('\D', '', rawLastPlace.getText())
overallPercent = results.find_next(name="td")
overallPoints = overallPercent.find_next(name="td")
division = overallPoints.find_next(name="td").find_next(name="td").find_next(name="td")

DivisionID = MySoup.find(name="option", text=division.getText())['value']

driver.get(f"{url}?q_division={DivisionID}")
html = driver.page_source
MySoup = BeautifulSoup(html, "html.parser")
results = MySoup.find(name="a", shooterid=ShooterID)
divisionPlace = re.sub('\D', '', results.getText())
rawLastPlace = MySoup.find_all("a", class_="shooterLink")[-1]
divisionLastPlace = re.sub('\D', '', rawLastPlace.getText())
divisionPercent = results.find_next(name="td")
divisionPoints = divisionPercent.find_next(name="td")
totalTime = divisionPoints.find_next(name="td")
percentOfPointsPossible = totalTime.find_next(name="td")
division = percentOfPointsPossible.find_next(name="td")
powerFactor = division.find_next(name="td").find_next("td").find_next("td")
alphas = powerFactor.find_next("td").find_next("td")
charlies = alphas.find_next(name="td").find_next("td")
deltas = charlies.find_next(name="td")
mikes = deltas.find_next(name="td")
NoPM = mikes.find_next(name="td")
NoS = NoPM.find_next(name="td")
Proc = NoS.find_next(name="td")

isMajor = powerFactor.getText().strip() == "MAJOR"

points = calc_points(alphas.getText(), charlies.getText(), deltas.getText(), mikes.getText(), NoS.getText(), Proc.getText(), isMajor)
totalPoints = total_points(alphas.getText(), charlies.getText(), deltas.getText(), mikes.getText())

print(f'''Overall Time {totalTime.getText()}
{divisionPlace}/{divisionLastPlace} {division.getText()} ({float(divisionPercent.getText()):.2f}%)
{overallPlace}/{lastPlace} Overall ({float(overallPercent.getText()):.2f}%)
A {alphas.getText()} C {charlies.getText()} D {deltas.getText()} M {mikes.getText()} NPM {NoPM.getText()} NS {NoS.getText()} PROC {Proc.getText()}
{points}/{totalPoints} ({round(points/totalPoints*100, 2)}%)
''')
print(" ")

driver.get(f"{url}?q_individual={ShooterID}&q_division=0")
html = driver.page_source
MySoup = BeautifulSoup(html, "html.parser")
divisionResults = MySoup.find_all(name="tr", class_="divisionRow")
results = MySoup.find_all(name="tr", class_="overallRow")
stagesPage = MySoup.find(name="a", type="button")['href']
driver.get(stagesPage)
time.sleep(2)
stagesHTML = driver.page_source
StagesSoup = BeautifulSoup(stagesHTML, "html.parser")
stages = stage_list(StagesSoup)

driver.close()

for i in range(len(stages)):
    startingPoint = results[i].find_next("td")
    video = startingPoint.find_next("td")
    place = video.find_next("td")
    percent = place.find_next("td")

    divisionPlace = divisionResults[i].find_next("span").find_next("td").find_next("td")
    divisionPercent = divisionPlace.find_next("td")
    divisionPoints = divisionPercent.find_next("td")
    hitFactor = divisionPoints.find_next("td").find_next("td")
    stageTime = hitFactor.find_next("td")
    powerFactor = stageTime.find_next("td").find_next("td").find_next("td").find_next("td")
    stageAlphas = powerFactor.find_next("td").find_next("td")
    stageCharlies = stageAlphas.find_next("td").find_next("td")
    stageDeltas = stageCharlies.find_next("td")
    stageMikes = stageDeltas.find_next("td")
    stageNPM = stageMikes.find_next("td")
    stageNS = stageNPM.find_next("td")
    stageProc = stageNS.find_next("td")

    place = place.getText()
    if len(place.split()) > 1:
        place = place.split("-")[0]
    
    divisionPlace = divisionPlace.getText()
    if len(divisionPlace.split()) > 1:
        divisionPlace = divisionPlace.split("-")[0]

    totalPoints = calc_points(stageAlphas.getText(), stageCharlies.getText(), stageDeltas.getText(), stageMikes.getText(), stageNS.getText(), stageProc.getText(), isMajor)
    totalPointsPerStage = total_points(stageAlphas.getText(), stageCharlies.getText(), stageDeltas.getText(), stageMikes.getText())
    stagePercentOfTotal = round(totalPoints/totalPointsPerStage * 100,2)

    finalStageName = stages[i]
    if finalStageName[0].isalpha():
        finalStageName = str(i + 1) + ": " + finalStageName

    if isMarcel:
        marcel_print(divisionPlace, divisionPercent.getText().strip(), finalStageName, stageTime.getText().strip(), stageAlphas.getText(), stageCharlies.getText(), 
        stageDeltas.getText(), stageMikes.getText(), stageNPM.getText(), stageNS.getText(), stageProc.getText(), hitFactor.getText(), division.getText())
    else:
        print(f'''
{finalStageName}
{divisionPlace.strip()}/{divisionLastPlace} {division.getText()} ({float(divisionPercent.getText()):.2f}%)
{place.strip()}/{lastPlace} Overall ({float(percent.getText()):.2f}%)
Time {stageTime.getText()}, HF {float(hitFactor.getText()):.4f}
A {stageAlphas.getText()} C {stageCharlies.getText()} D {stageDeltas.getText()} M {stageMikes.getText()} NPM {stageNPM.getText()} NS {stageNS.getText()} PROC {stageProc.getText()}
{totalPoints}/{totalPointsPerStage} ({float(stagePercentOfTotal):.2f}%)''')
    print(" ")
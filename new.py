import requests

matchCode = input("Match code (Code from URL such as 01e65294-8692-4adf-9897-29dc01a68360)? > ")
firstName = input("First name? > ")
lastName = input("Last name? >")


def get_shooterID(matchCode, lastName, firstName):
    response = requests.get(f"https://s3.amazonaws.com/ps-scores/production/{matchCode}/match_def.json").json()['match_shooters']
    for shooter in response:
        if shooter['sh_ln'] == lastName and shooter['sh_fn'] == firstName:
            return { 
                "id": shooter['sh_uuid'], 
                "class": shooter['sh_dvp']
              }


def get_stage_place(matchCode, shooter):
    shooterClass = shooter['class']
    shooterID = shooter['id']
    response = requests.get(f'https://s3.amazonaws.com/ps-scores/production/{matchCode}/results.json').json()
    stageInfo = []
    for i in range(1, len(response)):
        stageName = list(response[i].keys())[1]
        for div in response[i][stageName]:
            if shooterClass in div:
                for shooter in div[shooterClass]:
                    if shooter['shooter'] == shooterID:
                        info = {
                            "name": stageName, 
                            "place": shooter['place'], 
                            "percent": shooter['stagePercent'], 
                            "hitFactor": shooter['hitFactor']
                            }
                        stageInfo.append(info)
    return stageInfo


def find_scores(matchCode, shooter):
    response = requests.get(f"https://s3.amazonaws.com/ps-scores/production/{matchCode}/match_scores.json").json()
    totalScores = []
    shooterID = shooter['id']
    for stage in response['match_scores']:
        for shooter in stage['stage_stagescores']:
            if shooter['shtr'] == shooterID:
                rawScores = shooter['ts']
                scores = {
                    'A': 0,
                    'C': 0,
                    'D': 0,
                    'M': 0,
                    'NPM': 0,
                    'NS': 0,
                    'PROC': 0,
                    'time': 0
                }
                for timeInSec in shooter['str']:
                    scores['time'] += timeInSec
                if 'proc' in shooter:
                    scores['PROC'] += shooter['proc']
                scores['A'] += shooter['poph']
                scores['M'] += shooter['popm']
                for score in rawScores:
                    # alpha = 1
                    # charlie = 256
                    # delta = 4096
                    # ns = 65536
                    # mike = 1048577
                    # npm = 16777216
                    scores['NPM'] += score // 16777216
                    score %= 16777216
                    scores['M'] += score // 1048576
                    score %= 1048576
                    scores['NS'] += score // 65536
                    score %= 65536
                    scores['D'] += score // 4096
                    score %= 4096
                    scores['C'] += score // 256
                    score %= 256
                    scores['A'] += score
                totalScores.append(scores)   
    return totalScores


def marcel_print(stages, scores, shooter):
    for i in range(len(scores)):
        place = stages[i]['place']
        shooterClass = shooter['class'] 
        percent = stages[i]['percent']
        stage = stages[i]['name']
        time = scores[i]['time']
        if place == 1:
            printString = "Stage Win"
        elif place % 10 == 1 and place > 20:
            printString = f"{place}st {shooterClass} {percent}%"
        elif place % 10 == 2 and (place > 20 or place < 10):
            printString = f"{place}nd {shooterClass} {percent}%"
        elif place % 10 == 3 and (place > 20 or place < 10):
            printString = f"{place}rd {shooterClass} {percent}%"
        else:
            printString = f"{place}th {shooterClass} {percent}%"
        printString += f" - {stage}\nTime: {time}s, "
        for key in scores[i]:
            if scores[i][key] > 0 and key != "time":
                printString += f"{scores[i][key]}{key}, "
        printString += f"{float(stages[i]['hitFactor']):.4f}HF\n\n"
        print(printString)


shooterInfo = get_shooterID(matchCode, lastName, firstName)

stagePlace = get_stage_place(matchCode, shooterInfo)
scores = find_scores(matchCode,shooterInfo)

marcel_print(stagePlace, scores, shooterInfo)
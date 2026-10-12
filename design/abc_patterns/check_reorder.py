"""選択肢の並べ替え事故の検出：誤答解説が、その番号の選択肢ではなく別の選択肢の語を多く含んでいないか。"""
import json,glob,sys
def grams(t): return {t[i:i+2] for i in range(len(t)-1)}
for f in sorted(glob.glob(sys.argv[1]+'/out/*.json')):
    for q in json.load(open(f,encoding='utf-8')):
        ch=q['choices']
        for k,txt in q['wrongChoiceExplanations'].items():
            sc=[len(grams(c)&grams(txt))/max(1,len(grams(c))) for c in ch]
            best=max(range(4),key=lambda i:sc[i])
            if best!=int(k) and sc[best]-sc[int(k)]>0.25:
                print(q['id'],'誤答解説',k,'は選択肢',best,'の説明に見える',[round(s,2) for s in sc])
        c=q['correctAnswers'][0]
        sc=[len(grams(x)&grams(q['explanation']))/max(1,len(grams(x))) for x in ch]
        if max(range(4),key=lambda i:sc[i])!=c and max(sc)-sc[c]>0.3:
            print(q['id'],'解説が正解以外の選択肢',max(range(4),key=lambda i:sc[i]),'を指している？',[round(s,2) for s in sc])

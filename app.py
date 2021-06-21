from flask import Flask,render_template,request, url_for
import numpy as np
import cv2
import math
import os
import base64
import mysql.connector
import random
from PIL import ImageFont, ImageDraw, Image


import numpy as np






app = Flask(__name__)
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData
def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
      # I assume you have a way of picking unique filenames


    with open(filename, 'wb') as file:
        file.write(data)

@app.route('/insert')
def insert():
    idmatiere=request.args.get('path')
    print("Oui")
    db = mysql.connector.connect(host="127.0.0.1", user='root', password='', db='exams')
    c  = db.cursor()
    files= os.listdir('examss/')
    lst=[]
    for file in files:


        img = cv2.imread('examss/'+file)

        # horizontal
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 120)
        lines = cv2.HoughLinesP(edges, 1, math.pi / 2, 2, None, 30, 1);
        imgh = img
        for line in lines[0]:
            pt1 = (line[0], line[1])
            pt2 = (line[2], line[3])
            cv2.line(imgh, pt1, pt2, (0, 0, 255), 3)
        crop_img = imgh[0:line[0], 0:imgh.shape[1]]
        # extract head region
        cv2.imwrite('segments/head.jpg', crop_img)


        # vertical
        img = cv2.imread('examss/'+file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 120)
        lines1 = cv2.HoughLinesP(edges, 1, math.pi, 2, None, 30, 1);
        imgv = img
        for line1 in lines1[0]:
            pt1 = (line1[0], line1[1])
            pt2 = (line1[2], line1[3])
            cv2.line(imgv, pt1, pt2, (0, 0, 255), 3)

        crop_right = imgv[line1[3]:line1[1], line1[0]:imgv.shape[1]]
        cv2.imwrite('segments/right.jpg', crop_right)

        crop_left = imgv[line1[3]:line1[1], 0:line1[0]]
        cv2.imwrite('segments/left.jpg', crop_left)

        roi_right=convertToBinaryData('segments/right.jpg')
        roi_left=convertToBinaryData('segments/left.jpg')
        roi_img=convertToBinaryData('segments/head.jpg')
        roi_full=convertToBinaryData('examss/'+file)

        c.execute("SELECT distinct ID_PROF FROM EST_RESPONSABLE WHERE ID_MATIERE="+idmatiere)

        rowmat = c.fetchall()
        dicmat = dict()
        # dicmat['idmat'] = []
        dicmat['idprof'] = []
        for rowm in rowmat:
        #     dicmat['idmat'].append(str(rowm[0]))
            dicmat['idprof'].append(rowm[0])
        print(str(len(dicmat['idprof'])) + "-----------------------------------")


        n=random.randint(0,max(dicmat['idprof']))

        c.execute("INSERT INTO scan (`ID_MATIERE`, `ID_PROF`,`PJ1`,`PJ2`,`PJ3`, `full_img`, `AFFECTATION`, `CORRIGE`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)" , (idmatiere,n,roi_left,roi_right,roi_img,roi_full,1,0))
        db.commit()
    return 0
@app.route('/matieres')
def matieres():


     db = mysql.connector.connect(host="127.0.0.1", user="root", password='', db="exams")
     c = db.cursor()

     c.execute("SELECT ID_MATIERE,NOM_MATIERE, NB_QST_REDACTION FROM MATIERE")

     rows=c.fetchall()
     dic=dict()
     dic['idmat']=[]
     dic['mat']=[]
     dic['nb']=[]
     for row in rows:
         dic['idmat'].append(str(row[0]))
         dic['mat'].append(row[1])
         dic['nb'].append(row[2])


     return render_template('matieres.html', dicr=dic, lenght=len(dic['idmat']))

@app.route('/MatieresAdmin')
def matieresAdmin():


     db = mysql.connector.connect(host="127.0.0.1", user="root", password='', db="exams")
     c = db.cursor()

     c.execute("SELECT ID_MATIERE,NOM_MATIERE, NB_QST_REDACTION FROM MATIERE")

     rows=c.fetchall()
     dic=dict()
     dic['idmat']=[]
     dic['mat']=[]
     dic['nb']=[]
     for row in rows:
         dic['idmat'].append(str(row[0]))
         dic['mat'].append(row[1])
         dic['nb'].append(row[2])


     return render_template('MatieresAdmin.html', dicr=dic, lenght=len(dic['idmat']))


@app.route('/copies')
def copies():
    path=request.args.get('path')

    db = mysql.connector.connect(host="127.0.0.1", user="root", password='', db="exams")
    c = db.cursor()

    c.execute("SELECT ID_SCAN FROM scan where CORRIGE=0 and ID_MATIERE="+str(path))


    rows=c.fetchall()
    dic=dict()
    dic['idscan']=[]
    for row in rows:
        dic['idscan'].append(str(row[0]))
    longueur=len(dic['idscan'])




    return render_template('copies.html',dicr=dic, lenght=longueur)



@app.route('/splice', methods=['GET', 'POST'])
def splice():
    id=request.args.get('path')

    db = mysql.connector.connect(host="127.0.0.1", user="root", password='', db="exams")

    c = db.cursor()


    c.execute("SELECT PJ2,ID_MATIERE FROM scan where ID_SCAN="+str(id))
    row = c.fetchone()
    binary=row[0]
    idmat=row[1]

    c.execute("SELECT NB_QST_REDACTION FROM matiere where ID_MATIERE=" + str(idmat))
    row = c.fetchone()
    nb = row[0]
    write_file(binary,'forsplit/split.jpg')
    # print(str(binary)+'testprint')
    #
    #
    #
    # img = cv2.imread('forsplit/split.jpg')
    #
    # # horizontal
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # edges = cv2.Canny(gray, 80, 120)
    # lines = cv2.HoughLinesP(edges, 1, math.pi / 2, 2, None, 30, 1);
    # imgh = img
    # for line in lines[0]:
    #     pt1 = (line[0], line[1])
    #     pt2 = (line[2], line[3])
    #     cv2.line(imgh, pt1, pt2, (0, 0, 255), 3)
    # crop_img = imgh[0:line[0], 0:imgh.shape[1]]
    # # extract head region
    # cv2.imwrite('segments/head.jpg', crop_img)
    #
    # # vertical
    # img = cv2.imread("examss/copie_2_python.jpg")
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # edges = cv2.Canny(gray, 80, 120)
    # lines1 = cv2.HoughLinesP(edges, 1, math.pi, 2, None, 30, 1);
    # imgv = img
    # for line1 in lines1[0]:
    #     pt1 = (line1[0], line1[1])
    #     pt2 = (line1[2], line1[3])
    #     cv2.line(imgv, pt1, pt2, (0, 0, 255), 3)
    #
    # crop_right = imgv[line1[3]:line1[1], line1[0]:imgv.shape[1]]
    # cv2.imwrite('segments/right.jpg', crop_right)
    #
    # crop_left = imgv[line1[3]:line1[1], 0:line1[0]]
    # cv2.imwrite('segments/left.jpg', crop_left)
    #
    # vis = np.concatenate((crop_left, crop_right), axis=1)
    # cv2.imwrite('splice/spliced.jpg', vis)
    empPicture = convertToBinaryData('forsplit/split.jpg')

    image = base64.b64encode(empPicture).decode("utf-8")




    return render_template('test2.html',value=image,nbqst=nb)

@app.route('/finalsplice', methods=['POST'])
def finalsplice():

    nbqst=request.args.get('nb')

    lst=[]

    for i in range(int(nbqst)):
        path = request.form['q'+str(i)]
        print(path)
        lst.append(str(path))

    result = cv2.imread('templatefolder/testexamreal.jpeg')

    ###########num-dif 43-9
    firstnumx = 96
    firstnumy = 78 + 43 - 9

    secondnumx = 144
    secondnumy = 78 + 43 - 9

    ##############question-dif 43
    qst1x1 = 58
    qst1y1 = 67 + 43

    qst1x2 = 94
    qst1y2 = 78 + 43

    qst2x1 = 110
    qst2y1 = 67 + 43

    qst2x2 = 142
    qst2y2 = 78 + 43

    #################cases dif 43 -dif 12 between near cases
    case1x1 = 66
    case1y1 = 83 + 43
    case1x2 = 75
    case1y2 = 91 + 43

    case2x1 = 66
    case2y1 = 95 + 43
    case2x2 = 75
    case2y2 = 103 + 43
    ##################false-true#####dif-43
    ftx1 = 77
    fty1 = 81 + 43

    ftx2 = 97
    fty2 = 105 + 43

    for i in range(len(lst)):
        if i == 0:
            if lst[i] == 'true':

                cv2.rectangle(result, (66, 95), (75, 103), (0, 0, 0), -1)

            else:
                cv2.rectangle(result, (66, 83), (75, 91), (0, 0, 0), -1)
        else:
            result[qst1y1:qst1y2, qst1x1:qst1x2] = result[67:78, 58:94]
            result[qst2y1:qst2y2, qst2x1:qst2x2] = result[67:78, 110:142]
            result[fty1:fty2, ftx1:ftx2] = result[81:105, 77:97]
            if lst[i] == 'true':
                cv2.rectangle(result, (case2x1, case2y1), (case2x2, case2y2), (0, 0, 0), -1)
                cv2.rectangle(result, (case1x1, case1y1), (case1x2, case1y2), (0, 0, 0), 1)
            else:
                cv2.rectangle(result, (case2x1, case2y1), (case2x2, case2y2), (0, 0, 0), 1)
                cv2.rectangle(result, (case1x1, case1y1), (case1x2, case1y2), (0, 0, 0), -1)

            qst1y1 = qst1y1 + 43

            qst1y2 = qst1y2 + 43

            qst2y1 = qst2y1 + 43

            qst2y2 = qst2y2 + 43

            #################cases dif 43 -dif 12 between near cases

            case1y1 = case1y1 + 43

            case1y2 = case1y2 + 43

            case2y1 = case2y1 + 43

            case2y2 = case2y2 + 43
            ##################false-true#####dif-43

            fty1 = fty1 + 43

            fty2 = fty2 + 43

    #######################numbers
    cv2_im_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    # Pass the image to PIL
    pil_im = Image.fromarray(cv2_im_rgb)

    draw = ImageDraw.Draw(pil_im)
    font = ImageFont.truetype("arial.ttf", 7)
    font2 = ImageFont.truetype("arial.ttf", 6)

    for i in range(len(lst)):
        if i != 0:
            draw.text((firstnumx, firstnumy), str(i + 1), font=font, fill=(0, 0, 0))
            draw.text((secondnumx, secondnumy), str(i + 1), font=font2, fill=(0, 0, 0))

            firstnumy = firstnumy + 43
            secondnumy = secondnumy + 43

    result = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
    cv2.imwrite('redaction/corrected.jpg',result)





















    return "hello"













if __name__ == '__main__':
    app.run()

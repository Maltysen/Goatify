from flask import Flask, render_template, request, Response, send_file, after_this_request
import os
import time
import subprocess
import random
import script2

app = Flask(__name__, template_folder='.', static_folder='.')

@app.route('/')
def root():
    return render_template("index.html")

sndDir = 'sndFiles/'
@app.route('/goatify', methods=['POST'])
def goatify():
    inName = sndDir+repr(random.random())[2:]
    karName = sndDir+repr(random.random())[2:]
    outName = sndDir+repr(random.random())[2:]

    request.files["song"].save(inName+".wav")
    script2.do_goat(inName+".wav", outName+".wav", request.form.get("double")=="1")

    if "kareoke" in request.files:
        request.files["kareoke"].save(karName+".wav")
        os.system("ffmpeg -y -i %s.wav -i %s.wav -filter_complex amerge -ac 2 -c:a libmp3lame -q:a 4 %s.mp3" %(outName, karName, outName))

    else:
        os.system("ffmpeg -i %s.wav %s.mp3"%(outName, outName))

    resp = send_file(outName+".mp3", as_attachment = True)
    resp.headers["x-filename"] = "goatified.mp3"
    resp.headers["Access-Control-Expose-Headers"] = 'x-filename'

    @after_this_request
    def clean_up(response):
        os.remove(inName+".wav")
        os.remove(outName+".wav")
        os.remove(outName+".mp3")
        return response

    return resp

@app.route('/favicon.png')
def logo():
    return send_file("favicon.png")

@app.route('/style.css')
def style():
    return send_file("style.css")

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

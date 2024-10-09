import fastapi
from fastapi import FastAPI
from starlette.responses import StreamingResponse
import uvicorn
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import cv2
import threading

dash_app = Dash(__name__)

dash_app.layout = html.Div([
    html.H1(children='HALLO', style={'textAlign': 'center'}),
    html.Img(id='video-stream', src="/video_feed", style={'width': '640px', 'height': '480px'})
])

# Initialize FastAPI for handling OpenCV video stream
fastapi_app = FastAPI()
cap = cv2.VideoCapture(1)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# FastAPI route to stream video
@fastapi_app.get('/video_feed')
async def video_feed():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

# Run FastAPI and Dash in parallel
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    # Start FastAPI in a separate thread for handling video stream
    thread = threading.Thread(target=run_fastapi)
    thread.start()

    # Run Dash app
    dash_app.run_server(debug=True, use_reloader=False)

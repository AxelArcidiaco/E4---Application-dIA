# Importation des bibliothèques reqquises
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import uvicorn
import os

app = FastAPI()

# Load the trained models
vgg16_model = load_model("VGG16-model-classification-maladie-retine.h5")
# inceptionv3_model = load_model("InceptionV3-model-classification-maladie-retine.h5")

# Route de l'api qui gère la classification des images oct envoyé par la web app
@app.post("/classify/")
async def classify_image(file: UploadFile = File(...)):
    contents = await file.read()
    with open("temp_image.jpg", "wb") as f:
        f.write(contents)

    image = load_img("temp_image.jpg", target_size=(150, 150))
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = image / 255.0

    # You can choose which model to use for classification
    prediction = vgg16_model.predict(image)
    class_idx = np.argmax(prediction[0])
    class_labels = ["Normal", "CNV", "DME", "Drusen"]

    result = class_labels[class_idx]
    os.remove("temp_image.jpg")
    return JSONResponse(content={"result": result})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

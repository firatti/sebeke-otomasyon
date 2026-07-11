import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates
import cv2
import numpy as np
import math

st.set_page_config(layout="wide")
st.title("⚡ Kararlı & Kesintisiz Şebeke Tasarımı")

# --- Görseli Yükle ---
if "img_np" not in st.session_state:
    try:
        img = Image.open("uydu_goruntusu.jpg")
        st.session_state["img_np"] = np.array(img)
    except:
        st.session_state["img_np"] = np.zeros((600, 1000, 3), dtype=np.uint8) + 100

H, W, _ = st.session_state["img_np"].shape
PIKSEL_BASINA_METRE = 0.25

# --- Hafıza Yönetimi ---
if "trafo" not in st.session_state: st.session_state["trafo"] = None
if "hat" not in st.session_state: st.session_state["hat"] = []
if "evler" not in st.session_state: st.session_state["evler"] = []

def mesafe_hesapla(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def direkleri_hesapla(hat_noktalari, direk_araligi_metre=40.0):
    if len(hat_noktalari) < 2: return []
    adim_piksel = direk_araligi_metre / PIKSEL_BASINA_METRE
    direkler = [hat_noktalari[0]]
    kalan_mesafe = adim_piksel
    
    for i in range(len(hat_noktalari) - 1):
        p1, p2 = hat_noktalari[i], hat_noktalari[i+1]
        sz = mesafe_hesapla(p1, p2)
        while sz >= kalan_mesafe:
            t = kalan_mesafe / sz
            yeni_x = int(p1[0] + t * (p2[0] - p1[0]))
            yeni_y = int(p1[1] + t * (p2[1] - p1[1]))
            direkler.append((yeni_x, yeni_y))
            p1 = (yeni_x, yeni_y)
            sz = mesafe_hesapla(p1, p2)
            kalan_mesafe = adim_piksel
        kalan_mesafe -= sz
    return direkler

# --- Arayüz Seçimleri ---
mod = st.radio("İşlem Modu Seçin:", ("Trafo Konumu (TR)", "Hat Güzergahı (Mavi Hat)", "Ev Konumları (Yeşil Kare)"), horizontal=True)

open_cv_image = st.session_state["img_np"].copy()
direk_noktalari = direkleri_hesapla(st.session_state["hat"])

if st.session_state["trafo"]:
    cv2.circle(open_cv_image, st.session_state["trafo"], 10, (255, 0, 0), -1)
if len(st.session_state["hat"]) > 1:
    cv2.polylines(open_cv_image, [np.array(st.session_state["hat"])], isClosed=False, color=(255, 0, 0), thickness=2)
for drk in direk_noktalari:
    cv2.circle(open_cv_image, drk, 6, (0, 255, 255), -1)
for ev in st.session_state["evler"]:
    cv2.rectangle(open_cv_image, (ev[0]-8, ev[1]-8), (ev[0]+8, ev[1]+8), (0, 255, 0), -1)

drawn_img = Image.fromarray(open_cv_image)
value = streamlit_image_coordinates(drawn_img, key="harita_tıklama")

if value:
    point = (value["x"], value["y"])
    
    if "Trafo" in mod and st.session_state["trafo"] != point:
        st.session_state["trafo"] = point
        st.rerun()
    elif "Hat" in mod and (len(st.session_state["hat"]) == 0 or st.session_state["hat"][-1] != point):
        st.session_state["hat"].append(point)
        st.rerun()
    elif "Ev" in mod and (len(st.session_state["evler"]) == 0 or st.session_state["evler"][-1] != point):
        st.session_state["evler"].append(point)
        st.rerun()

if st.button("Seçimleri Temizle"):
    st.session_state["trafo"], st.session_state["hat"], st.session_state["evler"] = None, [], []
    st.rerun()
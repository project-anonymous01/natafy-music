"""
NATAFY - Backend Server
Flask API untuk platform streaming musik
Deploy: Vercel Serverless
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import time
import random
from datetime import datetime
from collections import defaultdict, Counter

# ==================== INISIALISASI ====================
app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ==================== STORAGE (In-Memory untuk Vercel) ====================
# Vercel adalah stateless serverless — data reset tiap cold start.
# Untuk persistensi, gunakan Supabase / PlanetScale / Upstash Redis.
_store = {
    'users': {},
    'history': [],
    'preferences': {},
    'playlists': {},
    'stats': {}
}

def load_data():
    return _store

def save_data(data):
    _store.update(data)

# ==================== DATA MUSIK ====================

ARTISTS_DATA = [
    {"id": "a1", "name": "Taylor Swift", "genre": ["pop", "country"], "image": "https://i.pravatar.cc/150?img=1"},
    {"id": "a2", "name": "Ed Sheeran", "genre": ["pop", "acoustic"], "image": "https://i.pravatar.cc/150?img=2"},
    {"id": "a3", "name": "Coldplay", "genre": ["alternative", "rock"], "image": "https://i.pravatar.cc/150?img=3"},
    {"id": "a4", "name": "Billie Eilish", "genre": ["pop", "indie"], "image": "https://i.pravatar.cc/150?img=4"},
    {"id": "a5", "name": "The Weeknd", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=5"},
    {"id": "a6", "name": "Dua Lipa", "genre": ["pop", "dance"], "image": "https://i.pravatar.cc/150?img=6"},
    {"id": "a7", "name": "Post Malone", "genre": ["hiphop", "pop"], "image": "https://i.pravatar.cc/150?img=7"},
    {"id": "a8", "name": "Ariana Grande", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=8"},
    {"id": "a9", "name": "Drake", "genre": ["hiphop", "rnb"], "image": "https://i.pravatar.cc/150?img=9"},
    {"id": "a10", "name": "Adele", "genre": ["pop", "soul"], "image": "https://i.pravatar.cc/150?img=10"},
    {"id": "a11", "name": "Bruno Mars", "genre": ["pop", "funk"], "image": "https://i.pravatar.cc/150?img=11"},
    {"id": "a12", "name": "Harry Styles", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=12"},
    {"id": "a13", "name": "Olivia Rodrigo", "genre": ["pop", "alternative"], "image": "https://i.pravatar.cc/150?img=13"},
    {"id": "a14", "name": "Justin Bieber", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=14"},
    {"id": "a15", "name": "Selena Gomez", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=15"},
    {"id": "a16", "name": "Shawn Mendes", "genre": ["pop", "acoustic"], "image": "https://i.pravatar.cc/150?img=16"},
    {"id": "a17", "name": "Charlie Puth", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=17"},
    {"id": "a18", "name": "Sam Smith", "genre": ["pop", "soul"], "image": "https://i.pravatar.cc/150?img=18"},
    {"id": "a19", "name": "Halsey", "genre": ["pop", "alternative"], "image": "https://i.pravatar.cc/150?img=19"},
    {"id": "a20", "name": "Imagine Dragons", "genre": ["rock", "alternative"], "image": "https://i.pravatar.cc/150?img=20"},
    # Indonesian Artists
    {"id": "a21", "name": "Raisa", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=21"},
    {"id": "a22", "name": "Tulus", "genre": ["pop", "jazz"], "image": "https://i.pravatar.cc/150?img=22"},
    {"id": "a23", "name": "Iwan Fals", "genre": ["folk", "rock"], "image": "https://i.pravatar.cc/150?img=23"},
    {"id": "a24", "name": "Sheila on 7", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=24"},
    {"id": "a25", "name": "Dewa 19", "genre": ["rock", "pop"], "image": "https://i.pravatar.cc/150?img=25"},
    {"id": "a26", "name": "Padi", "genre": ["rock", "pop"], "image": "https://i.pravatar.cc/150?img=26"},
    {"id": "a27", "name": "Slank", "genre": ["rock"], "image": "https://i.pravatar.cc/150?img=27"},
    {"id": "a28", "name": "Noah", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=28"},
    {"id": "a29", "name": "Ungu", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=29"},
    {"id": "a30", "name": "Peterpan", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=30"},
    {"id": "a31", "name": "Payung Teduh", "genre": ["folk", "indie"], "image": "https://i.pravatar.cc/150?img=31"},
    {"id": "a32", "name": "Fourtwnty", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=32"},
    {"id": "a33", "name": "Hindia", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=33"},
    {"id": "a34", "name": "Maliq & D'Essentials", "genre": ["jazz", "rnb"], "image": "https://i.pravatar.cc/150?img=34"},
    {"id": "a35", "name": "Fiersa Besari", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=35"},
    {"id": "a36", "name": "Yura Yunita", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=36"},
    {"id": "a37", "name": "Isyana Sarasvati", "genre": ["pop", "classical"], "image": "https://i.pravatar.cc/150?img=37"},
    {"id": "a38", "name": "Rizky Febian", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=38"},
    {"id": "a39", "name": "Afgan", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=39"},
    {"id": "a40", "name": "Judika", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=40"},
    # K-Pop & Asian
    {"id": "a41", "name": "BTS", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=41"},
    {"id": "a42", "name": "BLACKPINK", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=42"},
    {"id": "a43", "name": "TWICE", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=43"},
    {"id": "a44", "name": "EXO", "genre": ["kpop", "rnb"], "image": "https://i.pravatar.cc/150?img=44"},
    {"id": "a45", "name": "NCT 127", "genre": ["kpop", "hiphop"], "image": "https://i.pravatar.cc/150?img=45"},
    {"id": "a46", "name": "aespa", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=46"},
    {"id": "a47", "name": "NewJeans", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=47"},
    {"id": "a48", "name": "IVE", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=48"},
    {"id": "a49", "name": "Stray Kids", "genre": ["kpop", "hiphop"], "image": "https://i.pravatar.cc/150?img=49"},
    {"id": "a50", "name": "SEVENTEEN", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=50"},
    # More Global
    {"id": "a51", "name": "Lady Gaga", "genre": ["pop", "dance"], "image": "https://i.pravatar.cc/150?img=51"},
    {"id": "a52", "name": "Katy Perry", "genre": ["pop", "dance"], "image": "https://i.pravatar.cc/150?img=52"},
    {"id": "a53", "name": "Rihanna", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=53"},
    {"id": "a54", "name": "Beyoncé", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=54"},
    {"id": "a55", "name": "Eminem", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=55"},
    {"id": "a56", "name": "Kanye West", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=56"},
    {"id": "a57", "name": "Kendrick Lamar", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=57"},
    {"id": "a58", "name": "J. Cole", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=58"},
    {"id": "a59", "name": "Travis Scott", "genre": ["hiphop", "trap"], "image": "https://i.pravatar.cc/150?img=59"},
    {"id": "a60", "name": "Bad Bunny", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=60"},
    {"id": "a61", "name": "SZA", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=61"},
    {"id": "a62", "name": "Frank Ocean", "genre": ["rnb", "indie"], "image": "https://i.pravatar.cc/150?img=62"},
    {"id": "a63", "name": "Tyler, The Creator", "genre": ["hiphop", "alternative"], "image": "https://i.pravatar.cc/150?img=63"},
    {"id": "a64", "name": "Childish Gambino", "genre": ["hiphop", "rnb"], "image": "https://i.pravatar.cc/150?img=64"},
    {"id": "a65", "name": "Arctic Monkeys", "genre": ["rock", "indie"], "image": "https://i.pravatar.cc/150?img=65"},
    {"id": "a66", "name": "Radiohead", "genre": ["alternative", "rock"], "image": "https://i.pravatar.cc/150?img=66"},
    {"id": "a67", "name": "Linkin Park", "genre": ["rock", "alternative"], "image": "https://i.pravatar.cc/150?img=67"},
    {"id": "a68", "name": "Green Day", "genre": ["punk", "rock"], "image": "https://i.pravatar.cc/150?img=68"},
    {"id": "a69", "name": "Metallica", "genre": ["metal", "rock"], "image": "https://i.pravatar.cc/150?img=69"},
    {"id": "a70", "name": "Queen", "genre": ["rock", "classic"], "image": "https://i.pravatar.cc/150?img=70"},
    {"id": "a71", "name": "The Beatles", "genre": ["rock", "classic"], "image": "https://i.pravatar.cc/150?img=71"},
    {"id": "a72", "name": "Michael Jackson", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=72"},
    {"id": "a73", "name": "Elvis Presley", "genre": ["rock", "classic"], "image": "https://i.pravatar.cc/150?img=73"},
    {"id": "a74", "name": "David Bowie", "genre": ["rock", "glam"], "image": "https://i.pravatar.cc/150?img=74"},
    {"id": "a75", "name": "Pink Floyd", "genre": ["rock", "psychedelic"], "image": "https://i.pravatar.cc/150?img=75"},
    {"id": "a76", "name": "Bob Dylan", "genre": ["folk", "classic"], "image": "https://i.pravatar.cc/150?img=76"},
    {"id": "a77", "name": "Nirvana", "genre": ["grunge", "rock"], "image": "https://i.pravatar.cc/150?img=77"},
    {"id": "a78", "name": "Red Hot Chili Peppers", "genre": ["rock", "funk"], "image": "https://i.pravatar.cc/150?img=78"},
    {"id": "a79", "name": "U2", "genre": ["rock", "pop"], "image": "https://i.pravatar.cc/150?img=79"},
    {"id": "a80", "name": "Fleetwood Mac", "genre": ["rock", "pop"], "image": "https://i.pravatar.cc/150?img=80"},
    # Electronic/Dance
    {"id": "a81", "name": "Calvin Harris", "genre": ["dance", "electronic"], "image": "https://i.pravatar.cc/150?img=81"},
    {"id": "a82", "name": "David Guetta", "genre": ["dance", "electronic"], "image": "https://i.pravatar.cc/150?img=82"},
    {"id": "a83", "name": "Marshmello", "genre": ["edm", "electronic"], "image": "https://i.pravatar.cc/150?img=83"},
    {"id": "a84", "name": "Zedd", "genre": ["edm", "electronic"], "image": "https://i.pravatar.cc/150?img=84"},
    {"id": "a85", "name": "Avicii", "genre": ["edm", "dance"], "image": "https://i.pravatar.cc/150?img=85"},
    {"id": "a86", "name": "Martin Garrix", "genre": ["edm", "dance"], "image": "https://i.pravatar.cc/150?img=86"},
    {"id": "a87", "name": "Skrillex", "genre": ["dubstep", "edm"], "image": "https://i.pravatar.cc/150?img=87"},
    {"id": "a88", "name": "Diplo", "genre": ["electronic", "dance"], "image": "https://i.pravatar.cc/150?img=88"},
    # More Indonesian
    {"id": "a89", "name": "Andmesh", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=89"},
    {"id": "a90", "name": "Tiara Andini", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=90"},
    {"id": "a91", "name": "Mahalini", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=91"},
    {"id": "a92", "name": "Lyodra", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=92"},
    {"id": "a93", "name": "Ari Lasso", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=93"},
    {"id": "a94", "name": "Chrisye", "genre": ["pop", "classic"], "image": "https://i.pravatar.cc/150?img=94"},
    {"id": "a95", "name": "Glenn Fredly", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=95"},
    {"id": "a96", "name": "Endank Soekamti", "genre": ["punk", "rock"], "image": "https://i.pravatar.cc/150?img=96"},
    {"id": "a97", "name": "Superman Is Dead", "genre": ["punk", "rock"], "image": "https://i.pravatar.cc/150?img=97"},
    {"id": "a98", "name": "Burgerkill", "genre": ["metal", "rock"], "image": "https://i.pravatar.cc/150?img=98"},
    {"id": "a99", "name": "Nadin Amizah", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=99"},
    {"id": "a100", "name": "Pamungkas", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=100"},
]

SINGERS_DATA = [
    # Indonesian Singers (male)
    {"id": "s1", "name": "Afgan Syahreza", "gender": "male", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=11"},
    {"id": "s2", "name": "Rizky Febian", "gender": "male", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=12"},
    {"id": "s3", "name": "Judika", "gender": "male", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=13"},
    {"id": "s4", "name": "Tulus", "gender": "male", "genre": ["pop", "jazz"], "image": "https://i.pravatar.cc/150?img=14"},
    {"id": "s5", "name": "Andmesh Kamaleng", "gender": "male", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=15"},
    {"id": "s6", "name": "Glenn Fredly", "gender": "male", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=16"},
    {"id": "s7", "name": "Ariel Noah", "gender": "male", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=17"},
    {"id": "s8", "name": "Sheila on 7", "gender": "male", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=18"},
    {"id": "s9", "name": "Iwan Fals", "gender": "male", "genre": ["folk", "rock"], "image": "https://i.pravatar.cc/150?img=19"},
    {"id": "s10", "name": "Chrisye", "gender": "male", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=20"},
    {"id": "s11", "name": "Ari Lasso", "gender": "male", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=21"},
    {"id": "s12", "name": "Once Mekel", "gender": "male", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=22"},
    {"id": "s13", "name": "Fiersa Besari", "gender": "male", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=23"},
    {"id": "s14", "name": "Hindia", "gender": "male", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=24"},
    {"id": "s15", "name": "Pamungkas", "gender": "male", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=25"},
    # Indonesian Singers (female)
    {"id": "s16", "name": "Raisa Andriana", "gender": "female", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=26"},
    {"id": "s17", "name": "Isyana Sarasvati", "gender": "female", "genre": ["pop", "classical"], "image": "https://i.pravatar.cc/150?img=27"},
    {"id": "s18", "name": "Yura Yunita", "gender": "female", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=28"},
    {"id": "s19", "name": "Tiara Andini", "gender": "female", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=29"},
    {"id": "s20", "name": "Mahalini", "gender": "female", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=30"},
    {"id": "s21", "name": "Lyodra Margaretha", "gender": "female", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=31"},
    {"id": "s22", "name": "Nadin Amizah", "gender": "female", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=32"},
    {"id": "s23", "name": "Bunga Citra Lestari", "gender": "female", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=33"},
    {"id": "s24", "name": "Agnes Monica", "gender": "female", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=34"},
    {"id": "s25", "name": "Rossa", "gender": "female", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=35"},
    {"id": "s26", "name": "Siti Nurhaliza", "gender": "female", "genre": ["pop", "malay"], "image": "https://i.pravatar.cc/150?img=36"},
    {"id": "s27", "name": "Anggun", "gender": "female", "genre": ["pop", "world"], "image": "https://i.pravatar.cc/150?img=37"},
    {"id": "s28", "name": "Via Vallen", "gender": "female", "genre": ["dangdut", "pop"], "image": "https://i.pravatar.cc/150?img=38"},
    {"id": "s29", "name": "Nella Kharisma", "gender": "female", "genre": ["dangdut"], "image": "https://i.pravatar.cc/150?img=39"},
    {"id": "s30", "name": "Happy Asmara", "gender": "female", "genre": ["dangdut", "pop"], "image": "https://i.pravatar.cc/150?img=40"},
    # Global Singers (male)
    {"id": "s31", "name": "Ed Sheeran", "gender": "male", "genre": ["pop", "acoustic"], "image": "https://i.pravatar.cc/150?img=41"},
    {"id": "s32", "name": "Bruno Mars", "gender": "male", "genre": ["pop", "funk"], "image": "https://i.pravatar.cc/150?img=42"},
    {"id": "s33", "name": "The Weeknd", "gender": "male", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=43"},
    {"id": "s34", "name": "Justin Bieber", "gender": "male", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=44"},
    {"id": "s35", "name": "Harry Styles", "gender": "male", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=45"},
    {"id": "s36", "name": "Shawn Mendes", "gender": "male", "genre": ["pop", "acoustic"], "image": "https://i.pravatar.cc/150?img=46"},
    {"id": "s37", "name": "Charlie Puth", "gender": "male", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=47"},
    {"id": "s38", "name": "Sam Smith", "gender": "male", "genre": ["pop", "soul"], "image": "https://i.pravatar.cc/150?img=48"},
    {"id": "s39", "name": "Post Malone", "gender": "male", "genre": ["hiphop", "pop"], "image": "https://i.pravatar.cc/150?img=49"},
    {"id": "s40", "name": "Drake", "gender": "male", "genre": ["hiphop", "rnb"], "image": "https://i.pravatar.cc/150?img=50"},
    {"id": "s41", "name": "Eminem", "gender": "male", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=51"},
    {"id": "s42", "name": "Michael Jackson", "gender": "male", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=52"},
    {"id": "s43", "name": "Elton John", "gender": "male", "genre": ["pop", "classic"], "image": "https://i.pravatar.cc/150?img=53"},
    {"id": "s44", "name": "Freddie Mercury", "gender": "male", "genre": ["rock", "pop"], "image": "https://i.pravatar.cc/150?img=54"},
    {"id": "s45", "name": "David Bowie", "gender": "male", "genre": ["rock", "glam"], "image": "https://i.pravatar.cc/150?img=55"},
    # Global Singers (female)
    {"id": "s46", "name": "Taylor Swift", "gender": "female", "genre": ["pop", "country"], "image": "https://i.pravatar.cc/150?img=56"},
    {"id": "s47", "name": "Billie Eilish", "gender": "female", "genre": ["pop", "indie"], "image": "https://i.pravatar.cc/150?img=57"},
    {"id": "s48", "name": "Ariana Grande", "gender": "female", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=58"},
    {"id": "s49", "name": "Dua Lipa", "gender": "female", "genre": ["pop", "dance"], "image": "https://i.pravatar.cc/150?img=59"},
    {"id": "s50", "name": "Adele", "gender": "female", "genre": ["pop", "soul"], "image": "https://i.pravatar.cc/150?img=60"},
    {"id": "s51", "name": "Olivia Rodrigo", "gender": "female", "genre": ["pop", "alternative"], "image": "https://i.pravatar.cc/150?img=61"},
    {"id": "s52", "name": "Selena Gomez", "gender": "female", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=62"},
    {"id": "s53", "name": "Beyoncé", "gender": "female", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=63"},
    {"id": "s54", "name": "Rihanna", "gender": "female", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=64"},
    {"id": "s55", "name": "Lady Gaga", "gender": "female", "genre": ["pop", "dance"], "image": "https://i.pravatar.cc/150?img=65"},
    {"id": "s56", "name": "Katy Perry", "gender": "female", "genre": ["pop", "dance"], "image": "https://i.pravatar.cc/150?img=66"},
    {"id": "s57", "name": "SZA", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=67"},
    {"id": "s58", "name": "Halsey", "gender": "female", "genre": ["pop", "alternative"], "image": "https://i.pravatar.cc/150?img=68"},
    {"id": "s59", "name": "Lana Del Rey", "gender": "female", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=69"},
    {"id": "s60", "name": "Nicki Minaj", "gender": "female", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=70"},
    # K-Pop
    {"id": "s61", "name": "Jungkook (BTS)", "gender": "male", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=71"},
    {"id": "s62", "name": "V (BTS)", "gender": "male", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=72"},
    {"id": "s63", "name": "Jin (BTS)", "gender": "male", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=73"},
    {"id": "s64", "name": "Suga (BTS)", "gender": "male", "genre": ["kpop", "hiphop"], "image": "https://i.pravatar.cc/150?img=74"},
    {"id": "s65", "name": "Lisa (BLACKPINK)", "gender": "female", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=75"},
    {"id": "s66", "name": "Jennie (BLACKPINK)", "gender": "female", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=76"},
    {"id": "s67", "name": "Rose (BLACKPINK)", "gender": "female", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=77"},
    {"id": "s68", "name": "Jisoo (BLACKPINK)", "gender": "female", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=78"},
    {"id": "s69", "name": "IU", "gender": "female", "genre": ["kpop", "pop", "folk"], "image": "https://i.pravatar.cc/150?img=79"},
    {"id": "s70", "name": "Taeyeon", "gender": "female", "genre": ["kpop", "pop"], "image": "https://i.pravatar.cc/150?img=80"},
    # More Global
    {"id": "s71", "name": "John Legend", "gender": "male", "genre": ["rnb", "soul"], "image": "https://i.pravatar.cc/150?img=81"},
    {"id": "s72", "name": "Alicia Keys", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=82"},
    {"id": "s73", "name": "John Mayer", "gender": "male", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=83"},
    {"id": "s74", "name": "Amy Winehouse", "gender": "female", "genre": ["soul", "jazz"], "image": "https://i.pravatar.cc/150?img=84"},
    {"id": "s75", "name": "Hozier", "gender": "male", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=85"},
    {"id": "s76", "name": "Lorde", "gender": "female", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=86"},
    {"id": "s77", "name": "Troye Sivan", "gender": "male", "genre": ["pop", "indie"], "image": "https://i.pravatar.cc/150?img=87"},
    {"id": "s78", "name": "Camila Cabello", "gender": "female", "genre": ["pop", "latin"], "image": "https://i.pravatar.cc/150?img=88"},
    {"id": "s79", "name": "Khalid", "gender": "male", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=89"},
    {"id": "s80", "name": "Conan Gray", "gender": "male", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=90"},
    {"id": "s81", "name": "Gracie Abrams", "gender": "female", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=91"},
    {"id": "s82", "name": "Sabrina Carpenter", "gender": "female", "genre": ["pop"], "image": "https://i.pravatar.cc/150?img=92"},
    {"id": "s83", "name": "Chappell Roan", "gender": "female", "genre": ["pop", "alternative"], "image": "https://i.pravatar.cc/150?img=93"},
    {"id": "s84", "name": "Zach Bryan", "gender": "male", "genre": ["country", "folk"], "image": "https://i.pravatar.cc/150?img=94"},
    {"id": "s85", "name": "Noah Kahan", "gender": "male", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=95"},
    {"id": "s86", "name": "Hozier", "gender": "male", "genre": ["folk", "indie"], "image": "https://i.pravatar.cc/150?img=96"},
    {"id": "s87", "name": "Lewis Capaldi", "gender": "male", "genre": ["pop", "soul"], "image": "https://i.pravatar.cc/150?img=97"},
    {"id": "s88", "name": "James Arthur", "gender": "male", "genre": ["pop", "rnb"], "image": "https://i.pravatar.cc/150?img=98"},
    {"id": "s89", "name": "JP Saxe", "gender": "male", "genre": ["pop", "indie"], "image": "https://i.pravatar.cc/150?img=99"},
    {"id": "s90", "name": "Dermot Kennedy", "gender": "male", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=100"},
    # More female
    {"id": "s91", "name": "Phoebe Bridgers", "gender": "female", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=1"},
    {"id": "s92", "name": "Mitski", "gender": "female", "genre": ["indie", "alternative"], "image": "https://i.pravatar.cc/150?img=2"},
    {"id": "s93", "name": "Lucy Dacus", "gender": "female", "genre": ["indie", "rock"], "image": "https://i.pravatar.cc/150?img=3"},
    {"id": "s94", "name": "Faye Webster", "gender": "female", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=4"},
    {"id": "s95", "name": "Japanese Breakfast", "gender": "female", "genre": ["indie", "alternative"], "image": "https://i.pravatar.cc/150?img=5"},
    {"id": "s96", "name": "boygenius", "gender": "female", "genre": ["indie", "rock"], "image": "https://i.pravatar.cc/150?img=6"},
    {"id": "s97", "name": "Soccer Mommy", "gender": "female", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=7"},
    {"id": "s98", "name": "Snail Mail", "gender": "female", "genre": ["indie", "rock"], "image": "https://i.pravatar.cc/150?img=8"},
    {"id": "s99", "name": "Angel Olsen", "gender": "female", "genre": ["indie", "alternative"], "image": "https://i.pravatar.cc/150?img=9"},
    {"id": "s100", "name": "Sharon Van Etten", "gender": "female", "genre": ["indie", "rock"], "image": "https://i.pravatar.cc/150?img=10"},
    # Extra 100 singers
    {"id": "s101", "name": "Passenger", "gender": "male", "genre": ["folk", "indie"], "image": "https://i.pravatar.cc/150?img=11"},
    {"id": "s102", "name": "James Bay", "gender": "male", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=12"},
    {"id": "s103", "name": "Ben Howard", "gender": "male", "genre": ["folk", "indie"], "image": "https://i.pravatar.cc/150?img=13"},
    {"id": "s104", "name": "José González", "gender": "male", "genre": ["folk", "acoustic"], "image": "https://i.pravatar.cc/150?img=14"},
    {"id": "s105", "name": "Iron & Wine", "gender": "male", "genre": ["folk", "indie"], "image": "https://i.pravatar.cc/150?img=15"},
    {"id": "s106", "name": "James Blake", "gender": "male", "genre": ["electronic", "rnb"], "image": "https://i.pravatar.cc/150?img=16"},
    {"id": "s107", "name": "FKA twigs", "gender": "female", "genre": ["rnb", "electronic"], "image": "https://i.pravatar.cc/150?img=17"},
    {"id": "s108", "name": "Solange", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=18"},
    {"id": "s109", "name": "Janelle Monáe", "gender": "female", "genre": ["pop", "funk"], "image": "https://i.pravatar.cc/150?img=19"},
    {"id": "s110", "name": "Erykah Badu", "gender": "female", "genre": ["rnb", "soul"], "image": "https://i.pravatar.cc/150?img=20"},
    {"id": "s111", "name": "D'Angelo", "gender": "male", "genre": ["rnb", "soul"], "image": "https://i.pravatar.cc/150?img=21"},
    {"id": "s112", "name": "Maxwell", "gender": "male", "genre": ["rnb", "soul"], "image": "https://i.pravatar.cc/150?img=22"},
    {"id": "s113", "name": "Lauryn Hill", "gender": "female", "genre": ["rnb", "hiphop"], "image": "https://i.pravatar.cc/150?img=23"},
    {"id": "s114", "name": "Mary J. Blige", "gender": "female", "genre": ["rnb", "soul"], "image": "https://i.pravatar.cc/150?img=24"},
    {"id": "s115", "name": "Usher", "gender": "male", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=25"},
    {"id": "s116", "name": "Ne-Yo", "gender": "male", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=26"},
    {"id": "s117", "name": "Chris Brown", "gender": "male", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=27"},
    {"id": "s118", "name": "Trey Songz", "gender": "male", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=28"},
    {"id": "s119", "name": "Miguel", "gender": "male", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=29"},
    {"id": "s120", "name": "Anderson .Paak", "gender": "male", "genre": ["rnb", "funk"], "image": "https://i.pravatar.cc/150?img=30"},
    {"id": "s121", "name": "Steve Lacy", "gender": "male", "genre": ["rnb", "indie"], "image": "https://i.pravatar.cc/150?img=31"},
    {"id": "s122", "name": "Brent Faiyaz", "gender": "male", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=32"},
    {"id": "s123", "name": "Giveon", "gender": "male", "genre": ["rnb", "soul"], "image": "https://i.pravatar.cc/150?img=33"},
    {"id": "s124", "name": "Daniel Caesar", "gender": "male", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=34"},
    {"id": "s125", "name": "H.E.R.", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=35"},
    {"id": "s126", "name": "Jhené Aiko", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=36"},
    {"id": "s127", "name": "Summer Walker", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=37"},
    {"id": "s128", "name": "Kehlani", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=38"},
    {"id": "s129", "name": "Normani", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=39"},
    {"id": "s130", "name": "Tinashe", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=40"},
    {"id": "s131", "name": "Ari Lennox", "gender": "female", "genre": ["rnb", "soul"], "image": "https://i.pravatar.cc/150?img=41"},
    {"id": "s132", "name": "Chloe Bailey", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=42"},
    {"id": "s133", "name": "Victoria Monét", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=43"},
    {"id": "s134", "name": "Cleo Sol", "gender": "female", "genre": ["soul", "rnb"], "image": "https://i.pravatar.cc/150?img=44"},
    {"id": "s135", "name": "Little Simz", "gender": "female", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=45"},
    {"id": "s136", "name": "Megan Thee Stallion", "gender": "female", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=46"},
    {"id": "s137", "name": "Cardi B", "gender": "female", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=47"},
    {"id": "s138", "name": "Doja Cat", "gender": "female", "genre": ["pop", "hiphop"], "image": "https://i.pravatar.cc/150?img=48"},
    {"id": "s139", "name": "Ice Spice", "gender": "female", "genre": ["hiphop", "pop"], "image": "https://i.pravatar.cc/150?img=49"},
    {"id": "s140", "name": "GloRilla", "gender": "female", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=50"},
    {"id": "s141", "name": "Peso Pluma", "gender": "male", "genre": ["latin", "corridos"], "image": "https://i.pravatar.cc/150?img=51"},
    {"id": "s142", "name": "Feid", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=52"},
    {"id": "s143", "name": "Karol G", "gender": "female", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=53"},
    {"id": "s144", "name": "Rosalía", "gender": "female", "genre": ["flamenco", "pop"], "image": "https://i.pravatar.cc/150?img=54"},
    {"id": "s145", "name": "J Balvin", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=55"},
    {"id": "s146", "name": "Maluma", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=56"},
    {"id": "s147", "name": "Ozuna", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=57"},
    {"id": "s148", "name": "Anuel AA", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=58"},
    {"id": "s149", "name": "Myke Towers", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=59"},
    {"id": "s150", "name": "Sech", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=60"},
    {"id": "s151", "name": "Rauw Alejandro", "gender": "male", "genre": ["reggaeton", "rnb"], "image": "https://i.pravatar.cc/150?img=61"},
    {"id": "s152", "name": "Jhay Cortez", "gender": "male", "genre": ["latin", "pop"], "image": "https://i.pravatar.cc/150?img=62"},
    {"id": "s153", "name": "Tainy", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=63"},
    {"id": "s154", "name": "Marc Anthony", "gender": "male", "genre": ["salsa", "latin"], "image": "https://i.pravatar.cc/150?img=64"},
    {"id": "s155", "name": "Jennifer Lopez", "gender": "female", "genre": ["pop", "latin"], "image": "https://i.pravatar.cc/150?img=65"},
    {"id": "s156", "name": "Shakira", "gender": "female", "genre": ["pop", "latin"], "image": "https://i.pravatar.cc/150?img=66"},
    {"id": "s157", "name": "Enrique Iglesias", "gender": "male", "genre": ["pop", "latin"], "image": "https://i.pravatar.cc/150?img=67"},
    {"id": "s158", "name": "Pitbull", "gender": "male", "genre": ["latin", "dance"], "image": "https://i.pravatar.cc/150?img=68"},
    {"id": "s159", "name": "Luis Fonsi", "gender": "male", "genre": ["pop", "latin"], "image": "https://i.pravatar.cc/150?img=69"},
    {"id": "s160", "name": "Daddy Yankee", "gender": "male", "genre": ["reggaeton", "latin"], "image": "https://i.pravatar.cc/150?img=70"},
    {"id": "s161", "name": "Dimash Kudaibergen", "gender": "male", "genre": ["pop", "classical"], "image": "https://i.pravatar.cc/150?img=71"},
    {"id": "s162", "name": "Eason Chan", "gender": "male", "genre": ["cpop", "pop"], "image": "https://i.pravatar.cc/150?img=72"},
    {"id": "s163", "name": "Jay Chou", "gender": "male", "genre": ["cpop", "pop"], "image": "https://i.pravatar.cc/150?img=73"},
    {"id": "s164", "name": "G.E.M.", "gender": "female", "genre": ["cpop", "pop"], "image": "https://i.pravatar.cc/150?img=74"},
    {"id": "s165", "name": "Teresa Teng", "gender": "female", "genre": ["cpop", "classic"], "image": "https://i.pravatar.cc/150?img=75"},
    {"id": "s166", "name": "Jolin Tsai", "gender": "female", "genre": ["cpop", "pop"], "image": "https://i.pravatar.cc/150?img=76"},
    {"id": "s167", "name": "Mayday", "gender": "male", "genre": ["cpop", "rock"], "image": "https://i.pravatar.cc/150?img=77"},
    {"id": "s168", "name": "S.H.E", "gender": "female", "genre": ["cpop", "pop"], "image": "https://i.pravatar.cc/150?img=78"},
    {"id": "s169", "name": "Hacken Lee", "gender": "male", "genre": ["cpop", "pop"], "image": "https://i.pravatar.cc/150?img=79"},
    {"id": "s170", "name": "Andy Lau", "gender": "male", "genre": ["cpop", "pop"], "image": "https://i.pravatar.cc/150?img=80"},
    {"id": "s171", "name": "Yoasobi", "gender": "female", "genre": ["jpop", "indie"], "image": "https://i.pravatar.cc/150?img=81"},
    {"id": "s172", "name": "Aimyon", "gender": "female", "genre": ["jpop", "folk"], "image": "https://i.pravatar.cc/150?img=82"},
    {"id": "s173", "name": "King Gnu", "gender": "male", "genre": ["jpop", "rock"], "image": "https://i.pravatar.cc/150?img=83"},
    {"id": "s174", "name": "Kenshi Yonezu", "gender": "male", "genre": ["jpop", "pop"], "image": "https://i.pravatar.cc/150?img=84"},
    {"id": "s175", "name": "Official HIGE DANdism", "gender": "male", "genre": ["jpop", "pop"], "image": "https://i.pravatar.cc/150?img=85"},
    {"id": "s176", "name": "Aimer", "gender": "female", "genre": ["jpop", "pop"], "image": "https://i.pravatar.cc/150?img=86"},
    {"id": "s177", "name": "LiSA", "gender": "female", "genre": ["jpop", "rock"], "image": "https://i.pravatar.cc/150?img=87"},
    {"id": "s178", "name": "Hikaru Utada", "gender": "female", "genre": ["jpop", "pop"], "image": "https://i.pravatar.cc/150?img=88"},
    {"id": "s179", "name": "Ayumi Hamasaki", "gender": "female", "genre": ["jpop", "pop"], "image": "https://i.pravatar.cc/150?img=89"},
    {"id": "s180", "name": "Namie Amuro", "gender": "female", "genre": ["jpop", "rnb"], "image": "https://i.pravatar.cc/150?img=90"},
    {"id": "s181", "name": "Niki", "gender": "female", "genre": ["rnb", "pop"], "image": "https://i.pravatar.cc/150?img=91"},
    {"id": "s182", "name": "Beabadoobee", "gender": "female", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=92"},
    {"id": "s183", "name": "Rei Ami", "gender": "female", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=93"},
    {"id": "s184", "name": "Keshi", "gender": "male", "genre": ["indie", "rnb"], "image": "https://i.pravatar.cc/150?img=94"},
    {"id": "s185", "name": "joji", "gender": "male", "genre": ["indie", "rnb"], "image": "https://i.pravatar.cc/150?img=95"},
    {"id": "s186", "name": "88rising", "gender": "male", "genre": ["hiphop", "asian"], "image": "https://i.pravatar.cc/150?img=96"},
    {"id": "s187", "name": "Rich Brian", "gender": "male", "genre": ["hiphop", "rap"], "image": "https://i.pravatar.cc/150?img=97"},
    {"id": "s188", "name": "CHVRCHES", "gender": "female", "genre": ["synth-pop", "indie"], "image": "https://i.pravatar.cc/150?img=98"},
    {"id": "s189", "name": "Florence + The Machine", "gender": "female", "genre": ["indie", "alternative"], "image": "https://i.pravatar.cc/150?img=99"},
    {"id": "s190", "name": "Lykke Li", "gender": "female", "genre": ["indie", "pop"], "image": "https://i.pravatar.cc/150?img=100"},
    {"id": "s191", "name": "Sigrid", "gender": "female", "genre": ["pop", "indie"], "image": "https://i.pravatar.cc/150?img=1"},
    {"id": "s192", "name": "Birdy", "gender": "female", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=2"},
    {"id": "s193", "name": "Aurora", "gender": "female", "genre": ["indie", "folk"], "image": "https://i.pravatar.cc/150?img=3"},
    {"id": "s194", "name": "Lissie", "gender": "female", "genre": ["folk", "rock"], "image": "https://i.pravatar.cc/150?img=4"},
    {"id": "s195", "name": "Brandi Carlile", "gender": "female", "genre": ["folk", "country"], "image": "https://i.pravatar.cc/150?img=5"},
    {"id": "s196", "name": "Alanis Morissette", "gender": "female", "genre": ["rock", "alternative"], "image": "https://i.pravatar.cc/150?img=6"},
    {"id": "s197", "name": "Tori Amos", "gender": "female", "genre": ["alternative", "art rock"], "image": "https://i.pravatar.cc/150?img=7"},
    {"id": "s198", "name": "Kate Bush", "gender": "female", "genre": ["art rock", "pop"], "image": "https://i.pravatar.cc/150?img=8"},
    {"id": "s199", "name": "Annie Lennox", "gender": "female", "genre": ["pop", "rock"], "image": "https://i.pravatar.cc/150?img=9"},
    {"id": "s200", "name": "Sade", "gender": "female", "genre": ["soul", "jazz"], "image": "https://i.pravatar.cc/150?img=10"},
]

# Generate sample songs
SAMPLE_SONGS = []
song_titles_by_genre = {
    "pop": ["Blinding Lights", "Levitating", "Watermelon Sugar", "Peaches", "Good 4 U", "drivers license", "Stay", "Shivers", "Easy On Me", "Heat Waves", "As It Was", "Bad Habits", "Love Story", "Shake It Off", "Anti-Hero"],
    "rnb": ["Essence", "Leave The Door Open", "Peaches", "Telepatía", "Mood", "Kiss Me More", "Happier Than Ever", "Best Part", "Location", "Die For You"],
    "hiphop": ["HUMBLE.", "God's Plan", "Life Is Good", "Rockstar", "Lucid Dreams", "SAD!", "XO TOUR Llif3", "Mask Off", "SICKO MODE", "Money In The Grave"],
    "rock": ["Mr. Brightside", "Seven Nation Army", "Bohemian Rhapsody", "Smells Like Teen Spirit", "Hotel California", "Under The Bridge", "Come As You Are", "Learn To Fly", "Boulevard of Broken Dreams", "Welcome to the Black Parade"],
    "indie": ["Electric Feel", "Home", "Dog Days Are Over", "Little Talks", "Ho Hey", "Stubborn Love", "Flightless Bird", "The Less I Know The Better", "Ribs", "Team"],
    "folk": ["The Sound of Silence", "Fast Car", "Take Me Home Country Roads", "Jolene", "Hurt", "Hallelujah", "Blackbird", "The House of the Rising Sun", "Blowin' in the Wind", "The Times They Are A-Changin'"],
    "jazz": ["Take Five", "Autumn Leaves", "What a Wonderful World", "Fly Me to the Moon", "My Favorite Things", "Round Midnight", "Blue in Green", "A Love Supreme", "So What", "Kind of Blue"],
    "electronic": ["Midnight City", "Get Lucky", "Harder Better Faster Stronger", "Around the World", "One More Time", "Digital Love", "Instant Crush", "Lose Yourself to Dance", "Something About Us", "Da Funk"],
    "kpop": ["Dynamite", "How You Like That", "Ice Cream", "Next Level", "Ditto", "After LIKE", "MANIAC", "Pink Venom", "Shut Down", "Super Shy"],
}

artist_names = [a["name"] for a in ARTISTS_DATA]
genres = list(song_titles_by_genre.keys())

for i in range(200):
    genre = random.choice(genres)
    titles = song_titles_by_genre[genre]
    title = random.choice(titles) + (f" (Remix)" if random.random() > 0.8 else "")
    artist = random.choice(artist_names)
    duration = random.randint(150, 280)
    
    SAMPLE_SONGS.append({
        "id": f"song_{i+1}",
        "title": title,
        "artist": artist,
        "album": f"Album {chr(65 + i % 26)}",
        "genre": genre,
        "duration": duration,
        "cover": f"https://picsum.photos/seed/{i+10}/300/300",
        "popularity": random.randint(60, 100),
        "mood": random.choice(["chill", "energetic", "sad", "romantic", "focus", "relax"]),
        "time_of_day": random.choice(["morning", "afternoon", "evening", "night", "any"]),
        "videoId": f"dQw4w9WgXcQ",  # placeholder
        "year": random.randint(2015, 2024)
    })

# ==================== RECOMMENDATION ENGINE ====================

class RecommendationEngine:
    def __init__(self):
        self.genre_weights = defaultdict(float)
        self.artist_weights = defaultdict(float)
        self.mood_weights = defaultdict(float)
        self.time_weights = defaultdict(float)
    
    def analyze_history(self, history):
        if not history:
            return
        
        recent = history[-50:]  # Last 50 songs
        
        for item in recent:
            weight = 1.0
            if item.get('completed', False):
                weight = 1.5
            if item.get('skipped', False):
                weight = 0.3
            
            genre = item.get('genre', '')
            artist = item.get('artist', '')
            mood = item.get('mood', '')
            
            if genre:
                self.genre_weights[genre] += weight
            if artist:
                self.artist_weights[artist] += weight
            if mood:
                self.mood_weights[mood] += weight
        
        # Normalize
        total = sum(self.genre_weights.values()) or 1
        for k in self.genre_weights:
            self.genre_weights[k] /= total
    
    def get_current_mood(self):
        hour = datetime.now().hour
        if 5 <= hour < 10:
            return "morning", ["energetic", "focus", "chill"]
        elif 10 <= hour < 15:
            return "afternoon", ["focus", "energetic", "relax"]
        elif 15 <= hour < 20:
            return "evening", ["chill", "relax", "romantic"]
        else:
            return "night", ["chill", "sad", "romantic", "relax"]
    
    def score_song(self, song, preferences=None):
        score = song.get('popularity', 50) / 100.0
        
        genre = song.get('genre', '')
        artist = song.get('artist', '')
        mood = song.get('mood', '')
        
        score += self.genre_weights.get(genre, 0) * 2.0
        score += self.artist_weights.get(artist, 0) * 3.0
        score += self.mood_weights.get(mood, 0) * 1.5
        
        _, recommended_moods = self.get_current_mood()
        if mood in recommended_moods:
            score += 0.5
        
        if preferences:
            fav_artists = preferences.get('artists', [])
            fav_singers = preferences.get('singers', [])
            for fa in fav_artists:
                if fa.lower() in artist.lower():
                    score += 2.0
            for fs in fav_singers:
                if fs.lower() in artist.lower():
                    score += 1.5
        
        return score + random.uniform(0, 0.1)  # Small randomness
    
    def recommend(self, history, preferences, count=20, mood_filter=None):
        self.analyze_history(history)
        
        scored_songs = []
        for song in SAMPLE_SONGS:
            if mood_filter and song.get('mood') != mood_filter:
                continue
            score = self.score_song(song, preferences)
            scored_songs.append((score, song))
        
        scored_songs.sort(key=lambda x: x[0], reverse=True)
        top_songs = scored_songs[:count*2]
        random.shuffle(top_songs)
        
        return [s[1] for s in top_songs[:count]]
    
    def get_next_song(self, current_song, history):
        self.analyze_history(history)
        
        candidates = [s for s in SAMPLE_SONGS if s['id'] != current_song.get('id')]
        
        # Prioritize same genre/mood/artist
        scored = []
        for song in candidates:
            score = self.score_song(song)
            if song.get('genre') == current_song.get('genre'):
                score += 1.0
            if song.get('mood') == current_song.get('mood'):
                score += 0.8
            if song.get('artist') == current_song.get('artist'):
                score += 1.5
            scored.append((score, song))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:10]
        random.shuffle(top)
        return top[0][1] if top else random.choice(SAMPLE_SONGS)

engine = RecommendationEngine()

# ==================== ROUTES ====================

# index route removed for Vercel static
# 
    return send_from_directory('.', 'index.html')

@app.route('/api/artists', methods=['GET'])
def get_artists():
    return jsonify({"artists": ARTISTS_DATA})

@app.route('/api/singers', methods=['GET'])
def get_singers():
    return jsonify({"singers": SINGERS_DATA})

@app.route('/api/onboarding', methods=['POST'])
def save_onboarding():
    data_store = load_data()
    body = request.json
    user_id = body.get('user_id', 'default')
    
    data_store['preferences'][user_id] = {
        'artists': body.get('artists', []),
        'singers': body.get('singers', []),
        'completed': True,
        'timestamp': time.time()
    }
    save_data(data_store)
    return jsonify({"status": "ok", "message": "Preferensi tersimpan"})

@app.route('/api/preferences/<user_id>', methods=['GET'])
def get_preferences(user_id):
    data_store = load_data()
    prefs = data_store.get('preferences', {}).get(user_id, {})
    return jsonify(prefs)

@app.route('/api/home/<user_id>', methods=['GET'])
def get_home(user_id):
    data_store = load_data()
    history = [h for h in data_store.get('history', []) if h.get('user_id') == user_id]
    preferences = data_store.get('preferences', {}).get(user_id, {})
    
    e = RecommendationEngine()
    
    # Rekomendasi utama
    recommended = e.recommend(history, preferences, count=20)
    
    # Trending (high popularity)
    trending = sorted(SAMPLE_SONGS, key=lambda x: x['popularity'] + random.uniform(0, 10), reverse=True)[:20]
    
    # Playlist harian
    daily = e.recommend(history, preferences, count=15)
    random.shuffle(daily)
    
    # Album populer
    albums = []
    seen_albums = set()
    for song in trending:
        album_key = f"{song['album']}-{song['artist']}"
        if album_key not in seen_albums:
            seen_albums.add(album_key)
            albums.append({
                "id": f"album_{len(albums)+1}",
                "name": song['album'],
                "artist": song['artist'],
                "cover": song['cover'],
                "genre": song['genre'],
                "songs": [s for s in SAMPLE_SONGS if s['album'] == song['album'] and s['artist'] == song['artist']][:5]
            })
        if len(albums) >= 8:
            break
    
    # Mood-based playlists
    moods = ["chill", "energetic", "focus", "sad", "romantic", "relax"]
    mood_playlists = {}
    for mood in moods:
        mood_songs = e.recommend(history, preferences, count=10, mood_filter=mood)
        if not mood_songs:
            mood_songs = [s for s in SAMPLE_SONGS if s.get('mood') == mood][:10]
        mood_playlists[mood] = mood_songs
    
    # Time-based recommendation
    hour = datetime.now().hour
    time_label, _ = e.get_current_mood()
    
    return jsonify({
        "recommended": recommended,
        "trending": trending,
        "daily_mix": daily,
        "albums": albums,
        "mood_playlists": mood_playlists,
        "time_label": time_label,
        "hour": hour
    })

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"songs": [], "artists": [], "albums": []})
    
    # Search songs
    songs = [s for s in SAMPLE_SONGS if 
             query in s['title'].lower() or 
             query in s['artist'].lower() or 
             query in s['genre'].lower()][:20]
    
    # Search artists
    artists = [a for a in ARTISTS_DATA if query in a['name'].lower()][:10]
    
    # Search albums
    album_map = {}
    for s in SAMPLE_SONGS:
        if query in s['album'].lower() or query in s['artist'].lower():
            key = f"{s['album']}-{s['artist']}"
            if key not in album_map:
                album_map[key] = {
                    "name": s['album'],
                    "artist": s['artist'],
                    "cover": s['cover'],
                    "genre": s['genre']
                }
    albums = list(album_map.values())[:8]
    
    return jsonify({"songs": songs, "artists": artists, "albums": albums})

@app.route('/api/history', methods=['POST'])
def add_history():
    data_store = load_data()
    body = request.json
    
    entry = {
        "user_id": body.get('user_id', 'default'),
        "song_id": body.get('song_id'),
        "title": body.get('title'),
        "artist": body.get('artist'),
        "genre": body.get('genre'),
        "mood": body.get('mood'),
        "duration": body.get('duration', 0),
        "listen_duration": body.get('listen_duration', 0),
        "completed": body.get('completed', False),
        "skipped": body.get('skipped', False),
        "timestamp": time.time()
    }
    
    data_store['history'].append(entry)
    
    # Keep only last 500 entries
    if len(data_store['history']) > 500:
        data_store['history'] = data_store['history'][-500:]
    
    save_data(data_store)
    return jsonify({"status": "ok"})

@app.route('/api/next-song', methods=['POST'])
def next_song():
    body = request.json
    current = body.get('current_song', {})
    user_id = body.get('user_id', 'default')
    
    data_store = load_data()
    history = [h for h in data_store.get('history', []) if h.get('user_id') == user_id]
    
    e = RecommendationEngine()
    next_s = e.get_next_song(current, history)
    
    return jsonify(next_s)

@app.route('/api/radio/<song_id>', methods=['GET'])
def get_radio(song_id):
    """Get radio playlist based on a song"""
    base_song = next((s for s in SAMPLE_SONGS if s['id'] == song_id), None)
    if not base_song:
        return jsonify({"songs": random.sample(SAMPLE_SONGS, 15)})
    
    e = RecommendationEngine()
    similar = []
    
    for song in SAMPLE_SONGS:
        if song['id'] == song_id:
            continue
        score = 0
        if song['genre'] == base_song['genre']:
            score += 2
        if song['mood'] == base_song['mood']:
            score += 1.5
        if song['artist'] == base_song['artist']:
            score += 3
        score += song['popularity'] / 100
        similar.append((score + random.uniform(0, 0.5), song))
    
    similar.sort(key=lambda x: x[0], reverse=True)
    return jsonify({"songs": [s[1] for s in similar[:20]]})

@app.route('/api/stats/<user_id>', methods=['GET'])
def get_stats(user_id):
    data_store = load_data()
    history = [h for h in data_store.get('history', []) if h.get('user_id') == user_id]
    preferences = data_store.get('preferences', {}).get(user_id, {})
    
    if not history:
        return jsonify({
            "total_songs": 0,
            "total_hours": 0,
            "top_artists": [],
            "top_genres": [],
            "favorite_mood": "chill",
            "listening_pattern": []
        })
    
    # Calculate stats
    total_songs = len(history)
    total_seconds = sum(h.get('listen_duration', h.get('duration', 180)) for h in history)
    total_hours = round(total_seconds / 3600, 1)
    
    artist_count = Counter(h.get('artist', '') for h in history)
    genre_count = Counter(h.get('genre', '') for h in history)
    mood_count = Counter(h.get('mood', '') for h in history)
    
    top_artists = [{"name": a, "count": c} for a, c in artist_count.most_common(5)]
    top_genres = [{"name": g, "count": c} for g, c in genre_count.most_common(5)]
    favorite_mood = mood_count.most_common(1)[0][0] if mood_count else "chill"
    
    # Listening pattern by hour
    hour_count = defaultdict(int)
    for h in history:
        ts = h.get('timestamp', 0)
        hour = datetime.fromtimestamp(ts).hour
        hour_count[hour] += 1
    
    listening_pattern = [{"hour": h, "count": hour_count[h]} for h in range(24)]
    
    return jsonify({
        "total_songs": total_songs,
        "total_hours": total_hours,
        "top_artists": top_artists,
        "top_genres": top_genres,
        "favorite_mood": favorite_mood,
        "listening_pattern": listening_pattern,
        "preferences": preferences
    })

@app.route('/api/playlist/smart/<user_id>', methods=['GET'])
def smart_playlist(user_id):
    data_store = load_data()
    history = [h for h in data_store.get('history', []) if h.get('user_id') == user_id]
    preferences = data_store.get('preferences', {}).get(user_id, {})
    
    e = RecommendationEngine()
    songs = e.recommend(history, preferences, count=30)
    
    return jsonify({
        "name": "Mix Cerdas Untukmu",
        "description": "Dibuat berdasarkan selera musikmu",
        "songs": songs
    })

@app.route('/api/songs', methods=['GET'])
def get_songs():
    genre = request.args.get('genre')
    mood = request.args.get('mood')
    limit = int(request.args.get('limit', 20))
    
    songs = SAMPLE_SONGS
    if genre:
        songs = [s for s in songs if s['genre'] == genre]
    if mood:
        songs = [s for s in songs if s['mood'] == mood]
    
    random.shuffle(songs)
    return jsonify({"songs": songs[:limit]})

@app.route('/api/song/<song_id>/stream-url', methods=['GET'])
def get_stream_url(song_id):
    """
    In production this would use ytmusicapi to get the actual stream URL.
    For demo, we return a sample audio URL.
    """
    # ytmusicapi integration point:
    # from ytmusicapi import YTMusic
    # yt = YTMusic()
    # song_info = yt.get_song(song_id)
    # stream_url = song_info['streamingData']['adaptiveFormats'][0]['url']
    
    # Demo audio samples
    demo_urls = [
        "https://www.soundjay.com/music/sounds/electronic-1.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    ]
    
    song = next((s for s in SAMPLE_SONGS if s['id'] == song_id), None)
    if not song:
        return jsonify({"error": "Song not found"}), 404
    
    # Return consistent URL for same song (based on hash)
    url_index = hash(song_id) % len(demo_urls)
    
    return jsonify({
        "song_id": song_id,
        "stream_url": demo_urls[url_index],
        "song": song
    })

@app.route('/api/lyrics/<song_id>', methods=['GET'])
def get_lyrics(song_id):
    """
    Placeholder for lyrics - in production would use ytmusicapi or genius API
    """
    song = next((s for s in SAMPLE_SONGS if s['id'] == song_id), None)
    if not song:
        return jsonify({"lyrics": None, "message": "Lirik tidak tersedia"})
    
    # Demo lyrics
    sample_lyrics = [
        "🎵 Verse 1:",
        f"Di bawah langit biru yang indah",
        f"Kudengar melodi {song['title']}",
        f"Memenuhi setiap sudut hatiku",
        f"Membawaku terbang tinggi",
        "",
        "🎵 Chorus:",
        f"Oh {song['artist']}, lagumu menyentuh jiwa",
        f"Setiap nada adalah cerita",
        f"Yang mengalir dalam darahku",
        f"Tak pernah lelah kudengarkan",
        "",
        "🎵 Verse 2:",
        f"Irama yang mengalun lembut",
        f"Membawa kenangan indah",
        f"Saat kita bersama dulu",
        f"Dalam dekapan musikmu",
        "",
        "🎵 Bridge:",
        f"Genre {song['genre']} yang kupuja",
        f"Mood {song['mood']} yang kurasa",
        f"Tak ada yang bisa gantikan",
        f"Melodi dari {song['artist']}",
        "",
        "🎵 Outro:",
        f"Dan terus mengalun selamanya...",
        f"Musik ini untuk kita semua..."
    ]
    
    return jsonify({
        "lyrics": "\n".join(sample_lyrics),
        "source": "Demo",
        "available": True
    })

# Untuk development lokal jalankan: python app.py
if __name__ == '__main__':
    app.run(debug=True, port=5000)

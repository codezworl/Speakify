from flask import Flask, render_template, request, send_file, flash
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from main.py
from main import app

# This is the handler that Vercel will use
app = app